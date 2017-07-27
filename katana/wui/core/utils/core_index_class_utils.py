from utilities.directory_traversal_utils import get_parent_directory
from wui.core.utils.app_directory_class_utils import AppDirectoryClass
from wui.core.utils.core_utils import get_app_path_from_name
from wui.core.utils.settings_file_class_utils import SettingsFileDetailsClass
from wui.core.utils.urls_py_class_utils import UrlsFileDetailsClass
from wui.core.utils.wf_config_class_utils import WfConfigFileClass


class CoreIndex():

    def __init__(self, current_directory, settings_file_path=None, urls_file_path=None):
        """
        This is the constructor for the class CoreIndex()

        Args:
            current_directory: Absolute path of current working directory
            settings_file_path: Absolute path to the settings.py file
            urls_file_path: Absolute path to the urls.py file
        """
        self.current_directory = current_directory

        self.available_apps = []
        self.create_adc_object()

        self.settings_file_abs_path = settings_file_path
        if self.settings_file_abs_path is not None:
            self.create_sfd_object()
        else:
            self.sfd_obj = None

        self.urls_file_abs_path = urls_file_path
        if self.urls_file_abs_path is not None:
            self.create_ufd_object()
        else:
            self.ufd_obj = None

        self.config_file_path = None
        self.config_details_dict = None

        self.settings_installed_apps = []
        self.urls_dictionary = {}

    def create_sfd_object(self):
        """
        This function creates the SettingsFileDetailsClass() object

        """
        self.sfd_obj = SettingsFileDetailsClass(self.settings_file_abs_path)

    def create_ufd_object(self):
        """
        This function creates the UrlsFileDetailsClass() object
        """
        self.ufd_obj = UrlsFileDetailsClass(self.urls_file_abs_path)

    def create_adc_object(self):
        """
        This function creates the AppDirectoryClass() object
        """
        self.adc_obj = AppDirectoryClass(get_parent_directory(self.current_directory, level=2))

    def create_wcc_object(self):
        """
        This function creates the WfConfigFileClass() object
        """
        self.wcc_obj = WfConfigFileClass(self.config_file_path, self.config_details_dict)

    def set_settings_file_path(self, settings_file_path):
        """
        This function sets the settings.py file path and creates the SettingsFileDetailsClass()
        object

        Args:
            settings_file_path:

        """
        self.settings_file_abs_path = settings_file_path
        self.create_sfd_object()

    def set_urls_file_path(self, urls_file_path):
        """
         This function sets the urls.py file path and creates the UrlsFileDetailsClass() object
        Args:
            urls_file_path: Absolute path to the urls.py file

        """
        self.urls_file_abs_path = urls_file_path
        self.create_ufd_object()

    def set_config_file_path_and_details(self, config_file_path, config_details_dict=None):
        """
         This function sets the wf_config.json file path and config file details_dict and
         creates the WfConfigFileClass() object
        Args:
            config_file_path: absolute path to the config file
            config_details_dict(optional): dict of what is needed out of the wf_config file

        """
        self.config_file_path = config_file_path
        self.config_details_dict = config_details_dict
        self.create_wcc_object()

    def get_available_apps(self):
        """
        This function gets a list of app directories available in /warriorframework/katana/

        Returns:
            self.available_apps: list of app directories available in /warriorframework/katana/

        """
        self.available_apps = self.adc_obj.get_all_apps()
        return self.available_apps

    def get_apps_from_settings_file(self):
        """
        This function gets a list of installed apps from the settings.py file

        Returns:
            self.settings_installed_apps: list of installed apps from the settings.py file

        """
        self.settings_installed_apps = self.sfd_obj.get_installed_apps()
        return self.settings_installed_apps

    def get_urls_from_urls_file(self):
        """
        Tis file gets the urls from the urls.py file

        Returns:
            self.urls_dictionary: the urls from the urls.py file as a dictionary

        """
        self.urls_dictionary = self.ufd_obj.get_urls_from_urls_py()
        return self.urls_dictionary

    def consolidate_app_details(self, apps, config_file_name, config_details_dict,
                                available_apps=None,
                                settings_installed_apps=None, urls_dictionary=None):
        """
        This functions compares the list of apps available in self.available_apps to the list of
        apps in self.settings_installed_apps. The urls for the common apps in those lists are then
        obtained from the self.urls_dictionary

        Args:
            apps: list that would contain information about the apps (in JSON/dict format)
            app_content: JSON/dict containing keys of needed information about apps
            config_file_name: Name of the wf_config file
            config_details_dict: details to be obtained from the wf_config file
            available_apps: list of apps available in /warriorframework/katana/
            settings_installed_apps: lust of apps 'installed' in settings.py
            urls_dictionary: urls dictionary of the installed apps

        Returns:
            apps: list of information (dict) about the installed apps.

        """
        if available_apps is None:
            available_apps = self.available_apps
        if settings_installed_apps is None:
            settings_installed_apps = self.settings_installed_apps
        if urls_dictionary is None:
            urls_dictionary = self.urls_dictionary
        app_content = {}
        for app1 in available_apps:
            for app2 in settings_installed_apps:
                if app1 == app2:
                    apps.append(app_content)
                    index = len(apps) - 1

                    apps[index]["url"] = urls_dictionary[app1]
                    apps[index]["name"] = app1.split(".")[-1].title()

                    app_config_file_path = get_app_path_from_name(app1, config_file_name,
                                                                  get_parent_directory(
                                                                      self.current_directory))
                    self.set_config_file_path_and_details(app_config_file_path, config_details_dict)

                    final_dict = self.wcc_obj.get_details_from_file()

                    apps[index].update(final_dict)
        return apps