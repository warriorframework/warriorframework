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

from core.utils.core_utils import get_available_apps, get_apps_in_settings_py_file, \
    get_url_info_from_urls_py, consolidate_app_details
from utilities.file_utils import get_abs_path, readlines_from_file


def index(request):
    template = 'core/index.html'
    key = "app"
    apps = {key: []}
    app_content = {"name": "", "color": "", "url": "", "icon": ""}
    config_file = "details.txt"
    rel_path_settings_py = "../wui/settings.py"
    rel_path_urls_py = "../wui/urls.py"

    current_directory = os.path.dirname(os.path.realpath(__file__))
    available_apps = get_available_apps(current_directory)

    setting_path = get_abs_path(rel_path_settings_py, current_directory)
    apps_in_settings_py = get_apps_in_settings_py_file(setting_path)

    print apps_in_settings_py

    urls_path = get_abs_path(rel_path_urls_py, current_directory)
    print urls_path
    url_dict = get_url_info_from_urls_py(urls_path)

    apps = consolidate_app_details(apps=apps, app_content=app_content,
                                   available_apps=available_apps, key=key,
                                   apps_in_settings_py=apps_in_settings_py, url_dict=url_dict,
                                   current_directory=current_directory, config_file=config_file)

    print apps

    return render(request, template, {"apps": apps})
