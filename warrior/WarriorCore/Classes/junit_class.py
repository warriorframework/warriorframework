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
#helper methods to create a Junit file

import xml.etree.ElementTree as ET
import os
import  Tools
from Framework.Utils.print_Utils import print_info
from Framework.Utils import file_Utils
from WarriorCore.Classes.html_results_class import WarriorHtmlResults
from WarriorCore.Classes.execution_summary_class import ExecutionSummary


class Junit(object):
    """Junit class"""

    def __init__(self, filename, **kwargs):
        """constructor """
        self.junit_xslt = "{0}{1}Reporting{1}junit_to_html.xsl".format(Tools.__path__[0], os.sep)
        self.root = self.create_element("testsuites", tests="0", suites="0",
                                        **self.init_arg(**kwargs))
        self.filename = filename
        properties = self.create_element("properties")
        self.root.append(properties)

    def init_arg(self, **kwargs):
        """
            initialize the common attribute for an element
        """
        default_keys = ["errors", "failures", "skipped", "time", "passes"]
        result = {}
        for default_key in default_keys:
            result[default_key] = kwargs[default_key] if default_key in kwargs else "0"
        for key, val in kwargs.items():
            result[key] = val
        return result

    def create_testsuite(self, location, **kwargs):
        """
            Create a testsuite element
        """
        testsuite = self.create_element("testsuite", tests="0", **self.init_arg(**kwargs))
        properties = self.create_element("properties")
        testsuite.append(properties)

        properties.append(self.create_element("property", {"name": "location", "value": location}))

        self.root.append(testsuite)

    def create_testcase(self, location, timestamp, ts_timestamp, name,
                        classname="customTestsuite_independant_testcase_execution",
                        tag="testcase", **kwargs):
        """
            Create a testcase element
        """
        if self.root.find("testsuite") is None:
            self.update_attr("timestamp", timestamp, "pj", "0")
            self.create_testsuite(location=location, name=classname, timestamp=timestamp,
                                  display='False', **self.init_arg(**kwargs))

        for ts in self.root.findall("testsuite"):
            if ts.get("timestamp") == ts_timestamp:
                #create an element with name as in tag
                tc = self.create_element(tag, classname=classname, timestamp=timestamp,
                                         exceptions="0", keywords="0", name=name,
                                         display='True', **self.init_arg(**kwargs))
                ts.append(tc)
                properties = self.create_element("properties")
                tc.append(properties)

    @classmethod
    def create_element(cls, tagname="", attr=None, **kwargs):
        """create an xml element with given name and a dict of attribute"""
        if attr is None:
            attr = {}
        elem = ET.Element(tagname)
        for key, val in attr.items():
            elem.set(str(key), str(val))
        for key, val in kwargs.items():
            elem.set(str(key), str(val))
        return elem

    def get_family_with_timestamp(self, timestamp):
        """ Get case, suite & root element based on the timestamp value """
        for testsuite in list(self.root):
            for testcase in list(testsuite):
                if testcase.get("timestamp") == timestamp:
                    return [testcase, testsuite, self.root]

    def get_tc_with_timestamp(self, timestamp):
        """ Get case element based on the timestamp value """
        for testsuite in list(self.root):
            for testcase in list(testsuite):
                if testcase.get("timestamp") == timestamp:
                    return testcase

    def get_ts_with_timestamp(self, timestamp):
        """ Get suite element based on the timestamp value """
        for testsuite in list(self.root):
            if testsuite.get("timestamp") == timestamp:
                return testsuite

    def add_keyword_result(self, tc_timestamp, step_num, kw_name, status, kw_timestamp, duration,
                           resultfile, impact, onerror, desc="", info="", tc_name="",
                           tc_resultsdir=""):
        """form a keyword status dict with kw info and call function to build keyword elem"""
        if str(status).lower() == "true":
            status = "PASS"
        elif str(status).lower() == "false":
            status = "FAIL"


        keyword_items = {"type": "keyword", 'display': 'True', "step": step_num,
                         "name": kw_name, "status": status, "timestamp": kw_timestamp,
                         "time": duration, "resultfile": resultfile,
                         "impact": impact, "onerror": onerror, "description": desc,
                         "info":info}
        # if a failing status if encountered add a defects atribute to the keyword tag
        # and its value is the path to the defects file.
        failing_status = ['FAIL', 'EXCEPTION', 'ERROR']
        if str(status).upper() in failing_status:
            defects_dir = os.path.dirname(tc_resultsdir) + os.sep + 'Defects'
            kw_resultfile_nameonly = file_Utils.getNameOnly(os.path.basename(resultfile))
            defects_file = tc_name + "_" + kw_resultfile_nameonly + ".json"
            defects_filepath = defects_dir + os.sep + defects_file
            keyword_items['defects'] = defects_filepath



        self.add_property(name=kw_name, value="KEYWORD_DISCARD", elem_type="kw",
                          timestamp=tc_timestamp, keyword_items=keyword_items)

    def add_testcase_message(self, timestamp, status):
        """ Add a message element for fail/error/skip cases """
        elem = self.get_tc_with_timestamp(timestamp)
        if elem is None:
            elem = self.get_ts_with_timestamp(timestamp)
        if str(status).lower() == "false":
            elem.append(self.create_element("failure", {"message": "test failure"}))
        elif str(status).lower() == "error":
            elem.append(self.create_element("error", {}))
        elif str(status).lower() == "skipped":
            elem.append(self.create_element("skipped", {}))

    def add_requirement(self, requirement, timestamp):
        """add a new requirement when called"""
        self.get_ts_with_timestamp(timestamp).find("properties").append(self.create_element\
        ("property", {"name": "requirement", "value": requirement}))

    def add_property(self, name, value, elem_type, timestamp, **kwargs):
        """add a new property to specific element when called
        since steps are logged as property, need special handling to create kw item"""
        if elem_type == "pj":
            elem = self.root
        elif elem_type == "ts":
            elem = self.get_ts_with_timestamp(timestamp)
        else:
            elem = self.get_tc_with_timestamp(timestamp)

        if elem_type == "kw":
            item = self.create_element("property", kwargs["keyword_items"])
        else:
            item = self.create_element("property", {"name": name, "value": value})
        elem.find("properties").append(item)

    def add_jobid(self, jobid):
        """add a new requirement when called"""
        self.root.append(self.create_element("property", {"name": "jobid", "value": jobid}))

    def add_project_location(self, location):
        """add a new requirement when called"""
        self.root.find("properties").append(self.create_element(
            "property", {"name": "location", "value": location}))
        self.root.append(self.create_element(
            "property", {"name": "location", "value": location}))

    def update_count(self, attr, value, elem_type, timestamp="0"):
        """
            increase the value of an attribute based on
            element type (project, testsuite or testcase) and timestamp
        """
        if elem_type == "pj":
            elem = self.root
        elif elem_type == "ts":
            elem = self.get_ts_with_timestamp(timestamp)
        else:
            elem = self.get_tc_with_timestamp(timestamp)
        attr = str(attr).lower()

        statuses = {"true": "passes", "false": "failures", "exception": "exceptions",
                    "error": "errors", "skip": "skipped"}
        if attr in statuses:
            attr = statuses[attr]

        if elem.tag != "testcase" and attr == "exceptions":
            attr = "errors"
        if elem.get(attr) is not None:
            elem.set(attr, str(int(elem.get(attr)) + int(value)))

    def update_attr(self, attr, value, elem_type, timestamp=None):
        """
            update the value of an attribute based on
            element type (project, testsuite or testcase) and timestamp
            special handling to create failure message for fail/exception status
        """
        if elem_type == "pj":
            elem = self.root
        elif elem_type == "ts":
            elem = self.get_ts_with_timestamp(timestamp)
        else:
            elem = self.get_tc_with_timestamp(timestamp)

        if attr == "status":
            if elem.tag == "testcase":
                if attr == "false":
                    elem.append(self.create_element("failure", {"message": "test failure"}))
                elif attr == "exception" or attr == "error":
                    elem.append(self.create_element("failure",
                                                    {"message": "errors/exceptions "\
                                                     "encountered during testcase execution"}))
            if str(value).lower() == "true":
                value = "PASS"
            elif str(value).lower() == "false":
                value = "FAIL"

        elem.set(attr, value)

    def _junit_to_html(self, junit_file, print_summary=True):
        """ Convert junit file to html"""
        if not hasattr(self, 'html_result_obj'):
            self.html_result_obj = WarriorHtmlResults(junit_file)
        self.html_result_obj.generate_html(junit_file, None, print_summary)

    def remove_html_obj(self):
        """checks and removes html_results_obj from junit object usecase in parralel execution"""
        if hasattr(self, 'html_result_obj'):
            del self.html_result_obj

    def output_junit(self, path, print_summary=True):
        """output the actual file
        copy xslt to the results folder
        Print execution summary in console based on 'print_summary' value """

        fpath = path + os.sep + self.filename + "_junit.xml"
        tree = ET.ElementTree(self.root)
        tree.write(fpath)
        if print_summary is True:
            summary_obj = ExecutionSummary(fpath)
            summary_obj.print_result_in_console(fpath)
        print_info("\n")

        self._junit_to_html(fpath, print_summary)
