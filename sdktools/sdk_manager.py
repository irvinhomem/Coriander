
import logging
import os
import platform
import getpass


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

        self.set_android_sdk_path()


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