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
import shutil
from xml.etree import ElementTree

from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import native
from native.settings.settings import Settings
from utils.navigator_util import Navigator
from utils import file_utils

# Create your views here.

controls = Settings()

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
data_live_dir = os.path.join(os.path.dirname(__file__), '.data', 'live')



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
        self.config_json = os.path.join(self.katana_dir, 'config.json')




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
        Render the results index html to the client
        """
        fname = 'live_html_results'
        path = data_live_dir
        fpath = file_utils.get_new_filepath(fname, path, '.html')
        html_file = open(fpath, 'w')
        html_file.write('<div data-currentTable="1"> </div> ')
        html_file.close()


        result_setting = {'fpath': fpath}
        results_template = os.path.join(self.templates_dir, 'execution_results.html')
        return render(request, results_template, result_setting)


    def get_html_results(self, request):
        """
        Update the html results by reading the live html results
        file sent in the request
        """
        data_dict = json.loads(request.GET.get('data'))
        fpath = data_dict['liveHtmlFpath']
        with open(fpath) as htmlfile:
            data = htmlfile.readlines()
        return HttpResponse(data)

    def delete_live_html_file(self, request):
        """
        delete the live html file created
        """
        status = 'success'
        try:
            data_dict = json.loads(request.GET.get('data'))
            fpath = data_dict['liveHtmlFpath']
            os.remove(fpath)
        except Exception as err:
            status = 'failure'

        return HttpResponse(status)

    def get_logfile_contents(self, request):
        """
        Update the html results by reading the live html results
        file sent in the request
        """
        data_dict = json.loads(request.GET.get('data'))
        logpath = data_dict['logpath']
        logtype = data_dict['logtype']
        op_data = {}
        logfile_name = logpath.split(os.sep)[-1]

        if str(logtype.lower()) == 'defects':
            contents = json.loads(open(logpath).read())

        if str(logtype.lower()) == 'console_logs':
            contents = open(logpath).read()
            contents = contents.replace('\n', '<br>')

        op_data['logfile_name'] = logfile_name
        op_data['contents'] = contents


        return JsonResponse(op_data)

    def cleanup_data_live_dir(self, request):
        """
        Update the html results by reading the live html results
        file sent in the request
        """
        status = 'success'
        try:
            for item in os.listdir(data_live_dir):
                path = os.path.join(data_live_dir, item)
                if os.path.isfile(path) and not path.endswith('donotdeletethisfile.txt'):
                    os.remove(path)
                elif os.path.isdir(path):
                     shutil.rmtree(path, 'ignore_errors')
        except Exception as err:
            print "error ceaning up dir {0}".format(data_live_dir)
            print err
            status = 'failure'

        return HttpResponse(status)


    def get_ws(self, request):
        """
        return the dir tree json for warriorspace
        """
        data_dict = json.loads(request.GET.get('data'))
        ws_dir = data_dict['start_dir']
        layout = self.nav.get_dir_tree_json(ws_dir)
        return JsonResponse(layout)

    def execute_warrior(self, request):
        """
        Execute warrior command and send console logs to the client in a
        streaming fashion.
        """
        data_dict = json.loads(request.GET.get('data'))
        execution_file_list = data_dict['execution_file_list']
        cmd_string = data_dict['cmd_string']
        live_html_res_file = data_dict['liveHtmlFpath']
        config_json_dict = json.loads(open(self.config_json).read())
        python_path = config_json_dict['pythonpath']

        return StreamingHttpResponse(stream_warrior_output(self.warrior, cmd_string, execution_file_list, live_html_res_file, python_path))







def stream_warrior_output(warrior_exe, cmd_string, file_list, live_html_res_file, python_path=None):
    """
    Start warrior execution and stream console logs output to client
    """
    pypath = python_path if python_path else 'python'

    print_cmd = '{0} {1} {2}'.format(pypath, warrior_exe, cmd_string )
    warrior_cmd = '{0} {1} -livehtmllocn {2} {3}'.format(pypath, warrior_exe, live_html_res_file, cmd_string )


    output = subprocess.Popen(str(warrior_cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
#     output = subprocess.Popen('date', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    first_poll = True

    file_li_string = ""
    for item in file_list:
        li_string = "<li>{0}</li>".format(item)
        file_li_string += li_string


    file_list_html = "<ol>{0}</ol>".format(file_li_string)
    cmd_string = "<h6><strong>Command: </strong></h6>{0}<br>".format(print_cmd)
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
#             with open(live_html_res_file, 'a') as html_file:
#                 html_file.write("<div class='eoc'></div>")
            break

    # before returning set eoc div on the live html results file
    with open(live_html_res_file, 'a') as html_file:
        html_file.write("<div class='eoc'></div>")

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
