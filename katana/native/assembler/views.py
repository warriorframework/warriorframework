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
from utils.directory_traversal_utils import get_dir_from_path, delete_dir
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
        message = ""
        status = "success"
        if template == "false":
            json_data = copy.deepcopy(ref_data)
        else:
            if os.path.isfile(template):
                json_data = read_xml_get_json(template)
                if "error" in json_data:
                    message = json_data["error"]
                    status = "error"
                    json_data = copy.deepcopy(ref_data)
                else:
                    filename, ext = os.path.splitext(get_dir_from_path(template))
            else:
                json_data = copy.deepcopy(ref_data)
                message = "A directory was selected instead of a file."
                status = "error"

        final_data = copy.deepcopy(json_data)

        final_data = verify_dependency_json(json_data, final_data, ref_data)
        final_data = verify_drivers_json(final_data, ref_data)
        final_data = verify_warriorspace_data(final_data, ref_data)
        final_data = verify_tools_data(final_data, ref_data)

        # print json.dumps(final_data, indent=4, sort_keys=True)
        return JsonResponse({"xml_contents": final_data, "filename": filename, "status": status, "message": message})


def verify_tools_data(final_data, ref_data):
    if "tools" not in final_data["data"]:
        final_data["data"]["tools"] = copy.deepcopy(ref_data["data"]["tools"])
    else:
        if "@url" not in final_data["data"]["tools"]:
            final_data["data"]["tools"]["@url"] = ""
        if "@clone" not in final_data["data"]["tools"]:
            final_data["data"]["tools"]["@clone"] = "yes"
        if "@label" not in final_data["data"]["tools"]:
            final_data["data"]["tools"]["@label"] = ""
        url = final_data["data"]["tools"]["@url"]
        if url != "":
            final_data["data"]["tools"]["name"] = get_repository_name(url=url)
            final_data["data"]["tools"]["available"] = check_url_is_a_valid_repo(url=url)
        else:
            final_data["data"]["tools"]["available"] = False
    return final_data


def verify_warriorspace_data(final_data, ref_data):
    if "warriorspace" not in final_data["data"]:
        final_data["data"]["warriorspace"] = copy.deepcopy(ref_data["data"]["warriorspace"])

    if "repository" not in final_data["data"]["warriorspace"]:
        final_data["data"]["warriorspace"]["repository"] = copy.copy(
            ref_data["data"]["warriorspace"]["repository"])

    if not isinstance(final_data["data"]["warriorspace"]["repository"], list):
        final_data["data"]["warriorspace"]["repository"] = [
            final_data["data"]["warriorspace"]["repository"]]

    for i in range(0, len(final_data["data"]["warriorspace"]["repository"])):
        if "@url" not in final_data["data"]["warriorspace"]["repository"][i]:
            final_data["data"]["warriorspace"]["repository"][i]["@url"] = ""
        if "@clone" not in final_data["data"]["warriorspace"]["repository"][i]:
            final_data["data"]["warriorspace"]["repository"][i]["@clone"] = "yes"
        if "@label" not in final_data["data"]["warriorspace"]["repository"][i]:
            final_data["data"]["warriorspace"]["repository"][i]["@label"] = ""
        if "@overwrite" not in final_data["data"]["warriorspace"]["repository"][i]:
            final_data["data"]["warriorspace"]["repository"][i]["@overwrite"] = "yes"
        url = final_data["data"]["warriorspace"]["repository"][i]["@url"]
        if url != "":
            final_data["data"]["warriorspace"]["repository"][i]["name"] = get_repository_name(url=url)
            final_data["data"]["warriorspace"]["repository"][i]["available"] = check_url_is_a_valid_repo(url=url)
        else:
            final_data["data"]["warriorspace"]["repository"][i]["available"] = False
    return final_data


