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
from native.settings.settings import Settings
# Create your views here.

controls = Settings()

def index(request):
    return render(request, 'settings/index.html', {"data": controls.get_location()})

def email_setting_handler( request ):
    return render(request, 'settings/email_setting_handler.html', {"setting": controls.email_setting_handler(request)})

def secret_handler( request ):
    return render(request, 'settings/secret.html', {"secret": controls.secret_handler(request)})

def jira_setting_handler( request ):
    return render(request, 'settings/jira_setting_handler.html', {"jira": controls.jira_setting_handler(request)})
