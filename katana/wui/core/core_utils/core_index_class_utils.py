import os
from django.apps import apps
from utils.directory_traversal_utils import get_sub_folders
from wui.core.core_utils.core_utils import _get_package_name


class CoreIndex:

    def __init__(self, base_directory, settings_file_path=None):
        """
        This is the constructor for the class CoreIndex()

        Args:
            base_directory: Absolute path to the katana directory
            settings_file_path: Absolute path to the settings.py file
        """
        self.base_directory = base_directory
        self.available_apps = []
        self.settings_file_abs_path = settings_file_path
        self.settings_installed_apps = []
        self.user_apps = "wapps"
        self.native_apps = "native"

    def get_available_apps(self):
        """
        This function gets a list of app directories available in /warriorframework/katana/

        Returns:
            self.available_apps: list of app directories available in /warriorframework/katana/

        """

        self.available_apps.extend(_get_apps(os.path.join(self.base_directory, self.user_apps),
                                             _get_package_name(self.user_apps)))
        self.available_apps.extend(_get_apps(os.path.join(self.base_directory, self.native_apps),
                                             _get_package_name(self.native_apps)))
        return self.available_apps

    def get_apps_from_settings_file(self):
        """
        This function gets a list of installed apps from the settings.py file

        Returns:
            self.settings_installed_apps: list of installed apps from the settings.py file

        """

        for app in apps.get_app_configs():
            if not app.name.startswith('django.contrib.') and app.name != 'wui.core':
                self.settings_installed_apps.append(app.name)

        return self.settings_installed_apps


def _get_apps(apps_directory_path, apps_package_name):
    """
    This function gets all the app directories inside the "/katana/wapps" and "katana/native"
    directories

    Returns:
        apps_list: list of app paths

    """
    apps_list = []
    apps_sub_dir = get_sub_folders(apps_directory_path)
    for i in range(0, len(apps_sub_dir)):
        apps_sub_dir[i] = apps_package_name + apps_sub_dir[i]
    apps_list.extend(apps_sub_dir)
    return apps_list
