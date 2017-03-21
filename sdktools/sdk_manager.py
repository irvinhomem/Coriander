
import logging
import os
import platform
import getpass
#import sdktools.emulator_wrapper, sdktools.adb_wrapper
from sdktools import  emulator_wrapper, adb_wrapper
from multiprocessing import Queue
import time

class SdkManager(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.android_SDK_path = ''
        self.emulator_instances = []
        self.adb_instances = []
        self.shared_msg_queue = Queue()

        self.set_android_sdk_path()
        self.set_up_new_emulator('Nexus_5_API_22', self.shared_msg_queue)
        #self.logger.debug("Queue Size: %i" % self.shared_msg_queue.qsize())
        self.check_msg_queue()
        #self.logger.debug()
        #self.shared_msg_queue.join_thread()
        #self.logger.debug("Queue Length: %i" % self.shared_msg_queue.)

        self.set_up_new_adb()

    def set_android_sdk_path(self):
        self.android_SDK_path = self.find_android_sdk_path()
        if self.android_SDK_path == '':
            self.logger.error("Android SDK Path not set!")
            exit()
        else:
            self.logger.info('Android SDK PATH: %s' % self.android_SDK_path)

    def find_android_sdk_path(self):
        sdk_path = ''
        self.logger.debug('*************************')
        self.logger.debug('Config Info:')
        self.logger.debug('*************************')
        # OS Independent stuff
        os_name = os.name
        self.logger.debug("OS: %s" % os_name)
        platform_system = platform.system()
        self.logger.debug('Platform System: %s' % platform_system)
        user_name = getpass.getuser()
        self.logger.debug('Username: %s' % user_name)
        home_dir = os.path.expanduser('~')
        self.logger.debug("Home Directory: %s " % home_dir)
        root_dir = os.path.abspath(os.sep)
        self.logger.debug("Root Directory: %s" % root_dir)
        self.logger.debug('*************************')

        android_sdk_dir = os.path.join("Android", 'sdk')

        # OS Dependent stuff
        #under_win_sdk_loc = os.path.join('platform-tools', 'adb.exe')
        #under_linux_sdk_loc = os.path.join('platform-tools', 'adb')
        if platform_system == 'Windows':
            # Root Loc
            win_root_loc = os.path.join(root_dir, android_sdk_dir)
            # User Dir
            app_data_local_path = os.path.join("AppData", "Local")
            win_user_dir = os.path.join(home_dir, app_data_local_path, android_sdk_dir)

            if os.path.exists(win_root_loc):
                #adb_loc = os.path.join(win_root_loc, under_win_sdk_loc)
                sdk_path = win_root_loc
            elif os.path.exists(os.path.join(win_user_dir)):
                #adb_loc = os.path.join(win_user_dir, under_win_sdk_loc)
                sdk_path = win_user_dir
        elif platform_system == 'Linux':
            # Not yet complete for the Linux side of things (Will currently throw error and exit)
            sdk_path = ''

        return sdk_path

    def get_android_sdk_path(self):
        return self.android_SDK_path

    def get_adb_instance(self, index):
        if len(self.adb_instances) > index:
            return self.adb_instances[index]
        else:
            self.logger.error('ADB instance Index{} NOT found'.format(index))
            exit()

    def set_up_new_emulator(self, emu_name, msq_queue):
        self.logger.debug('Queue Type: %s' % str(type(msq_queue)))
        # Create a new Emulator instance and add it to the SDK Manager's list of emulators
        instance_id = len(self.emulator_instances)
        my_Emulator = emulator_wrapper.EmulatorWrapper(self, emu_name, msq_queue, instance_id)
        self.emulator_instances.append(my_Emulator)

    def get_emulator_instance(self, index):
        if len(self.emulator_instances) > index:
            return self.emulator_instances[index]
        else:
            self.logger.error('Emulator instance Index{} NOT found'.format(index))
            exit()

    def set_up_new_adb(self):
        # Create a new ADB Wrapper instance and append it to the SDK Manager's list of ADB Wrappers
        my_ADB = adb_wrapper.AdbWrapper(self)
        self.adb_instances.append(my_ADB)

    def check_msg_queue(self):
        emulator_ready = "Serial number of this emulator"
        while True:
            line = self.shared_msg_queue.get()
            #if line is None:
            #    break
            self.logger.debug("Queue line: [%i] : %s" % (line['instance_id'], line['content']))
            if emulator_ready in line['content']:
                # Give the emulator time to start up completely
                time.sleep(15)
                self.logger.info('EMULATOR IS READY!')

                break

            #self.shared_msg_queue.
