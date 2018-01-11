# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os
import subprocess
import xmltodict
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from wapps.assembler.assembler_utils.repository_details import KwRepositoryDetails
from wapps.assembler.assembler_utils.verify_file_contents import VerifyFileContents
from utils.directory_traversal_utils import delete_dir
from utils.git_utils import get_repository_name, check_url_is_a_valid_repo
from utils.navigator_util import Navigator
nav_obj = Navigator()
REF_FILE = os.path.join(nav_obj.get_katana_dir(), "wapps", "assembler", "static", "assembler",
                        "base_templates", "empty.xml")


class AssemblerView(View):

    def get(self, request):
        return render(request, 'assembler/assembler.html')


class ConfigurationFileOps(View):

    def post(self, request):
        template = request.POST.get('filepath')
        filename = "Untitled"
        final_data = {}

        if template == "false":
            vfd_obj = VerifyFileContents(REF_FILE, REF_FILE)
        else:
            vfd_obj = VerifyFileContents(template, REF_FILE)

        output = vfd_obj.verify_file()
        if output["status"]:
            final_data = vfd_obj.data

        return JsonResponse({"xml_contents": final_data, "filename": filename, "status": output["status"], "message": output["message"]})


def check_repo_availability(request):
    available = True
    url = request.POST.get('url')
    repo_name = get_repository_name(url)
    drivers = []
    if not check_url_is_a_valid_repo(url):
        available = False
    else:
        temp_directory = os.path.join(nav_obj.get_katana_dir(), "wapps", "assembler", ".data")
        kw_repo_obj = KwRepositoryDetails(url, temp_directory)
        drivers = kw_repo_obj.get_pd_names()
        if os.path.isdir(kw_repo_obj.repo_directory):
            delete_dir(kw_repo_obj.repo_directory)
    return JsonResponse({"available": available, "repo_name": repo_name, "drivers": drivers})


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
        directory = os.path.join(nav_obj.get_katana_dir(), "wapps", "assembler", ".data")
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
        directory = os.path.join(nav_obj.get_katana_dir(), "wapps", "assembler", ".data")
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
    directory = os.path.join(nav_obj.get_katana_dir(), "wapps", "assembler", ".data")
    return JsonResponse({"data_directory": directory})
