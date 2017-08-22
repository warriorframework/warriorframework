from utils.directory_traversal_utils import get_abs_path, join_path, get_parent_directory, \
    get_dir_from_path
from utils.json_utils import read_json_data


class Uninstaller:

    def __init__(self, base_directory, app_path, app_type):
        self.base_directory = base_directory
        self.plugin_dir = join_path(self.base_directory, "warrior", "plugins")
        self.app_dir = join_path(self.base_directory, "katana", app_type)
        self.app_path = get_abs_path(get_dir_from_path(app_path), self.app_dir)
        self.app_type = app_type
        self.config_file = join_path(self.app_path, "wf_config.json")
        self.related_plugins = self.__extract_plugin_names()
        self.valid_app_types = {"apps"}

    def uninstall(self):
        output = self.__validate_app_uninstallation()
        # delete folders
        # edit settings.py and urls.py
        return output

    def __extract_plugin_names(self):
        plugins = []
        data = read_json_data(self.config_file)
        if "plugins" in data:
            plugins = data[plugins]
        for i in range(0, len(plugins)):
            plugins[i] = get_abs_path(plugins[i], self.plugin_dir)
        return plugins

    def __validate_app_uninstallation(self):
        output = False
        # check if plugins are in place
        # check if app can be deleted safely
        return output
