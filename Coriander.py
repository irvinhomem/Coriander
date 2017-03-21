"""
DocString
"""
import logging
import sys
from sdktools import sdk_manager
#import  sdktools.sdk_manager
from apktools import apk_store
from cookbook import recipe


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
        self.apk_store = apk_store.ApkStore()

        # self.my_recipe = recipe.Recipe(self.sdk_manager.get_emulator_instance(0),
        #                                self.sdk_manager.get_adb_instance(0),
        #                                self.apk_store)
        self.my_recipe = recipe.Recipe(self.sdk_manager, self.apk_store, instructions)
        # self.emulator_wrapper = emulator_wrapper.EmulatorWrapper(self.sdk_manager)
        # self.adb_wrapper = adb_wrapper.AdbWrapper(self.sdk_manager)


def main():
        coriander = Coriander()

if __name__ == "__main__":
    main()
