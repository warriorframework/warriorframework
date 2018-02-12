 #-*- coding: utf-8 -*-
import os
import time
import json
import subprocess
import shutil
from xml.etree import ElementTree

from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import native
from native.settings.settings import Settings
from utils.navigator_util import Navigator
from utils import file_utils

try:
    import xmltodict
except ImportError:
    print "Please install xmltodict"
import xmltodict, json, xml.etree.ElementTree as xml_controler
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
data_live_dir = os.path.join(os.path.dirname(__file__), '.data', 'live')
navigator = Navigator()

class Editor:

    def __init__(self):
        self.navigator = Navigator()
        self.katana_dir = os.path.dirname(native.__path__[0])
        self.wf_dir = os.path.dirname(self.katana_dir)
        self.warrior = os.path.join(self.wf_dir, 'warrior', 'Warrior')
        self.default_ws = os.path.join(self.wf_dir, 'warrior', 'Warriorspace')
        self.templates_dir = os.path.join(templates_dir, 'execution')
        self.jira_settings_file = os.path.join(self.wf_dir, 'warrior', 'Tools', 'jira', 'jira_config.xml')
        self.execution_settings_json = os.path.join(templates_dir, 'execution', 'execution_settings.json')
        self.config_json = os.path.join(self.katana_dir, 'config.json')

    def getEditorListTree(self,request):
        path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"
        x= json.loads(open(path_to_config_file).read());
        fpath = x['testsuitedir'];
        template = loader.get_template("editor.html")
        jtree = navigator.get_dir_tree_json(fpath)
        jtree['state']= { 'opened': True };
        return JsonResponse({'treejs': jtree })


    def get_location(self):
        pass

    #def getJSONEditorData(request):
