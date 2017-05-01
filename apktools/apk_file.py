
import logging
import os
import axmlparserpy.axmlprinter as axmlprinter
import  axmlparserpy.apk
#import xml.dom.minidom as minidom
from xml.etree import ElementTree as ET
import zipfile
import traceback


class ApkFile(object):

    def __init__(self, apk_path):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.apk_rel_file_path = apk_path
        self.apk_sha_256_filename = self.apk_rel_file_path.rsplit(os.path.sep, 1)[1]
        self.package_name = ''
        self.activity_list = []
        self.app_permissions_list = []
        self.user_def_permissions = []

        self.root_tag = ''
        self.child_elements = 0
        self.main_package_name = None
        self.version_code = ''

        self.successful_parse = self.parse_android_manifest()

    def get_file_path(self):
        return self.apk_rel_file_path

    def parse_android_manifest(self):
        self.logger.debug('Temp APK location: {}'.format(self.apk_rel_file_path))
        # Reading a file inside a normal directory
        #manifest_path = os.path.join(self.apk_file_path, 'AndroidManifest.xml')
        #ap = axmlprinter.AXMLPrinter(open(manifest_path, 'rb').read())

        successful_parse = True

        try:
            #apk_archive = zipfile.ZipFile.open(self.apk_file_path, 'rb')
            #a_file = axmlparserpy.apk.APK(self.apk_file_path).get_file('AndroidManifest.xml')
            apk_archive = zipfile.ZipFile(self.apk_rel_file_path)
            self.logger.debug('APK File list: {}'.format(apk_archive.namelist()))
            manifest_file = apk_archive.open('AndroidManifest.xml', 'r').read()
            ap = axmlprinter.AXMLPrinter(manifest_file)

            #buff = minidom.parseString(ap.getBuff()).toxml()
            ## "buff" contains the parsed AXML in Minidom format and can be printed to screen

            xml_doc = ET.fromstring(ap.getBuff())

            self.root_tag = xml_doc.tag
            self.child_elements = len(list(xml_doc))
            self.main_package_name = xml_doc.get('package')
            self.version_code = xml_doc.get('{http://schemas.android.com/apk/res/android}versionCode')

            self.load_activity_list(xml_doc)
            self.load_permissions_list(xml_doc)

            if not self.do_apk_parse_sanity_check():
                successful_parse = False
                return successful_parse
        except Exception as err:
            self.logger.debug("APK Parsing failed: {}".format(err))
            self.logger.debug('Traceback:\n {}'.format(traceback.print_stack()))
            self.logger.error('Something failed with parsing the APK file ...')

            self.do_apk_parse_sanity_check()
            successful_parse = False
            return successful_parse

        if successful_parse:
            self.logger.debug('APK was parsed successfully - Package name: {}'.format(self.main_package_name))

        return successful_parse

    def do_apk_parse_sanity_check(self):
        sanity_success = True
        if self.main_package_name in (None, '') or not self.main_package_name.strip():
            self.logger.debug("PACKAGE name is empty - FAILED: {}".format(self.apk_sha_256_filename))
            self.main_package_name = 'FAILED_TO_PARSE_' + self.apk_sha_256_filename
            sanity_success = False
        if len(self.activity_list) == 0:
            self.logger.debug("PACKAGE contains NO ACTIVITIES: {}".format(self.apk_sha_256_filename))
            sanity_success = False

        return sanity_success

    def check_if_parse_was_successful(self):
        return self.successful_parse

    def load_activity_list(self, xmldoc):
        #for activity in xmldoc.findall('application/activity'):
        for activity in xmldoc.findall('.//activity'):
            activity_name = activity.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("APP ACTIVITY Name: %s" % activity_name)
            self.activity_list.append(activity_name)

    def load_permissions_list(self, xmldoc):
        for perm in xmldoc.findall('.//uses-permission'):
            perm_name = perm.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("APP PERMISSION Name: %s" % perm_name)
            self.app_permissions_list.append(perm_name)

    def load_user_def_perms_list(self, xmldoc):
        for perm in xmldoc.findall('.//permission'):
            perm_name = perm.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("USER DEFINED PERMISSION Name: %s" % perm_name)
            self.app_permissions_list.append(perm_name)

    def get_package_name(self):
        return self.main_package_name

    def get_activity_list(self):
        return self.activity_list

    def get_first_or_main_activity_label(self):
        activity_label = None
        activity_num = len(self.activity_list)
        if activity_num > 0:
            if activity_num > 1:
                activity_label_list = []
                criteria = ['Main', 'MainActivity']
                #activity_name_list = [item for item in self.activity_list if criteria in item]

                first_dotted_activity = None
                for activity_name_item in self.activity_list:
                    # Store first item if it has a dot (might be used in the condition towards the end)
                    if first_dotted_activity is None:
                        if '.' in activity_name_item:
                            first_dotted_activity = activity_name_item
                    for criterion_item in criteria:
                        if criterion_item.lower() in activity_name_item.lower():
                            activity_label_list.append(activity_name_item)
                            # Preference for .MainActivity
                            if criterion_item.lower() == criteria[1].lower:
                                activity_label = activity_name_item
                                self.logger.debug("Picked the activity with 'MainActivity in the name: {}".format(activity_label))
                                return activity_label
                            # Else pick the first in the list
                            else:
                                activity_label = activity_label_list[0]
                                self.logger.debug("Multiple labels with 'Main' in the name ...picking the first: {}".format(activity_label))
                        else:
                            # Check if there is at least 1 dot (in the name)
                            # if '.' in activity_name_item:
                            #     # Get the first one, and break
                            #     activity_label = activity_name_item
                            #     break
                            # else:
                            #    activity_label = self.activity_list[0]
                            # Pick the stored 'First-Dotted' Activity that we stored in the beginning of the loop
                            activity_label = first_dotted_activity
                            self.logger.debug('Picked the First-Dotted-ActivityLabel : {}'.format(activity_label))
            else:
                # Just pick the first activity, and if it doesn't have a dot, try add a dot to it
                activity_label = self.activity_list[0]
                if '.' not in activity_label:
                    activity_label = '.' + activity_label
                    self.logger.debug("Tried to prepend a dot [.] to the ActivityLabel: {}".format(activity_label))
        else:
            self.logger.debug('No Activities in APK')
            self.logger.error('No Activities in APK')

        self.logger.debug('ACTIVITY name chosen: {}'.format(activity_label))
        return activity_label

