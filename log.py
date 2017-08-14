import json
import json_log_formatter

class Log:

    def config_log(self):
        formatter = json_log_formatter.JSONFormatter()
        json_handler = logging.FileHandler(filename='./device_logs/logs.json')
        json_handler.setFormatter(formatter)
        logger = logging.getLogger('log')
        logger.addHandler(json_handler)
        logger.setLevel(logging.INFO)
