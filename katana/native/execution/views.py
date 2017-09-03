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
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render

import native
from native.settings.settings import Settings
from utils.navigator_util import Navigator

# Create your views here.

controls = Settings()

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')


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
        self.default_ws = os.path.join(self.wf_dir, 'warrior', 'Warriorspace')
        self.templates_dir = os.path.join(templates_dir, 'execution')
        
        self.execution_settings_json = os.path.join(templates_dir, 'execution', 'execution_settings.json')
        

    
    def index(self, request):
        """
        Index page for exeution app
        """
        execution_settings_dict = json.loads(open(self.execution_settings_json).read())
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
        
        data_dict = json.loads(request.GET.get('data'))
        execution_file_list = data_dict['execution_file_list']
        execution_file_list_string = " ".join(execution_file_list)
        
        print "execution_file_list: ", execution_file_list_string
        #warrior_cmd = "{0} {1} {2}".format('python', 'warrior', execution_file_list_string)
        
        # harcode a warrior command to test
        demo_case = "/home/sradhakr/workspace/war-1359/warriorframework/warrior/Warriorspace/Testcases/Demo_Cases/Demo_Test_Of_Inventory_Management_System.xml"
        warrior_cmd = '{0} {1} {2}'.format('python', '/home/sradhakr/workspace/war-1359/warriorframework/warrior/Warrior', demo_case )
     
        args = warrior_cmd.split(" ")
        stream_warrior_output(args)
        print "warrior command is :", warrior_cmd
        
        return StreamingHttpResponse(stream_warrior_output(args))
        
        
    def get_ws(self, request):
        """
        return the dir tree json for warriorspace
        """
        print request.GET
        data_dict = json.loads(request.GET.get('data'))
        ws_dir = self.default_ws if data_dict['start_dir'] == 'default' else data_dict['start_dir']      
        layout = self.nav.get_dir_tree_json(ws_dir)
        return JsonResponse(layout)

# 
# def get_dir_tree(dir_path, dir_icon=None, file_icon='jstree-file'):
#     """
#     """
#     
#     
#     layout = {'text': os.path.basename(dir_path)}
#     if os.path.isdir(dir_path):        
#         layout['li_attr'] = {'data-path': dir_path}
#         layout['icon'] = dir_icon if dir_icon else ""        
#         layout['children'] = [get_dir_tree(os.path.join(dir_path, x)) for x in os.listdir(dir_path)]
#     else:
#         layout['icon'] = file_icon
#     return layout
#         
    


# def index(request, execution_file_list):
#     index_template = os.path.join(templates_dir, 'execution', 'execution.html')
#     return render(request, index_template)
# 
# 
# def execute_warrior(request):
#     """
#     index view for execution page
#     """
#      
#     results_dict = {}
#     execution_template = os.path.join(templates_dir, 'execution.html')
#     demo_case = "/home/sradhakr/workspace/war-1359/warriorframework/warrior/Warriorspace/Testcases/Demo_Cases/Demo_Test_Of_Inventory_Management_System.xml"
#     pj = '/home/sradhakr/workspace/war-1359/warriorframework/wftests/warrior_tests/projects/pj_cond_var.xml'
#      
#     warrior_cmd = '{0} {1} {2}'.format('python', '/home/sradhakr/workspace/war-1359/warriorframework/warrior/Warrior', demo_case )
#      
#     args = warrior_cmd.split(" ")
#     #oput = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
#     #console_logs = oput.stdout.readlines()
#  
#     #stream_warrior_output(args)
#      
#     #console_logs = []     
#     #results_dict['console_logs'] = console_logs
#        
#     #return render(request, execution_template, results_dict)
#     return StreamingHttpResponse(stream_warrior_output(args))
#      
# 
def stream_warrior_output(args):
     
    output = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
     
    while output.poll() is None:
        line = output.stdout.readline()
        # Yield this line to be used by streaming http response
        yield line + '<br>'
        if line.startswith('-I- DONE'):
            print "line starts with DONE"
            break 
         
    time.sleep(10)
    return
