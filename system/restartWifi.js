const piWifi = require('pi-wifi');

piWifi.detectSupplicant(function(err, iface, configFile) {
  if (err) {
    return console.error(err.message);
  }
  console.log('Supplicant running in interface', iface, 'using the configuration file', configFile);
});


piWifi.interfaceDown('wlan0', function(err) {
  if (err) {
    return console.error(err.message);
  }
  console.log('Interface dropped succesfully!');
});

piWifi.interfaceUp('wlan0', function(err) {
  if (err) {
    return console.error(err.message);
  }
  console.log('Interface raised succesfully!');
});
