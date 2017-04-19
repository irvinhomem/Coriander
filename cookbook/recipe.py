
import logging
import time
import os

#from sdktools import sdk_manager

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
        self.config_file = ''

    def run_recipe(self):
        self.logger.debug("****************************************")
        self.logger.debug("RUNNING RECIPE: {} ". format(self.instructions))
        self.logger.debug("****************************************")

        emu = self.sdk_manager.get_emulator_instance(0)
        adb = self.sdk_manager.get_adb_instance(0)
        emu_console = self.sdk_manager.get_emulator_console_instance(0)
        #apk_data_list = self.apk_store.get_all_apk_file_data_from_source('malicious')
        apk_data_list = self.apk_store.get_all_apk_file_data_from_source('benign')
        #apk_name_list = self.apk_store.get_all_apk_filenames_from_source('benign')

        # Configure AndroMemdump for first run
        # (Given the system.img.qcow2 file preconfigured with Andromemdump-beta installed in System partition)
        andromemdump_pkg_name = 'com.zwerks.andromemdumpbeta'
        andromemdump_main_activity = 'com.zwerks.andromemdumpbeta.MainActivity'
        andromemdump_pkg_activity = andromemdump_pkg_name + '/' + andromemdump_main_activity
        andromemdump_cmd = ['shell', 'am', 'start', '-n', andromemdump_pkg_activity]
        adb.run_adb_command('-e', andromemdump_cmd)
        time.sleep(5)

        # Andromemdump can be closed, or killed here,
        # because the configuration is done while running the MainActivity [onCreate()]

        for apk_item in apk_data_list:
            self.logger.debug("APK item: {}".format(apk_item))

        #for apk_item in apk_name_list:
        #    self.logger.debug("APK item names: {}".format(apk_item))

        filename_list = self.apk_store.get_single_column_as_list('sha256')
        self.logger.debug('Filename List length: {}'.format(len(filename_list)))

        # Get 3rd filename (just for testing)
        self.logger.debug('3rd Filename: {}'.format(filename_list[4])) #[2]
        an_apk_file = self.apk_store.get_an_apk(filename_list[4])

        self.logger.debug("APK TEMP file path: {}".format(an_apk_file.get_file_path()))
        #********************
        # Install the APK
        # Method 1
        adb.run_adb_command('install', [an_apk_file.get_file_path()])
        ### Method 2
        ##adb.install_apk(an_apk_file)

        time.sleep(10)
        # *******************
        # Go to FIRST activity and dump memory //// OR //// Go through each activity and dump memory ?
        # *******************
        # Run first activity
        # adb shell am start -n com.package.name/com.package.name.xyz.ActivityName
        pkg_and_activity_name = an_apk_file.get_package_name() + '/' + an_apk_file.get_activity_list()[1]
        self.logger.debug('Package and Activity name to run: {}'.format(pkg_and_activity_name))
        #adb.run_adb_command(['shell', 'am', 'start', '-n', pkg_and_activity_name])
        full_cmd = ['shell', 'am', 'start', '-n', pkg_and_activity_name]
        #full_cmd = ['am', 'start', '-n', pkg_and_activity_name]
        #full_cmd = ['shell', 'ls']
        #full_cmd = ['devices']
        #full_cmd = 'shell am start' # -n ' #+ pkg_and_activity_name
        adb.run_adb_command('-e', full_cmd)
        #adb.run_adb_command('shell', full_cmd)

        # Dump process memory
        time.sleep(10)  # Delay before Starting Memory Dump
        adb.dump_process_memory(an_apk_file.get_package_name(), 'local_host_disk')


        # Close app
        time.sleep(5) # Delay before closing
        force_stop_cmd = ['shell', 'am', 'force-stop', an_apk_file.get_package_name()]
        adb.run_adb_command('-e', force_stop_cmd)

        # *******************
        # Uninstall the APK
        time.sleep(5)  # Delay before Uninstalling
        # Method 1
        adb.run_adb_command('uninstall', [an_apk_file.get_package_name()])
        ### Method 2
        ##adb.uninstall_apk(an_apk_file)

        # ******************
        # Reset Emulator / AVD instance back to original snapshot, or wipe-data
        # Couldn't get snapshotting working, so "wipe-data" is the next best option for now.
        # Shutdown emulator first, then wipe-data
        # Looks like you have to wipe [wipe-data] before booting the emulator ... so change of plans

        # ******************
        # Kill emulator instance (Using the emulator telnet console "kill" command
        # or, telnet console "vm stop" command; or, telnet console "avd stop" command)
        time.sleep(5)  # Delay before Killing Emulator Instance
        emu_console.run_tty_command('kill')
        #emu_console.run_tty_command('vm stop') # Didn't seem to work (doesn't exit in Build Tools v26)
        #emu_console.run_tty_command('avd stop') # Seems to freeze the VM, not to kill and quit (May be needed before 'kill'?)