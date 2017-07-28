import os

from utils.directory_traversal_utils import get_sub_folders
from wui.core.core_utils.core_utils import _get_package_name


class AppDirectoryClass():

    def __init__(self, file_path, apps_directory="apps", default_directory="default"):
        """
        This is the constructor for AppDirectoryClass.

        Arguments:
            file_path: Absolute path to the katana directory
            apps_directory: Name of the user defined apps directory
            default_directory: Name of the default apps directory

        """
        self.file_path = file_path
        self.apps_directory = apps_directory
        self.default_directory = default_directory

        self.apps_package_name = _get_package_name(self.apps_directory)
        self.default_package_name = _get_package_name(self.default_directory)

        self.apps_directory_path = os.path.join(file_path, apps_directory)
        self.default_directory_path = os.path.join(file_path, default_directory)

        self.user_defined_apps = []
        self.default_apps = []
        self.all_apps = []

    def get_user_defined_apps(self):
        """
        This function gets all the directories inside the "/katana/apps" directory

        Returns:
            self.user_defined_apps: list of user defined apps

        """
        apps_sub_dir = get_sub_folders(self.apps_directory_path)
        for i in range(0, len(apps_sub_dir)):
            apps_sub_dir[i] = self.apps_package_name + apps_sub_dir[i]
        self.user_defined_apps.extend(apps_sub_dir)
        return self.user_defined_apps

    def get_default_apps(self):
        """
        This function gets all the directories inside the "/katana/default" directory

        Returns:
            self.default_apps: list of default apps

        """
        apps_sub_dir = get_sub_folders(self.default_directory_path)
        for i in range(0, len(apps_sub_dir)):
            apps_sub_dir[i] = self.default_package_name + apps_sub_dir[i]
        self.default_apps.extend(apps_sub_dir)
        return self.default_apps

    def get_all_apps(self, rerun=True):
        """
        This functions gets all (user defined and default) apps list. When the "rerun" flag is
        True, get_user_defined_apps() and get_default_apps() will be called and their returns
        will be consolidated into a single list, otherwise, self.user_defined_apps and
        self.default_apps will be consolidated into one list

        Args:
            rerun: Flag the calls get_user_defined_apps() and get_default_apps() if needed

        Returns:
            self.all_apps: Consolidated list of all apps

        """
        if rerun:
            self.all_apps.extend(self.get_user_defined_apps())
            self.all_apps.extend(self.get_default_apps())
        else:
            self.all_apps.extend(self.user_defined_apps)
            self.all_apps.extend(self.default_apps)
        return self.all_apps
