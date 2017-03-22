
import logging
import os
import json
import requests

class ApkStore(object):

    def __init__(self, path_type):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.apk_files_path = ''
        self.config_loc = os.path.join('config', 'APK_PATH.json')
        self.loaded_config_file = self.read_config_file(self.config_loc)

        self.apk_files_path = self.loaded_config_file['config'][path_type]['apk_path']

        self.logger.debug('APK Config Path: {}'.format(self.apk_files_path))

    def read_config_file(self, configPath):
        self.logger.debug("Config Path: %s" % str(configPath))
        with open(configPath) as data_file:
            data = json.load(data_file)
            #self.logger.debug("APK Config Path (in func): %s" % str(data['config'][apk_path_type]['apk_path']))

        #return str(data['config'][apk_path_type]['apk_path'])
            return data

    def get_api_key_from_config(self):

    def get_apk_path_from_config(self, path_type):
        # apk_path = ''
        # if type == 'local':
        #     apk_path = self.loaded_config_file['config'][type]['apk_path']
        # elif type == 'remote':
        #     self.apk_files_path = self.set_up_remote_from_config(self.config_loc, type)

        return self.loaded_config_file['config'][path_type]['apk_path']

    def get_an_apk(self, path_type):
        apk_file = None

        if path_type == 'local':

        elif path_type == 'remote':
            requests.post(self.apk_files_path)


        return apk_file

    def set_up_remote_from_config(self, config_loc, path_type):
        self.read_config_file(config_loc, path_type)
