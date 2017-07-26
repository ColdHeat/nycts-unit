const express = require('express');
const app = express();
const bonjour = require('bonjour')()

let config = {
  "client_id" : 29,
  "dev": true,
  "image_file": "emoji.png",
  "text_line_1": "HAPPY HOUR 4-8PM",
  "text_line_2": "$2 SHOT  $3 PBR  $4 WELL",
  "weather_zip": 11237,
  "transition_time": 0.05
};

app.get('/', function (req, res) {
  res.json(config)
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!')
});

bonjour.publish({ name: 'NYCTS', type: 'http', port: 3000 })
