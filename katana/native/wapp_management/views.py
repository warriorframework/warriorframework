"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from __future__ import unicode_literals
import os
import copy
import shutil
import zipfile

import binascii
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
import xml.etree.cElementTree as ET

from native.wapp_management.forms import UploadFileForm
from native.wapp_management.wapp_management_utils.app_validator import AppValidator
from native.wapp_management.wapp_management_utils.installer import Installer
from native.wapp_management.wapp_management_utils.uninstaller import Uninstaller
from utils.directory_traversal_utils import join_path, get_sub_files, get_parent_directory, \
    create_dir, get_dir_from_path
from utils.file_utils import copy_dir
from utils.string_utils import get_repository_name
from wui.core.core_utils.app_info_class import AppInformation


class WappManagementView(View):

    template = 'wapp_management/wapp_management.html'
    dot_data_directory = join_path(os.getcwd(), "native", "wapp_management", ".data")

    def get(self, request):
        """
        Get Request Method
        """
        files = get_sub_files(WappManagementView.dot_data_directory)
        preferences = []
        for subfile in files:
            filename, file_extension = os.path.splitext(subfile)
            if file_extension == ".xml":
                preferences.append(filename)
        output = {"data": {"app": AppInformation.information.apps, "preferences": preferences}}
        return render(request, WappManagementView.template, output)


def uninstall_an_app(request):
    app_path = request.POST.get("app_path", None)
    app_type = request.POST.get("app_type", None)
    uninstaller_obj = Uninstaller(get_parent_directory(os.getcwd()), app_path, app_type)
    output = uninstaller_obj.uninstall()
    if output:
        temp = []
        index = -1
        for i in range(0, len(AppInformation.information.apps)):
            if AppInformation.information.apps[i].path == app_path:
                index = i
                break
        temp.extend(AppInformation.information.apps[:index])
        temp.extend(AppInformation.information.apps[index+1:])
        AppInformation.information.apps = copy.deepcopy(temp)
    output = {"data": {"app": AppInformation.information.apps}}
    return render(request, 'wapp_management/installed_apps.html', output)


def install_an_app(request):
    app_paths = request.POST.getlist("app_paths[]", None)
    for app_path in app_paths:
        installer_obj = Installer(get_parent_directory(os.getcwd()), app_path)
        installer_obj.install()
    output_data = {"data": {"app": AppInformation.information.apps}}
    return render(request, 'wapp_management/installed_apps.html', output_data)


class AppInstallConfig(View):

    def post(self, request):
        app_paths = request.POST.getlist("app_paths[]")
        filename = request.POST.get("filename")

        root = ET.Element("data")
        for app_path in app_paths:
            app = ET.SubElement(root, "app")
            if os.path.exists(app_path):
                ET.SubElement(app, "filepath").text = app_path
            else:
                ET.SubElement(app, "repository").text = app_path
        fpath = join_path(WappManagementView.dot_data_directory, "{0}.xml".format(filename))
        xml_str = ET.tostring(root, encoding='utf8', method='xml')
        with open(fpath, "w") as f:
            f.write(xml_str)

        files = get_sub_files(WappManagementView.dot_data_directory)
        preferences = []
        for subfile in files:
            filename, file_extension = os.path.splitext(subfile)
            if file_extension == ".xml":
                preferences.append(filename)
        output_data = {"data": {"preferences": preferences}}

        return render(request, 'wapp_management/saved_preferences.html', output_data)


def load_configs(request):
    files = get_sub_files(WappManagementView.dot_data_directory)
    config_files = []
    for subfile in files:
        filename, file_extension = os.path.splitext(subfile)
        if file_extension == ".xml":
            config_files.append(filename)
    output_data = {"data": {"config_files": {"names": config_files}}}
    return render(request, 'wapp_management/popup.html', output_data)


def open_config(request):
    config_name = request.GET['config_name']
    config_path = join_path(WappManagementView.dot_data_directory, "{0}.xml".format(config_name))

    config_file_data_dir = join_path(WappManagementView.dot_data_directory, config_name)

    info = []
    show_install_btn = True
    with open(config_path, 'r') as f:
        data = f.read()
    tree = ET.ElementTree(ET.fromstring(data))
    apps = tree.findall('app')
    for app in apps:
        temp = {}
        if app.find('zip', None) is not None:
            node = app.find('zip', None)
            type_of_app = "zip"
            text = node.text
            if not os.path.exists(join_path(config_file_data_dir, text)):
                show_install_btn = False
                needs_update = True
            else:
                needs_update = False
        elif app.find('repository', None) is not None:
            node = app.find('repository', None)
            type_of_app = "repository"
            text = node.text
            needs_update = False
        else:
            node = app.find('filepath', None)
            type_of_app = "filepath"
            text = node.text
            if not os.path.exists(text):
                show_install_btn = False
                needs_update = True
            else:
                needs_update = False
        temp["name"] = text
        temp["type"] = type_of_app
        temp["needs_update"] = needs_update

        info.append(temp)

    output_data = {"config_name": config_name, "preference_details": info,
                   "show_install_btn": show_install_btn}
    return render(request, 'wapp_management/config_details.html', output_data)


def validate_app_path(request):
    output = False
    detail_type = request.POST.get("type", None)
    detail_info = request.POST.get("value", None)
    dot_data_dir = join_path(os.getcwd(), "native", "wapp_management", ".data")
    temp_dir_path = join_path(dot_data_dir, "temp")
    app_path = False

    if os.path.exists(temp_dir_path):
        shutil.rmtree(temp_dir_path)
    if create_dir(temp_dir_path):
        if detail_type == "repository":
            repo_name = get_repository_name(detail_info)
            os.system("git clone {0} {1}".format(detail_info, join_path(temp_dir_path, repo_name)))
            app_path = join_path(temp_dir_path, repo_name)
        elif detail_type == "zip":
            if os.path.exists(detail_info):
                temp = detail_info.split(os.sep)
                temp = temp[len(temp)-1]
                shutil.copyfile(detail_info, join_path(temp_dir_path, temp))
                zip_ref = zipfile.ZipFile(join_path(temp_dir_path, temp), 'r')
                zip_ref.extractall(temp_dir_path)
                zip_ref.close()
                app_path = join_path(temp_dir_path, temp[:-4])
            else:
                print "-- An Error Occurred -- {0} does not exist".format(detail_info)
        elif detail_type == "filepath":
            if os.path.isdir(detail_info):
                filename = get_dir_from_path(detail_info)
                copy_dir(detail_info, join_path(temp_dir_path, filename))
                app_path = join_path(temp_dir_path, filename)
            else:
                print "-- An Error Occurred -- {0} does not exist or is not a directory".format(detail_info)
        else:
            print "-- An Error Occurred -- Type of validation not given."
        if app_path:
            app_validator_obj = AppValidator(app_path)
            output = app_validator_obj.is_valid()
            shutil.rmtree(temp_dir_path)
    else:
        print "-- An Error Occurred -- Could not create temporary directory."
    return JsonResponse({"valid": output})

