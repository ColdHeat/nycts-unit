
    ##### WEATHER SCREEN #####
        swap.Clear()

        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = "select item.condition from weather.forecast where woeid in (select woeid from geo.places(1) where text='"+ str(config["weather_zip"]) + "')"
        yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
        try:
            result = urllib2.urlopen(yql_url)
            logger.info('Weather Screen', extra={'status': 1, 'job': 'weather_screen'})
        except urllib2.URLError as e:
            error_message = e.reason
            logger.info('Weather Screen', extra={'status': 0, 'job': 'weather_screen'})
            weather = weather_offline_data['weather']
            conditions = weather_offline_data['conditions']
        else:
            data = json.loads(result.read())
            weather = data['query']['results']['channel']['item']['condition']['temp']
            conditions = data['query']['results']['channel']['item']['condition']['text'].upper()

            weather_offline_data['weather'] = weather
            weather_offline_data['conditions'] = conditions

        weatherImage = Image.new('RGB', (width, height))
        weatherDraw  = ImageDraw.Draw(weatherImage)

        weatherDraw.text((2, 0), 'IT IS ' + weather + ' FUCKING DEGREES' , font=font, fill=red)
        weatherDraw.text((2, 16), '& ' + conditions + ' OUTSIDE', font=font, fill=green)

        swap.SetImage(weatherImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)
