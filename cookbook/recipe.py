
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
        self.logger.debug("****************************************")
        self.logger.debug("RUNNING RECIPE: {} ". format(self.instructions))
        self.logger.debug("****************************************")

        emu = self.sdk_manager.get_emulator_instance(0)
        adb = self.sdk_manager.get_adb_instance(0)
        #apk_data_list = self.apk_store.get_all_apk_file_data_from_source('malicious')
        apk_data_list = self.apk_store.get_all_apk_file_data_from_source('benign')
        #apk_name_list = self.apk_store.get_all_apk_filenames_from_source('benign')

        for apk_item in apk_data_list:
            self.logger.debug("APK item: {}".format(apk_item))

        #for apk_item in apk_name_list:
        #    self.logger.debug("APK item names: {}".format(apk_item))

        filename_list = self.apk_store.get_single_column_as_list('sha256')
        self.logger.debug('Filename List length: {}'.format(len(filename_list)))

        # Get 3rd filename (just for testing)
        self.logger.debug('3rd Filename: {}'.format(filename_list[2]))
        an_apk_file = self.apk_store.get_an_apk(filename_list[2])

        self.logger.debug("APK TEMP file path: {}".format(an_apk_file.get_file_path()))
        # Install the APK
        adb.run_adb_command('install', [an_apk_file.get_file_path()])

        # Uninstall the APK
        adb.run_adb_command('uninstall', [an_apk_file.get_package_name()])