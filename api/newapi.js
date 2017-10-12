const fs = require('fs');
const deviceModule = require('./device');
let config = require('./config.json');

//begin module
const jsonReplacer = (key, value) => {
  if (value === 'false') return false;
  if (value === 'true') return true;
  return value;
};

const writeToConfigFile = callback => {
  fs.writeFile(
    './config.json',
    JSON.stringify(config, jsonReplacer, '  '),
    err => {
      if (err) console.log(err);
      callback();
    }
  );
};

const setConfig = (setting, key, value) => {
  if (
    value === 'false' &&
    typeof config[setting][key] === 'boolean'
  )
    value = false;
  if (value === 'true') value = true;

  config[setting][key] = value;
  writeToConfigFile(() => console.log('done'));

}

const sub = () => {

   const device = deviceModule({
      keyPath: 'NYCTS-Unit.private.key',
      certPath: 'NYCTS-Unit.cert.pem',
      caPath: 'root-CA.crt',
      host: "a1cnhiys64c1si.iot.us-east-1.amazonaws.com",
   });

   device.subscribe(`set_config/${config.settings.client_id}`);

   device
      .on('connect', function() {
         console.log('connect');
      });
   device
      .on('close', function() {
         console.log('close');
      });
   device
      .on('reconnect', function() {
         console.log('reconnect');
      });
   device
      .on('offline', function() {
         console.log('offline');
      });
   device
      .on('error', function(error) {
         console.log('error', error);
      });
   device
      .on('message', function(topic, payload) {
         let newConfig = JSON.parse(payload);
         setConfig(newConfig.setting, newConfig.key, newConfig.value);
         console.log(JSON.parse(payload).toString());
      });

}

sub();
