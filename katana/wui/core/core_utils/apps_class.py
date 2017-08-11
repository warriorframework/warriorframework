from utils.json_utils import read_json_data
from wui.core.core_utils.app_info_class import AppInformation
from wui.core.core_utils.core_utils import get_app_path_from_name


class App:

    def __init__(self, json_data):
        self.data = json_data


class Apps:

    def __init__(self):
        self.apps = []
        self.paths = []

    def set_apps(self, data):
        """ call this to build Apps array and make app objects """
        self.get_config_paths(data)
        for url in self.paths:
            app = App(read_json_data(url))
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
            logs = "--Warning-- {0} package is available for installation, but has not been " \
                  "installed.".format(app)
            AppInformation.log_obj.append_log(logs)
