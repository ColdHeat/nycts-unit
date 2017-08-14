class api:

    def config_api:
        config = json.loads('{}')
        baseurl = "http://127.0.0.1:3000/getConfig"
        try:
            result = urllib2.urlopen(baseurl)
            logger.info('API Config', extra={'status': 1, 'job': 'api_config'})
        except urllib2.URLError as e:
            logger.info('API Config', extra={'status': 0, 'job': 'api_config'})
        else:
            config = json.loads(result.read())

        dev = config["dev"]

        if config["reboot"] == "1":
            baseurl = "http://127.0.0.1:3000/setConfig/reboot/0"
            try:
                result = urllib2.urlopen(baseurl)
                logger.info('API Reboot', extra={'status': 1, 'job': 'api_reboot'})
            except urllib2.URLError as e:
                error_message = e.reason
                logger.info('API Reboot', extra={'status': 0, 'job': 'api_reboot'})
            else:
                config = json.loads(result.read())
                os.system('reboot now')
