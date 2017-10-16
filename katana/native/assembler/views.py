# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
import json
import os
import subprocess
import xmltodict
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from native.assembler.assembler_utils.repository_details import KwRepositoryDetails
from utils.directory_traversal_utils import get_dir_from_path
from utils.navigator_util import Navigator


class AssemblerView(View):

    def get(self, request):
        return render(request, 'assembler/assembler.html')


class ConfigurationFileOps(View):

    def post(self, request):
        nav_obj = Navigator()
        template = request.POST.get('filepath')
        ref_data = read_xml_get_json(os.path.join(nav_obj.get_katana_dir(), "native", "assembler",
                                                  "static", "assembler", "base_templates",
                                                  "empty.xml"))
        filename = "Untitled"
        if template == "false":
            json_data = copy.deepcopy(ref_data)
        else:
            json_data = read_xml_get_json(template)
            filename, ext = os.path.splitext(get_dir_from_path(template))

        final_data = copy.deepcopy(json_data)

        final_data = verify_dependency_json(json_data, final_data)
        final_data = verify_drivers_json(final_data, ref_data)
        final_data = verify_warriorspace_data(final_data, ref_data)
        final_data = verify_tools_data(final_data, ref_data)

        # print json.dumps(final_data, indent=4, sort_keys=True)
        return JsonResponse({"xml_contents": final_data, "filename": filename})


def verify_tools_data(final_data, ref_data):
    if "tools" not in final_data["data"]:
        final_data["data"]["tools"] = copy.copy(ref_data["data"]["tools"])
    return final_data


def verify_warriorspace_data(final_data, ref_data):
    if "warriorspace" not in final_data["data"]:
        final_data["data"]["warriorspace"] = copy.copy(ref_data["data"]["warriorspace"])

    if "repository" not in final_data["data"]["warriorspace"]:
        final_data["data"]["warriorspace"]["repository"] = copy.copy(
            ref_data["data"]["warriorspace"]["repository"])

    if not isinstance(final_data["data"]["warriorspace"]["repository"], list):
        final_data["data"]["warriorspace"]["repository"] = [
            final_data["data"]["warriorspace"]["repository"]]
    return final_data


def verify_drivers_json(final_data, ref_data):
    if "drivers" not in final_data["data"]:
        final_data["data"]["drivers"] = copy.copy(ref_data["data"]["drivers"])

    if "repository" not in final_data["data"]["drivers"]:
        final_data["data"]["drivers"]["repository"] = copy.copy(
            ref_data["data"]["drivers"]["repository"])

    if not isinstance(final_data["data"]["drivers"]["repository"], list):
        final_data["data"]["drivers"]["repository"] = [final_data["data"]["drivers"]["repository"]]
    for i in range(0, len(final_data["data"]["drivers"]["repository"])):
        if "driver" not in final_data["data"]["drivers"]["repository"][i]:
            final_data["data"]["drivers"]["repository"][i]["driver"] = copy.copy(
                ref_data["data"]["drivers"]["repository"]["driver"])

        if not isinstance(final_data["data"]["drivers"]["repository"][i]["driver"], list):
            final_data["data"]["drivers"]["repository"][i]["driver"] = [
                final_data["data"]["drivers"]["repository"][i]["driver"]]
    return final_data


