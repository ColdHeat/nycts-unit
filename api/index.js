const express = require('express');
const app = express();
const fs = require('fs');
const deviceModule = require('./device');
let config = require('./config.json');
const multer = require('multer');
const bodyParser = require('body-parser');
let jsonParser = bodyParser.json();
const fetch = require('node-fetch');
const PROD_API_KEY = 'rKlRPviE105H3paeGQyo9u7NGjhaauQ7TvyYSv91';
const GET_CONFIG_URL = 'https://api.trainsignapi.com/prod-get-config/get';

//begin module
const jsonReplacer = (key, value) => {
  if (value === 'false') return false;
  if (value === 'true') return true;
  return value;
};
let storage = multer.diskStorage({
  destination: function(req, file, cb) {
    cb(null, __dirname + '/uploads/');
  },
  filename: function(req, file, cb) {
    cb(null, 'emoji.jpg');
  }
});
let upload = multer({
  storage: storage
});


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

   device.subscribe(`set_config/${config.settings.sign_id}`);

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
         console.log(payload.toString());
      });

}
const sleep = (time) => {
  return new Promise((resolve) => setTimeout(resolve, time));
}
const getNewConfig = (callback) => {
  const params = {
  method: 'POST',
  timeout: 5000,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'x-api-key': PROD_API_KEY
  },
  body: JSON.stringify({
    clientId: config['settings']['client_id']
  })
};

fetch(GET_CONFIG_URL, params)
  .then(response => {
    return response.json();
  })
  .then(json => {
    let newConfig = json[config['settings']['sign_id']];
    callback(newConfig);
  })
  .catch(err => {
    console.log(err);
    sleep(2000).then(() => {
      getNewConfig(callback);
    })
  });
}

if(fs.existsSync('./config.json')) {
  getNewConfig((newConfig) => {
    config = newConfig;
    writeToConfigFile(() => { void(0) });
  })
}


app.get('/', function(req, res) {
  res.send("Hello darkness my old friend, I've come to talk with you again.");
});

app.get('/getConfig', function(req, res) {
  res.json(config);
});
app.get('/getNewConfig', function(req, res) {
  if(fs.existsSync('./config.json')) {
    getNewConfig((newConfig) => {
      config = newConfig;
      writeToConfigFile(() => {
        res.json(config)
      });
    })
  }
  else {
    res.json({ error: 'error' });
  }
});

app.get('/setConfig/:route/:settingKey/:settingValue', function(req, res) {
  let value = req.params.settingValue;
  if (
    value === 'false' &&
    typeof config[req.params.route][req.params.settingKey] === 'boolean'
  )
    value = false;
  if (value === 'true') value = true;

  config[req.params.route][req.params.settingKey] = value;
  writeToConfigFile(() => res.json(config));
});

app.get('/getLogo', function(req, res) {
  res.sendFile(config.logo.image_file, { root: __dirname + '/uploads/' });
});

app.post('/setLogo', upload.single('image'), function(req, res) {
  config['logo']['updated'] = true;
  res.json(req.body);
});

app.post('/checkPin', jsonParser, function(req, res) {
  const isRight = checkPin(req.body.pin);
  res.json(isRight);
});

app.post('/setPin', jsonParser, function(req, res) {
  setPin(req.body.pin);
  res.json(req.body);
});

app.listen(3000, function() {
  console.log('NYC Train Sign Server listening on port 3000!');
  sub();
});
