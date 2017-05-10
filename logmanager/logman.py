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
        outfilepath = os.path.join(os.path.pardir, 'logs_unified', log_type+'.log')
        #if not os.path.exists(outfilepath):
        self.logger.debug("Log File Out path: {}".format(outfilepath))
        unified_outfile = open(outfilepath, "w")
        for log_file in only_files:
            # Check if it is the correct Log Type ('Success', 'FAILURE')
            if log_file.startswith(log_type):
                log_file_path = os.path.join(log_path, log_file)
                self.logger.debug("Dealing with LOG file: -> {}".format(log_file_path))
                # Open file
                with open(log_file_path, "r") as curr_log:
                    # sha256 and package name might be the same, but not timestamp
                    for line in curr_log:
                        sha_256 = line.split("::")[0]
                        if sha_256 not in lines_seen: # not a duplicate
                            self.logger.debug("New Line found: {}".format(line))
                            #with open(outfilepath, "a") as unified_outfile:
                            unified_outfile.write(line)
                            lines_seen.add(sha_256)
        #unified_outfile.close()



myLogMan = LogManager()
myLogMan.deduplicate_log_files('Success')
myLogMan.deduplicate_log_files("FAILURE")

