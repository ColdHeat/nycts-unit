const mdns = require('mdns');
let config = require('./config.json');

const createAd = () => {
  let newAd = mdns.createAdvertisement(mdns.tcp('http-nycts'), 3000, {
    name: 'NYCTrainSign-' + config["settings"]["name"] + "-" + Date.now()
  });
  return newAd;
}
let ad = createAd();
ad.start();

const restart = () => {
  ad.stop();
  ad = createAd();
  ad.start();
}

setInterval(() => { restart() }, 300000)
