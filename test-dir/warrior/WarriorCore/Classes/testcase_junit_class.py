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

"""helper methods to create a testcase Junit file"""
import xml.etree.ElementTree as ET
import os

class TestcaseJunit(object):
    """Testcase Junit class """

    def __init__(self, testcase, result_dir, testcase_dir,
                 suite_name):
        """constructor """
        self.root = self.create_element('testsuites')
        self.filename = os.path.join(result_dir, testcase + "_tcjunit.xml")
        self.testcase_name = testcase
        self.testcase_dir = testcase_dir
        if suite_name is None:
            self.suite_name = "customTestsuite_independant_testcase_execution"
        else:
            self.suite_name = suite_name

        self._build_tree()

    def _build_tree(self):
        """main function to call when creating a new Junit result file"""

        self.testsuite = self.create_element('testsuite', {'name':self.suite_name,
                                                    'errors': "0", 'skipped':"0", 'tests':"1",
                                                    'failures':"0", 'time':"0"})
        self.root.append(self.testsuite)

        properties = self.create_element("properties")
        self.testsuite.append(properties)

        properties.append(self.create_element("property", {"name":"title",
                                                           "value":self.suite_name}))
        properties.append(self.create_element("property",
                                              {"name":"location",
                                               "value":str(os.path.join(self.testcase_dir))}))

        self.testcase = self.create_element("testcase", {"classname":self.suite_name,
                                                         "name":self.testcase_name + ".xml", "time":"0"})
        self.testsuite.append(self.testcase)

    @classmethod
    def create_element(cls, name="", attr=None):
        """create an xml element with given name and a dict of attribute"""
        if attr is None:
            attr = {}
        elem = ET.Element(name)
        for key, val in attr.items():
            elem.set(str(key), val)
        return elem

    def add_keyword_result(self, name, status):
        self.testcase.append(self.create_element("keyword", {"name":name, "status":status}))

    def add_requirement(self, requirement):
        """add a new requirement when called"""
        self.testsuite.find("properties").append(self.create_element("property", {"name":"requirement",
                                                         "value":requirement}))

    def update_fail(self, failures):
        """if it is a fail testcase, update all fields that
        are linked to failure count"""
        if failures == "1":
            self.testcase.append(self.create_element("failure", {"message":"test failure"}))
            self.testsuite.set('failures', '1')

    def update_errors(self, errors):
        """if it is a fail testcase, update all fields that
        are linked to failure count"""
        self.testcase.append(self.create_element("failure",
                                                 {"message":"errors/exceptions "\
                                                  "encountered during testcase execution"}))
        self.testsuite.set('errors', errors)

    def update_time(self, time):
        """update the running time"""
        self.testsuite.set('time', str(time))

    def update_timestamp(self, timestamp):
        self.testsuite.set("timestamp", str(timestamp))

    def add_property(self, name, value):
        for node in self.root.iter():
            if node.tag == "testsuite":
                node.find('properties').append(self.create_element(name="property", attr={"name":name, "value":value}))

    def output_junit(self):
        """output the actual file"""
        tree = ET.ElementTree(self.root)
        tree.write(self.filename)
