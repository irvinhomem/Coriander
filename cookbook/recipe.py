
import logging
import time
import os

#from sdktools import sdk_manager

#GO_AHEAD_FLAG = True

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
        self.go_ahead_flag = True
        #global GO_AHEAD_FLAG = True

    def run_recipe(self):
        self.logger.debug("****************************************")
        self.logger.debug("RUNNING RECIPE: {} ". format(self.instructions))
        self.logger.debug("****************************************")

        #apk_data_list = self.apk_store.get_all_apk_file_data_from_source('malicious')
        apk_data_list = self.apk_store.get_all_apk_file_data_from_source('benign')
        #apk_name_list = self.apk_store.get_all_apk_filenames_from_source('benign')

        for apk_item in apk_data_list:
            self.logger.debug("APK item: {}".format(apk_item))

        #for apk_item in apk_name_list:
        #    self.logger.debug("APK item names: {}".format(apk_item))

        filename_list = self.apk_store.get_single_column_as_list('sha256')
        self.logger.debug('Filename List LENGTH: {}'.format(len(filename_list)))

        # # Get 3rd filename (just for testing)
        # self.logger.debug('3rd Filename: {}'.format(filename_list[4])) #[2]
        # an_apk_file = self.apk_store.get_an_apk(filename_list[4])

        for single_apk_filename in filename_list:
            # Set up Emulator for current task
            #self.sdk_manager.set_up_new_emulator('Nexus_5_API_22_2', self.sdk_manager.get_shared_message_queue())
            self.sdk_manager.set_up_new_emulator('Nexus_5_API_22_2')
            emu = self.sdk_manager.get_emulator_instance(0)

            self.sdk_manager.set_up_new_adb()
            adb = self.sdk_manager.get_adb_instance(0)

            # # Set up Emulator Console (Need to pick up hostname and port from MSG_QUEUE)
            # self.sdk_manager.set_up_new_emulator_console('localhost', 5554)
            # emu_console = self.sdk_manager.get_emulator_console_instance(0)

            adb.check_if_emulator_has_booted()

            # Configure AndroMemdump for first run
            # (Given the system.img.qcow2 file preconfigured with Andromemdump-beta installed in System partition)
            andromemdump_pkg_name = 'com.zwerks.andromemdumpbeta'
            andromemdump_main_activity = 'com.zwerks.andromemdumpbeta.MainActivity'
            andromemdump_pkg_activity = andromemdump_pkg_name + '/' + andromemdump_main_activity
            andromemdump_cmd = ['shell', 'am', 'start', '-n', andromemdump_pkg_activity]
            adb.run_adb_command('-e', andromemdump_cmd, 'Starting: Intent', 'None')
            self.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++")
            self.logger.debug("------ Running AndroMemdump - First RUN -------")
            self.logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++")
            time.sleep(15)

            # Andromemdump can be closed, or killed here,
            # because the configuration is done while running the MainActivity [onCreate()]

            self.logger.debug('APK Filename: {}'.format(single_apk_filename))
            an_apk_file = self.apk_store.get_an_apk(single_apk_filename)

            self.logger.debug("APK TEMP file path: {}".format(an_apk_file.get_file_path()))

            #if self.go_ahead_flag:
            #********************
            # Install the APK
            # Method 1
            adb.run_adb_command('install', [an_apk_file.get_file_path()], 'Success', 'Failure')
            ### Method 2
            ##adb.install_apk(an_apk_file)

            #adb.check_adb_msg_queue('Success', 'Failure')
            time.sleep(10)

            #if self.go_ahead_flag:
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
            adb.run_adb_command('-e', full_cmd, 'Starting: Intent', 'None')
            #adb.run_adb_command('shell', full_cmd)

            # Dump process memory
            time.sleep(10)  # Delay before Starting Memory Dump
            adb.dump_process_memory(an_apk_file.get_package_name(), single_apk_filename, 'local_host_disk')

            # Close app
            #time.sleep(5) # Delay before closing
            force_stop_cmd = ['shell', 'am', 'force-stop', an_apk_file.get_package_name()]
            adb.run_adb_command('-e', force_stop_cmd, 'None', 'None')

            # *******************
            # Uninstall the APK
            time.sleep(5)  # Delay before Uninstalling
            # Method 1
            adb.run_adb_command('uninstall', [an_apk_file.get_package_name()], 'Success', 'Failure')
            ### Method 2
            ##adb.uninstall_apk(an_apk_file)

            # ******************
            # Reset Emulator / AVD instance back to original snapshot, or wipe-data
            # Couldn't get snapshotting working, so "wipe-data" is the next best option for now.
            # Shutdown emulator first, then wipe-data
            # Looks like you have to wipe [wipe-data] before booting the emulator ... so change of plans

            # ******************
            # Set up Emulator Console (Need to pick up hostname and port from MSG_QUEUE)
            emu_console = self.sdk_manager.set_up_new_emulator_console('localhost', 5554)
            #emu_console = self.sdk_manager.get_emulator_console_instance(0)

            # ******************
            # Kill emulator instance (Using the emulator telnet console "kill" command
            # or, telnet console "vm stop" command; or, telnet console "avd stop" command)
            time.sleep(5)  # Delay before Killing Emulator Instance
            #emu_console.run_tty_command('kill')
            emu_console.run_kill_command()
            #emu_console.run_tty_command('vm stop') # Didn't seem to work (doesn't exit in Build Tools v26)
            #emu_console.run_tty_command('avd stop') # Seems to freeze the VM, not to kill and quit (May be needed before 'kill'?)
            time.sleep(5)
            self.logger.debug('------ FINISHED DEALING WITH APK: {} ----------'.format(an_apk_file.get_package_name()))

        self.logger.debug('+++++++++++++++++++++++++++++++++++++')
        self.logger.debug('----------  END OF RECIPE -----------')
        self.logger.debug('+++++++++++++++++++++++++++++++++++++')

    def check_go_ahead_flag(self):
        return self.go_ahead_flag

    def set_go_ahead_flag(self, new_bool_val):
        self.go_ahead_flag = new_bool_val