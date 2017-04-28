
import logging
import os
import axmlparserpy.axmlprinter as axmlprinter
import  axmlparserpy.apk
#import xml.dom.minidom as minidom
from xml.etree import ElementTree as ET
import zipfile



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
        self.apk_sha_256_filename = ''
        self.package_name = ''
        self.activity_list = []
        self.app_permissions_list = []
        self.user_def_permissions = []

        self.root_tag = ''
        self.child_elements = 0
        self.main_package_name = ''
        self.version_code = ''

        self.parse_android_manifest()

    def get_file_path(self):
        return self.apk_rel_file_path

    def parse_android_manifest(self):
        self.logger.debug('Temp APK location: {}'.format(self.apk_rel_file_path))
        # Reading a file inside a normal directory
        #manifest_path = os.path.join(self.apk_file_path, 'AndroidManifest.xml')
        #ap = axmlprinter.AXMLPrinter(open(manifest_path, 'rb').read())

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
                for activity_name_item in self.activity_list:
                    for criterion_item in criteria:
                        if criterion_item.lower() in activity_name_item.lower():
                            activity_label_list.append(activity_name_item)
                            # Preference for .MainActivity
                            if criterion_item.lower() == criteria[1].lower:
                                activity_label = activity_name_item
                                return activity_label
                            # Else pick the first in the list
                            else:
                                activity_label = activity_label_list[0]
                        else:
                            # Check if there is at least 1 dot (in the name)
                            if '.' in activity_name_item:
                                # Get the first one, and break
                                activity_label = activity_name_item
                                break
                            else:
                                activity_label = self.activity_list[0]
            else:
                activity_label = self.activity_list[0]
        else:
            self.logger.debug('No Activities in APK')
            self.logger.error('No Activities in APK')

        self.logger.debug('ACTIVITY name chosen: {}'.format(activity_label))
        return activity_label

