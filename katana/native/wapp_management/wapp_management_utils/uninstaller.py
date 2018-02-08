from os import sep, path

from utils.directory_traversal_utils import get_dir_from_path, join_path, get_abs_path, create_dir, \
    delete_dir, get_parent_directory
from utils.file_utils import copy_dir, readlines_from_file, write_to_file
from utils.json_utils import read_json_data


class Uninstaller:

    def __init__(self, base_directory, app_path, app_type):
        self.app_name = get_dir_from_path(app_path)
        self.base_directory = base_directory
        self.plugin_dir = join_path(self.base_directory, "warrior", "plugins")
        self.app_dir = join_path(self.base_directory, "katana", app_type)
        self.settings_file = join_path(self.base_directory, "katana", "wui", "settings.py")
        self.urls_file = join_path(self.base_directory, "katana", "wui", "urls.py")
        self.app_path = get_abs_path(self.app_name, self.app_dir)
        self.app_type = app_type
        self.config_file = join_path(self.app_path, "wf_config.json")
        self.config_file_data = read_json_data(self.config_file)
        self.related_plugins = self.__extract_plugin_names()
        self.pkg_in_settings = self.__get_setting_file_info()
        self.include_urls = self.__get_urls_info()
        self.valid_app_types = {"wapps"}
        self.cache_dir = create_dir(join_path(self.base_directory, "katana", ".data", self.app_name))
        self.settings_backup = []
        self.urls_backup = []

    def uninstall(self):
        output = self.__copy_app_to_cache()

        if output:
            output = output and self.__remove_app_from_urls()

        if output:
            output = output and self.__delete_app_dirs()

        if output:
            output = output and self.__remove_app_from_settings()

        if not output:
            if self.__recover_app():
                print "App successfully recovered."

        output = self.__delete_cache_dir()

        return output

    def __extract_plugin_names(self):
        plugins = []
        temp = []
        default_plugin = "{0}_plugin".format(self.app_name)

        if "plugins" in self.config_file_data:
            temp = self.config_file_data[plugins]
        if default_plugin not in temp:
            temp.append(default_plugin)

        for plugin in temp:
            temp_path = get_abs_path(plugin, base_path=self.plugin_dir, silence_error=True)
            if path.exists(temp_path):
                plugins.append(temp_path)

        return plugins

    def __get_setting_file_info(self):
        return "{0}.{1}".format(self.app_type, self.app_name.replace(sep, "."))

    def __get_urls_info(self):
        include = []
        app_info = []
        if "app" in self.config_file_data:
            app_info = self.config_file_data["app"]

        if "include" in app_info:
            include.append(app_info["include"])
        return include

    def __copy_app_to_cache(self):
        output = True
        for plugin in self.related_plugins:
            if output:
                output = output and copy_dir(plugin, get_abs_path(get_dir_from_path(plugin),
                                                                  self.cache_dir,
                                                                  silence_error=True))
            else:
                print "-- An Error Occurred -- Could not backup the plugins. Uninstallation " \
                      "suspended."
        if output:
            output = output and copy_dir(self.app_path, get_abs_path(self.app_name,
                                                                     self.cache_dir,
                                                                     silence_error=True))
        else:
            print "-- An Error Occurred -- Could not backup the app. Uninstallation suspended."

        return output

    def __remove_app_from_settings(self):
        data = readlines_from_file(self.settings_file)
        sf_data = []
        for line in data:
            if line.strip() != "'{0}',".format(self.pkg_in_settings):
                sf_data.append(line)

        settings_data = ""
        for line in sf_data:
            settings_data += line

        output = write_to_file(self.settings_file, settings_data)
        return output

    def __remove_app_from_urls(self):
        print self.include_urls
        data = readlines_from_file(self.urls_file)

        urls_data = ""
        for url in self.include_urls:
            urls_data = ""
            for line in data:
                if url not in line:
                    urls_data += line
            data = urls_data
        output = write_to_file(self.urls_file, urls_data)
        return output

    def __delete_app_dirs(self):
        output = delete_dir(self.app_path)
        for plugin in self.related_plugins:
            output = output and delete_dir(plugin)
        return output

    def __recover_app(self):
        if len(self.settings_backup) > 0:
            settings_data = ""
            for line in self.settings_backup:
                settings_data += line
            write_to_file(self.settings_file, settings_data)

        if len(self.urls_backup) > 0:
            urls_data = ""
            for line in self.urls_backup:
                urls_data += line
            write_to_file(self.urls_file, urls_data)

    def __delete_cache_dir(self):
        output = delete_dir(get_parent_directory(self.cache_dir))
        return output
