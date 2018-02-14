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
 #-*- coding: utf-8 -*-
import os
import time
import json
import subprocess
import shutil
import xml.dom.minidom

from xml.etree import ElementTree
from xml.dom.minidom import parse, parseString
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import native
from native.settings.settings import Settings
from utils.navigator_util import Navigator
from django.core.files import File
from utils import file_utils

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
data_live_dir = os.path.join(os.path.dirname(__file__), '.data', 'live')

controls = Settings()

class Editor(object):

    def __init__(self):
        self.nav = Navigator()
        self.katana_dir = os.path.dirname(native.__path__[0])
        self.wf_dir = os.path.dirname(self.katana_dir)
        self.warrior = os.path.join(self.wf_dir, 'warrior', 'Warrior')
        self.default_ws = os.path.join(self.wf_dir, 'warrior', 'Warriorspace')
        self.templates_dir = os.path.join(templates_dir, 'editor')
        self.jira_settings_file = os.path.join(self.wf_dir, 'warrior', 'Tools', 'jira', 'jira_config.xml')
        self.editor_settings_json = os.path.join(templates_dir, 'editor', 'editor_settings.json')
        self.config_json = os.path.join(self.katana_dir, 'config.json')

    def index(self, request):
        """
        Index page for Editor app
        """
        editor_settings_dict = update_jira_proj_list(self.jira_settings_file, self.editor_settings_json)
        #json.loads(open(self.editor_settings_json).read())
        start_dir = self.default_ws if editor_settings_dict['defaults']['start_dir'] == 'default' \
        else editor_settings_dict['defaults']['start_dir']
        editor_settings_dict['defaults']['start_dir'] = start_dir
        index_template = os.path.join(self.templates_dir, 'editor.html')



        return render(request, index_template, editor_settings_dict)



    def get_files(self, request):
        data_dict = json.loads(request.GET.get('data'))
        ws_dir = data_dict['start_dir']
        layout = self.nav.get_dir_tree_json(ws_dir)
        return JsonResponse(layout)


    def get_file_content(self,request):   #return content of the file
        #print request.POST.get('data')
        file_dict = request.POST.get('data') #load the request object 'data'
        print file_dict
        with open(file_dict) as f:
            myfile = f.readlines()

        return HttpResponse(myfile)

    def save_file_content(self,request):        #need the filepath to open and text to write to file
        json_content = json.loads(request.GET.get('data'))
        file_content = json_content['text']
        print file_content

        return HttpResponse(file_content)

def update_jira_proj_list(jira_settings_file, editor_settings_json):
    """
    get the dict of jira settings by parsing the jira settings file
    """

    editor_settings_dict = json.loads(open(editor_settings_json).read())
    def_jira_proj = ""
    jira_proj_list = []

    node = ElementTree.parse(jira_settings_file).getroot()
    proj_node_list = node.findall('system')
    def_set = False
    for proj in proj_node_list:
        opdict = {}
        opdict['name'] = proj.get('name')
        if not def_set:
            if str(proj.get('default')).lower() == 'true':
                def_jira_proj = proj.get('name')
                def_set = True
        jira_proj_list.append(opdict)

    editor_settings_dict['jira_proj'] = jira_proj_list
    editor_settings_dict['defaults']['jira_proj'] = def_jira_proj

    with open(editor_settings_json, 'w') as fp:
        json.dump(editor_settings_dict, fp)

    return editor_settings_dict



    #def getJSONEditorData(request):
