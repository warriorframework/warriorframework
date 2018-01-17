# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from utils.directory_traversal_utils import join_path
from utils.json_utils import read_json_data, read_xml_get_json
from utils.navigator_util import Navigator
from wapps.cases.cases_utils.verify_case_file import VerifyCaseFile

navigator = Navigator()
CONFIG_FILE = join_path(navigator.get_katana_dir(), "config.json")
APP_DIR = join_path(navigator.get_katana_dir(), "wapps", "cases")
STATIC_DIR = join_path(APP_DIR, "static", "cases")
TEMPLATE = join_path(STATIC_DIR, "base_templates", "Untitled.xml")


class CasesView(View):

    def get(self, request):
        """
        Get Request Method
        """
        return render(request, 'cases/cases.html')


def get_list_of_cases(request):
    config = read_json_data(CONFIG_FILE)
    return JsonResponse({"data": navigator.get_dir_tree_json(config["xmldir"])})


def get_file(request):
    file_path = request.GET.get('path')
    if file_path == "false":
        file_path = TEMPLATE
    vcf_obj = VerifyCaseFile(TEMPLATE, file_path)
    output, data = vcf_obj.verify_file()
    # print output
    # print json.dumps(data, indent=4, sort_keys=True)
    return render(request, 'cases/display_case.html', {"data": data})
