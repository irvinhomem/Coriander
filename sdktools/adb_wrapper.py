
import logging
import os
import platform
import subprocess
import multiprocessing as mp

#import sdktools.sdk_manager
from sdktools import sdk_manager, adb_proc
from tqdm import tqdm
import sys
import time
#from multiprocessing import Queue
from queue import Queue, Empty
import psutil

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
        self.shared_adb_msg_queue = Queue()
        self.logger.debug('Queue Type: %s' % str(type(self.shared_adb_msg_queue)))

        self.set_adb_location(sdkManager.get_android_sdk_path())
        #self.start_adb_server()
        self.adb_process = adb_proc.AdbProc(self.adb_loc, self.shared_adb_msg_queue, ['devices'])
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

    def run_adb_command(self, adb_command, params, pos_msg, neg_msg):
        """
        @type params: list
        :param adb_command: 
        :param params: 
        :return: 
        """
        adb_cmd_successful = True
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

        #self.logger.debug('ADB output: \n %s' % self.adb_process.stdout.readline())
        for line in self.adb_process.stdout:
            self.logger.debug('-->: %s ' % line)
            self.put_to_msg_queue(line)


        if len(self.adb_process.stderr.read()) > 0:
            for err_line in self.adb_process.stderr:
                self.logger.debug('Err:-->: %s ' % err_line)
                self.put_to_msg_queue(err_line)
        #self.adb_process.communicate('\n')

        adb_cmd_successful = self.check_adb_msg_queue(pos_msg, neg_msg)

        return adb_cmd_successful

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

    def check_if_emulator_has_booted(self):
        successfully_booted = True
        cmd = ['shell', 'getprop', 'sys.boot_completed']
        # resp = self.run_adb_command_return_list(cmd)
        # self.logger.debug("Command Output List: {}".format(resp))
        timeout = time.time() + 60 * 1 # 60 sec or 1min timeout
        self.logger.debug('Checking if Emulator has finished booting. \n'
                          'Expecting to timeout at: {}'.format(time.asctime(time.localtime(timeout))))
        while time.time() <= timeout:
            resp = self.run_adb_command_return_list(cmd)
            self.logger.debug("Command Output List: {}".format(resp))

            self.logger.debug("Stripped condition: {}".format(resp[0].strip()))
            if resp[0].strip() == '1':
            #if int(resp[0].strip()) == 1:
                self.logger.debug('Emulator has FINISHED BOOTING.')
                #break
                successfully_booted = True
                return successfully_booted
            else:
                time.sleep(5)
        else:
            # Emulator has probably hung up / crashed
            self.logger.debug("Emulator boot ... TIMED OUT: {}".format(time.asctime(time.localtime(time.time()))))
            # IF process has started, try to kill it
            proc_name = 'qemu-system'   # qemu-system-i386
            for proc in psutil.process_iter():
                if proc_name in proc.name():
                    proc.kill()
            successfully_booted = False

        return successfully_booted


    def check_adb_msg_queue(self, pos_criteria, neg_criteria):
        success_flag = True
        #timeout = time.time() + 60 * 1.5    # 90sec or 1.5min from now
        # timeout = time.time() + 60 * 1  # 60sec or 1min from now
        #timeout = time.time() + 60 * 0.5  # 30sec from now
        #timeout = time.time() + 20  # 20sec from now
        timeout = time.time() + 10  # 10sec from now
        time_fmt = '%'
        self.logger.debug('Expecting to timeout at: {}'.format(time.asctime(time.localtime(timeout))))
        while True:
            #line = self.shared_adb_msg_queue.get()
            self.logger.debug('Current time: {}'.format(time.asctime(time.localtime(time.time()))))
            try:
                line = self.shared_adb_msg_queue.get_nowait()
                #self.logger.debug("Queue line: [%i] : %s" % (line['instance_id'], line['content']))
                self.logger.debug("Queue line Content: %s" % (line['content']))
                content = line['content']
                self.logger.debug('Checking ADB Msg Queue: => {}'.format(content))
                if pos_criteria in content:
                    self.logger.debug('Success in ADB Message: => {}'.format(content))
                    break
                elif neg_criteria in content:
                    self.logger.debug('Failure in ADB Message: => {}'.format(content))
                    self.logger.error(content)
                    success_flag = False
                    #sys.exit()
                else:
                    self.logger.debug("ADB Msg Queue => Not hit 'pos' or 'neg' message yet (Could sleep here ...)")
                    self.logger.debug(" ... or waiting for timeout: {}".format(time.asctime(time.localtime(timeout))))
                #     self.logger.debug('ADB Msg Queue sleeping for 5 sec ...')
                #     time.sleep(5)
            except Empty as empty_err:
                self.logger.debug('ADB Message Queue is EMPTY ... : {}'.format(empty_err))
                if time.time() > timeout:
                    self.logger.debug('EXCEEDED TIMEOUT [{}] in ADB Message Queue: '.format(time.asctime(time.localtime(timeout))))
                    break
                time.sleep(5)
                pass

            # if time.time() > timeout:
            #     self.logger.debug('EXCEEDED TIMEOUT [{}] in ADB Message Queue: '.format(timeout))
            #     break
        return success_flag

    def put_to_msg_queue(self, line):
        self.logger.debug('ADB output:-->: %s' % line)

        msg = dict()
        # msg['instance_id'] = self.instance_id
        msg['content'] = line
        self.shared_adb_msg_queue.put_nowait(msg)

    def check_cpu_abi(self):
        abi_list = self.run_adb_command_return_list(['shell','getprop', 'ro.product.cpu.abilist'])
        self.logger.debug('First in ABI list: {}'.format(abi_list[0]))
        return abi_list

    def check_memdump_is_in_place(self):

        self.logger.debug('===========')
        self.logger.debug("Check if Memdump is in place:")
        self.logger.debug('===========')
        memdump_path = ''

        #packages_list_dir = self.list_dir_contents(os.path.join(os.sep, 'data', 'data'))
        #list_dir_cmd = ['shell', 'ls', '-al', '/data/data']
        list_dir_cmd = ['shell', 'ls', '/data/data']
        packages_list_dir = self.run_adb_command_return_list(list_dir_cmd)
        memdump_pkg = 'com.zwerks.andromemdump'
        # #if any(memdump_pkg_name in item for item in packages_list_dir):
        memdump_pkg_name = [item for item in packages_list_dir if memdump_pkg in item]
        if len(memdump_pkg_name) > 0:
            #memdump_loc = os.path.join('data', 'data', memdump_pkg_name[0], 'files')
            #abi_dir = self.check_cpu_abi()
            ##memdump_loc = '/data/data/' + memdump_pkg_name[0].strip() + '/files/' + abi_dir[0].strip()
            #memdump_loc = '/data/data/' + memdump_pkg_name[0].strip() + '/files/' + abi_dir[0].strip() + '/'
            memdump_loc = '/data/data/' + memdump_pkg_name[0].strip() + '/files/' #+ abi_dir[0].strip() + '/'
            andromemdump_dir_list = self.run_adb_command_return_list(['shell', 'ls', '-al', memdump_loc])
            # NB: The list returned above as trailing "new-line" characters that need to be stripped
        #cmd = [self.adb_loc, ls_memdump_cmd]
            memdump_criteria = 'memdump'
            memdump_present = [item for item in andromemdump_dir_list if memdump_criteria in item.strip()[-7:]]
            self.logger.debug('Memdump-Present LIST: {}'.format(memdump_present))
            if len(memdump_present) > 0:
                self.logger.debug('*****')
                self.logger.debug('MEMDUMP CORRECTLY INSTALLED IN: {}'.format(memdump_loc) )
                self.logger.debug('*****')
                memdump_path = memdump_loc + 'memdump' # '/' + 'memdump'
            else:
                self.logger.debug('MEMDUMP not found IN: {}'.format(memdump_loc))
                #exit(9)
                sys.exit()
        else:
            self.logger.debug('MEMDUMP package DIR: [{}] not found'.format(memdump_pkg))
            #exit(9)
            sys.exit()

        return memdump_path

    def get_process_id(self, proc_name_str):

        proc_id = None
        ps_list_cmd = ['shell', 'ps']
        process_list = self.run_adb_command_return_list(ps_list_cmd)

        proc_item_list = [item for item in process_list if proc_name_str in item]
        if len(proc_item_list) > 0:
            self.logger.debug('Process: [{}] :: INFO: {}'. format(proc_name_str, proc_item_list[0]))
            proc_items = self.parse_ps_info_line(proc_item_list[0])
            proc_id = proc_items[1]
        return proc_id

    def parse_ps_info_line(self, proc_info_str):
        proc_info_items = proc_info_str.split()
        return proc_info_items

    def get_single_process_id(self, proc_name_str):
        proc_id = None
        #ps_list_cmd = ['shell', '"', 'ps', '|', 'grep', proc_name_str, '"']
        piped_cmd_str = 'ps | grep ' +  proc_name_str
        ps_list_cmd = ['shell', piped_cmd_str]
        process_list = self.run_adb_command_return_list(ps_list_cmd)

        if len(process_list) > 0:
            self.logger.debug('Process: [{}] :: INFO: {}'.format(proc_name_str, process_list[0]))
            proc_items = self.parse_ps_info_line(process_list[0])
            proc_id = proc_items[1]

        self.logger.debug('Proc ID: {}'.format(proc_id))
        return proc_id

    def dump_process_memory(self, package_name, sha256_filename, dump_dest_type):
        # May be move some of this to MemDumper package?
        dump_memory_success = True
        memdump_path = self.check_memdump_is_in_place()
        pkg_to_dump_pid = None
        # Wait for the process to start in order to get a Process ID
        #timeout =  time.time() + 60 * 1 # Timeout after 1min (60 sec)
        timeout = time.time() + 60 * 0.5  # Timeout after 1min (30 sec)
        while pkg_to_dump_pid is None:
            pkg_to_dump_pid = self.get_single_process_id(package_name)
            self.logger.debug("WAITING for Process to Start-up [Proc_id to appear]: {}".format(package_name))
            time.sleep(5)
            if time.time() > timeout:
                self.logger.debug('TIME-OUT passed while waiting for ProcID to appear')
                self.logger.error('TIME-OUT passed while waiting for ProcID to appear')
                dump_memory_success = False
                return dump_memory_success

        memdumps_dir = 'MEM_DUMPS'
        piped_memdump_cmd = []

        if dump_dest_type == 'local_emu_sdcard':
            #dump_loc = '/storage/extSdcard/MEM_DUMPS/' + package_name + '.dmp'
            #dump_loc = '/storage/extSdcard/' + package_name + '_DUMP.dmp'
            dump_loc = '/storage/sdcard/' + sha256_filename +'_'+ package_name +'_DUMP.dmp'  # Works
            # Emulator Disk Location (Note the '>' redirection) # Works
            piped_memdump_cmd = [memdump_path + ' ' + pkg_to_dump_pid + ' > ' + dump_loc]
        elif dump_dest_type == 'remote_network':
            host_ip = ''
            port_num = ''
            network_dump_loc = host_ip + ' ' + port_num
            # Network Location (no redirection operator) # Works
            piped_memdump_cmd = [memdump_path + ' ' + pkg_to_dump_pid + ' ' + network_dump_loc]
        elif dump_dest_type == 'local_host_disk':
            home_dir = os.path.expanduser('~')
            host_dump_loc = os.path.join(home_dir, memdumps_dir, sha256_filename + '_'+ package_name +'_DUMP.dmp')
            # Host Disk Location (Note the '>' redirection)
            #piped_memdump_cmd = [memdump_path + ' ' + pkg_to_dump_pid + ' > ' + host_dump_loc]
            # Host Disk Location (Note the '>' redirection) # Works
            #piped_memdump_cmd = [memdump_path , pkg_to_dump_pid, '>', host_dump_loc]
            # Host Disk Location WITH STRINGS Command from BusyBox (Note the '>' redirection) # Works
            piped_memdump_cmd = [memdump_path, pkg_to_dump_pid + ' | strings', '>', host_dump_loc]

        memdump_cmd = ['shell']
        for params in piped_memdump_cmd:
            memdump_cmd.append(params)
        dump_memory_success = self.run_adb_command('-e', memdump_cmd, 'None', 'None')

        return dump_memory_success





