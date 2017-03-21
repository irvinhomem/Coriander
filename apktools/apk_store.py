
import logging
import os
import json

class ApkStore(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.config_loc = os.path.join('config', 'APK_PATH.json')
        self.apk_files_path = self.read_config_file(self.config_loc)

        self.logger.debug('APK Config Path: {}'.format(self.apk_files_path))

    def read_config_file(self, configPath):
        self.logger.debug("Config Path: %s" % str(configPath))
        with open(configPath) as data_file:
            data = json.load(data_file)
            self.logger.debug("APK Config Path (in func): %s" % str(data['config']['apk_path']))

        return str(data['config']['apk_path'])

    def get_an_apk(self):
        apk_file = None


        return apk_file