import logging
from telnetlib import Telnet
import os

class EmulatorConsole(object):

    def __init__(self, hostname, port_num):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.host = hostname
        self.port = port_num
        self.telnet_conn = Telnet()

        self.telnet_conn.open(hostname, port_num)
        self.user_home_dir = os.path.expanduser('~')
        self.authtoken_filepath = self.user_home_dir + '/' + '.emulator_console_auth_token'

        auth_token = self.read_auth_token(self.authtoken_filepath)
        self.logger.debug("Auth Token: {}".format(auth_token))

        self.telnet_conn.read_until(b"OK")
        auth_code_cmd = 'auth ' + auth_token
        self.telnet_conn.write(auth_code_cmd.encode('ascii') + b"\n")
        #self.logger.debug('Telnet OUTPUT: {}'.format(self.telnet_conn.read_all()))
        self.logger.debug('**************** TELNET OUTPUT *******************')
        self.logger.debug('Telnet OUTPUT: {}'.format(self.telnet_conn.read_until(b"OK")))

    def read_auth_token(self, file_path):

        self.logger.debug("Config Path: %s" % str(file_path))
        with open(file_path) as token_file:
            data = token_file.read().replace('\n','')
            # self.logger.debug("APK Config Path (in func): %s" % str(data['config'][apk_path_type]['apk_path']))

            # return str(data['config'][apk_path_type]['apk_path'])
            return data