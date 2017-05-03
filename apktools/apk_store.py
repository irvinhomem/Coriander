
import logging
import os
import json
import csv
import requests
from contextlib import closing
from itertools import islice
import codecs
import hashlib
from tqdm import tqdm
import datetime

from apktools import apk_file

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
        self.apk_data_source_url = ''
        self.all_apk_data = None
        self.row_zero_header = []

        self.apk_files_path = self.loaded_config_file['config'][self.apk_store_path_type]['apk_path']
        self.logger.debug('APK Config Path: {}'.format(self.apk_files_path))
        self.apk_data_source_url = self.loaded_config_file['config']['apk_dataset']['apk_url']
        self.logger.debug('APK Dataset Source (csv): {}'.format(self.apk_data_source_url))

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

    def get_an_apk(self, file_name, mal_type=''):
        apk = None
        #apk_file_path = ''

        if self.apk_store_path_type == 'local':
            #Pick file from local path
            self.logger.debug('Getting APK from local path: {}'.format(self.apk_store_path_type))
        elif self.apk_store_path_type == 'remote':
            self.logger.debug('Getting APK from REMOTE path: {}'.format(self.apk_store_path_type))
            # https://androzoo.uni.lu/api/download?apikey=${APIKEY}&sha256=${SHA256}
            params = {'apikey': self.apk_path_API_key, 'sha256': file_name}
            #resp = requests.post(self.apk_files_path, data=params)
            resp = requests.get(self.apk_files_path, data=params, stream=True)
            self.logger.debug('Response Code: \n {}:{}'.format(resp.status_code, resp.reason))
            #self.logger.debug('Response: \n {}'.format(resp.text))
            extension = '.apk'

            sub_dir = mal_type
            if sub_dir != '':
                if os.path.exists(os.path.join('downloads', sub_dir)):
                    self.logger.debug('Sub-dir [{}] exists.'.format(sub_dir))
                else:
                    os.mkdir(os.path.join('downloads', sub_dir))
                    self.logger.debug('Created Sub-dir: [{}]'.format(sub_dir))

            temp_filepath = os.path.join('temp', sub_dir, file_name + extension)
            if resp.ok:
                total_size = int(resp.headers.get('content-length'))
                self.logger.info('File Length: {}'.format(total_size))
                with open(temp_filepath, 'wb') as file_handle:
                    # if the file is large we do the writing in chunks
                    # tqdm is a library for a portable progressbar (Default unit is "it" --> number of iterations)
                    for block in tqdm(resp.iter_content(1024), unit='B', total=total_size/1024, unit_scale=True):
                        file_handle.write(block)
                        #currsize = (file_handle/1000000)
                    #apk_file = file_handle
                    #apk_file_path = temp_filepath

                # Check the hash if the transfer has completed successfully
                # Create an APK_File object (checking if parsing went correctly also)
                apk = apk_file.ApkFile(temp_filepath)
                self.logger.debug('Local SHA 256: {}'.format(self.get_sha256_hash(temp_filepath)))
            else:
                self.logger.error("Something went wrong with the file download: {} - {}".format(resp.status_code, resp.reason))

        #return apk_file
        #return apk_file_path
        return apk

    def get_sha256_hash(self, filepath, block_size=65536):
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return str(sha256.hexdigest()).upper()


    def get_all_apk_filenames_from_source(self, mal_state): # This is not used anymore
        url = self.apk_data_source_url
        self.logger.debug("Current APK Source: {}".format(url))
        apk_filenames = []
        with closing(requests.get(url, stream=True)) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
            # Picking all the filenames from the data source
            # for row in reader:
            #     apk_filenames.append(row[0])
            #     self.logger.debug('APK SHA256 (name): {}'.format(row[0]))

            # Picking only the first 10 file names
            self.row_zero_header = next(reader)
            self.logger.debug("Header Row: {}".format(self.row_zero_header))
            vt_detection_idx = self.row_zero_header.index('vt_detection')
            self.logger.debug("vt_detection INDEX: {}".format(vt_detection_idx))
            for row in islice(reader, 10): # This value here [islice(reader,VALUE)] throttles the number of APK's to be downloaded
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

    def get_all_apk_file_data_from_source(self, mal_state):     # THIS is the function that we use in the recipe <---
        url = self.apk_data_source_url
        self.logger.debug("Current APK Source: {}".format(url))
        apk_file_data = []
        with closing(requests.get(url, stream=True)) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
            # Picking all the filenames from the data source
            # for row in reader:
            #     apk_file_data.append(row)
            #     self.logger.debug('APK SHA256 (name): {}'.format(row))

            # ******************************************
            # Picking only the first 10 file names
            # ******************************************
            self.row_zero_header = next(reader)
            self.logger.debug("Header Row: {}".format(self.row_zero_header))
            vt_detection_idx = self.row_zero_header.index('vt_detection')
            self.logger.debug("vt_detection INDEX: {}".format(vt_detection_idx))
            # Approx 3850 to 1000 Malicious samples (1011)
            # Approx 1490 to 1000 Benign samples (1009)
            # This value here [islice(reader, start_point, VALUE)] throttles the number of APK's to be downloaded
            for row in islice(reader, 1263, 5490):
                if row[vt_detection_idx] == '':
                    # Skip because we don't know if the item was classified by VirusTotal as malicious or not (Do nothing)
                    self.logger.debug("Data Store doesn't have value for MALICIOUS OR BENIGN. Skipping ...")
                elif mal_state == 'malicious':
                        if int(row[vt_detection_idx]) > 0:
                            apk_file_data.append(row)
                            self.logger.debug('APK SHA256 (name): {}'.format(row))
                            # print("SHA256: {}".format(row[0]))
                            # print(row)
                elif mal_state == 'benign':
                    if int(row[vt_detection_idx]) == 0:  #row[0].index('vt_detection')
                        apk_file_data.append(row)
                        self.logger.debug('APK SHA256 (name): {}'.format(row))

        self.all_apk_data = apk_file_data

        timestamp = datetime.datetime.now().isoformat().replace(':',"-")
        output_file_path = os.path.join('logs', timestamp + '_LOG.csv')
        self.write_list_to_file(output_file_path, apk_file_data)

        return  apk_file_data

    def write_list_to_file(self, file_path, list_to_write):
        with open(file_path, "w", newline="") as out_file:
            csv_writer = csv.writer(out_file)
            csv_writer.writerows(list_to_write)

    def get_single_column_as_list(self, column_name):
        column_as_list = []
        if len(self.all_apk_data) > 0:
            #header_row = next(self.all_apk_data)
            #col_idx = header_row.index(column_name)
            col_idx = self.row_zero_header.index(column_name)
            column_as_list = [row[col_idx] for row in self.all_apk_data]
            self.logger.debug("First Item in Col: {}".format(column_as_list[0]))
        else:
            self.logger.error('No APK file data loaded from source yet!')
            exit()
        self.logger.debug('Column [{}] List length: {}'.format(column_name, len(column_as_list)))

        return column_as_list

    def get_single_apk_filename_by_index(self, idx):
        apk_filename = ''
        if len(self.all_apk_data) > 0:
            if len(self.all_apk_data)-1 > idx:
                apk_filename = self.all_apk_data[idx]
            else:
                self.logger.error('Index is too large')
                exit()
        else:
            self.logger.error('No APK file data loaded from source yet!')
            exit()
        self.logger.debug('APK Filename: {}'.format(apk_filename))
        return apk_filename
