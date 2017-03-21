
import logging


class Recipe(object):

    #def __init__(self, emulator, adb, apk_store):
    def __init__(self, sdk_mgr, apk_store, instructions):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        #self.emulator_instance = emulator
        #self.adb_instance = adb
        self.sdk_manager = sdk_mgr
        self.apk_store = apk_store
        self.instructions = instructions

    def run_recipe(self):
        self.logger.debug(self.instructions)

        emu = self.sdk_manager.get_emulator_instance(0)
        adb = self.sdk_manager.get_adb_instance(0)