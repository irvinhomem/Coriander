
import logging
import threading
import subprocess
import multiprocessing
#import time
import os
from shutil import copyfile, copy2
#import sys


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

        self.needs_wiping = True


    def run(self):
        emulator_name = self.avdName
        # Original simple command to start up emulator
        #cmd = [self.emulator_loc, '-avd', emulator_name]
        # With debugging options since Google has changed the normal output of the "AVD Serial" and "console port"
        #cmd = [self.emulator_loc, '-avd', emulator_name, '-debug', 'init']
        # With -wipe-data directive to ensure the AVD is wiped before starting it
        # wipe_data = ''
        # if self.needs_wiping:
        #     wipe_data = '-wipe-data'
            #self.needs_wiping = False
        self.clean_out_avd_dir()
        self.inject_emu_system_img_from_temp()

        #cmd = [self.emulator_loc, '-avd', emulator_name, '-wipe-data', '-debug', 'init'] # '-report-console' could be an interesting idea
        cmd = [self.emulator_loc, '-avd', emulator_name, '-netfast' ,'-debug', 'init']
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

            # # Finding out when 'wipe-data' process is over or at least 'system.img.qcow2' is deleted
            # # so that we can inject the original 'system.img.qcow2' back in
            # wiped_emu_done = ''
            # system_file_path = os.path.join(os.path.expanduser('~'),'.android','avd','Nexus_5_API_22_2.avd', 'system.img.qcow2')
            # #deleted_system_img_done = 'Deleting file '+ system_file_path +' done'
            # #deleted_system_img_done = 'system.img.qcow2 done'
            # deleted_system_img_done = 'emulator-user.ini done'
            # self.logger.debug('EMULATOR PROC - AVD SYSTEM LOC: {}'.format(deleted_system_img_done))
            # if deleted_system_img_done in msg['content']:
            #     self.logger.debug('Matched CONTENT')
            #     self.emu_process.kill()
            #     #exit(0)
            #     #self.copy_emu_system_img_to_temp()
            #     #self.inject_emu_system_img_from_temp()
            #     #sys.exit()
            #     #wipe_data = ''
            #     #cmd = [self.emulator_loc, '-avd', emulator_name, '-debug', 'init']
            #     #self.emu_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            #     #                                    universal_newlines=True, shell=True)

    def clean_out_avd_dir(self):
        avd_dir_name = self.avdName + '.avd'
        emu_dir_path = os.path.join(os.path.expanduser('~'),'.android','avd',avd_dir_name)
        dir_contents_list = os .listdir(emu_dir_path)

        for file_name in dir_contents_list:
            criterion = ".qcow"
            if criterion in file_name:
                file_to_remove =  os.path.join(emu_dir_path, file_name)
                self.logger.debug("Clearing out FILE: {}".format(file_to_remove))
                os.remove(file_to_remove)


    def inject_emu_system_img_from_temp(self):
        src_path = os.path.join('system-img-qcow2','android-22','system.img.qcow2')
        dst_path = os.path.join(os.path.expanduser('~'),'.android','avd','Nexus_5_API_22_2.avd', 'system.img.qcow2')
        #copyfile(src_path, dst_path)
        copy2(src_path, dst_path)
        self.logger.debug('Copied FROM: {}'.format(src_path) )
        self.logger.debug('Copied TO: {}'.format(dst_path))
        #return
