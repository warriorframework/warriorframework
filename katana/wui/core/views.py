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

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
import json

from utils.directory_traversal_utils import get_parent_directory, join_path
from utils.navigator_util import Navigator
from wui.core.apps import AppInformation


class CoreView(View):
    
    def __init__(self):
        self.navigator = Navigator()

    def get_user_data(self):
        json_file = self.navigator.get_katana_dir() + '/user_profile.json'
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        return json_data

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

        return render(request, template, {"apps": AppInformation.information.apps, "userData": self.get_user_data()})


def refresh_landing_page(request):
    return render(request, 'core/landing_page.html', {"apps": AppInformation.information.apps})


def get_file_explorer_data(request):
    nav_obj = Navigator()
    if "data[path]" in request.POST and request.POST["data[path]"] != "false":
        start_dir = get_parent_directory(request.POST["data[path]"])
    else:
        start_dir = join_path(nav_obj.get_warrior_dir(), "Warriorspace")
    output = nav_obj.get_dir_tree_json(start_dir_path=start_dir)
    return JsonResponse(output)
