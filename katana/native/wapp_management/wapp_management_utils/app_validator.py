import copy
import os
import re
from distutils.version import LooseVersion

from utils.directory_traversal_utils import join_path, get_sub_dirs_and_files, \
    get_paths_of_subfiles, get_sub_folders
from utils.json_utils import read_json_data
from utils.navigator_util import Navigator


class AppValidator:

    def __init__(self, filepath):
        self.navigator = Navigator()
        self.app_name = get_sub_folders(join_path(filepath, "warriorframework", "katana", "wapps"))[0]
        self.path_to_app = join_path(filepath, "warriorframework", "katana", "wapps", self.app_name)
        self.wf_config_file = join_path(self.path_to_app, "wf_config.json")
        self.urls_inclusions = []
        self.mandatory_fields = ["app", "version", "warrior-compatibility", "warrior-incompatibility"]

    def is_valid(self):
        output = {"status": True, "message": ""}
        if os.path.exists(self.wf_config_file):
            data = read_json_data(self.wf_config_file)
            if data is not None:
                for field in self.mandatory_fields:
                    if output["status"] and field not in data:
                        output["status"] = False
                        output["message"] = "wf_config.json is not in the correct format."
                        print "-- An Error Occurred -- {0}".format(output["message"])

                if output["status"]:
                    output = self.__verify_app_details(data["app"])

                # validate version compatibility
                if output["status"]:
                    output = self.__is_compatible(data)

                # validate databases if any
                if output["status"] and "database" in data:
                    if isinstance(data["database"], list):
                        for db_details in data["database"]:
                            if output["status"]:
                                output = self.__verify_db_details(db_details)
                    else:
                        output = self.__verify_db_details(data["database"])
            else:
                output["status"] = False
                output["message"] = "wf_config.json is not in the correct format."
                print "-- An Error Occurred -- {0}".format(output["message"])

            if output["status"]:
                output = self.__validate_static_directory()
        else:
            output["status"] = False
            output["message"] = "wf_config.json does not exist."
            print "-- An Error Occurred -- {0}".format(output["message"])
        return output

    def __verify_app_details(self, app_details):
        output = {"status": True, "message": ""}
        if "name" not in app_details or "url" not in app_details or "include" not in app_details:
            print "-- An Error Occurred -- wf_config.json file is not in the correct format."
            output["status"] = False
        else:
            self.urls_inclusions.append("url(r'^" + app_details["url"] +
                                        "', include('" + app_details["include"] + "')),")
            path_dir = app_details["include"].split(".")
            path_urls = ""
            for d in range(2, len(path_dir)):
                path_urls += os.sep + path_dir[d]
            path_urls = path_urls.strip(os.sep)
            path_urls += ".py"
            path_to_urls_abs = join_path(self.path_to_app, path_urls)
            if not os.path.isfile(path_to_urls_abs):
                output["status"] = False
                output["message"] = "Package {0} does not exist.".format(app_details["include"])
                print "-- An Error Occurred -- {0}".format(output["message"])
        return output

    def __is_compatible(self, data):
        output = {"status": True, "message": ""}
        allowed, bounds = self.__get_version_list(data[self.mandatory_fields[2]])
        disallowed, excluded_bounds = self.__get_version_list(data[self.mandatory_fields[3]])
        warrior_version = self.navigator.get_wf_version()
        all_warrior_versions = self.navigator.get_all_wf_versions()

        in_allowed = self.__check_against_version_list(warrior_version, allowed, bounds)
        in_disallowed = self.__check_against_version_list(warrior_version, disallowed, excluded_bounds)

        if not in_allowed:
            output["status"] = False
            output["message"] = "-- An Error Occurred -- {0} (Version: {1}) incompatible with " \
                                "the current WarriorFramework (Version: {2})."\
                .format(self.app_name, data["version"], warrior_version)
        elif in_disallowed:
            output["status"] = False
            output["message"] = "-- An Error Occurred -- {0} (Version: {1}) appears to be both, " \
                                "compatible and incompatible with WarriorFramework (Version: {2})."\
                .format(self.app_name, data["version"], warrior_version)
        return output

    def __check_against_version_list(self, version, version_list, version_bounds):
        status = False
        for el in version_list:
            if version == el:
                status = True
                break
        if not status:
            for bound in version_bounds:
                if LooseVersion(version) <= LooseVersion(bound["upper"]):
                    if "lower" in bound:
                        if LooseVersion(version) >= LooseVersion(bound["lower"]):
                            status = True
                            break
                    else:
                        status = True
                        break
        return status

    def __get_version_list(self, versions):
        bounds = []
        individual = []
        version_list = versions.split(",")
        for el in version_list:
            el = el.strip()
            bound = {}
            if el.startswith(":"):
                bound["upper"] = el[1:].strip()
                bounds.append(copy.deepcopy(bound))
            elif "::" in el:
                el_list = el.split("::")
                bound["lower"] = el_list[0]
                bound["upper"] = el_list[1]
                bounds.append(copy.deepcopy(bound))
            else:
                individual.append(el)
        return individual, bounds


    def __verify_db_details(self, db_details):
        output = {"status": True, "message": ""}
        for key in db_details:
            if not key.startswith(self.app_name):
                output["status"] = False
                output["message"] = "wf_config.json file is not formatted correctly"
                print "-- An Error Occurred -- {0}".format(output["message"])
        return output

    def __validate_static_directory(self):
        output = {"status": True, "message": ""}
        if os.path.isdir(join_path(self.path_to_app, "static")):
            subs = get_sub_dirs_and_files(join_path(self.path_to_app, "static"))
            if len(subs["files"]) > 0:
                output["status"] = False
                output["message"] = "static directory does not follow the required " \
                                    "directory structure."
                print "-- An Error Occurred -- {0}".format(output["message"])
            else:
                if not os.path.isdir(join_path(self.path_to_app, "static", self.app_name)):
                    output["status"] = False
                    output["message"] = "static directory does not follow the required " \
                                        "directory structure."
                    print "-- An Error Occurred -- {0}".format(output["message"])
                else:
                        
                    subs_files = get_paths_of_subfiles(join_path(self.path_to_app, "static",
                                                                 self.app_name),
                                                       re.compile("\.js$"))
                    path_to_js = join_path(self.path_to_app, "static", self.app_name, "js")
                    for sub_file in subs_files:
                        if not sub_file.startswith(path_to_js):
                            output["status"] = False
                            output["message"] = "A .js file cannot be outside the 'js' folder."
                            print "-- An Error Occurred -- {0}".format(output["message"])
        return output
