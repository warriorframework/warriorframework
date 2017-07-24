"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render
from utils.file_utils import get_sub_folders, get_abs_path


def index(request):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    sub_dirs = get_sub_folders(os.path.dirname(current_directory))
    installed_apps = ["core"]
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

    setting_path = get_abs_path("../wui/settings.py", current_directory)
    with open(setting_path, "r") as f:
        data = f.readlines()
    apps_list = []
    flag = False
    for line in data:
        if flag and line == "]\n":
            break
        if flag:
            apps_list.append(line)
        if not flag and line.startswith("INSTALLED_APPS = ["):
            flag = True
    final_apps = []
    for i in range(0, len(apps_list)):
        apps_list[i] = apps_list[i].strip(" ")
        apps_list[i] = apps_list[i].strip("\n")
        apps_list[i] = apps_list[i].strip(",")
        apps_list[i] = apps_list[i].strip("'")
        if not apps_list[i].startswith("django."):
            final_apps.append(apps_list[i])


    print installed_apps
    print final_apps

    apps = {"app": []}

    for app1 in installed_apps:
        for app2 in final_apps:
            if app1 == app2:
                apps["app"].append({"name": app1, "color": "blue", "url": "", "icon": ""})


    return render(request, 'core/index.html', {"data": "This is the main Katana Core page"})
