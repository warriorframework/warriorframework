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
from utils.navigator_util import Navigator


class AssemblerView(View):

    def get(self, request):
        return render(request, 'assembler/assembler.html')


class ConfigurationFileOps(View):

    def post(self, request):

        dependency_dict = {"jira": "1.0.3", "lxml": "3.5", "ncclient": "0.4.6",
                           "paramiko": "1.16.0", "pexpect": "4.2.0", "pysnmp": "4.3.7",
                           "requests": "2.9.1", "selenium": "2.48.0", "xlrd": "1.0.0",
                           "cloudshell-automation-api": "7.1.0.34"}
        nav_obj = Navigator()
        empty_template = os.path.join(nav_obj.get_katana_dir(), "native", "assembler",
                                      "static",
                                      "assembler", "base_templates", "empty.xml")
        xml_contents = open(empty_template, 'r')
        ordered_dict_json = xmltodict.parse(xml_contents)
        json_data = json.loads(json.dumps(ordered_dict_json))

        final_data = copy.deepcopy(json_data)

        for i in range(0, len(json_data["data"]["warhorn"]["dependency"])):
            for key, value in json_data["data"]["warhorn"]["dependency"][i].items():
                if key == "@name":
                    if value in dependency_dict:
                        final_data["data"]["warhorn"]["dependency"][i]["version"] = dependency_dict[value]
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
                            print "-- An Exception Occurred -- while getting details about {0}: {1}".format(value, e)
                            final_data["data"]["warhorn"]["dependency"][i]["installed"] = False
                            final_data["data"]["warhorn"]["dependency"][i]["matched"] = False
                        break
                    else:
                        pass

        if not isinstance(final_data["data"]["drivers"]["repository"], list):
            final_data["data"]["drivers"]["repository"] = [final_data["data"]["drivers"]["repository"]]
        for i in range(0, len(final_data["data"]["drivers"]["repository"])):
            if not isinstance(final_data["data"]["drivers"]["repository"][i]["driver"], list):
                final_data["data"]["drivers"]["repository"][i]["driver"] = [final_data["data"]["drivers"]["repository"][i]["driver"]]
        if not isinstance(final_data["data"]["warriorspace"]["repository"], list):
            final_data["data"]["warriorspace"]["repository"] = [final_data["data"]["warriorspace"]["repository"]]

        return JsonResponse({"xml_contents": final_data})


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
    nav_obj = Navigator()
    available = True
    url = request.POST.get('url')
    repo_name = get_repository_name(url)
    drivers = []
    if not check_url_is_a_valid_repo(url):
        available = False
    return JsonResponse({"available": available, "repo_name": repo_name})
