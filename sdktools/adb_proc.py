
import logging
import threading
import subprocess
#import time


class AdbProc(threading.Thread):

    def __init__(self, adb_loc, cmd_params):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        threading.Thread.__init__(self)
        self.adb_loc = adb_loc
        self.adb_process = None
        self.cmd_params = cmd_params

    def run(self):
        cmd = [self.adb_loc, self.cmd_params]
        # self.emu_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        self.adb_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True, shell=True)
        # self.emu_proc_thread = mp.Process(target=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False))
        # p.start()
        # self.emu_proc_thread.start()

        self.logger.debug('Emulator output: \n %s' % self.adb_process.stdout.readline())
        for line in self.adb_process.stdout:
            self.logger.debug('-->: %s' % line)