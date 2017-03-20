
import logging
import os
import platform

import sdktools.sdk_manager


class EmulatorWrapper(object):

    def __init__(self, sdkManager):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.emulator_loc = ''

        self.set_emulator_location(sdkManager.get_android_sdk_path())

    def set_emulator_location(self, sdk_path):
        tools_path = 'tools'

        if platform.system() == 'Windows':
            self.emulator_loc = os.path.join(sdk_path, tools_path, 'emulator.exe')
        elif platform.system() == 'Linux':
            self.emulator_loc = os.path.join(sdk_path, tools_path, 'emulator')
        elif platform.system() == 'Darwin':
            self.emulator_loc = os.path.join(sdk_path, tools_path, 'emulator')

        self.get_emulator_loc()

    def get_emulator_loc(self):
        if self.emulator_loc == '':
            self.logger.error("Emulator Path not set!")
            exit()
        else:
            self.logger.info('Emulator Path: %s' % self.emulator_loc)

        return self.emulator_loc
