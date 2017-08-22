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

from __future__ import unicode_literals
from django.shortcuts import render
from django.views import View
from native.appstore.appstore_utils.uninstaller import Uninstaller
from wui.core.core_utils.app_info_class import AppInformation


class AppStoreView(View):

    template = 'appstore/appstore.html'

    def get(self, request):
        """
        Get Request Method
        """
        return render(request, AppStoreView.template, {"data": AppInformation.information.apps})


def uninstall_an_app(request):
    app_details = request.POST.get("app_details", None)
    uninstaller_obj = Uninstaller()
    uninstaller_obj.uninstall(app_details)
    return render(request, AppStoreView.template, {"data": AppInformation.information.apps})