def verify_dependency_json(json_data, final_data):
    dependency_dict = {"jira": "1.0.3", "lxml": "3.5", "ncclient": "0.4.6",
                       "paramiko": "1.16.0", "pexpect": "4.2.0", "pysnmp": "4.3.2",
                       "requests": "2.9.1", "selenium": "2.48.0", "xlrd": "1.0.0",
                       "cloudshell-automation-api": "7.1.0.34"}
    for i in range(0, len(json_data["data"]["warhorn"]["dependency"])):
        for key, value in json_data["data"]["warhorn"]["dependency"][i].items():
            if key == "@name":
                if value in dependency_dict:
                    final_data["data"]["warhorn"]["dependency"][i]["version"] = dependency_dict[
                        value]
                    try:
                        module_name = __import__(value)
                        some_var = module_name.__version__
                        final_data["data"]["warhorn"]["dependency"][i]["installed"] = some_var
                        if dependency_dict[value] == some_var:
                            final_data["data"]["warhorn"]["dependency"][i]["matched"] = True
                        elif dependency_dict[value] > some_var:
                            final_data["data"]["warhorn"]["dependency"][i]["matched"] = "lower"
                        else:
                            final_data["data"]["warhorn"]["dependency"][i]["matched"] = "higher"
                    except ImportError:
                        final_data["data"]["warhorn"]["dependency"][i]["installed"] = False
                        final_data["data"]["warhorn"]["dependency"][i]["matched"] = False
                    except Exception as e:
                        print "-- An Exception Occurred -- while getting details about {0}: {1}".format(
                            value, e)
                        final_data["data"]["warhorn"]["dependency"][i]["installed"] = False
                        final_data["data"]["warhorn"]["dependency"][i]["matched"] = False
                    break
                else:
                    pass
    return final_data


def read_xml_get_json(filepath):
    xml_contents = open(filepath, 'r')
    ordered_dict_json = xmltodict.parse(xml_contents)
    json_data = json.loads(json.dumps(ordered_dict_json))
    return json_data


def check_repo_availability(request):
    nav_obj = Navigator()
    available = True
    url = request.POST.get('url')
    repo_name = get_repository_name(url)
    drivers = []
    if not check_url_is_a_valid_repo(url):
        available = False
    else:
        temp_directory = os.path.join(nav_obj.get_katana_dir(), "native", "assembler", ".data")
        kw_repo_obj = KwRepositoryDetails(url, temp_directory)
        drivers = kw_repo_obj.get_pd_names()
    return JsonResponse({"available": available, "repo_name": repo_name, "drivers": drivers})


def check_url_is_a_valid_repo(url):
    print "Verifying if {0} is a valid git repository.".format(url)
    if subprocess.call(["git", "ls-remote", url]) != 0:
        print "-- An Error Occurred -- {0} is not a valid git repository.".format(url)
        return False
    print "{0} is available".format(url)
    return True


def get_repository_name(url):
    li_temp_1 = url.rsplit('/', 1)
    return li_temp_1[1][:-4] if \
        li_temp_1[1].endswith(".git") else li_temp_1[1]


def check_ws_repo_availability(request):
    available = True
    url = request.POST.get('url')
    repo_name = get_repository_name(url)
    if not check_url_is_a_valid_repo(url):
        available = False
    return JsonResponse({"available": available, "repo_name": repo_name})


def check_tools_repo_availability(request):
    available = True
    url = request.POST.get('url')
    repo_name = get_repository_name(url)
    if not check_url_is_a_valid_repo(url):
        available = False
    return JsonResponse({"available": available, "repo_name": repo_name})


def save_warhorn_config_file(request):
    filepath = os.path.join(request.POST.get('directory'), request.POST.get('filename') + ".xml")
    json_data = json.loads(request.POST.get('json_data'))
    json_data["data"]["warriorframework"] = "Test"
    data = xmltodict.unparse(json_data)
    response = _save_file(filepath, data)

    return JsonResponse(response)


def save_and_run_warhorn_config_file(request):
    filepath = os.path.join(request.POST.get('directory'), request.POST.get('filename') + ".xml")
    json_data = json.loads(request.POST.get('json_data'))
    json_data["data"]["warriorframework"] = "Test"
    data = xmltodict.unparse(json_data)
    response = _save_file(filepath, data)
    nav_obj = Navigator()
    warhorn_dir = nav_obj.get_warhorn_dir()
    current_dir = os.getcwd()
    output = ""
    if response["saved"]:
        os.chdir(warhorn_dir)
        output = subprocess.Popen(["python", "warhorn.py", filepath], stdout=subprocess.PIPE).communicate()[0]
        os.chdir(current_dir)
        os.remove(filepath)
    return JsonResponse({"output": output})


def _save_file(filepath, data):
    filepath = os.path.join(filepath)
    message = ""
    saved = True
    try:
        with open(filepath, 'w') as f:
            f.write(data)
    except Exception as e:
        saved = False
        message = e
    return {"saved": saved, "message": message}
