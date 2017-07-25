import os
from utilities.file_utils import get_sub_folders, get_current_directory, readlines_from_file, \
    get_abs_path


def get_available_apps(current_directory):
    installed_apps = []
    installed_apps.append(get_current_directory(current_directory))

    sub_dirs = get_sub_folders(os.path.dirname(current_directory))
    if "apps" in sub_dirs:
        apps_sub_dir = get_sub_folders(os.path.dirname(current_directory) + os.sep + "apps")
        for i in range(0, len(apps_sub_dir)):
            apps_sub_dir[i] = "apps." + apps_sub_dir[i]
        installed_apps.extend(apps_sub_dir)
    if "default" in sub_dirs:
        def_sub_dir = get_sub_folders(os.path.dirname(current_directory) + os.sep + "default")
        for i in range(0, len(def_sub_dir)):
            def_sub_dir[i] = "default." + def_sub_dir[i]
        installed_apps.extend(def_sub_dir)
    return installed_apps


def strip_list_elements_of(element_list, strip_list):
    for i in range(0, len(element_list)):
        for el in strip_list:
            element_list[i] = element_list[i].strip(el)
    return element_list


def strip_list_element_of(element, strip_list):
    for el in strip_list:
        element = element.strip(el)

    return element


def get_apps_in_settings_py_file(path):
    final_list = []

    apps_list = readlines_from_file(path, start="INSTALLED_APPS = [", end="]\n")
    formatted_apps_list = strip_list_elements_of(apps_list, [" ", "\n", ",", "'"])

    for i in range(0, len(formatted_apps_list)):
        if not formatted_apps_list[i].startswith("django."):
            final_list.append(formatted_apps_list[i])

    return formatted_apps_list


def split_str_at_last_index(str, split_at):
    temp = str.split(split_at)

    output = ""
    for j in range(0, len(temp) - 1):
        output += temp[j]
        output += split_at

    output = output.strip(split_at)

    return output


def get_url_info_from_urls_py(path):

    url_dict = {}

    urls_list = readlines_from_file(path, start="urlpatterns = [", end="]\n")
    urls_list = strip_list_elements_of(urls_list, [" ", "url(", ",\n", ")"])

    for i in range(0, len(urls_list)):

        temp = urls_list[i].split(",")

        temp[0] = strip_list_element_of(temp[0], [" ", "r", "'", "^"])
        temp[0] = "/" + temp[0]

        temp[1] = strip_list_element_of(temp[1], [" ", "include(", ")", "'"])

        output = split_str_at_last_index(temp[1], ".")
        url_dict[output] = temp[0]

    return url_dict


def consolidate_app_details(apps, app_content, available_apps, apps_in_settings_py, url_dict,
                            current_directory, key, config_file,
                            config_details_dict={"icon": "", "color": ""}):
    for app1 in available_apps:
        for app2 in apps_in_settings_py:
            if app1 == app2:
                apps[key].append(app_content)
                index = len(apps[key]) - 1

                apps[key][index]["url"] = url_dict[app1]
                apps[key][index]["name"] = app1.split(".")[-1].title()

                app_config_file_path = get_app_path_from_name(app1, config_file, current_directory)

                data = readlines_from_file(app_config_file_path)

                for i in range(0, len(data)):
                    data[i] = data[i].strip()
                    temp = data[i].split("=")
                    temp[0] = temp[0].strip()
                    temp[1] = temp[1].strip()
                    config_details_dict[temp[0]] = temp[1]

                apps[key][index].update(config_details_dict)
    return apps


def get_app_path_from_name(app_name, config_file, current_directory):
    temp = app_name.split(".")
    app_config_file_rel_path = ".." + os.sep
    for el in temp:
        app_config_file_rel_path += el
        app_config_file_rel_path += os.sep

    app_config_file_rel_path += config_file

    app_config_file_path = get_abs_path(app_config_file_rel_path, current_directory)

    return app_config_file_path