
import logging
import threading
import subprocess
#import time


class AdbProc(threading.Thread):

    def __init__(self, adb_loc, msg_queue, cmd_params):
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
        self.adb_msg_queue = msg_queue

    def run(self):
        cmd = [self.adb_loc, self.cmd_params]
        # self.emu_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        self.adb_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            universal_newlines=True, shell=True)
        # self.emu_proc_thread = mp.Process(target=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False))
        # p.start()
        # self.emu_proc_thread.start()

        #self.logger.debug('ADB output: \n %s' % self.adb_process.stdout.readline())
        for line in self.adb_process.stdout:
            self.logger.debug('ADB output:-->: %s' % line)

            msg = dict()
            #msg['instance_id'] = self.instance_id
            msg['content'] = line
            self.adb_msg_queue.put_nowait(msg)