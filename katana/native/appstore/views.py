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

from django.shortcuts import render
from django.views import View
from native.appstore.appstore_utils.installer import Installer
from native.appstore.appstore_utils.uninstaller import Uninstaller
from utils.directory_traversal_utils import get_parent_directory, join_path, get_sub_files
from wui.core.core_utils.app_info_class import AppInformation
import xml.etree.cElementTree as ET


class AppStoreView(View):

    template = 'appstore/appstore.html'

    def get(self, request):
        """
        Get Request Method
        """
        return render(request, AppStoreView.template, {"data": {"app": AppInformation.information.apps}})


def uninstall_an_app(request):
    app_path = request.POST.get("app_path", None)
    app_type = request.POST.get("app_type", None)
    uninstaller_obj = Uninstaller(get_parent_directory(os.getcwd()), app_path, app_type)
    output = uninstaller_obj.uninstall()
    return render(request, AppStoreView.template, {"data": {"app": AppInformation.information.apps}})


def install_an_app(request):
    app_paths = request.POST.getlist("app_paths[]", None)
    for app_path in app_paths:
        installer_obj = Installer(get_parent_directory(os.getcwd()), app_path)
        output = installer_obj.install()
    return render(request, AppStoreView.template, {"data": {"app": AppInformation.information.apps}})


class AppInstallConfig(View):

    def post(self, request):
        app_paths = request.POST.getlist("app_paths[]")
        filename = request.POST.get("filename")

        root = ET.Element("data")
        app = ET.SubElement(root, "app")
        for app_path in app_paths:
            if os.path.exists(app_path):
                ET.SubElement(app, "filepath").text = app_path
            else:
                ET.SubElement(app, "repository").text = app_path
        fpath = join_path(os.getcwd(), "native", "appstore", ".config", "{0}.xml".format(filename))
        xml_str = ET.tostring(root, encoding='utf8', method='xml')
        with open(fpath, "w") as f:
            f.write(xml_str)
        return render(request, AppStoreView.template, {"data": {"app": AppInformation.information.apps}})


def load_configs(request):
    config_path = join_path(os.getcwd(), "native", "appstore", ".config")
    files = get_sub_files(config_path)
    config_files = []
    for subfile in files:
        filename, file_extension = os.path.splitext(subfile)
        if file_extension == ".xml":
            config_files.append(filename)
    return render(request, 'appstore/popup.html', {"data": {"config_files": {"names": config_files}}})


def open_config(request):
    config_name = request.GET['config_name']
    config_path = join_path(os.getcwd(), "native", "appstore", ".config", "{0}.xml".format(config_name))
    info = []
    with open(config_path, 'r') as f:
        data = f.read()
    tree = ET.ElementTree(ET.fromstring(data))
    apps = tree.findall('app')
    for app in apps:
        if app.find('filepath', None) is not None:
            node = app.find('filepath', None)
            text = node.text
        else:
            node = app.find('repository', None)
            text = node.text
        info.append(text)
    return render(request, 'appstore/load_config.html', {"data": {"app": AppInformation.information.apps,
                                                                  "config_files": {"info": info}}})
