
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

    def __init__(self, sdkManager, emu_name, msq_queue, instance_id):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.ON_POSIX = 'posix' in sys.builtin_module_names
        self.emulator_loc = ''
        self.emu_process = None
        self.shared_queue = msq_queue
        self.instance_id = instance_id

        self.set_emulator_location(sdkManager.get_android_sdk_path())
        #self.start_up_emulator(emu_name)

        #self.emu_process = mp.Process(target=self.start_up_emulator, args=emu_name)
        #self.emu_process.start()
        #self.emu_process.join()

        emulator_process = emulator_proc.EmulatorProc(self.emulator_loc, emu_name, self.shared_queue, self.instance_id)
        emulator_process.start()
        #emulator_process.join()

        #self.emulator_console = emulator_console.EmulatorConsole('localhost', 5554)
        #self.emulator_console = None

        # Give emulator process time to start up
        #time.sleep(20)

    def set_emulator_location(self, sdk_path):
        tools_path = 'tools'

        if platform.system() == 'Windows':
            self.emulator_loc = os.path.join(sdk_path, tools_path, 'emulator.exe')
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

    def start_up_emulator(self, emulator_name):
        #[This is not explicitly used at the moment]
        # Original simple command to start up emulator
        #cmd = [self.emulator_loc, '-avd', emulator_name]
        # With debugging options since Google has changed the normal output of the "AVD Serial" and "console port"
        #cmd = [self.emulator_loc, '-avd', emulator_name, '-debug', 'init']
        cmd = [self.emulator_loc, '-avd', emulator_name, '-debug-init']
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




