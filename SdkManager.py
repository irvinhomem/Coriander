
import logging
import os
import platform
import getpass


class SdkManager(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.android_SDK_path = self.find_android_sdk_path()

    def find_android_sdk_path(self):
        sdk_path = ''
        self.logger.debug('*************************')
        self.logger.debug('Config Info:')
        self.logger.debug('------------------------')
        os_name = os.name
        self.logger.debug("OS:\t %s" % os_name)
        platform_system = platform.system()
        self.logger.debug('Platform System:\t %s' % platform_system)
        user_name = getpass.getuser()
        self.logger.debug('Username:\t %s' % platform_system)
        home_dir = os.path.expanduser('~')
        self.logger.debug("Home Directory:\t %s " % home_dir)
        self.logger.debug('*************************')


        return sdk_path

    def get_android_sdk_path(self):
        return