import os
from utilities.file_utils import get_sub_folders, get_current_directory, readlines_from_file, \
    get_abs_path


class CoreIndex():

    def __init__(self, current_directory, rel_path_settings_py=None, rel_path_urls_py=None,
                 apps=None, app_content=None, config_file=None, config_details_dict=None):
        self.current_directory = current_directory
        self.available_apps = []
        self.get_available_apps()

        self.apps_in_settings_py = []
        if rel_path_settings_py is not None:
            self.setting_path = get_abs_path(rel_path_settings_py, current_directory)
            self.get_apps_in_settings_py_file()

        self.url_dict = {}
        if rel_path_urls_py is not None:
            self.urls_path = get_abs_path(rel_path_urls_py, current_directory)
            self.get_url_info_from_urls_py()

        self.apps = apps
        self.app_content = app_content
        self.config_file = config_file
        self.config_details_dict = config_details_dict

    def get_available_apps(self):
        sub_dirs = get_sub_folders(os.path.dirname(self.current_directory))
        if "apps" in sub_dirs:
            apps_sub_dir = get_sub_folders(os.path.dirname(self.current_directory) + os.sep + "apps")
            for i in range(0, len(apps_sub_dir)):
                apps_sub_dir[i] = "apps." + apps_sub_dir[i]
                self.available_apps.extend(apps_sub_dir)
        if "default" in sub_dirs:
            def_sub_dir = get_sub_folders(os.path.dirname(self.current_directory) + os.sep + "default")
            for i in range(0, len(def_sub_dir)):
                def_sub_dir[i] = "default." + def_sub_dir[i]
                self.available_apps.extend(def_sub_dir)
        return self.available_apps

    def get_apps_in_settings_py_file(self, path=None):

        path = path or self.setting_path

        apps_list = readlines_from_file(path, start="INSTALLED_APPS = [", end="]\n")
        formatted_apps_list = strip_list_elements_of(apps_list, [" ", "\n", ",", "'"])

        for i in range(0, len(formatted_apps_list)):
            if not formatted_apps_list[i].startswith("django."):
                self.apps_in_settings_py.append(formatted_apps_list[i])

        return self.apps_in_settings_py

    def get_url_info_from_urls_py(self):
        urls_list = readlines_from_file(self.urls_path, start="urlpatterns = [", end="]\n")
        urls_list = strip_list_elements_of(urls_list, [" ", "url(", ",\n", ")"])

        for i in range(0, len(urls_list)):

            temp = urls_list[i].split(",")

            temp[0] = strip_list_element_of(temp[0], [" ", "r", "'", "^"])
            temp[0] = "/" + temp[0]

            temp[1] = strip_list_element_of(temp[1], [" ", "include(", ")", "'"])

            output = split_str_at_last_index(temp[1], ".")
            self.url_dict[output] = temp[0]

        return self.url_dict

    def consolidate_app_details(self):
        for app1 in self.available_apps:
            for app2 in self.apps_in_settings_py:
                if app1 == app2:
                    self.apps.append(self.app_content.copy())
                    index = len(self.apps) - 1

                    self.apps[index]["url"] = self.url_dict[app1]
                    self.apps[index]["name"] = app1.split(".")[-1].title()

                    app_config_file_path = get_app_path_from_name(app1, self.config_file,
                                                                       self.current_directory)

                    data = readlines_from_file(app_config_file_path)

                    for i in range(0, len(data)):
                        data[i] = data[i].strip()
                        temp = data[i].split("=")
                        temp[0] = temp[0].strip()
                        temp[1] = temp[1].strip()
                        self.config_details_dict[temp[0]] = temp[1]

                    self.apps[index].update(self.config_details_dict)
        return self.apps


def get_app_path_from_name(app_name, config_file, current_directory):
    temp = app_name.split(".")
    app_config_file_rel_path = ".." + os.sep
    for el in temp:
        app_config_file_rel_path += el
        app_config_file_rel_path += os.sep

    app_config_file_rel_path += config_file

    app_config_file_path = get_abs_path(app_config_file_rel_path, current_directory)

    return app_config_file_path


def split_str_at_last_index(str, split_at):
    temp = str.split(split_at)

    output = ""
    for j in range(0, len(temp) - 1):
        output += temp[j]
        output += split_at

    output = output.strip(split_at)

    return output


def strip_list_element_of(element, strip_list):
    for el in strip_list:
        element = element.strip(el)

    return element


def strip_list_elements_of(element_list, strip_list):
    for i in range(0, len(element_list)):
        for el in strip_list:
            element_list[i] = element_list[i].strip(el)
    return element_list