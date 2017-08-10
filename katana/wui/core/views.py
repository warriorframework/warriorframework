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
from django.views import View
from utils.directory_traversal_utils import get_abs_path, get_parent_directory
from wui.core.core_utils.core_index_class_utils import CoreIndex
from wui.core.core_utils.apps_class import Apps


class CoreView(View):

    def get(self, request):
        """
        This get function get information about the installed apps

        Args:
            request: HttpRequest that contains metadata about the request

        Returns:
            HttpResponse: containing an HTML template and data
                HTML template: core/index.html
                Data: [{"url":"/url/of/app", "name": "app_name",
                        "icon": "icon_name", "color": "red"}]

        """

        template = 'core/index.html'

        base_directory = get_parent_directory(os.path.dirname(os.path.realpath(__file__)), 2)
        apps = []
        config_file_name = "wf_config.json"
        settings_file_path = get_abs_path(os.path.join("wui", "settings.py"), base_directory)
        urls_file_path = get_abs_path(os.path.join("wui", "urls.py"), base_directory)
        config_details_dict = {"icon": "", "color": ""}

        core_index_obj = CoreIndex(base_directory, settings_file_path=settings_file_path,
                                   urls_file_path=urls_file_path)

        available_apps = core_index_obj.get_available_apps()
        # print available_apps

        settings_installed_apps = core_index_obj.get_apps_from_settings_file()
        # print settings_installed_apps

        urls_dictionary = core_index_obj.get_urls_from_urls_file()
        # print urls_in_urls_file
        appObj = Apps()
        apps = appObj.setApps( { 'config_file_name': config_file_name,
                                                         'config_details_dict': config_details_dict,
                                                         'available_apps': available_apps,
                                                         'settings_installed_apps': settings_installed_apps,
                                                         'urls_dictionary': urls_dictionary } )

        return render(request, template, {"apps": apps})
