'''
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
'''

"""Class that generates html results using hte junit result file """


import os
import xml.etree.ElementTree as ET
from collections import OrderedDict

import  Tools
from Framework.Utils import xml_Utils, file_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_info
from Framework.Utils.xml_Utils import getElementWithTagAttribValueMatch
class WarriorHtmlResults():
    """Warrior html results class """

    def __init__(self, junit_file=None):
        """ Constructor """
        self.junit_file = junit_file
        self.html_template = "{0}{1}Reporting{1}html_results_template.html"\
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
                    tc_resultsdir = testcase_node.get("resultsdir")
                    tc_logsdir = testcase_node.get("logsdir")
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

            for param, _ in summary_details.items():
                #creating summary heading in html
                element = xml_Utils.create_element("td")
                element.text = "{0} {1}".format(subnode_head_type, param)
                parent_node.append(element)

            summary_values = xml_Utils.create_element("tr")
            for _, value in summary_details.items():
                element = xml_Utils.create_element("td")
                element.text = junit_node.get(value)
                summary_values.append(element)
        return summary_values

    def _link_to_logs(self, junit_node, file_type):
        """Link to logs of Testcase """
        href_link = False
        html_results_dir = os.path.dirname(self.html_results_path)
        if file_type == "Testcase":
            logs_exec_dir = junit_node.get("logsdir")
            logs_path = str(logs_exec_dir) + os.sep + "Logs"
            rel_filepath = os.path.relpath(logs_path, html_results_dir)
            href_link= xml_Utils.create_element("span", style="padding-left:10px; padding-right: 10px;")
            #href_link.text = "|"
            href = xml_Utils.create_element("a", href=rel_filepath)
            logs_icon = self._get_icon("logs")
            logs_icon.text = " "
            href.append(logs_icon)
            href_link.append(href)
        return href_link

    def _link_to_defects(self, junit_node, filetype, **kwargs):
        """Link to defects of keywords"""
        rel_filepath = False
        status = junit_node.get("status")
        failing_status = ["fail", "error"]
        if filetype == "Keyword" and str(status).lower() in failing_status:
            tc_details = kwargs.get("tc_details", {})
            tc_resultsdir = tc_details.get("tc_resultsdir", None)
            tc_name = tc_details.get("tc_name", None)
            defects_dir = tc_resultsdir + os.sep + "Defects"
