const express = require('express');
const app = express();
const mdns = require('mdns');
const fs = require('fs');
const multer = require('multer');
const bodyParser = require('body-parser');

let jsonParser = bodyParser.json();

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

let config = require('./config.json');

let ad = mdns.createAdvertisement(mdns.tcp('http-nycts'), 3000, {
  name: 'NYCTrainSign-' + config["settings"]["name"]
});
ad.start();

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
const checkPin = pin => {
  var fileContents;
  try {
    fileContents = fs.readFileSync('pin', 'utf-8');
    json = JSON.parse(fileContents);
    if (pin === json.pin) {
      return true;
    }
  } catch (err) {
    // Here you get the error when the file was not found,
    // but you also get any other error
  }
  return false;
};

const setPin = pin => {
  const fileContents = {
    pin: pin
  };
  const json = JSON.stringify(fileContents);
  fs.writeFile('./pin', json, 'utf8', function(err) {
    if (err) {
      return console.log(err);
    }
    console.log('The file was saved!');
  });
};

app.get('/', function(req, res) {
  res.json(config);
});

app.get('/getConfig', function(req, res) {
  res.json(config);
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
});
