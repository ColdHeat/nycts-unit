const piWifi = require('pi-wifi');

piWifi.restartInterface('wlan0', function(err) {
  if (err) {
    return console.error(err.message);
  }
  console.log('Interface raised succesfully!');
});
