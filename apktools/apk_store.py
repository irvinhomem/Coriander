
import logging
import os
import json
import csv
import requests
from contextlib import closing
from itertools import islice
import codecs


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
        self.apk_store_path_type = path_type
        self.apk_data_source = ''

        self.apk_files_path = self.loaded_config_file['config'][self.apk_store_path_type]['apk_path']
        self.logger.debug('APK Config Path: {}'.format(self.apk_files_path))
        self.apk_data_source = self.loaded_config_file['config']['apk_dataset']['apk_url']
        self.logger.debug('APK Dataset Source (csv): {}'.format(self.apk_data_source))

        self.apk_path_API_key = ''
        if self.apk_store_path_type == 'remote':
            self.apk_path_API_key = self.loaded_config_file['config'][self.apk_store_path_type]['api_key']
            self.logger.debug('API Key: {}'.format(self.apk_path_API_key))

    def read_config_file(self, configPath):
        self.logger.debug("Config Path: %s" % str(configPath))
        with open(configPath) as data_file:
            data = json.load(data_file)
            #self.logger.debug("APK Config Path (in func): %s" % str(data['config'][apk_path_type]['apk_path']))

        #return str(data['config'][apk_path_type]['apk_path'])
            return data

    def get_an_apk(self, file_name):
        apk_file = None

        if self.apk_store_path_type == 'local':
            #Pick file from local path
            self.logger.debug('Getting APK from local path: {}'.format(self.apk_store_path_type))
        elif self.apk_store_path_type == 'remote':
            self.logger.debug('Getting APK from REMOTE path: {}'.format(self.apk_store_path_type))
            # https://androzoo.uni.lu/api/download?apikey=${APIKEY}&sha256=${SHA256}
            params = {'apikey': self.apk_path_API_key, 'sha256': file_name}
            #resp = requests.post(self.apk_files_path, data=params)
            resp = requests.get(self.apk_files_path, data=params)
            self.logger.debug('Respose Code: \n {}:{}'.format(resp.status_code, resp.reason))
            self.logger.debug('Respose: \n {}'.format(resp.text))

        return apk_file

    def get_all_apk_filenames_from_source(self, mal_state):
        url = self.apk_data_source
        self.logger.debug("Current APK Source: {}".format(url))
        apk_filenames = []
        with closing(requests.get(url, stream=True)) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
            # Picking all the filenames from the data source
            # for row in reader:
            #     apk_filenames.append(row[0])
            #     self.logger.debug('APK SHA256 (name): {}'.format(row[0]))

            # Picking only the first 10 file names
            row_zero = next(reader)
            vt_detection_idx = row_zero.index('vt_detection')
            self.logger.debug("vt_detection INDEX: {}".format(vt_detection_idx))
            for row in islice(reader, 10):
                if mal_state == 'malicious':
                    if int(row[vt_detection_idx]) > 0:
                        apk_filenames.append(row[0])
                        self.logger.debug('APK SHA256 (name): {}'.format(row[0]))
                        # print("SHA256: {}".format(row[0]))
                        # print(row)
                elif mal_state == 'benign':
                    if int(row[vt_detection_idx]) == 0:
                        apk_filenames.append(row[0])
                        self.logger.debug('APK SHA256 (name): {}'.format(row[0]))
                        # print("SHA256: {}".format(row[0]))
                        # print(row)

        return  apk_filenames

    def get_all_apk_file_data_from_source(self, mal_state):
        url = self.apk_data_source
        self.logger.debug("Current APK Source: {}".format(url))
        apk_file_data = []
        with closing(requests.get(url, stream=True)) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
            # Picking all the filenames from the data source
            # for row in reader:
            #     apk_file_data.append(row)
            #     self.logger.debug('APK SHA256 (name): {}'.format(row))

            # Picking only the first 10 file names
            row_zero = next(reader)
            vt_detection_idx = row_zero.index('vt_detection')
            self.logger.debug("vt_detection INDEX: {}".format(vt_detection_idx))
            for row in islice(reader, 10):
                if mal_state == 'malicious':
                    if int(row[vt_detection_idx]) > 0:
                        apk_file_data.append(row)
                        self.logger.debug('APK SHA256 (name): {}'.format(row))
                        # print("SHA256: {}".format(row[0]))
                        # print(row)
                elif mal_state == 'benign':
                    if int(row[vt_detection_idx]) == 0:  #row[0].index('vt_detection')
                        apk_file_data.append(row)
                        self.logger.debug('APK SHA256 (name): {}'.format(row))

        return  apk_file_data
