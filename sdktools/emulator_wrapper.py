
import logging
import os
import sys
import platform
import multiprocessing as mp
import subprocess
from threading import Thread
import time
from queue import Queue, Empty

import sdktools.sdk_manager


class EmulatorWrapper(object):

    def __init__(self, sdkManager, emu_name):
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

        self.set_emulator_location(sdkManager.get_android_sdk_path())
        self.start_up_emulator(emu_name)

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
        cmd = [self.emulator_loc, '-avd', emulator_name]
        #self.emu_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        #self.emu_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        self.emu_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            bufsize=1, close_fds=self.ON_POSIX)
        q = Queue()
        t = Thread(target=self.enqueue_emu_output, args=(self.emu_process.stdout, q))
        t.daemon = True
        t.start()
        #self.emu_proc_thread = threading.Thread(subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True))
        #self.emu_proc_thread.start()
        #self.emu_process.communicate()
        # newproc = mp.Process(target=self.emu_process)
        # newproc.start()
        # newproc.join()
        self.logger.debug('Started new instance of emulator: %s' % emulator_name)

        try: line = q.get_nowait()
        except Empty:
            self.logger.debug('No output yet')
        else:
            self.logger.debug('Emulator output: \n %s' % line)
        # self.logger.debug('Emulator output: \n %s' % self.emu_process.stdout)
        #self.logger.debug('Emulator output: \n %s' % self.emu_proc_thread)
        #time.sleep(15)

    def enqueue_emu_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()



