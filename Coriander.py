"""
DocString
"""
import logging
import sys
from sdktools import sdk_manager, emulator_wrapper ,adb_wrapper
#import  sdktools.sdk_manager


class Coriander(object):
    #Space for shared (usually non-mutable data members)

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.sdk_manager = sdk_manager.SdkManager()
        self.emulator_wrapper = emulator_wrapper.EmulatorWrapper(self.sdk_manager)
        self.adb_wrapper = adb_wrapper.AdbWrapper(self.sdk_manager)


def main():
        coriander = Coriander()

if __name__ == "__main__":
    main()
