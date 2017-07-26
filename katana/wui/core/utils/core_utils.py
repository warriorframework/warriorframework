import os
from utilities.file_utils import get_abs_path, readlines_from_file
from wui.core.utils.app_directory_class_utils import AppDirectoryClass
from wui.core.utils.reg_utils import get_app_path_from_name
from wui.core.utils.settings_file_class_utils import SettingsFileDetailsClass
from wui.core.utils.urls_py_class_utils import UrlsFileDetailsClass


class CoreIndex():

    def __init__(self, current_directory, settings_file_path=None, urls_file_path=None):
        self.current_directory = current_directory

        self.available_apps = []
        self.create_adc_object()

        self.settings_file_abs_path = None
        self.sfd_obj = None
        if settings_file_path is not None:
            self.set_settings_file_path(settings_file_path)
            self.create_sfd_object()

        self.urls_file_abs_path = None
        self.ufd_obj = None
        if urls_file_path is not None:
            self.set_urls_file_path(urls_file_path)
            self.create_ufd_object()

        self.settings_installed_apps = []
        self.urls_dictionary = {}

    def set_settings_file_path(self, settings_file_path):
        self.settings_file_abs_path = get_abs_path(settings_file_path, self.current_directory)

    def create_sfd_object(self):
        self.sfd_obj = SettingsFileDetailsClass(self.settings_file_abs_path)

    def set_urls_file_path(self, urls_file_path):
        self.urls_file_abs_path = get_abs_path(urls_file_path, self.current_directory)

    def create_ufd_object(self):
        self.ufd_obj = UrlsFileDetailsClass(self.urls_file_abs_path)

    def get_available_apps(self):
        self.available_apps = self.adc_obj.get_all_apps()
        return self.available_apps

    def create_adc_object(self):
        self.adc_obj = AppDirectoryClass(os.path.dirname(os.path.dirname(self.current_directory)))

    def get_apps_from_settings_file(self):
        self.settings_installed_apps = self.sfd_obj.get_installed_apps()
        return self.settings_installed_apps

    def get_urls_from_urls_file(self):
        self.urls_dictionary = self.ufd_obj.get_urls_from_urls_py()
        return self.urls_dictionary

    def consolidate_app_details(self, apps, app_content, config_file, config_details_dict):
        for app1 in self.available_apps:
            for app2 in self.settings_installed_apps:
                if app1 == app2:
                    apps.append(app_content.copy())
                    index = len(apps) - 1

                    apps[index]["url"] = self.urls_dictionary[app1]
                    apps[index]["name"] = app1.split(".")[-1].title()

                    app_config_file_path = get_app_path_from_name(app1, config_file,
                                                                       os.path.dirname(self.current_directory))

                    data = readlines_from_file(app_config_file_path)

                    for i in range(0, len(data)):
                        data[i] = data[i].strip()
                        temp = data[i].split("=")
                        temp[0] = temp[0].strip()
                        temp[1] = temp[1].strip()
                        config_details_dict[temp[0]] = temp[1]

                    apps[index].update(config_details_dict)
        return apps