
import logging
import os
import platform
import subprocess
import multiprocessing as mp

#import sdktools.sdk_manager
from sdktools import sdk_manager, adb_proc
from tqdm import tqdm


class AdbWrapper(object):

    def __init__(self, sdkManager):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.adb_loc = ''
        self.adb_process = None

        self.set_adb_location(sdkManager.get_android_sdk_path())
        #self.start_adb_server()
        self.adb_process = adb_proc.AdbProc(self.adb_loc, ['devices'])
        self.adb_process.start()

    def set_adb_location(self, sdk_path):
        platform_tools_path = 'platform-tools'

        if platform.system() == 'Windows':
            self.adb_loc = os.path.join(sdk_path, platform_tools_path, 'adb.exe')
        elif platform.system() == 'Linux':
            self.adb_loc = os.path.join(sdk_path, platform_tools_path, 'adb')
        elif platform.system() == 'Darwin':
            self.adb_loc = os.path.join(sdk_path, platform_tools_path, 'adb')

        self.get_adb_loc()

    def get_adb_loc(self):
        if self.adb_loc == '':
            self.logger.error("ADB Path not set!")
            exit()
        else:
            self.logger.info('ADB Path: %s' % self.adb_loc)

        return self.adb_loc

    def start_adb_server(self):
        self.logger.debug('******* STARTING ADB ************')
        cmd = [self.adb_loc, 'devices']
        #self.adb_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        self.adb_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        # newproc = mp.Process(target=self.adb_process)
        # newproc.start()
        # newproc.join()
        #self.logger.debug('Started new instance of emulator: %s' % emulator_name)
        #self.logger.debug('ADB output: \n %s' % self.adb_process.stdout)

        self.logger.debug('ADB output: \n %s' % self.adb_process.stdout.readline())
        for line in self.adb_process.stdout:
            self.logger.debug('-->: %s' % line)

    def run_adb_command(self, adb_command, params=''):
        cmd = [self.adb_loc, adb_command]
        for item in params:
            cmd.append(item)
        self.logger.debug("cmd: {}".format(cmd))
        self.adb_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             universal_newlines=True, shell=True) # stdin= subprocess.PIPE,
        #self.adb_process.communicate(' '.join(cmd))

        self.logger.debug('Args: {}'.format(self.adb_process.args))

        self.logger.debug('ADB output: \n %s' % self.adb_process.stdout.readline())
        for line in self.adb_process.stdout:
            self.logger.debug('-->: %s ' % line)

        if len(self.adb_process.stderr.read()) > 0:
            for line in self.adb_process.stderr:
                self.logger.debug('Err:-->: %s ' % line)
        #self.adb_process.communicate('\n')

        return

    # def run_adb_get_output(self, adb_command, params=''):
    #     cmd = [self.adb_loc, adb_command, params]
    #     self.adb_process = subprocess.check_output(cmd, stderr=subprocess.PIPE,
    #                                         universal_newlines=True, shell=True)

    def install_apk(self, apk_file):
        cmd =[self.adb_loc, 'install', apk_file.get_file_path()]
        self.adb_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True, shell=True)

        self.logger.debug('ADB output: \n %s' % self.adb_process.stdout.readline())
        for line in self.adb_process.stdout:
            self.logger.debug('-->: %s ' % line)

        return

    def uninstall_apk(self, apk_file):
        cmd =[self.adb_loc, 'uninstall', apk_file.get_package_name()]
        self.adb_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True, shell=True)

        self.logger.debug('ADB output: \n %s' % self.adb_process.stdout.readline())
        for line in self.adb_process.stdout:
            self.logger.debug('-->: %s ' % line)

        return




