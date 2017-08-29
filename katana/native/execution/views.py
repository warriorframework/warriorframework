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
import os, time, subprocess
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from native.settings.settings import Settings
import json
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

        pass
    
    def index(self, request):
        """
        Index page for exeution app
        """
        index_template = os.path.join(templates_dir, 'execution', 'execution.html')
        return render(request, index_template)
    
    
    def execute_warrior(self, request):
        """
        """
        print request
        print request.POST
        
        
        
        data_dict = json.loads(request.POST.get('data'))
        print "printing data_dict: ",data_dict
        execution_file_list = data_dict['execution_file_list']
        execution_file_list_string = " ".join(execution_file_list)
        
        # 
        #warrior_cmd = "{0} {1} {2}".format('python', 'warrior', execution_file_list_string)
        
        # harcode a warrior command to test
        demo_case = "/home/sradhakr/workspace/war-1359/warriorframework/warrior/Warriorspace/Testcases/Demo_Cases/Demo_Test_Of_Inventory_Management_System.xml"
        warrior_cmd = '{0} {1} {2}'.format('python', '/home/sradhakr/workspace/war-1359/warriorframework/warrior/Warrior', demo_case )
     
        args = warrior_cmd.split(" ")
        stream_warrior_output(args)
        print "warrior command is :", warrior_cmd
        
        return HttpResponse(request, 'abc')
        
        


def index(request, execution_file_list):
    index_template = os.path.join(templates_dir, 'execution', 'execution.html')
    return render(request, index_template)


def execute_warrior(request):
    """
    index view for execution page
    """
     
    results_dict = {}
    execution_template = os.path.join(templates_dir, 'execution.html')
    demo_case = "/home/sradhakr/workspace/war-1359/warriorframework/warrior/Warriorspace/Testcases/Demo_Cases/Demo_Test_Of_Inventory_Management_System.xml"
    pj = '/home/sradhakr/workspace/war-1359/warriorframework/wftests/warrior_tests/projects/pj_cond_var.xml'
     
    warrior_cmd = '{0} {1} {2}'.format('python', '/home/sradhakr/workspace/war-1359/warriorframework/warrior/Warrior', demo_case )
     
    args = warrior_cmd.split(" ")
    #oput = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
    #console_logs = oput.stdout.readlines()
 
    #stream_warrior_output(args)
     
    #console_logs = []     
    #results_dict['console_logs'] = console_logs
       
    #return render(request, execution_template, results_dict)
    return StreamingHttpResponse(stream_warrior_output(args))
     

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
