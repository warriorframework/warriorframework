from utilities.file_utils import readlines_from_file
from wui.core.utils.reg_utils import strip_list_elements_of


class SettingsFileDetailsClass():

    def __init__(self, file_path=None):
        """
        Constructor for SettingsFileDetailsClass.

        Arguments:
            file_path: absolute path to the settings file
        """
        self.file_path = file_path
        self.apps_in_settings_py = []

    def get_settings_file_path(self):
        """
        Method to get the settings file path.

        Returns:
            self.file_path: path to the settings.py file

        """
        return self.file_path

    def update_settings_file_path(self, file_path):
        """
        This method updates the settings file path.

        Args:
            file_path: An absolute path to the settings.py file

        Returns:
            No return

        """
        self.file_path = file_path

    def get_installed_apps(self, start="INSTALLED_APPS = [", end="]\n", starts_with="django.",
                           formatting_list=None):
        """
        This method reads the settings.py file and gets the list of installed apps.

        Returns:
            self.apps_in_settings_file: list of installed apps

        """
        if formatting_list is None:
            formatting_list = [" ", "\n", ",", "'"]
        apps_list = readlines_from_file(self.file_path, start=start, end=end)
        formatted_apps_list = strip_list_elements_of(apps_list, formatting_list)

        for i in range(0, len(formatted_apps_list)):
            if not formatted_apps_list[i].startswith(starts_with):
                self.apps_in_settings_py.append(formatted_apps_list[i])

        return self.apps_in_settings_py
