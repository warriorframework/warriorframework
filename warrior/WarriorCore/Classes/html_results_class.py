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

import Tools
from Framework.Utils import xml_Utils, file_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_info
from Framework.Utils.xml_Utils import getElementWithTagAttribValueMatch
<<<<<<< HEAD
=======
class WarriorHtmlResults():
    """Warrior html results class """

    def __init__(self, junit_file=None):
        """ Constructor """
        self.junit_file = junit_file
        self.html_template = "{0}{1}reporting{1}html_results_template.html"\
                             .format(Tools.__path__[0], os.sep)
        self.junit_root = xml_Utils.getRoot(self.junit_file)
        self.html_root = xml_Utils.getRoot(self.html_template)
        self.table = getElementWithTagAttribValueMatch(self.html_root, "table",
                                               "name", "ResultsSummaryTable")
        self.html_results_path = self._get_html_resultspath()
        self.html_results_dir = os.path.dirname(self.html_results_path)

    def html_from_junit(self):
        """Generate html file from the junit result file
        using the html template """

        heading_row = getElementWithTagAttribValueMatch(self.html_root, "tr",
                                                        "name", "HeadingRow")
        # get project node from junit file.
        # project_node is the root of the junit file
        project_node_list = [self.junit_root]
        for project_node in project_node_list:
            # for each project node in project_node_list create project records
            self.create_project_records(project_node)
            # for each project node in project_node_list get its testsuite node list.
            testsuite_node_list = project_node.findall("testsuite")
            for testsuite_node in testsuite_node_list:
                # for each testsuite in testsuite node list create testsuite records.
                self.create_testsuite_records(testsuite_node)
                # for each testsuite node in testsuite node list get its testcase list.
                testcase_node_list = testsuite_node.findall("testcase")
                # for each testcase in testcase node list create testcase record.
                for testcase_node in testcase_node_list:
                    self.create_testcase_record(testcase_node)
                    tc_results_node = xml_Utils.getElementWithTagAttribValueMatch(testcase_node,
                                                                                  'property',
                                                                                  'name',
                                                                                  'resultsdir')
                    if tc_results_node is not None:
                        tc_resultsdir = tc_results_node.get("value")
                    else:
                        tc_resultsdir = None
                    tc_logs_node = xml_Utils.getElementWithTagAttribValueMatch(testcase_node,
                                                                               'property',
                                                                               'name',
                                                                               'logsdir')
                    if tc_logs_node is not None:
                        tc_logsdir = tc_logs_node.get("value")
                    else:
                        tc_logsdir = None
                    tc_name = testcase_node.get("name")
                    tc_details = {"tc_resultsdir": tc_resultsdir,
                                  "tc_logsdir": tc_logsdir,
                                  "tc_name": tc_name}
                    # for each testcase node in testcase node list get its
                    # keyword(property type = 'keyword') list.
                    kw_node_list = xml_Utils.\
                        getChildElementsListWithTagAttribValueMatch(
                         testcase_node, 'property', 'type', 'keyword')
                    # for each kw nod ein kw_node_list create kw record
                    for kw_node in kw_node_list:
                        self.create_keyword_record(kw_node, tc_details=tc_details)

    def create_project_records(self, project_node):
        """Creating project records in html table """
        if self.table is not None and\
        project_node.get("display") != "False":
            ##59b300
            details = { "filetype":"Project",
                        "row_name":"ProjectRecord",
                        "bgcolor":"#b2b266",
                        "subnode_type":"Testsuites"
                        }
            project_record, project_summary = self._generic_create_records(project_node,**details)
            self.table.append(project_record)
            self.table.append(project_summary)

    def create_testsuite_records(self, testsuite_node):
        """Create teststuite records in the html table"""
        if self.table is not None and\
        testsuite_node.get("display") != "False":
            ##e5f2ff
            details = { "filetype":"Testsuite",
                        "row_name":"TestsuiteRecord",
                        "bgcolor":"#ccffe6",
                        "subnode_type":"Testcases"
                        }
            testsuite_record, testsuite_summary = self._generic_create_records(testsuite_node,**details)
            self.table.append(testsuite_record)
            self.table.append(testsuite_summary)
    
    def create_testcase_record(self, testcase_node):
        """Create testcase records in the html table"""
        if self.table is not None:
            details = { "filetype":"Testcase",
                        "row_name":"TestcaseRecord",
                        "bgcolor":"#e5e5ff",
                        "subnode_type":"Keywords"
                        }
            testcase_record, testcase_summary = self._generic_create_records(testcase_node,**details)
            self.table.append(testcase_record)
            self.table.append(testcase_summary)


    def create_keyword_record(self, kw_node, tc_details):
        """Create keyword records in the html table"""
        if self.table is not None:
            details = { "filetype":"Keyword",
                        "row_name":"KeywordRecord",
                        "bgcolor":"#ffffe5",
                        "subnode_type":None,
                        "tc_details": tc_details
                        }
            kw_record, _ = self._generic_create_records(kw_node, **details)
            self.table.append(kw_record)


    def _generic_create_records(self, node, **kwargs):
        """Generic method to create table records
        This will be used to create project/testsuite/
        testcase/keyword records. """
        row=''
        try:
            filetype = kwargs.get("filetype")
            row_name = kwargs.get("row_name")
            bgcolor = kwargs.get("bgcolor")
            subnode_type = kwargs.get("subnode_type")
            tc_details = kwargs.get("tc_details", {})
            #tc_exec_dir = kwargs.get("tc_exec_dir", None)
            row = xml_Utils.create_element("tr", bgcolor=bgcolor, name=row_name)
            self._create_common_details(row, node, filetype, tc_details=tc_details)
            summary_values = self._create_summary(row, node, subnode_type)
        except Exception as exception:
            pNote(exception, "exception")

        return row, summary_values
            
    def _create_common_details(self, parent_node, junit_node, filetype, **kwargs):
        """Create the common details
        (type, name, info, timestamp, duration, status)
        for projects, suites, testcase, keywords """
        common_details = OrderedDict([("type", filetype), 
                                       ("name", "name"),
                                       ("info", "info"),
                                       ("timestamp", "timestamp"),
                                       ("time", "time"),
                                       ("status", "status"),
                                       ("impact", "impact"),
                                       ("onerror", "onerror"),
                                       ("results/logs/defects", "logs"),
                                       ]
                                     )
        
        type_map = {"Project":"Project", "Testsuite": "Suite", "Testcase": "Case", "Keyword": "Keyword"}
        status = junit_node.get("status")
        span = "1" if filetype == "Keyword" else "2"
        for item, value in common_details.items():
            td_element = xml_Utils.create_element("td", rowspan=span)
            element = xml_Utils.create_element("div", style="word-wrap: normal; width: 100px")
            self._set_col_width(element, item)
            text = type_map.get(filetype) if item == "type" else junit_node.get(value)
            if item == "name" and filetype != "Keyword":
                actual_file_href = self._link_to_file(junit_node)
                actual_file_href.text = text
                element.append(actual_file_href)
 
            elif item == "info":
                element = self._get_info(junit_node, filetype, element)

            elif item == "results/logs/defects":
                if str(status).lower()!= "skipped":
                    results_href = self._link_to_results(junit_node, filetype, **kwargs)
                    element.append(results_href)
                    logs_href = self._link_to_logs(junit_node, filetype)
                    if logs_href is not False:
                        element.append(logs_href)
                    defects_href = self._link_to_defects(junit_node, filetype, **kwargs)
                    if defects_href is not False:
                        element.append(defects_href)
            else:
                element.text = text

            if element is not None:
                td_element.append(element)
                parent_node.append(td_element)

    def _set_col_width(self, element, item):
        """Set col width based on item name """
        col_width = {"type": "70",
                     "name": "275",
                     "info": "275",
                     "timestamp": "90",
                     "time": "40",
                     "status": "60",
                     "impact": "80",
                     "onerror": "90",
                     "results/logs/defects": "100"
                    }.get(item, "100")
        element.set("style", "word-wrap: break-word; width: {0}px".format(col_width))


    def _create_summary(self, parent_node, junit_node,
                                subnode_type):
        """Create the summary heading row for
        each file type """
        junit_count_attrib = {"Testsuites":"suites", "Testcases":"tests",
                              "Keywords":"keywords"}.get(subnode_type, None)

        subnode_head_type = {"Testsuites":"Ts", "Testcases":"Tc",
                              "Keywords":"Kw"}.get(subnode_type, None)
        summary_values = None
        if subnode_type is not None:
            summary_details = OrderedDict([("Count", junit_count_attrib),
                                           ("Passed", "passes"),
                                           ("Failed", "failures"),
                                           ("Errors", "errors"),
                                           ("Exceptions", "exceptions"),
                                           ("Skipped","skipped")])
