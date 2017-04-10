
import logging
import threading
import subprocess
import multiprocessing
#import time


class EmulatorProc(threading.Thread):

    def __init__(self, emu_loc, avd_name, msg_queue, instance_id):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        threading.Thread.__init__(self)
        self.avdName = avd_name
        self.emulator_loc = emu_loc
        self.msg_queue = msg_queue
        self.instance_id = instance_id

    def run(self):
        emulator_name =self.avdName
        # Original simple command to start up emulator
        #cmd = [self.emulator_loc, '-avd', emulator_name]
        # With debugging options since Google has changed the normal output of the "AVD Serial" and "console port"
        cmd = [self.emulator_loc, '-avd', emulator_name, '-debug', 'init']
        # self.emu_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        self.emu_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True, shell=True)
        # self.emu_proc_thread = mp.Process(target=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False))
        # p.start()
        # self.emu_proc_thread.start()

        self.logger.debug('Emulator output: \n %s' % self.emu_process.stdout.readline())
        for line in self.emu_process.stdout:
            self.logger.debug('-->: %s' % line)
            #self.msg_queue.put(line)
            msg = dict()
            msg['instance_id'] = self.instance_id
            msg['content'] = line
            self.msg_queue.put_nowait(msg)