#             step_num = junit_node.get("step")
#             kw_name = junit_node.get("name")
            kw_resultfile = junit_node.get("resultfile")
            kw_resultfile_nameonly = file_Utils.getNameOnly(os.path.basename(kw_resultfile))
            defects_file = tc_name + "_" + kw_resultfile_nameonly + ".json"
            defects_filepath = defects_dir + os.sep + defects_file
            rel_filepath = os.path.relpath(defects_filepath, self.html_results_dir)

        elif filetype == "Testcase" and str(status).lower() != "pass":
            tc_resultsdir = junit_node.get("resultsdir")
            defects_dir = str(tc_resultsdir) + os.sep + "Defects"
            rel_filepath = os.path.relpath(defects_dir, self.html_results_dir)

        if rel_filepath:
            href_link= xml_Utils.create_element("span", style="padding-left:8px; padding-right: 8px;")
            #href_link.text = "|"
            href = xml_Utils.create_element("a", href=rel_filepath)
            logs_icon = self._get_icon("defects")
            logs_icon.text = " "
            href.append(logs_icon)
            href_link.append(href)
        else:
            href_link = rel_filepath
        return href_link

    def _link_to_results(self, junit_node, filetype, **kwargs):
        """Create a link to result files of
        project/testcase/testsuite/keywords """
        html_results_dir = os.path.dirname(self.html_results_path)
        
        results_file = self.junit_file if filetype == "Project" \
        else self._get_resultfile(junit_node, filetype, **kwargs)
        
        if filetype == "Testsuite":
            results_file = os.path.dirname(self.junit_file)

        rel_filepath = os.path.relpath(results_file, html_results_dir)

        href_link= xml_Utils.create_element("span", style="padding-left:10px; padding-right: 10px;")
        #href_link.text = "|"
        href = xml_Utils.create_element("a", href=rel_filepath)
        results_icon = self._get_icon("results")
        results_icon.text = " "
        href.append(results_icon)
        href_link.append(href)
        return href_link

    def _get_info(self, junit_node, filetype, element):
        """Get info for testcase, kw """
        if filetype == "Testcase":
            element =  self._get_testcase_info(junit_node, element)
        elif filetype == "Keyword":
            element =  self._get_keyword_info(junit_node, filetype, element)

        return element

    def _get_testcase_info(self, junit_node, element):
        """Get info for testcase """
        title = junit_node.get("title")
        subelem = xml_Utils.create_element("span")
        element.text = str(title)
        element.append(subelem)
        return element

    def _get_keyword_info(self, junit_node,
                          filetype, element):
        """ Get the info for keyword
        i.e. the name and value of the arguments """

        resultfile = self._get_resultfile(junit_node, filetype)
        if resultfile == "skipped":
            return element
        name_list, value_list = self._get_argument_namevalue_list(resultfile)


        for i in range(len(name_list)):
            subelem = xml_Utils.create_element("span")
            subelem.text = "{0}. {1} = {2}".format(str(i+1), name_list[i], value_list[i])
            brk = xml_Utils.create_element("br")
            element.append(brk)
            element.append(subelem)

        return element

    def _get_argument_namevalue_list(self, resultfile):
        """Get the name list and value list for all
        the arguments of a keyword """
        name_list, value_list = [], []
        arg_list = self._get_arglist(resultfile)
        for arg in arg_list:
            name = arg.get("name")
            value = arg.get("value")
            name_list.append(name)
            value_list.append(value)
        return name_list, value_list

    def _get_arglist(self, resultfile):
        """Get argument list from kw result file"""
        args = xml_Utils.getChildElementWithSpecificXpath(resultfile, "./Keyword/Arguments")
        args_list = args.findall("argument")
        return args_list

    def _get_resultfile(self, junit_node, filetype, **kwargs):
        """ get result file fro testcase/keywords"""
        filepath = "None"
        filename = junit_node.get("name")
#         if filetype == "Keyword":
#             tc_details = kwargs.get("tc_details", {})
#             resultsdir = tc_details.get("tc_resultsdir", None)        
#         else:
            
        if filetype == "Testcase":
            resultsdir = junit_node.get("resultsdir")
            filepath = str(resultsdir) + os.sep + "Results" + os.sep + str(filename) + "_results.xml"
        elif filetype == "Keyword":
            filepath = junit_node.get("resultfile")
        return filepath
        
    def _get_icon(self, icon_type):
        """Create a results icon"""
        class_value = {"results":"fa fa-line-chart",
                       "logs":"fa fa-book",
                       "defects":"fa fa-bug"
                       }.get(icon_type)
        details = {"class":class_value}
        results_icon = xml_Utils.create_element("i", **details)
        return results_icon
        
    def _link_to_file(self, junit_node):
        """Create a link to actual warrior file
        based on the filetype"""
        
        filename = junit_node.get("name")
        resultsdir = junit_node.get("resultsdir")
        filepath = str(resultsdir) + os.sep + str(filename) + ".xml"
        html_results_dir = os.path.dirname(self.html_results_path)
        rel_filepath = os.path.relpath(filepath, html_results_dir)
        href_link = xml_Utils.create_element("a", href=rel_filepath)
        return href_link

    def _get_html_resultspath(self):
        """Get the results path for the 
        html results file"""
        filename = file_Utils.getNameOnly(os.path.basename(self.junit_file))
        filename = filename.split("_junit")[0]
        html_filename = filename + ".html"
        results_dir = os.path.dirname(self.junit_file)
        html_results_path = results_dir + os.sep + html_filename
        return html_results_path

    def output_html(self):
        """Output the html file and its required
        script/stylesheets/bootstrap files to results folder """
        tree = ET.ElementTree(self.html_root)
        tree.write(self.html_results_path)
        print_info("++++ Results Summary ++++")
        print_info("Open the Results summary file given below in a browser to "\
                   "view results summary for this execution")
        print_info("Results sumary file: {0}".format(self.html_results_path))
        print_info("+++++++++++++++++++++++++")
        
