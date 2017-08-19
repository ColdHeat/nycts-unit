var _         = require("underscore")._,
    async     = require("async"),
    fs        = require("fs"),
    systemctl = require("./systemctl")(),
    exec      = require("child_process").exec,
    config    = require("../config.json"),
    iwconfig  = require("./iwconfig");

// Better template format
_.templateSettings = {
    interpolate: /\{\{(.+?)\}\}/g,
    evaluate :   /\{\[([\s\S]+?)\]\}/g
};

// Helper function to write a given template to a file based on a given context
function write_template_to_file(template_path, file_name, context, callback) {
    async.waterfall([

        function read_template_file(next_step) {
            fs.readFile(template_path, {encoding: "utf8"}, next_step);
        },

        function update_file(file_txt, next_step) {
            var template = _.template(file_txt);
            fs.writeFile(file_name, template(context), next_step);
        }

    ], callback);
}

/*****************************************************************************\
    Return a set of functions which we can use to manage and check our wifi
    connection information
\*****************************************************************************/
module.exports = function() {
    // Detect which wifi driver we should use, the rtl871xdrv or the nl80211
    exec("iw list", function(error, stdout, stderr) {
        if (stderr.match(/^nl80211 not found/)) {
            config.wifi_driver_type = "rtl871xdrv";
        }
        // console.log("config.wifi_driver_type = " + config.wifi_driver_type);
    });

    // Hack: this just assumes that the outbound interface will be "wlan0"

    // Define some globals
    var ifconfig_fields = {
        "hw_addr":         /HWaddr\s([^\s]+)/,
        "inet_addr":       /inet addr:([^\s]+)/,
    },  iwconfig_fields = {
        "ap_addr":         /Access Point:\s([^\s]+)/,
        "ap_ssid":         /ESSID:\"([^\"]+)\"/,
        "unassociated":    /(unassociated)\s+Nick/,
    };

    // TODO: wifi-config-ap hardcoded, should derive from a constant

    // Get generic info on an interface
    var _get_wifi_info = function(callback) {
        var output = {
            hw_addr:      "<unknown>",
            inet_addr:    "<unknown>",
            ap_addr:      "<unknown_ap>",
            ap_ssid:      "<unknown_ssid>",
            unassociated: "<unknown>",
        };

        // Inner function which runs a given command and sets a bunch
        // of fields
        function run_command_and_set_fields(cmd, fields, callback) {
            exec(cmd, function(error, stdout, stderr) {
                if (error) return callback(error);
                for (var key in fields) {
                    re = stdout.match(fields[key]);
                    if (re && re.length > 1) {
                        output[key] = re[1];
                    }
                }
                callback(null);
            });
        }

        // Run a bunch of commands and aggregate info
        async.series([
            function run_ifconfig(next_step) {
                run_command_and_set_fields("ifconfig " + config.wifi_interface, ifconfig_fields, next_step);
            },
            function run_iwconfig(next_step) {
                run_command_and_set_fields("iwconfig " + config.wifi_interface, iwconfig_fields, next_step);
            },
        ], function(error) {
            return callback(error, output);
        });
    },

    _restart_wireless_network = function(wlan_iface, callback) {
        async.series([
            function down(next_step) {
                exec("sudo ip link set " + wlan_iface + " down", function(error, stdout, stderr) {
                    if (!error) console.log("ifdown " + wlan_iface + " successful...");
                    next_step();
                });
            },
            function up(next_step) {
                exec("sudo ip link set " + wlan_iface + " up", function(error, stdout, stderr) {
                    if (!error) console.log("ifup " + wlan_iface + " successful...");
                    next_step();
                });
            },
        ], callback);
    },

    _get_wifi_interface_name = function(callback) {
        iwconfig.status(function(error, status) {
            callback(error, status[0]['interface'] || null);
        });
    }

    // Wifi related functions
    _is_wifi_enabled_sync = function(info) {
        // If we are not an AP, and we have a valid
        // inet_addr - wifi is enabled!
        if (null        == _is_ap_enabled_sync(info) &&
            "<unknown>" != info["inet_addr"]         &&
            "<unknown>" == info["unassociated"] ) {
            return info["inet_addr"];
        }
        return null;
    },

    _is_wifi_enabled = function(callback) {
        _get_wifi_info(function(error, info) {
            if (error) return callback(error, null);
            return callback(null, _is_wifi_enabled_sync(info));
        });
    },

    // Access Point related functions
    _is_ap_enabled_sync = function(info) {
        // If the hw_addr matches the ap_addr
        // and the ap_ssid matches "wifi-config-ap"
        // then we are in AP mode
        var is_ap  =
            info["hw_addr"].toLowerCase() == info["ap_addr"].toLowerCase() &&
            info["ap_ssid"] == config.access_point.ssid;
        return (is_ap) ? info["hw_addr"].toLowerCase() : null;
    },

    _is_ap_enabled = function(callback) {
        _get_wifi_info(function(error, info) {
            if (error) return callback(error, null);
            return callback(null, _is_ap_enabled_sync(info));
        });
    },

    // Enables the accesspoint w/ bcast_ssid. This assumes that both
    // isc-dhcp-server and hostapd are installed using:
    // $sudo npm run-script provision
    _enable_ap_mode = function(bcast_ssid, callback) {
        _is_ap_enabled(function(error, result_addr) {
            if (error) {
                console.log("ERROR: " + error);
                return callback(error);
            }

            if (result_addr && !config.access_point.force_reconfigure) {
                console.log("\nAccess point is enabled with ADDR: " + result_addr);
                return callback(null);
            } else if (config.access_point.force_reconfigure) {
                console.log("\nForce reconfigure enabled - reset AP");
            } else {
                console.log("\nAP is not enabled yet... enabling...");
            }

            var context = config.access_point;
            context["enable_ap"] = true;
            context["wifi_driver_type"] = config.wifi_driver_type;

            // Here we need to actually follow the steps to enable the ap
            async.series([
                function disable_auto_wifi(next_step) {
                    systemctl.stop('netctl-auto@' + context["wifi_interface"], next_step)
                },

                // Enable the access point ip and netmask + static
                // DHCP for the wlan0 interface
                function update_interfaces(next_step) {
                    write_template_to_file(
                        "./assets/etc/systemd/network/wifi.network.template",
                        "/etc/systemd/network/" + context["wifi_interface"] + ".network",
                        context, next_step);
                },

                // Enable DHCP conf, set authoritative mode and subnet
                function update_dhcpd(next_step) {
                    var context = config.access_point;
                    // We must enable this to turn on the access point
                    write_template_to_file(
                        "./assets/etc/dhcpd.conf.template",
                        "/etc/dhcpd.conf",
                        context, next_step);
                },

                function copy_custom_dhcpd_service(next_step) {
                    write_template_to_file(
                        "./assets/etc/systemd/system/dhcpd4@.service.template",
                        "/etc/systemd/system/dhcpd4@.service",
                        context, next_step);
                },

                function update_hostapd_conf(next_step) {
                    write_template_to_file(
                        "./assets/etc/hostapd/hostapd.conf.template",
                        "/etc/hostapd/hostapd.conf",
                        context, next_step);
                },

                function reload_systemd(next_step) {
                    systemctl.daemon_reload(next_step);
                },

                function restart_systemd_networkd(next_step) {
                    systemctl.restart('systemd-networkd', next_step);
                },

                function restart_network_interfaces(next_step) {
                    _restart_wireless_network(context.wifi_interface, next_step);
                },

                function restart_dhcp_service(next_step) {
                    systemctl.restart('dhcpd4@' + context.wifi_interface, next_step);
                },

                function restart_hostapd_service(next_step) {
                    systemctl.restart('hostapd', next_step);
                }
                
            ], callback);
        });
    },

    // Disables AP mode and reverts to wifi connection
    _enable_wifi_mode = function(connection_info, callback) {
        _is_wifi_enabled(function(error, result_ip) {
            if (error) return callback(error);

            if (result_ip) {
                console.log("\nWifi connection is enabled with IP: " + result_ip);
                return callback(null);
            }

            async.series([
                function remove_networkd_wifi_profile(next_step) {
                    fs.unlink("/etc/systemd/network/" + context["wifi_interface"] + ".template", next_step);
                },

                function restart_systemd_networkd_service(next_step) {
                    systemctl.restart('systemd-networkd', next_step);
                },

                function update_interfaces(next_step) {
                    write_template_to_file(
                        "./assets/etc/netctl/wifi.template",
                        "/etc/netctl/" + context.wifi_interface,
                        connection_info, next_step);
                },

                function stop_dhcp_service(next_step) {
                    systemctl.stop('dhcpd4@' + context.wifi_interface, next_step);
                },

                function stop_hostapd_service(next_step) {
                    systemctl.stop('hostapd', next_step);
                },

                function enable_netctl_auto(next_step) {
                    systemctl.restart('netctl-auto@' + context.wifi_interface, next_step);
                },

                function restart_network_interfaces(next_step) {
                    _restart_wireless_network(config.wifi_interface, next_step);
                },

            ], callback);
        });

    };

    return {
        enable_ap_mode:           _enable_ap_mode,
        enable_wifi_mode:         _enable_wifi_mode,
        get_wifi_info:            _get_wifi_info,
        is_wifi_enabled:          _is_wifi_enabled,
        is_wifi_enabled_sync:     _is_wifi_enabled_sync,
        is_ap_enabled:            _is_ap_enabled,
        is_ap_enabled_sync:       _is_ap_enabled_sync,
        restart_wireless_network: _restart_wireless_network,
        get_wifi_interface_name:  _get_wifi_interface_name
    };
}
