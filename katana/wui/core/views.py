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
from django.shortcuts import render
from django.views import View
from wui.core.apps import AppInformation


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
        # writing pending logs to the log file
        # AppInformation.log_obj.flush()

        return render(request, template, {"apps": AppInformation.information.apps})
