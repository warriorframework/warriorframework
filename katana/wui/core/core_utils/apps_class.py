from utils.directory_traversal_utils import get_parent_directory, get_dir_from_path, join_path, \
    get_paths_of_subfiles, get_relative_path
from utils.json_utils import read_json_data
from utils.regex_utils import compile_regex
from wui.core.core_utils.app_info_class import AppInformation
from wui.core.core_utils.core_utils import get_app_path_from_name


class App:

    def __init__(self, json_data, path, base_directory):
        """Constructor of the App Class"""
        self.data = json_data
        self.path = get_relative_path(path, base_directory)
        self.static_file_dir = join_path("static", get_dir_from_path(path))
        self.app_type = get_dir_from_path(get_parent_directory(path))


class Apps:

    def __init__(self):
        """Constructor of the Apps Class"""
        self.apps = []
        self.paths = []

    def set_apps(self, data):
        """ call this to build Apps array and make app objects """
        self.get_config_paths(data)
        for url in self.paths:
            json_data = read_json_data(url)
            if json_data is not None:
                app_path = get_parent_directory(url)
                app = App(json_data, app_path, data["base_directory"])
                js_urls = get_paths_of_subfiles(join_path(app_path, app.static_file_dir, "js"),
                                                extension=compile_regex("^\.js$"))
                for i in range(0, len(js_urls)):
                    js_urls[i] = get_relative_path(js_urls[i], app_path)
                app.data["js_urls"] = js_urls
                self.apps.append(app)
        return self.apps

    def get_config_paths(self, data):
        """ sets paths array to paths of json files"""
        available_apps = set(data["available_apps"])
        settings_apps = set(data["settings_apps"])

        installed_apps = available_apps.intersection(settings_apps)

        for app in installed_apps:
            self.paths.append(get_app_path_from_name(app, data['config_file_name'],
                                                     data['base_directory']))

        extra_app_dirs = available_apps.union(settings_apps) - settings_apps
        for app in extra_app_dirs:
            print "--Warning-- {0} package is available for installation, but has not been " \
                  "installed.".format(app)
