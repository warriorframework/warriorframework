# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.utils.safestring import SafeText
from django.views import View
from utils.directory_traversal_utils import join_path
from utils.json_utils import read_json_data, read_xml_get_json
from utils.navigator_util import Navigator
from utils.treeview_converter import TreeviewConverter
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
    if output["status"]:
        details_tmpl = _get_details_tmpl('cases/details_display_template.html', {"data": data["Testcase"]["Details"]})
        mid_req = (len(data["Testcase"]["Requirements"]["Requirement"]) + 1) / 2
        reqs_tmpl = _get_details_tmpl('cases/requirements_display_template.html', {"data": data["Testcase"]["Requirements"], "mid_req": mid_req})
        steps_tmpl = _get_details_tmpl('cases/steps_display_template.html', {"data": data["Testcase"]["Steps"]})
        return JsonResponse({"status": output["status"], "message": output["message"],
                             "details": str(details_tmpl), "requirements": str(reqs_tmpl), "steps": str(steps_tmpl)})
    else:
        JsonResponse({"status": output["status"], "message": output["message"]})


def _get_details_tmpl(template, data):
    return render_to_string(template, data)


def get_details_template(request):
    return render(request, 'cases/details_template.html')


def get_steps_template(request):
    return render(request, 'cases/steps_template.html')


def get_reqs_template(request):
    return render(request, 'cases/requirements_template.html')