>>>>>>> origin/develop

__author__ = 'Keenan Jabri'


class LineResult():
    """Class that generates html result line items"""
    data = {}
    html = ''

    def __init__(self):
        pass

    def set_dynamic_content(self, line):
        self.data['dynamic'] = [line.get("keywords"), line.get("passes"), line.get("failures"), line.get("errors"),
                                line.get("exceptions"), line.get("skipped")]
        self.data['timestamp'] = line.get("timestamp")

    def set_attributes(self, line, type, stepcount):
        if 'Keyword' not in type and 'step' not in type:
            stepcount = ''
        self.data = {'nameAttr': type + 'Record',
                     'type': type.replace('Test', '').replace('Keyword', 'step ') + str(stepcount),
                     'name': line.get("name"),
                     'info': line.get("title"),
                     'timestamp': line.get("timestamp"),
                     'duration': line.get("time"),
                     'status': line.get("status"),
                     'impact': line.get("impact"),
                     'onerror': line.get("onerror"),
                     'msc': '<span style="padding-left:10px; padding-right: 10px;"><a href="' + (
                         line.get("resultfile") if line.get(
                             "resultfile") else '') + '"><i class="fa fa-line-chart"> </i></a></span><span '
                                                      'style="padding-left:10px; padding-right: 10px;"><a href="' + ( 
                                line.get("logsdir") if line.get(
                                    "logsdir") else '') + '"><i class="fa fa-book"> </i></a></span>',
                     'static': ['Count', 'Passed', 'Failed', 'Errors', 'Exceptions', 'Skipped']
                     }
        self.keys = ['type', 'name', 'info', 'timestamp', 'duration', 'status', 'impact', 'onerror', 'msc', 'static',
                     'dynamic']

    def set_html(self, line, type, stepcount):
        if self.html == '':
            self.set_attributes(line, type, stepcount)
        self.set_dynamic_content(line)
        top_level = ''
        top_level_next = ''
        if self.data['nameAttr'] != 'KeywordRecord':
            for elem in self.keys:
                if elem == 'dynamic':
                    for dynamicElem in self.data['dynamic']:
                        top_level_next += '<td>' + (dynamicElem if dynamicElem else '0') + '</td>'
                elif elem == 'static':
                    for staticElem in self.data['static']:
                        top_level += '<td>' + (staticElem if staticElem else '') + '</td>'
                else:
                    top_level += '<td rowspan="2"><div>' + (self.data[elem] if self.data[elem] else '') + '</div></td>'
            top_level_next = '<tr>' + top_level_next + '</tr>'
        else:
            for elem in self.keys:
                if elem != 'static' and elem != 'dynamic':
                    top_level += '<td rowspan="2"><div>' + (self.data[elem] if self.data[elem] else '') + '</div></td>'

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
        self.html_template = "{0}{1}Reporting{1}html_results_template.html" \
            .format(Tools.__path__[0], os.sep)
        self.junit_root = xml_Utils.getRoot(self.junit_file)

    def create_line_result(self, line, type):
        """ create new objs"""
        temp = LineResult()
        temp.set_html(line, type, self.steps)
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

