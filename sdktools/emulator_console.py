import logging
from telnetlib import Telnet
import os
import time

class EmulatorConsole(object):
    '''
    Telnet connection through emulator console is needed so as to kill the emulator at the end of the process,
    but also in preparation for "snapshotting" when the Google eventually fixes the snapshotting capabilties. They seem
    to have been there, but are currently disabled or not working at the momment (the directives are still there in 
    the -help command).
    '''
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
        self.logger.debug('++++++++++++++++ TELNET OUTPUT ++++++++++++++++')
        self.logger.debug('Telnet OUTPUT: {}'.format(self.telnet_conn.read_until(b"OK")))

    def read_auth_token(self, file_path):

        self.logger.debug("Config Path: %s" % str(file_path))
        with open(file_path) as token_file:
            data = token_file.read().replace('\n','')
            # self.logger.debug("APK Config Path (in func): %s" % str(data['config'][apk_path_type]['apk_path']))

            # return str(data['config'][apk_path_type]['apk_path'])
            return data

    def run_tty_command(self, cmd):
        self.logger.debug('++++++++++++++++++++')
        self.logger.debug("TELNET COMMAND: {}".format(cmd))
        self.logger.debug('++++++++++++++++++++')
        self.telnet_conn.write(cmd.encode('ascii') + b'\n')
        try:
            self.logger.debug('Telnet might throw an error here if the connection closes ...')
            self.logger.debug('Telnet OUTPUT: {}'.format(self.telnet_conn.read_until(b"OK")))
        except ConnectionResetError:
            self.logger.error("Telnet Connection was INTENTIONALLY closed. But still throws an error")
            self.logger.error('Just Continue ...')
        self.logger.debug('--------------------------------------------------')
        self. logger.debug('------  CLEANING UP AFTER Telnet Command   ------')
        self.logger.debug('--------------------------------------------------')

    def run_kill_command(self):
        cmd = 'kill'
        self.logger.debug('++++++++++++++++++++')
        self.logger.debug("TELNET kill COMMAND: {}".format(cmd))
        self.logger.debug('++++++++++++++++++++')
        try:
            self.telnet_conn.write(cmd.encode('ascii') + b'\n')
            self.logger.debug('Telnet OUTPUT: {}'.format(self.telnet_conn.read_until(b"Connection to host lost.")))
            self.logger.debug('-------------------------------------------------------------------------')
            self.logger.debug('*************** MANAGED TO CLOSE WITHOUT A PROBLEM **********************')
            self.logger.debug('-------------------------------------------------------------------------')
            #self.telnet_conn.close()
        except ConnectionResetError as err:
            self.logger.debug("Error Msg: {}".format(err.strerror))
            self.logger.error("Telnet Connection was INTENTIONALLY closed. But still throws an error")
            self.logger.error('Just Continue ...')
        #if self.telnet_conn.
        #self.telnet_conn.close()
        self.logger.debug('----------------------------------------------------------------')
        self.logger.debug('------  CLEANING UP AFTER Telnet Emulator Kill Command   ------')
        self.logger.debug('----------------------------------------------------------------')
        time.sleep(5)