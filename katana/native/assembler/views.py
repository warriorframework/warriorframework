# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

import xmltodict
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from utils.navigator_util import Navigator


class AssemblerView(View):

    def get(self, request):
        return render(request, 'assembler/assembler.html')


class ConfigurationFileOps(View):

    def post(self, request):

        dependency_dict = {"jira": "1.0.3", "lxml": "3.5", "ncclient": "0.4.6",
                           "paramiko": "1.16.0", "pexpect": "4.2", "pysnmp": "4.3.1",
                           "requests": "2.9.1", "selenium": "2.48.0"}
        nav_obj = Navigator()
        empty_template = os.path.join(nav_obj.get_katana_dir(), "native", "assembler",
                                      "static",
                                      "assembler", "base_templates", "empty.xml")
        xml_contents = open(empty_template, 'r')
        ordered_dict_json = xmltodict.parse(xml_contents)
        json_data = json.loads(json.dumps(ordered_dict_json))

        for i in range(0, len(json_data["data"]["warhorn"]["dependency"])):
            for key, value in json_data["data"]["warhorn"]["dependency"][i].items():
                if key == "@name":
                    if value in dependency_dict:
                        json_data["data"]["warhorn"]["dependency"][i]["version"] = dependency_dict[value]
                    else:
                        pass

        if not isinstance(json_data["data"]["drivers"]["repository"], list):
            json_data["data"]["drivers"]["repository"] = [
                json_data["data"]["drivers"]["repository"]]
        if not isinstance(json_data["data"]["warriorspace"]["repository"], list):
            json_data["data"]["warriorspace"]["repository"] = [
                json_data["data"]["warriorspace"]["repository"]]
        return JsonResponse({"xml_contents": json_data})
