import logging
import os
#from os import listdir
#from os.path import isfile, join

class LogManager(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)


    def deduplicate_log_files(self, log_type):
        #dir_contents = os.listdir(os.path.join(os.path.pardir, "logs"))
        #self.logger.debug('Number of items in DIR: {}'.format(len(dir_contents)))
        log_path = os.path.join(os.path.pardir, "logs")
        only_files = [myFile for myFile in os.listdir(log_path) if os.path.isfile(os.path.join(log_path, myFile))]
        self.logger.debug('Number of files in DIR: {}'.format(len(only_files)))

        lines_seen = set()
        for log_file in only_files:
            # Check if it is the correct Log Type ('Success', 'FAILURE')
            if log_file.startswith(log_type):
                log_file_path = os.path.join(log_path, log_file)
                # Open file
                with open(log_file_path) as curr_log:
                    # sha256 and package name might be the same, but not timestamp





myLogMan = LogManager()
myLogMan.deduplicate_log_files('Success')

