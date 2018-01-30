# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict

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
ERRORS = ["Next", "Abort", "Abort as Error", "Go To"]


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
        details_tmpl = _get_tmpl('cases/details_display_template.html', get_details_data(data))

        reqs_tmpl = _get_tmpl('cases/requirements_display_template.html', get_reqs_data(data))
        steps_tmpl = _get_tmpl('cases/steps_display_template.html', get_steps_data(data))
        new_step = _get_tmpl('cases/steps_template.html', _get_defaults(step=True, ts=len(data["Testcase"]["Steps"]["step"]) + 1))
        return JsonResponse({"filepath": file_path, "status": output["status"], "message": output["message"],
                             "details": str(details_tmpl), "requirements": str(reqs_tmpl), "steps": str(steps_tmpl),
                             "case_data_json": data, "new_step": str(new_step)})
    else:
        JsonResponse({"status": output["status"], "message": output["message"]})


def _get_defaults(details=False, requirement=False, step=False, ts="1"):
    output = False
    template_data = read_xml_get_json(TEMPLATE, ordered_dict=True)
    if details:
        return get_details_data(template_data)
    if requirement:
        return get_reqs_data(template_data)
    if step:
        return get_steps_data(template_data, ts=ts)
    return output


def get_details_data(data):
    output = {"data": data["Testcase"]["Details"]}
    output["data"]["states"] = ["New", "Test-Assigned", "Released", "Add Another"]
    output["data"]["default_on_errors"] = ERRORS
    output["data"]["datatypes"] = ["Custom", "Iterative", "Hybrid"]
    return output


def get_reqs_data(data):
    output = {"data": data["Testcase"]["Requirements"]}
    mid_req = (len(data["Testcase"]["Requirements"]["Requirement"]) + 1) / 2
    output["data"]["mid_req"] = mid_req
    return output


def get_steps_data(data, ts="1"):
    output = {"data": data["Testcase"]["Steps"]}
    if isinstance(output["data"]["step"], OrderedDict):
        output["data"]["step"]["@TS"] = ts
    output["data"]["execute_types"] = ["Yes", "No", "If", "If Not"]
    output["data"]["execute_elses"] = ERRORS
    output["data"]["run_modes"] = ["Run Multiple Times", "Run Until Pass", "Run Until Failure"]
    output["data"]["iteration_types"] = ["Standard", "Once Per Case", "End Of Case"]
    output["data"]["contexts"] = ["Positive", "Negative"]
    output["data"]["impacts"] = ["Impact", "No Impact"]
    output["data"]["on_errors"] = ERRORS
    return output


def _get_tmpl(template, data):
    return render_to_string(template, data)


def get_details_template(request):
    data = {"data": json.loads(request.POST.get("data"))}
    return render(request, 'cases/details_template.html', data)


def get_steps_template(request):
    print request.POST.get("data")
    return render(request, 'cases/steps_template.html')


def get_reqs_template(request):
    return render(request, 'cases/requirements_template.html')
