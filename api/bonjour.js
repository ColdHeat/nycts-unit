const mdns = require('mdns');
let config = require('./config.json');

let ad = mdns.createAdvertisement(mdns.tcp('http-nycts'), 3000, {
  name: 'NYCTrainSign-' + config["settings"]["name"] + "-" + Date.now()
});
ad.start();

const restart = () => {
  ad.stop();
  ad.start();
}

setInterval(() => { restart() }, 300000)
