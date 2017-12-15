import os
from utils.directory_traversal_utils import join_path, get_dir_from_path, get_sub_folders, \
    delete_dir
from utils.file_utils import copy_dir, readlines_from_file, write_to_file
from utils.json_utils import read_json_data


class Installer:

    def __init__(self, base_directory, path_to_app):
        self.base_directory = base_directory
        self.app_directory = join_path(self.base_directory, "katana", "apps")
        self.plugin_directory = join_path(self.base_directory, "warrior", "plugins")
        self.settings_file = join_path(self.base_directory, "katana", "wui", "settings.py")
        self.urls_file = join_path(self.base_directory, "katana", "wui", "urls.py")

        self.app_name = get_sub_folders(join_path(path_to_app, "warriorframework", "katana", "apps"))[0]
        self.path_to_app = join_path(path_to_app, "warriorframework", "katana", "apps", self.app_name)
        self.path_to_plugin_dir = join_path(path_to_app, "warriorframework", "warrior", "plugins")
        self.wf_config_file = join_path(self.path_to_app, "wf_config.json")

        self.plugins_paths = get_sub_folders(self.path_to_plugin_dir, abs_path=True)
        self.pkg_in_settings = "apps.{0}".format(self.app_name)
        self.urls_inclusions = []
        self.settings_backup = []
        self.urls_backup = []
        self.delete_app_dir = []
        self.delete_plugins_dir = []
        self.config_data = None
        self.message = ""

    def install(self):
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

        return output

    def __add_plugins(self):
        output = True
        for plugin in self.plugins_paths:
            if output:
                plugin_name = get_dir_from_path(plugin)
                temp_pl_path= join_path(self.plugin_directory, plugin_name)
                if os.path.exists(temp_pl_path):
                    output = False
                    message = "-- An Error Occurred -- Directory already exists: {0}.".format(temp_pl_path)
                    print message
                    self.message += message
                else:
                    output = copy_dir(plugin, temp_pl_path)
                    self.delete_plugins_dir.append(plugin)
        return output

    def __add_app_directory(self):
        temp_app_path = join_path(self.app_directory, self.app_name)
        if os.path.exists(temp_app_path):
            output = False
            message = "-- An Error Occurred -- Directory already exists: {0}.".format(temp_app_path)
            print message
            self.message += message
        else:
            output = copy_dir(self.path_to_app, temp_app_path)
            self.delete_app_dir.append(self.path_to_app)
        return output

    def __edit_urls_py(self):
        checker = "RedirectView.as_view(url='/katana/')"
        data = read_json_data(self.wf_config_file)
        if "app" in data:
            if not isinstance(data["app"], list):
                data["app"] = [data["app"]]

        for app_details in data["app"]:
            if app_details["url"].startswith("/"):
                app_url = app_details["url"][1:]
            else:
                app_url = app_details["url"]
            self.urls_inclusions.append("url(r'^" + app_url + "', include('" + app_details["include"] + "')),")

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
        print urls_data
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

        for app_path in self.delete_app_dir:
            output = delete_dir(app_path)

        if output:
            for plugin_path in self.delete_plugins_dir:
                if output:
                    output = delete_dir(plugin_path)

        return output