def verify_drivers_json(final_data, ref_data):
    nav_obj = Navigator()
    if "drivers" not in final_data["data"]:
        final_data["data"]["drivers"] = copy.deepcopy(ref_data["data"]["drivers"])

    if "repository" not in final_data["data"]["drivers"]:
        final_data["data"]["drivers"]["repository"] = copy.deepcopy(ref_data["data"]["drivers"]["repository"])

    if not isinstance(final_data["data"]["drivers"]["repository"], list):
        final_data["data"]["drivers"]["repository"] = [final_data["data"]["drivers"]["repository"]]

    for i in range(0, len(final_data["data"]["drivers"]["repository"])):
        if "@url" not in final_data["data"]["drivers"]["repository"][i]:
            final_data["data"]["drivers"]["repository"][i]["@url"] = ""
        if "@clone" not in final_data["data"]["drivers"]["repository"][i]:
            final_data["data"]["drivers"]["repository"][i]["@clone"] = "yes"
        if "@label" not in final_data["data"]["drivers"]["repository"][i]:
            final_data["data"]["drivers"]["repository"][i]["@label"] = ""
        if "@all_drivers" not in final_data["data"]["drivers"]["repository"][i]:
            final_data["data"]["drivers"]["repository"][i]["@all_drivers"] = "yes"
        if "driver" not in final_data["data"]["drivers"]["repository"][i]:
            final_data["data"]["drivers"]["repository"][i]["driver"] = copy.deepcopy(ref_data["data"]["drivers"]["repository"]["driver"])

        if not isinstance(final_data["data"]["drivers"]["repository"][i]["driver"], list):
            final_data["data"]["drivers"]["repository"][i]["driver"] = [final_data["data"]["drivers"]["repository"][i]["driver"]]

        url = final_data["data"]["drivers"]["repository"][i]["@url"]
        if url != "":
            final_data["data"]["drivers"]["repository"][i]["name"] = get_repository_name(url=url)
            available = check_url_is_a_valid_repo(url=url)
            final_data["data"]["drivers"]["repository"][i]["available"] = available
            if available:
                drivers_data = []
                drivers_index = set()
                temp_directory = os.path.join(nav_obj.get_katana_dir(), "native", "assembler", ".data")
                kw_repo_obj = KwRepositoryDetails(url, temp_directory)
                drivers = set(kw_repo_obj.get_pd_names())
                for j in range(0, len(final_data["data"]["drivers"]["repository"][i]["driver"])):
                    if "@name" not in final_data["data"]["drivers"]["repository"][i]["driver"][j]:
                        final_data["data"]["drivers"]["repository"][i]["driver"][j]["@name"] = ""
                    else:
                        if final_data["data"]["drivers"]["repository"][i]["driver"][j]["@name"] in drivers:
                            drivers.remove(final_data["data"]["drivers"]["repository"][i]["driver"][j]["@name"])
                        else:
                            drivers_index.add(j)
                    if "@clone" not in final_data["data"]["drivers"]["repository"][i]["driver"][j]:
                        final_data["data"]["drivers"]["repository"][i]["driver"][j]["@clone"] = "yes"
                for j in range(0, len(final_data["data"]["drivers"]["repository"][i]["driver"])):
                    if j not in drivers_index:
                        drivers_data.append(copy.deepcopy(final_data["data"]["drivers"]["repository"][i]["driver"][j]))
                final_data["data"]["drivers"]["repository"][i]["driver"] = copy.deepcopy(drivers_data)
                for driver_name in drivers:
                    final_data["data"]["drivers"]["repository"][i]["driver"].append({"@name": driver_name, "@clone": "no"})
                if os.path.isdir(kw_repo_obj.repo_directory):
                    delete_dir(kw_repo_obj.repo_directory)
        else:
            final_data["data"]["drivers"]["repository"][i]["available"] = False
    return final_data


def __get_dependency_dict(ref_data):
    output = {}
    for el in ref_data["data"]["warhorn"]["dependency"]:
        output[el["@name"]] = {"version": el["@version"], "description": el["@description"]}
    return output


def verify_dependency_json(json_data, final_data, ref_data):
    dependency_dict = __get_dependency_dict(ref_data)
    extra_dependencies = set()
    for i in range(0, len(json_data["data"]["warhorn"]["dependency"])):
        for key, value in json_data["data"]["warhorn"]["dependency"][i].items():
            if key == "@name":
                if value in dependency_dict:
                    final_data["data"]["warhorn"]["dependency"][i]["version"] = dependency_dict[
                        value]["version"]
                    final_data["data"]["warhorn"]["dependency"][i]["description"] = dependency_dict[
                        value]["description"]
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
                    extra_dependencies.add(i)
    dependency_list = []
    for i in range(0, len(final_data["data"]["warhorn"]["dependency"])):
        if i not in extra_dependencies:
            dependency_list.append(copy.deepcopy(final_data["data"]["warhorn"]["dependency"][i]))
    final_data["data"]["warhorn"]["dependency"] = copy.deepcopy(dependency_list)
    return final_data


def read_xml_get_json(filepath):
    json_data = {}
    try:
        xml_contents = open(filepath, 'r')
    except Exception as e:
        json_data["error"] = e
    else:
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
        if os.path.isdir(kw_repo_obj.repo_directory):
            delete_dir(kw_repo_obj.repo_directory)
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
    nav_obj = Navigator()
    directory = request.POST.get('directory')
    if directory == "default":
        directory = os.path.join(nav_obj.get_katana_dir(), "native", "assembler", ".data")
    filepath = os.path.join(directory, request.POST.get('filename') + ".xml")
    json_data = json.loads(request.POST.get('json_data'))
    json_data["data"]["warriorframework"] = "Test"
    data = xmltodict.unparse(json_data)
    response = _save_file(filepath, data)

    return JsonResponse(response)


def save_and_run_warhorn_config_file(request):
    nav_obj = Navigator()
    directory = request.POST.get('directory')
    if directory == "default":
        directory = os.path.join(nav_obj.get_katana_dir(), "native", "assembler", ".data")
    filepath = os.path.join(directory, request.POST.get('filename') + ".xml")
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


def get_data_directory(request):
    nav_obj = Navigator()
    directory = os.path.join(nav_obj.get_katana_dir(), "native", "assembler", ".data")
    return JsonResponse({"data_directory": directory})
