# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

import xmltodict
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from wapps.cli_data.cli_data_utils.verify_cli_data_class import VerifyCliDataClass
from utils.directory_traversal_utils import join_path, get_dir_from_path
from utils.navigator_util import Navigator


class CliDataView(View):

    template = 'cli_data/cli_data.html'

    def get(self, request):
        """
        Get Request Method
        """

        return render(request, CliDataView.template)


class CliDataFileClass(View):
    nav_obj = Navigator()
    app_directory = join_path(nav_obj.get_katana_dir(), "wapps", "cli_data")
    app_static_dir = join_path(app_directory, "static")

    def get(self, request):
        filepath = request.GET.get('path')
        # filepath = join_path(CliDataFileClass.app_static_dir, "base_templates", "test.xml")
        base_filepath = join_path(CliDataFileClass.app_static_dir, "base_templates", "empty.xml")
        if filepath == "false":
            filepath = base_filepath
            name = "Untitled"
        else:
            name, _ = os.path.splitext(get_dir_from_path(filepath))
        vcdc_obj = VerifyCliDataClass(filepath, base_filepath)
        json_data = vcdc_obj.verify_contents()
        return JsonResponse({"contents": json_data, "name": name})

    def post(self, request):
        json_data = json.loads(request.POST.get('json_data'))
        data = xmltodict.unparse(json_data)
        directory = request.POST.get('directory')
        filepath = os.path.join(directory, request.POST.get('filename') + ".xml")
        message = ""
        saved = True
        try:
            with open(filepath, 'w') as f:
                f.write(data)
        except Exception as e:
            saved = False
            message = e
        return JsonResponse({"saved": saved, "message": message})