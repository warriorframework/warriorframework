"""
Copyright 2017, Fujitsu Network Communications, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os

import json
import getpass
import multiprocessing
import Tools
from Framework.Utils import xml_Utils, file_Utils, data_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_info
from Framework.Utils.xml_Utils import getElementWithTagAttribValueMatch
import WarriorCore.Classes.katana_interface_class as katana_interface_class

__author__ = 'Keenan Jabri'


class LineResult:
    """Class that generates html result line items"""
    data = {}
    html = ''

    def __init__(self):
        """Constructor for class LineResult"""
        self.keys = ['type', 'name', 'info', 'description', 'timestamp', 'duration', 'status', 'impact', 'onerror', 'msc', 'static',
                     'dynamic']

    def get_info(self, line):
        """gets info for line"""
        inf_obj = line.get("info") if line.get("info") else ' '
        info = json.dumps(inf_obj)
        info = info.replace('}"', ',').replace('"{', '').replace("'", "").replace('"', '')
        return info

    def set_dynamic_content(self, line):
        """sets content that is subjected to change"""

        self.data['dynamic'] = [line.get("keywords"), line.get("passes"), line.get("failures"),
                                line.get("errors"), line.get("exceptions"), line.get("skipped")]
        self.data['timestamp'] = line.get("timestamp")

    def set_attributes(self, line, variant, stepcount):
        """sets attributes"""
        if 'Keyword' not in variant and 'step' not in variant:
            stepcount = ''
        result_path = line.get("resultsfile") if line.get("resultsfile") else line.get("resultsdir") if line.get("resultsdir") else ''
        logs_path = line.get("console_logfile") if line.get("console_logfile") else ''
#         defects_path = line.get("defects") if line.get("defects") else ''
        status_name = line.get("status") if line.get("status") else ''

        #
        #katana-click='execution.resultsViewer.openLogs'

        # There won't be results link in html anymore as we decided we will not be linking xml files in our html results
#         results_span = "<span style='padding-left:10px; padding-right: 10px;'>"\
#                         "<a  name='results-link' href='{0}' target='_blank' >"\
#                         "<i name='results-icon' class='fa fa-line-chart'  data-logPath='{0}' katana-click='execution.resultsViewer.openLogs'> </i>"\
#                         "</a>"\
#                         "</span>".format(result_path)

        # the link to logs should only be applied to a testcase and it will open the console logs of the testcase
        logs_span = "<span style='padding-left:10px; padding-right: 10px;'>"\
                    "<a  name='results-link' href='{0}' target='_blank' >"\
                    "<i name='logs-icon' class='fa fa-book'  data-logPath='{0}' katana-click='execution.resultsViewer.openConsoleLogFile' > </i>"\
                    "</a>"\
                    "</span>".format(line.get("console_logfile")) if line.get("console_logfile") else ''

        # link to defects will only be applied to a keyword and it will open the defects json file in a popup
        defects_span = "<span style='padding-left:10px; padding-right: 10px;'>"\
                        "<a name='bug-link' href='{0}' target='_blank' >"\
                        "<i name='bug-icon' class='fa fa-bug'  data-logPath='{0}' katana-click='execution.resultsViewer.openDefectsJson'> </i>"\
                        "</a>"\
                        "</span>".format(line.get("defects"))  if line.get("defects") else ''
        span_html = ""
        if variant == "Testcase":
            span_html =  logs_span
            locn = line.get('testcasefile_path')
        elif variant =="Keyword":
            span_html = defects_span
            locn =""
        else:
            locn_tag = line.find('./properties/property[@name="location"]')
            locn = locn_tag.get('value') if locn_tag is not None else ""

        self.data = {'nameAttr': variant + 'Record',
                     'type': variant.replace('Test', '').replace('Keyword', 'step ') + str(stepcount),
                     'name': line.get("name"),
                     'info': self.get_info(line),
                     'description': line.get("description"),
                     'timestamp': line.get("timestamp"),
                     'duration': line.get("time"),
                     'status': '<span class=' + status_name + '>' + status_name + '</span>',
                     'impact': line.get("impact"),
                     'onerror': line.get("onerror"),
                     'msc': span_html,
                     'static': ['Count', 'Passed', 'Failed', 'Errors', 'Exceptions', 'Skipped'],
                     'locn': locn
                     }

    def set_html(self, line, variant, stepcount):
        """sets the html code"""
        if self.html == '':
            self.set_attributes(line, variant, stepcount)
        self.set_dynamic_content(line)
        top_level = ''
        top_level_next = ''
        if not line.get("display") or line.get("display") == 'True':
            if self.data['nameAttr'] != 'KeywordRecord':
                for elem in self.keys:
                    if elem == 'dynamic':
                        for dynamicElem in self.data['dynamic']:
                            top_level_next += '<td>' + (dynamicElem if dynamicElem else '0') + '</td>'
                    elif elem == 'static':
                        for staticElem in self.data['static']:
                            top_level += '<td>' + (staticElem if staticElem else '') + '</td>'
                    elif elem == 'name':
                        div_html = '<div data-path="{0}", data-type="{1}", katana-click="execution.resultsViewer.openXmlInApp">'.format(self.data['locn'], self.data['type'])
                        top_level += '<td rowspan="2">'+ div_html + (
                            self.data[elem] if self.data[elem] else '') + '</div></td>'

                    elif elem == 'type':
                        div_html = '<div  katana-click="execution.resultsViewer.openAccordian">'
                        top_level += '<td rowspan="2">'+ div_html + (
                            self.data[elem] if self.data[elem] else '') + '</div></td>'

                    else:
                        top_level += '<td rowspan="2"><div>' + (
                            self.data[elem] if self.data[elem] else '') + '</div></td>'
                top_level_next = '<tr>' + top_level_next + '</tr>'
            else:
                for elem in self.keys:
                    if elem != 'static' and elem != 'dynamic':
                        top_level += '<td rowspan="2"><div>' + (
                            self.data[elem] if self.data[elem] else '') + '</div></td>'

            self.html = '<tr name="' + self.data['nameAttr'] + '">' + top_level + '</tr>' + top_level_next

class WarriorHtmlResults:
    """Class that generates html results using hte junit result file """
    lineObjs = []
    lineCount = 0
    recount = 0
    steps = 0

    def __init__(self, junit_file=None):
        """ init function"""
        self.junit_file = junit_file
        self.html_template = "{0}{1}reporting{1}html_results_template.html" \
            .format(Tools.__path__[0], os.sep)
        self.junit_root = xml_Utils.getRoot(self.junit_file)

    def create_line_result(self, line, variant):
        """ create new objs"""
        temp = LineResult()
        temp.set_html(line, variant, self.steps)
        self.lineObjs.append(temp)
        self.lineCount += 1

    def set_line_objs(self):
        """ call to create a new obj per item"""
        self.lineCount = 0
        project_node_list = [self.junit_root]
        for project_node in project_node_list:
            self.create_line_result(project_node, "Project")
            for testsuite_node in project_node.findall("testsuite"):
                self.create_line_result(testsuite_node, "Testsuite")
                for testcase_node in testsuite_node.findall("testcase"):
                    self.create_line_result(testcase_node, "Testcase")
                    self.steps = 0
                    for step_node in testcase_node.findall("properties"):
                        for node in step_node.findall("property"):
                            if node.get('type') == 'keyword':
                                self.steps += 1
                                self.create_line_result(node, "Keyword")

    def get_path(self):
        """ get the html results path """
        filename = file_Utils.getNameOnly(os.path.basename(self.junit_file))
        filename = filename.split("_junit")[0]
        html_filename = filename + ".html"
        if hasattr(self, 'givenPath'):
            html_results_path = self.givenPath + os.sep + html_filename
        else:
            results_dir = os.path.dirname(self.junit_file)
            html_results_path = results_dir + os.sep + html_filename

        return html_results_path

    def merge_html(self, dynamic_html):
        """ merge html from template and dynamic """
        temp = open(self.html_template)
        template_html = temp.read().replace('\n', '')
        temp.close()
        index = template_html.rfind('</table>')
        return template_html[:index] + dynamic_html + template_html[index:] + self.get_war_version()

    def get_war_version(self):
        """ find the warrior version """
        path = self.get_path().split('warriorframework')[0] + 'warriorframework/version.txt'
        if os.path.isfile(path):
            version = open(path, 'r').read().splitlines()[1].split(':')[1]
            return '<div class="version">' + version + '</div>'
        else:
            return ''

    def create_live_table(self, dynamic_cont, livehtmllocn, live_html_iter):
        """
        Create the table for live update by reading the
        table portion of live html file, and adding the dynamic content to it.
        The table will then be added to the live html result file
        """

        template_file = open(self.html_template)

        for num, line in enumerate(template_file, 1):
            if '<table ' in line:
                table_start = num
            if '</table>' in line:
                table_end = num
        lines = file_Utils.get_lines_between(template_file, table_start, table_end)
        lines.insert(len(lines)-1, dynamic_cont)
        table_string = ''.join(lines)
        table_string = table_string.replace('\n', '')

        if isinstance(livehtmllocn, str):
            # Passed as a path, means it is a cli execution
            with open(livehtmllocn) as live_file:
                live_string = live_file.read()
        elif isinstance(livehtmllocn, multiprocessing.managers.DictProxy):
            # Passed as a dict, means it is a python function call
            live_string = livehtmllocn["html_result"]

        marker_start = '<!--table-{0}starts-->'.format(str(live_html_iter))
        marker_end = '<!--table-{0}ends-->'.format(str(live_html_iter))

        prefix = live_string.split(marker_start)[0]
        suffix = live_string.split(marker_end)[-1]

        live_final_string = prefix + marker_start + table_string + marker_end + suffix

        if isinstance(livehtmllocn, str):
            with open(livehtmllocn, 'w') as live_file:
                live_file.write(live_final_string)
        elif isinstance(livehtmllocn, multiprocessing.managers.DictProxy):
            livehtmllocn["html_result"] = live_final_string

    def write_live_results(self, junitObj, givenPath, is_final):
        """ build the html givenPath: added this feature in case of later down the line calling from outside junit
        file ( no actual use as of now )
        """
        if junitObj:
            self.junit_file = junitObj
            self.junit_root = xml_Utils.getRoot(self.junit_file)
        if givenPath:
            self.givenPath = givenPath

        self.set_line_objs()
        html = ''
        for item in self.lineObjs:
            html += item.html
        if is_final is True:
            #html += '<div class="complete"></div>'
            pass
        live_html_dict = data_Utils.get_object_from_datarepository('live_html_dict', verbose=False)
        if live_html_dict:
            livehtmllocn = live_html_dict['livehtmllocn']
            live_html_iter = live_html_dict['iter']
            self.create_live_table(html, livehtmllocn, live_html_iter)

        html = self.merge_html(html)
        elem_file = open(self.get_path(), 'w')
        elem_file.write(html)
        elem_file.close()

        self.lineObjs = []
        print_info("++++ Results Summary ++++")
        print_info("Open the Results summary file given below in a browser to "
                   "view results summary for this execution")
        print_info("Results sumary file: {0}".format(self.get_path()))
        print_info("+++++++++++++++++++++++++")

    def generate_html(self, junitObj, givenPath, is_final):
        """ build the html givenPath: added this feature in case of later down the line calling from outside junit
        file ( no actual use as of now )
        """
        if junitObj:
            self.junit_file = junitObj
            self.junit_root = xml_Utils.getRoot(self.junit_file)
        if givenPath:
            self.givenPath = givenPath

        self.set_line_objs()
        html = ''
        for item in self.lineObjs:
            html += item.html
        html = self.merge_html(html)

        if is_final is True:
            html += '<div class="complete"></div>'

        elem_file = open(self.get_path(), 'w')
        elem_file.write(html)
        elem_file.close()
        katana = katana_interface_class.KatanaInterface()
        katana.send_file(self.get_path(), '/execution/updateHtmlResult')

        if is_final is True:
            katana.end_comunication()

        self.lineObjs = []
        print_info("++++ Results Summary ++++")
        print_info("Open the Results summary file given below in a browser to "
                   "view results summary for this execution")
        print_info("Results sumary file: {0}".format(self.get_path()))
        print_info("+++++++++++++++++++++++++")