<<<<<<< HEAD
    def merge_html(self, dynamic_html):
        """ merge html from template and dynamic """
        temp = open(self.html_template)
        templateHTML = temp.read().replace('\n', '')
        temp.close()
        index = templateHTML.rfind('</table>')
        return templateHTML[:index] + dynamic_html + templateHTML[index:] + self.get_war_version()

    def get_war_version(self):
        """ find the warrior version """
        path = self.get_path().split('warriorframework')[0] + 'warriorframework/version.txt'
        if os.path.isfile(path):
            version = open(path, 'r').read().split(':')[2]
            return '<div class="version">' + version + '</div>'
        else:
            return ''

    def generateHTML(self, junitObj, givenPath):
        """ build the html """
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

        elem_file = open(self.get_path(), 'w')
        elem_file.write(html)
        elem_file.close()
        self.lineObjs = []
        print_info("++++ Results Summary ++++")
        print_info("Open the Results summary file given below in a browser to "
                   "view results summary for this execution")
        print_info("Results sumary file: {0}".format(self.get_path()))
        print_info("+++++++++++++++++++++++++")
=======
    def output_html(self, print_summary=True):
        """Output the html file and its required
        script/stylesheets/bootstrap files to results folder """
        tree = ET.ElementTree(self.html_root)
        tree.write(self.html_results_path)
        if print_summary is True:
            print_info("++++ Results Summary ++++")
            print_info("Open the Results summary file given below in a browser"
                       " to view results summary for this execution")
            print_info("Results sumary file: {0}".format(self.html_results_path))
            print_info("+++++++++++++++++++++++++")

>>>>>>> origin/develop
