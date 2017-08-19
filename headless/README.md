# captive-wifi-configuration

A Node application which makes connecting your SoC to your wifi network easier.

These directions are for Archlinux ARM but can be easily adapted to other OSes.

## Why?

I manage a lot of different Raspberry Pis and Raspberry Pi-like devices, and I frequently need a way to configure wifi as part of its setup. This is one of the only steps that requires manual intervention most of the time, having to plug it into a network and log in to configure the SSH.

Most IoT devices have some way to help configure the WiFi network, so that's what I wanted to do.

This is based on the raspberry-wifi-config repo from sabhiram.

That in turn broadly follows these [instructions](http://www.maketecheasier.com/set-up-raspberry-pi-as-wireless-access-point/) in setting up a RaspberryPi as a wireless AP.

## Requirements

- Archlinux ARM (or adapt these instructions for your OS)

## Install

```sh
$sudo pacman -Sy bower dhcp hostapd
$sudo mkdir -p /opt/wifi-config
$cd /opt/wifi-config
$sudo git clone https://github.com/bmcclure/captive-wifi-configuration.git .
$npm update
$bower install
$sudo npm start
```

#### Gotchas

The `hostapd` application does not like to behave itself on some wifi adapters (RTL8192CU et al). This link does a good job explaining the issue and the remedy: [Edimax Wifi Issues](http://willhaley.com/blog/raspberry-pi-hotspot-ew7811un-rtl8188cus/). The gist of what you need to do is as follows:

```sh
# run iw to detect if you have a rtl871xdrv or nl80211 driver
$iw list
```

If the above says `nl80211 not found.` it means you are running the `rtl871xdrv` driver and probably need to update the `hostapd` binary as follows:
```sh
$cd raspberry-wifi-conf
$sudo mv /usr/sbin/hostapd /usr/sbin/hostapd.OLD
$sudo mv assets/bin/hostapd.rtl871xdrv /usr/sbin/hostapd
$sudo chmod 755 /usr/sbin/hostapd
```

Note that the `wifi_driver_type` config variable is defaulted to the `nl80211` driver. However, if `iw list` fails on the app startup, it will automatically set the driver type of `rtl871xdrv`. Remember that even though you do not need to update the config / default value - you will need to use the updated `hostapd` binary bundled with this app.

TODO: Automatically maintain the correct version of `hostapd` based on the `wifi_driver_type`.

## Usage

This is approximately what occurs when we run this app:

1. Check to see if we are connected to a wifi AP
2. If connected to a wifi, do nothing -> exit
3. (if not wifi, then) Convert system to act as an AP (with a configurable SSID)
4. Host a lightweight HTTP server which allows for the user to connect and configure the system's wifi connection. The interfaces exposed are RESTy so other applications can similarly implement their own UIs around the data returned.
5. Once the system is successfully configured, reset it to act as a wifi device (not AP anymore), and setup it's wifi network based on what the user selected.
6. At this stage, the system is named, and has a valid wifi connection which it is now bound to.

```sh
$cd /opt/wifi-config
$sudo node server.js < /dev/null &
```

## User Interface

In the default config file, the static ip when in AP mode is set to `192.168.44.1` and the AP's broadcast SSID to `wifi-config-ap`.

Connect as follows:

1. Power on the system which runs this app on startup (assume it is not configured for a wifi connection). Once it boots up, you will see `wifi-config-ap` among the wifi connections.  The password is configured in config.json (the default is `piconfig`).
2. Join the network, and navigate to the static IP and port we set in config.json (`http://192.168.44.1:88`).
3. Select your preferred network, enter the wifi passcode if any, and click `Submit`. You are done!

## Testing

TODO

## TODO

1. Automate the deployment of alternate `hostapd` application
2. Automate provisioning of the application dependencies
3. Make the running of scripts cleaner and more easy to read
4. Add tests
5. Add travis ci / coveralls hook(s)
