# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from native.cli_data.cli_data_utils.verify_cli_data_class import VerifyCliDataClass
from utils.directory_traversal_utils import join_path
from utils.navigator_util import Navigator
from utils.json_utils import read_xml_get_json


class CliDataView(View):

    template = 'cli_data/cli_data.html'

    def get(self, request):
        """
        Get Request Method
        """

        return render(request, CliDataView.template)


class CliDataFileClass(View):
    nav_obj = Navigator()
    app_directory = join_path(nav_obj.get_katana_dir(), "native", "cli_data")
    app_static_dir = join_path(app_directory, "static")

    def get(self, request):
        filepath = request.GET.get('path')
        base_filepath = join_path(CliDataFileClass.app_static_dir, "base_templates", "empty.xml")
        if filepath == "false":
            filepath = base_filepath
        vcdc_obj = VerifyCliDataClass(filepath, base_filepath)
        json_data = vcdc_obj.verify_contents()
        return JsonResponse(json_data)
