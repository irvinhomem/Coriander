
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
        self.logger.debug("RUNNING RECIPE: {} ". format(self.instructions))

        emu = self.sdk_manager.get_emulator_instance(0)
        adb = self.sdk_manager.get_adb_instance(0)
        apk_data_list = self.apk_store.get_all_apk_file_data_from_source('benign')
        apk_name_list = self.apk_store.get_all_apk_filenames_from_source('benign')

        for apk_item in apk_data_list:
            self.logger.debug("APK item: {}".format(apk_item))

        for apk_item in apk_name_list:
            self.logger.debug("APK item names: {}".format(apk_item))

        #self.apk_store.get_an_apk('')