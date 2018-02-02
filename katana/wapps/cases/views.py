# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict

from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View
from utils.directory_traversal_utils import join_path
from utils.json_utils import read_json_data, read_xml_get_json
from utils.navigator_util import Navigator
from wapps.cases.cases_utils.defaults import impacts, on_errors, runmodes, iteration_types, contexts
from wapps.cases.cases_utils.get_drivers import GetDriversActions
from wapps.cases.cases_utils.verify_case_file import VerifyCaseFile

navigator = Navigator()
CONFIG_FILE = join_path(navigator.get_katana_dir(), "config.json")
APP_DIR = join_path(navigator.get_katana_dir(), "wapps", "cases")
STATIC_DIR = join_path(APP_DIR, "static", "cases")
TEMPLATE = join_path(STATIC_DIR, "base_templates", "Untitled.xml")
DROPDOWN_DEFAULTS = read_json_data(join_path(STATIC_DIR, "base_templates", "dropdowns_data.json"))


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
        steps_tmpl = _get_tmpl('cases/steps_display_template.html', get_steps_data(data, default=True))
        return JsonResponse({"filepath": file_path, "status": output["status"], "message": output["message"],
                             "details": str(details_tmpl), "requirements": str(reqs_tmpl), "steps": str(steps_tmpl),
                             "case_data_json": data})
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
        return get_steps_data(template_data, ts=ts, default=True)
    return output


def get_details_data(data):
    output = {"data": data["Testcase"]["Details"]}
    output["data"].update(DROPDOWN_DEFAULTS["details"])
    return output


def get_reqs_data(data):
    output = {"data": data["Testcase"]["Requirements"]}
    mid_req = (len(data["Testcase"]["Requirements"]["Requirement"]) + 1) / 2
    output["data"]["mid_req"] = mid_req
    return output


def get_steps_data(data, ts="1", default=False):
    output = {"data": {}}
    if default:
        output["data"] = data["Testcase"]["Steps"]
    else:
        output["data"] = {"step": data}
    if isinstance(output["data"]["step"], OrderedDict):
        output["data"]["step"]["@TS"] = ts
    output["data"].update(DROPDOWN_DEFAULTS["step"])
    da_obj = GetDriversActions(navigator.get_warrior_dir()[:-1])
    output["data"]["drivers"] = da_obj.get_all_actions()
    return output


def _get_tmpl(template, data):
    return render_to_string(template, data)


def get_details_template(request):
    data = {"data": json.loads(request.POST.get("data"))}
    return render(request, 'cases/details_template.html', data)


def get_steps_template(request):
    if request.POST.get("data") == "false":
        output = _get_defaults(step=True, ts=request.POST.get("ts"))
    else:
        output = get_steps_data(json.loads(request.POST.get("data")))
    return render(request, 'cases/steps_template.html', output)


def get_reqs_template(request):
    print request.POST
    data = {"data": json.loads(request.POST.get("data"))}
    return render(request, 'cases/requirements_template.html', data)


def get_details_display_template(request):
    output = {"data": json.loads(request.POST.get("data"))}
    output["data"].update(DROPDOWN_DEFAULTS["details"])
    return render(request, 'cases/details_display_template.html', output)


def get_reqs_display_template(request):
    output = {"data": {}}
    output["data"]["Requirement"] = json.loads(request.POST.get("data"))
    mid_req = (len(output["data"]["Requirement"]) + 1) / 2
    output["data"]["mid_req"] = mid_req
    return render(request, 'cases/requirements_display_template.html', output)


def get_steps_display_template(request):
    output = {"data": {"step": {}}}
    if request.POST.get("data") == "false":
        output["data"]["step"] = _get_defaults(step=True)
    else:
        output["data"]["step"] = convert_data(json.loads(request.POST.get("data")), int(request.POST.get("ts")))
    return render(request, 'cases/steps_display_template.html', output)


def convert_data(data, ts):
    print json.dumps(data[ts], indent=1)
    if data[ts]["impact"] in impacts():
        data[ts]["impact"] = impacts()[data[ts]["impact"]]
    if data[ts]["context"] in contexts():
        data[ts]["context"] = contexts()[data[ts]["context"]]
    if data[ts]["Execute"]["Rule"]["@Else"] in on_errors():
        data[ts]["Execute"]["Rule"]["@Else"] = on_errors()[data[ts]["Execute"]["Rule"]["@Else"]]
    if data[ts]["runmode"]["@type"] in runmodes():
        data[ts]["runmode"]["@type"] = runmodes()[data[ts]["runmode"]["@type"]]
    if data[ts]["Iteration_type"]["@type"] in iteration_types():
        data[ts]["Iteration_type"]["@type"] = iteration_types()[data[ts]["Iteration_type"]["@type"]]
    if data[ts]["onError"]["@action"] in iteration_types():
        data[ts]["onError"]["@action"] = on_errors()[data[ts]["onError"]["@action"]]
    print json.dumps(data[ts], indent=1)
    return data