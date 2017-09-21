import os
import re

from utils.directory_traversal_utils import join_path, get_dir_from_path, get_sub_folders, \
    get_sub_dirs_and_files, get_paths_of_subfiles, delete_dir, get_parent_directory, \
    get_relative_path
from utils.file_utils import copy_dir, readlines_from_file, write_to_file
from utils.json_utils import read_json_data
from utils.navigator_util import Navigator
from utils.regex_utils import compile_regex
from wui.core.core_utils.app_info_class import AppInformation
from wui.core.core_utils.apps_class import App


class Installer:

    def __init__(self, base_directory, path_to_app):
        self.base_directory = base_directory
        self.app_directory = join_path(self.base_directory, "katana", "apps")
        self.plugin_directory = join_path(self.base_directory, "warrior", "plugins")
        self.settings_file = join_path(self.base_directory, "katana", "wui", "settings.py")
        self.urls_file = join_path(self.base_directory, "katana", "wui", "urls.py")

        self.app_name = get_dir_from_path(path_to_app)
        self.path_to_app = join_path(path_to_app, "warriorframework", "katana", "apps", self.app_name)
        self.path_to_plugin_dir = join_path(path_to_app, "warriorframework", "warrior", "plugins")
        self.wf_config_file = join_path(self.path_to_app, "wf_config.json")

        self.plugins_paths = get_sub_folders(self.path_to_plugin_dir, abs_path=True)
        self.pkg_in_settings = "apps.{0}".format(self.app_name)
        self.urls_inclusions = []
        self.settings_backup = []
        self.urls_backup = []

    def install(self):
        output = self.__validate_app()

        if output:
            output = self.__add_app_directory()

        if output:
            output = self.__add_plugins()

        if output:
            output = self.__edit_settings_py()

        if output:
            output = self.__edit_urls_py()

        if not output:
            if self.__revert_installation():
                print "App installation successfully reverted."
        else:
            self.__update_app_information()

        return output

    def __validate_app(self):
        # validate if wf_config exists and is in the correct format
        output = self.__validate_wf_config_contents()

        # validate if static dir exists - and if it does, it is in the correct structure
        if output:
            output = self.__validate_static_directory()

        return output

    def __validate_wf_config_contents(self):
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
                                                       re.compile("\.css$"))
                    if len(subs_files) > 0:
                        print "-- An Error Occurred -- static directory has a css file."
                        output = False
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

    def __add_plugins(self):
        output = True
        for plugin in self.plugins_paths:
            if output:
                plugin_name = get_dir_from_path(plugin)
                output = copy_dir(plugin, join_path(self.plugin_directory, plugin_name))
        return output

    def __add_app_directory(self):
        output = copy_dir(self.path_to_app, join_path(self.app_directory, self.app_name))
        return output

    def __edit_urls_py(self):
        checker = "RedirectView.as_view(url='/katana/')"

        data = readlines_from_file(self.urls_file)
        self.urls_backup = data
        index = -1
        for i in range(0, len(data)):
            if checker in data[i]:
                index = i+1
                break
        white_space = data[index].split("url")
        for i in range(0, len(self.urls_inclusions)):
            self.urls_inclusions[i] = white_space[0] + self.urls_inclusions[i] + "\n"

        u_data = data[:index]
        u_data.extend(self.urls_inclusions)
        u_data.extend(data[index:])

        urls_data = ""
        for line in u_data:
            urls_data += line
        output = write_to_file(self.urls_file, urls_data)
        return output

    def __edit_settings_py(self):
        data = readlines_from_file(self.settings_file)
        self.settings_backup = data
        index = -1
        for i in range(0, len(data)):
            if "wui.core" in data[i]:
                index = i
                break

        white_space = data[index].split("'")

        self.pkg_in_settings = white_space[0] + "'" + self.pkg_in_settings + "',\n"
        sf_data = data[:index]
        sf_data.append(self.pkg_in_settings)
        sf_data.extend(data[index:])

        settings_data = ""
        for line in sf_data:
            settings_data += line

        output = write_to_file(self.settings_file, settings_data)
        return output

    def __revert_installation(self):
        output = True
        if len(self.urls_backup) > 0:
            urls_data = ""
            for line in self.urls_backup:
                urls_data += line

            output = write_to_file(self.urls_file, urls_data)

        if len(self.settings_backup) > 0:
            settings_data = ""
            for line in self.settings_backup:
                settings_data += line

            output = write_to_file(self.settings_file, settings_data)

        path_to_app = join_path(self.app_directory, self.app_name)
        if os.path.exists(path_to_app):
            output = delete_dir(path_to_app)

        if output:
            for plugin in self.plugins_paths:
                if output:
                    plugin_name = get_dir_from_path(plugin)
                    path_to_plugin = join_path(self.plugin_directory, plugin_name)
                    if os.path.exists(path_to_plugin):
                        output = delete_dir(path_to_plugin)

        return output

    def __update_app_information(self):
        json_data = read_json_data(self.wf_config_file)
        if json_data is not None:
            app_path = get_parent_directory(self.wf_config_file)
            app = App(json_data, app_path, self.base_directory)
            js_urls = get_paths_of_subfiles(join_path(app_path, app.static_file_dir, "js"),
                                            extension=compile_regex("^\.js$"))
            for i in range(0, len(js_urls)):
                js_urls[i] = get_relative_path(js_urls[i], app_path)
            app.data["js_urls"] = js_urls
            AppInformation.information.apps.append(app)
