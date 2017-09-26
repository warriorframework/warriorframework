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

# -*- coding: utf-8 -*-
import os
import time
import json
import subprocess
from xml.etree import ElementTree

from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import native
from native.settings.settings import Settings
from utils.navigator_util import Navigator
from utils.warrior_interface_utils import WarriorInterface


# Create your views here.

controls = Settings()

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
warrior_interface = ''



class Execution(object):
    """
    Execution app class
    """


    def __init__(self):
        """
        Constructor for execution app
        """
        self.nav = Navigator()
        self.katana_dir = os.path.dirname(native.__path__[0])
        self.wf_dir = os.path.dirname(self.katana_dir)
        self.warrior = os.path.join(self.wf_dir, 'warrior', 'Warrior')
        self.default_ws = os.path.join(self.wf_dir, 'warrior', 'Warriorspace')
        self.templates_dir = os.path.join(templates_dir, 'execution')
        self.jira_settings_file = os.path.join(self.wf_dir, 'warrior', 'Tools', 'jira', 'jira_config.xml')        
        self.execution_settings_json = os.path.join(templates_dir, 'execution', 'execution_settings.json')
        

    
    def index(self, request):
        """
        Index page for exeution app
        """
        execution_settings_dict = update_jira_proj_list(self.jira_settings_file, self.execution_settings_json)
        #json.loads(open(self.execution_settings_json).read())
        start_dir = self.default_ws if execution_settings_dict['defaults']['start_dir'] == 'default' \
        else execution_settings_dict['defaults']['start_dir']
        execution_settings_dict['defaults']['start_dir'] = start_dir
        index_template = os.path.join(self.templates_dir, 'execution.html')        
        
        
        
        return render(request, index_template, execution_settings_dict)
    
    
    def get_results_index(self, request):
        """
        """
        results_template = os.path.join(self.templates_dir, 'execution_results.html')
        return render(request, results_template)
    
    
    def execute_warrior(self, request):
        """
        """      
        global warrior_interface
        warrior_interface = WarriorInterface()

        data_dict = json.loads(request.GET.get('data'))
        execution_file_list = data_dict['execution_file_list']
        cmd_string = data_dict['cmd_string']
           
        warrior_cmd = '{0} {1} {2}'.format('python', self.warrior, cmd_string )
        args = warrior_cmd.split()
   
   
        return StreamingHttpResponse(stream_warrior_output(args, warrior_cmd, execution_file_list))
           
    def get_ws(self, request):
        """
        return the dir tree json for warriorspace
        """
        data_dict = json.loads(request.GET.get('data'))
        ws_dir = data_dict['start_dir']      
        layout = self.nav.get_dir_tree_json(ws_dir)
        return JsonResponse(layout)


    def get_jira_proj_list(self, request):
        """
        """
        
        return render(request, results_template) 


@csrf_exempt
def update_html_results(request):
    """
    update html results on recieving a post request from warrior
    """

    data_dict =  request.POST.dict()
    file_path = data_dict['file_path']
    global warrior_interface
    html = warrior_interface.update_html_result(file_path)

    return HttpResponse( "<h1>update html results</h1>")

def get_html_results(request):
    """
    update html results on recieving a post request from warrior
    """


    global warrior_interface
    if warrior_interface is not "":
        print "================printing html to screen==============="
        data =  warrior_interface.htmlResults
    
    return HttpResponse( data)


def stream_warrior_output(args, cmd, file_list):

    output = subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    first_poll = True
    
    file_li_string = ""
    for item in file_list:
        li_string = "<li>{0}</li>".format(item)
        file_li_string += li_string
        
    
    file_list_html = "<ol>{0}</ol>".format(file_li_string)
    cmd_string = "<h6><strong>Command: </strong></h6>{0}<br>".format(cmd)
    logs_heading = "<br><h6><strong>Logs</strong>:</h6>"
    init_string = "<br><h6><strong>Executing:</strong></h6>{0}"\
    .format(file_list_html) + cmd_string + logs_heading
                                                                                          
    
    
    while output.poll() is None:
        line = output.stdout.readline()
        if first_poll:
            line = init_string + line
            first_poll = False  
        # Yield this line to be used by streaming http response
        yield line + '</br>'
        if line.startswith('-I- DONE'):
            print "line starts with DONE"
            warrior_interface.set_eoc()
            break 
    warrior_interface.set_eoc()
    return


def update_jira_proj_list(jira_settings_file, exec_settings_json):
    """
    get the dict of jira settings by parsing the jira settings file
    """
    
    execution_settings_dict = json.loads(open(exec_settings_json).read())
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
    
    execution_settings_dict['jira_proj'] = jira_proj_list
    execution_settings_dict['defaults']['jira_proj'] = def_jira_proj
    
    with open(exec_settings_json, 'w') as fp:
        json.dump(execution_settings_dict, fp)
        
    return execution_settings_dict
        
        
        
        
        
        
        
        
        
        
    
    
    
    
    

