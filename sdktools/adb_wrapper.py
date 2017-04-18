
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
        self.logger.debug('===========')
        self.logger.debug("ADB Command Run: {}".format(cmd))
        self.logger.debug('===========')
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

    def run_adb_command_return_list(self, params):

        dir_list =[]
        #list_pkg_cmd = ['shell', 'ls', '-al', dir_path]
        cmd = [self.adb_loc]
        for items in params:
            cmd.append(items)

        self.logger.debug('===========')
        self.logger.debug("Run Command Return List: {}".format(cmd))
        self.logger.debug('===========')
        self.adb_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True, shell=True)  # stdin= subprocess.PIPE,
        # self.adb_process.communicate(' '.join(cmd))

        self.logger.debug('Args: {}'.format(self.adb_process.args))

        #self.logger.debug('ADB FIRST-LINE output: \n %s' % self.adb_process.stdout.readline())
        for line in self.adb_process.stdout:
            self.logger.debug('ADB Output -->: %s ' % line)
            dir_list.append(line)

        if len(self.adb_process.stderr.read()) > 0:
            for line in self.adb_process.stderr:
                self.logger.debug('Err:-->: %s ' % line)
        # self.adb_process.communicate('\n')

        return dir_list

    def check_cpu_abi(self):
        abi_list = self.run_adb_command_return_list(['shell','getprop', 'ro.product.cpu.abilist'])
        self.logger.debug('First in ABI list: {}'.format(abi_list[0]))
        return abi_list

    def check_memdump_is_in_place(self):

        self.logger.debug('===========')
        self.logger.debug("Check if Memdump is in place:")
        self.logger.debug('===========')

        #packages_list_dir = self.list_dir_contents(os.path.join(os.sep, 'data', 'data'))
        #list_dir_cmd = ['shell', 'ls', '-al', '/data/data']
        list_dir_cmd = ['shell', 'ls', '/data/data']
        packages_list_dir = self.run_adb_command_return_list(list_dir_cmd)
        memdump_pkg = 'com.zwerks.andromemdump'
        #if any(memdump_pkg_name in item for item in packages_list_dir):
        memdump_pkg_name = [item for item in packages_list_dir if memdump_pkg in item]
        if len(memdump_pkg_name) > 0:
            #memdump_loc = os.path.join('data', 'data', memdump_pkg_name[0], 'files')
            abi_dir = self.check_cpu_abi()
            #memdump_loc = '/data/data/' + memdump_pkg_name[0].strip() + '/files/' + abi_dir[0].strip()
            memdump_loc = '/data/data/' + memdump_pkg_name[0].strip() + '/files/' + abi_dir[0].strip() + '/'
            andromemdump_dir_list = self.run_adb_command_return_list(['shell', 'ls', '-al', memdump_loc])
        #cmd = [self.adb_loc, ls_memdump_cmd]
            if 'memdump' in andromemdump_dir_list:
                self.logger.debug('*****')
                self.logger.debug('MEMDUMP CORRECTLY INSTALLED IN: {}'.format(memdump_loc) )
                self.logger.debug('*****')
            else:
                self.logger.debug('MEMDUMP not found IN: {}'.format(memdump_loc))
        else:
            self.logger.debug('MEMDUMP package DIR: [{}] not found'.format(memdump_pkg))

        return




