
import logging
import os
import platform

import sdktools.sdk_manager


class AdbWrapper(object):

    def __init__(self, sdkManager):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.adb_loc = ''

        self.set_adb_location(sdkManager.get_android_sdk_path())

    def set_adb_location(self, sdk_path):
        platform_tools_path = 'platform-tools'

        if platform.system() == 'Windows':
            self.adb_loc = os.path.join(sdk_path, platform_tools_path, 'adb.exe')
        elif platform.system() == 'Linux':
            self.adb_loc = os.path.join(sdk_path, platform_tools_path, 'adb')
        elif platform.system() == 'Darwin':
            self.adb_loc = os.path.join(sdk_path, platform_tools_path, 'adb')

        self.get_adb_loc()

    def get_adb_loc(self):
        if self.adb_loc == '':
            self.logger.error("ADB Path not set!")
            exit()
        else:
            self.logger.info('ADB Path: %s' % self.adb_loc)

        return self.adb_loc


