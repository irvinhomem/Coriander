
import logging
import os
import sys
import platform
import multiprocessing as mp
import subprocess
import threading
import time
from queue import Queue, Empty
from telnetlib import Telnet

#import sdktools.sdk_manager
from sdktools import sdk_manager, emulator_proc, emulator_console


class EmulatorWrapper(object):

    #def __init__(self, sdkManager, emu_name, msq_queue, instance_id):
    def __init__(self, sdkManager, emu_name, tcp_dump_params, instance_id):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.ON_POSIX = 'posix' in sys.builtin_module_names
        self.emulator_loc = ''
        #self.emulator_loc_x86 = ''
        self.emu_process = None
        self.shared_msg_queue = Queue()
        self.logger.debug('Queue Type: %s' % str(type(self.shared_msg_queue)))
        #self.shared_queue = msq_queue
        self.instance_id = instance_id
        self.tcpdump_params =  tcp_dump_params

        self.set_emulator_location(sdkManager.get_android_sdk_path())
        #self.start_up_emulator(emu_name)

        #self.emu_process = mp.Process(target=self.start_up_emulator, args=emu_name)
        #self.emu_process.start()
        #self.emu_process.join()

        self.logger.debug('+++++++++++++++++++++++++++++++++++++++++++++++++++++')
        self.logger.debug('--  Emulator Wrapper --> Starting New Emulator !  --')
        self.logger.debug('+++++++++++++++++++++++++++++++++++++++++++++++++++++')
        emulator_process = emulator_proc.EmulatorProc(self.emulator_loc, emu_name, self.tcpdump_params, self.shared_msg_queue, self.instance_id)
        #emulator_process = emulator_proc.EmulatorProc(self.emulator_loc_x86, emu_name, self.tcpdump_params, self.shared_msg_queue, self.instance_id)
        emulator_process.start()
        #emulator_process.join()

        self.check_msg_queue()

        #self.emulator_console = emulator_console.EmulatorConsole('localhost', 5554)
        #self.emulator_console = None

        # Give emulator process time to start up
        #time.sleep(20)

    def set_emulator_location(self, sdk_path):
        tools_path = 'tools'
        emulators_path = 'emulator'

        if platform.system() == 'Windows':
            self.emulator_loc = os.path.join(sdk_path, tools_path, 'emulator.exe')
            # Do not use the /emulators folder ... the emulator's there are slow and buggy' (emulator.exe,emulator-x86 etc)
            # Don't use them with the "-engine classic" directive either
            # It will overwrite the Original AVD Image files ...causing a mess
            #self.emulator_loc = os.path.join(sdk_path, emulators_path, 'emulator.exe')
            #self.emulator_loc_x86 = os.path.join(sdk_path, emulators_path, 'emulator-x86.exe')
        elif platform.system() == 'Linux':
            self.emulator_loc = os.path.join(sdk_path, tools_path, 'emulator')
        elif platform.system() == 'Darwin':
            self.emulator_loc = os.path.join(sdk_path, tools_path, 'emulator')

        self.get_emulator_loc()

    def get_emulator_loc(self):
        if self.emulator_loc == '':
            self.logger.error("Emulator Path not set!")
            exit()
        else:
            self.logger.info('Emulator Path: %s' % self.emulator_loc)

        return self.emulator_loc

    def start_up_emulator(self, emulator_name, tcpdump_params):
        #[This is not explicitly used at the moment]
        # Original simple command to start up emulator
        #cmd = [self.emulator_loc, '-avd', emulator_name]
        # With debugging options since Google has changed the normal output of the "AVD Serial" and "console port"
        #cmd = [self.emulator_loc, '-avd', emulator_name, '-debug', 'init']
        #cmd = [self.emulator_loc, '-avd', emulator_name, '-debug-init']
        #cmd = [self.emulator_loc, '-avd', emulator_name, '-wipe-data','-debug-init']
        #tcpdump_params = ['-tcpdump', os.path.join(homedir), 'MEM_DUMPS', mal_state]
        tcpdump_cmd = ''
        for params in tcpdump_params:
            tcpdump_cmd = tcpdump_cmd + params + ' '
        cmd = [self.emulator_loc, '-avd', emulator_name, tcpdump_cmd, '-netfast' ,'-debug', 'init']
        self.logger.debug('Emulator Command: {}'.format(cmd))
        #self.emu_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        self.emu_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        #self.emu_proc_thread = mp.Process(target=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False))
        #p.start()
        #self.emu_proc_thread.start()

        self.logger.debug('Emulator output: \n %s' % self.emu_process.stdout.readline())
        for line in self.emu_process.stdout:
            self.logger.debug('-->: %s' % line)

        #self.emu_proc.communicate()
        # self.emu_process.wait()

        #time.sleep(15)

    # def set_up_emulator_console(self, hostname, port_num):
    #     self.emulator_console = emulator_console.EmulatorConsole(hostname, port_num)

    def check_msg_queue(self):
        #emulator_ready = "Serial number of this emulator"
        #emulator_ready = "Adb connected, start proxing data"
        # emulator_ready_criteria = ["Serial number of this emulator",
        #                   "emulator: Listening for console connections on port:",
        #                   "emulator: Serial number of this emulator (for ADB):",
        #                   "emulator: control console listening on port",
        #                   "Adb connected, start proxing data"]
        emulator_ready_criteria = ["Adb connected, start proxing data"]
        while True:
            line = self.shared_msg_queue.get()
            #if line is None:
            #    break
            self.logger.debug("Queue line: [%i] : %s" % (line['instance_id'], line['content']))
            #if emulator_ready in line['content']:
            #if any(item in emulator_ready for item in line['content']):
            criterion = line['content']
            # Check for "Emulator is Ready" criteria
            if any(item in criterion for item in emulator_ready_criteria):
                # Give the emulator time to start up completely
                self.logger.info('Waiting for EMULATOR (time delay) !')
                time.sleep(20) # 15s # 20s
                self.logger.info('EMULATOR IS Almost READY!')

                break

            #self.shared_msg_queue.




