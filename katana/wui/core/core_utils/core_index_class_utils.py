import os

from utils.directory_traversal_utils import get_sub_folders
from utils.file_utils import readlines_from_file
from utils.string_utils import remove_trailing_characters_from_list
from wui.core.core_utils.core_utils import _get_package_name


class CoreIndex():

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

    def get_available_apps(self):
        """
        This function gets a list of app directories available in /warriorframework/katana/

        Returns:
            self.available_apps: list of app directories available in /warriorframework/katana/

        """

        self.available_apps.extend(_get_user_defined_apps(os.path.join(self.base_directory, "apps"),
                                                          _get_package_name("apps")))
        self.available_apps.extend(_get_default_apps(os.path.join(self.base_directory, "native"),
                                                     _get_package_name("native")))
        return self.available_apps

    def get_apps_from_settings_file(self, start="INSTALLED_APPS = [", end="]\n",
                                    starts_with="django.", formatting_list=None):
        """
        This function gets a list of installed apps from the settings.py file

        Returns:
            self.settings_installed_apps: list of installed apps from the settings.py file

        """

        if formatting_list is None:
            formatting_list = [" ", "\n", ",", "'"]
        apps_list = readlines_from_file(self.settings_file_abs_path, start=start, end=end)
        formatted_apps_list = remove_trailing_characters_from_list(apps_list, formatting_list)

        for i in range(0, len(formatted_apps_list)):
            if not formatted_apps_list[i].startswith(starts_with):
                self.settings_installed_apps.append(formatted_apps_list[i])

        return self.settings_installed_apps


def _get_user_defined_apps(apps_directory_path, apps_package_name):
    """
    This function gets all the directories inside the "/katana/apps" directory

    Returns:
        self.user_defined_apps: list of user defined apps

    """
    apps_list = []
    apps_sub_dir = get_sub_folders(apps_directory_path)
    for i in range(0, len(apps_sub_dir)):
        apps_sub_dir[i] = apps_package_name + apps_sub_dir[i]
    apps_list.extend(apps_sub_dir)
    return apps_list


def _get_default_apps(default_directory_path, default_package_name):
    """
    This function gets all the directories inside the "/katana/native" directory

    Returns:
        self.default_apps: list of default apps

    """
    apps_list = []
    apps_sub_dir = get_sub_folders(default_directory_path)
    for i in range(0, len(apps_sub_dir)):
        apps_sub_dir[i] = default_package_name + apps_sub_dir[i]
    apps_list.extend(apps_sub_dir)
    return apps_list
