var async               = require("async"),
    wifi_manager        = require("./app/wifi_manager")(),
    dependency_manager  = require("./app/dependency_manager")(),
    config              = require("./config.json"),
    ping                = require("net-ping").createSession(),
    api                 = require('./app/api');

/*****************************************************************************\
    1. Check for an existing internet connection
    2. Check for dependencies
    3. Check to see if we are connected to a wifi AP
    4. If connected to a wifi, do nothing -> exit
    5. Convert system to act as a AP (with a configurable SSID)
    6. Host a lightweight HTTP server which allows for the user to connect and
       configure the system's wifi connection. The interfaces exposed are RESTy so
       other applications can similarly implement their own UIs around the
       data returned.
    7. Once the system is successfully configured, reset it to act as a wifi
       device (not AP anymore), and setup its wifi network based on what the
       user picked.
    8. At this stage, the system is named, and has a valid wifi connection which
       its bound to, reboot the system and re-run this script on startup.
\*****************************************************************************/
async.series([

    // Ensure a wireless interface actually exists
    function test_if_wireless_interface_exists(next_step) {
        wifi_manager.get_wifi_interface_name(function (error, interface) {
            if (!interface) {
                console.log("\nNo Wifi interface found. Exiting.");
                process.exit(0);
            }
            next_step(error);
        });
    },

    // Ensure we don't already have an active internet connection
    function test_is_internet_up(next_step) {
        ping.pingHost('www.google.com', function (error, target) {
            if (!error) {
                console.log("There is an existing internet connection. Exiting.")
                process.exit(0);
            }
            next_step();
        });
    },

    // Ensure we have the required dependencies installed
    function check_deps(next_step) {
        var deps = ["dhcpd", "hostapd", "iw"]
        dependency_manager.check_deps({
            "binaries": deps
        }, function(error) {
            if (error) {
                console.log("\nOne or more dependencies missing, attempting to install dependencies.");
                dependency_manager.install_binary_deps(deps, next_step)
            } else {
                next_step();
            }
        });
    },

    // Ensure Wifi isn't already connected
    function test_is_wifi_enabled(next_step) {
        wifi_manager.is_wifi_enabled(function(error, result_ip) {
            if (result_ip) {
                console.log("\nWifi is enabled, and IP " + result_ip + " assigned");
                process.exit(0);
            } else {
                console.log("\nWifi is not enabled, Enabling AP for self-configure");
            }
            next_step(error);
        });
    },

    // Turn system into an access point
    function enable_system_ap(next_step) {
        wifi_manager.enable_ap_mode(config.access_point.ssid, function(error) {
            if(error) {
                console.log("... AP Enable ERROR: " + error);
            } else {
                console.log("... AP Enable Success!");
            }
            next_step(error);
        });
    },

    // Host HTTP server for wifi configuration
    function start_http_server(next_step) {
        api(wifi_manager, next_step);
    }

], function(error) {
    if (error) {
        console.log("ERROR: " + error);
    }
});
