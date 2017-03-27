
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

        self.apk_file_path = apk_path
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
        return self.apk_file_path

    def parse_android_manifest(self):
        self.logger.debug('Temp APK location: {}'.format(self.apk_file_path))
        # Reading a file inside a normal directory
        #manifest_path = os.path.join(self.apk_file_path, 'AndroidManifest.xml')
        #ap = axmlprinter.AXMLPrinter(open(manifest_path, 'rb').read())

        #apk_archive = zipfile.ZipFile.open(self.apk_file_path, 'rb')
        #a_file = axmlparserpy.apk.APK(self.apk_file_path).get_file('AndroidManifest.xml')
        apk_archive = zipfile.ZipFile(self.apk_file_path)
        manifest_file = apk_archive.open('AndroidManifest.xml', 'r').read()
        #manifest_file = apk_archive.read('AndroidManifest.xml')
        #apk_file = zipfile.ZipFile.open(self.apk_file_path, 'rb').read()
        ap = axmlprinter.AXMLPrinter(manifest_file)

        #buff = minidom.parseString(ap.getBuff()).toxml()
        ## "buff" contains the parsed AXML in Minidom format and can be printed to screen

        xml_doc = ET.fromstring(ap.getBuff())

        self.root_tag = xml_doc.tag
        self.child_elements = len(list(xml_doc))
        self.main_package_name = xml_doc.get('package')
        self.version_code = xml_doc.get('{http://schemas.android.com/apk/res/android}versionCode')

        self.get_activity_list(xml_doc)
        self.get_permissions_list(xml_doc)

    def get_activity_list(self, xmldoc):
        #for activity in xmldoc.findall('application/activity'):
        for activity in xmldoc.findall('.//activity'):
            activity_name = activity.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("APP ACTIVITY Name: %s" % activity_name)
            self.activity_list.append(activity_name)

    def get_permissions_list(self, xmldoc):
        for perm in xmldoc.findall('.//uses-permission'):
            perm_name = perm.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("APP PERMISSION Name: %s" % perm_name)
            self.app_permissions_list.append(perm_name)

    def get_user_def_perms_list(self, xmldoc):
        for perm in xmldoc.findall('.//permission'):
            perm_name = perm.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("USER DEFINED PERMISSION Name: %s" % perm_name)
            self.app_permissions_list.append(perm_name)

