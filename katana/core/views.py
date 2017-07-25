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
from django.views.generic import DetailView

from core.utils.core_utils import CoreIndex


class CoreView(View):

    def get(self, request):
        template = 'core/index.html'
        key = "app"
        apps = {key: []}
        app_content = {"name": "", "color": "", "url": "", "icon": ""}
        config_file = "details.txt"
        rel_path_settings_py = "../wui/settings.py"
        rel_path_urls_py = "../wui/urls.py"
        config_details_dict = {"icon": "", "color": ""}

        current_directory = os.path.dirname(os.path.realpath(__file__))
        core_index_obj = CoreIndex(current_directory, rel_path_settings_py, rel_path_urls_py, apps,
                                   app_content, config_file, config_details_dict, key)

        apps = core_index_obj.consolidate_app_details()

        return render(request, template, {"apps": apps})
