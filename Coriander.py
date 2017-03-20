
import logging
from SdkManager import SdkManager
from adb_wrapper import AdbWrapper
import emulator_wrapper


class Coriander(object):
    #Space for shared (usually non-mutable data members)

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.emulator_wrapper
        self.adb_wrapper


    def main(self):
        coriander = Coriander()

if __name__ == "__main__": main()