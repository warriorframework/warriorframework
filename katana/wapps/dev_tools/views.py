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
import os
import json
from main import Main

from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

controls = Main()

def index(request):
    return render(request, 'dev_tools/index.html', {"data": ""})

def new_app(request):
    return render(request, 'dev_tools/new_app.html', {"data": ""})

def build_new_app(request):
    return render(request, 'dev_tools/new_app.html', {"data": controls.build_new_app(request)})

def edit_app(request):
    return render(request, 'dev_tools/edit_app.html', {"data": ""})

def get_urls(request):
    return JsonResponse(controls.get_urls(request))

def open_file(request):
    return JsonResponse(controls.open_file(request))

def save_file(request):
    return JsonResponse(controls.save_file(request))
