import os
import re
from utils.directory_traversal_utils import join_path, get_sub_dirs_and_files, \
    get_paths_of_subfiles, get_dir_from_path
from utils.json_utils import read_json_data


class AppValidator:

    def __init__(self, filepath):
        self.app_name = get_dir_from_path(filepath)
        self.path_to_app = join_path(filepath, "warriorframework", "katana", "apps", self.app_name)
        self.wf_config_file = join_path(self.path_to_app, "wf_config.json")
        self.urls_inclusions = []

    def is_valid(self):
        output = True
        if os.path.exists(self.wf_config_file):
            data = read_json_data(self.wf_config_file)
            if data is not None:
                if "app" in data:
                    if isinstance(data["app"], list):
                        for app_details in data["app"]:
                            if output:
                                output = self.__verify_app_details(app_details)
                            else:
                                break

                    else:
                        output = self.__verify_app_details(data["app"])
                else:
                    print "-- An Error Occurred -- wf_config.json is not in the correct format."
                    output = False

                # validate databases if any
                if "database" in data:
                    if isinstance(data["database"], list):
                        for db_details in data["database"]:
                            if output:
                                output = self.__verify_db_details(db_details)
                    else:
                        output = self.__verify_db_details(data["database"])
            else:
                print "-- An Error Occurred -- wf_config.json is not in the correct format."
                output = False

            if output:
                output = self.__validate_static_directory()
        else:
            print "-- An Error Occurred -- wf_config.json does not exist."
            output = False
        return output

    def __verify_app_details(self, app_details):
        output = True
        if "name" not in app_details or "url" not in app_details or "include" not in app_details:
            print "-- An Error Occurred -- wf_config.json file is not in the correct format."
            output = False
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
                print "-- An Error Occurred -- Package {0} does not exist.".format(app_details["include"])
                output = False
        return output

    def __verify_db_details(self, db_details):
        output = False
        for key in db_details:
            if not key.startswith(self.app_name):
                print "-- An Error Occurred -- wf_config.json file is not formatted correctly"
                output = False
        return output

    def __validate_static_directory(self):
        output = True
        if os.path.isdir(join_path(self.path_to_app, "static")):
            subs = get_sub_dirs_and_files(join_path(self.path_to_app, "static"))
            if len(subs["files"]) > 0:
                print "--An Error Occurred -- static directory does not follow the required " \
                      "directory structure."
                output = False
            else:
                if not os.path.isdir(join_path(self.path_to_app, "static", self.app_name)):
                    print "-- An Error Occurred -- static directory does not follow the required " \
                          "directory structure."
                    output = False
                else:
                        
                    subs_files = get_paths_of_subfiles(join_path(self.path_to_app, "static",
                                                                 self.app_name),
                                                       re.compile("\.js$"))
                    path_to_js = join_path(self.path_to_app, "static", self.app_name, "js")
                    for sub_file in subs_files:
                        if not sub_file.startswith(path_to_js):
                            print "-- An Error Occurred -- A .js file cannot be outside the " \
                                  "'js' folder."
                            output = False
        return output
