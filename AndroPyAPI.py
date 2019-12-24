import collections
import os

from .features_managment import *
from .aux_functions import *

API_SYSTEM_COMMANDS_LIST_FILE = 'info/system_commands.txt'
API_PACKAGES_LIST_FILE = 'info/package_index.txt'
API_CLASSES_LIST_FILE = 'info/class_index.txt'

class AndroPyAPI:

    api_system_commands = []
    api_packages_list = []
    api_classes_list = []

    def __init__(self):
        # Get paths to info files

        module_path = os.path.abspath(__file__)
        module_dir = os.path.dirname(module_path)

        commands_file = os.path.join(module_dir, API_SYSTEM_COMMANDS_LIST_FILE)
        pkgs_file = os.path.join(module_dir, API_PACKAGES_LIST_FILE)
        classes_file = os.path.join(module_dir, API_CLASSES_LIST_FILE)

        self.api_system_commands = [x.strip() for x in load_file(commands_file)]
        self.api_packages_list = [x.strip() for x in load_file(pkgs_file)]
        self.api_classes_list = [x.strip() for x in load_file(classes_file)]
        #print(self.api_system_commands)

    def get_static_features(self, apk):

        analysis_dict = {}

        list_smali_api_calls, list_smali_strings = read_strings_and_apicalls(apk, self.api_packages_list, self.api_classes_list)

        analysis_dict['commands'] = self._get_system_commands(apk, list_smali_strings)
        analysis_dict['api-calls'] = self._get_api_calls(apk, list_smali_api_calls)
        analysis_dict['api-pkgs'] = self._get_api_packages(apk, list_smali_api_calls)

        return analysis_dict

    def _get_system_commands(self, apk, list_smali_strings):
        
        list_system_commands = read_system_commands(list_smali_strings, self.api_system_commands)
        return Counter(list_system_commands)

    def _get_api_calls(self, apk, list_smali_api_calls):
        
        for api_call in list_smali_api_calls.keys():
            new_api_call = '.'.join(api_call.split(".")[:-1])
            if new_api_call in list_smali_api_calls.keys():
                list_smali_api_calls[new_api_call] = list_smali_api_calls[new_api_call] + list_smali_api_calls[api_call]
            else:
                list_smali_api_calls[new_api_call] = list_smali_api_calls[api_call]
                del list_smali_api_calls[api_call]

        return list_smali_api_calls

    def _get_api_packages(self, apk, list_smali_api_calls):

        API_packages_dict = {}
        android_list_packages_lenghts = [len(x.split(".")) for x in self.api_packages_list]

        list_api_calls_keys = list_smali_api_calls.keys()
        for api_call in list_api_calls_keys:
            score = 0
            package_chosen = None
            for i, package in enumerate(self.api_packages_list):
                len_package = android_list_packages_lenghts[i]
                if api_call.startswith(package) and len_package > score:
                    score = len_package
                    package_chosen = package
            if package_chosen is not None:
                if not package_chosen in API_packages_dict.keys():
                    API_packages_dict[package_chosen] = list_smali_api_calls[api_call]
                else:
                    API_packages_dict[package_chosen] += list_smali_api_calls[api_call]

        return API_packages_dict