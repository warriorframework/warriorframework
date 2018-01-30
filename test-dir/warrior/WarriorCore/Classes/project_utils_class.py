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

"""Api's related project result file reporting """
import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime


class ProjectUtils(object):
    """Project Utils class"""
    def __init__(self):
        """Constructor"""
        self.root = None
        self.errors = 0
        self.failures = 0
        self.skipped = 0
        self.tests = 0
        self.time = 0.0
        self.filename = None

    def create_result_file(self, result_file, errors="0", failures="0",
                           name="", skipped="0", tests="0", time="0", timestamp="0"):
        """Create root tag"""

        self.filename = result_file
        self.root = ET.Element('testsuites')
        self.root.set('name', name)
        self.root.set('errors', errors)
        self.root.set('skipped', skipped)
        self.root.set('tests', tests)
        self.root.set('failures', failures)
        self.root.set('time', time)
        self.root.set('timestamp', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        ET.SubElement(self.root,"properties")

    @classmethod
    def create_element(cls, name="", attr=None):
        """create an xml element with given name and a dict of attribute"""
        if attr is None:
            attr = {}
        elem = ET.Element(name)
        for key, val in attr.items():
            elem.set(str(key), val)
        return elem

    def add_property(self, name, value):
        for node in self.root.iter():
            if node.tag == "properties":
                node.append(self.create_element(name="property",attr={"name":name, "value":value}))

    @staticmethod
    def format_element(elem):
        """Formatting to utf-8"""
        org = ET.tostring(elem, 'utf-8')
        output = minidom.parseString(org)
        # print output.toprettyxml(indent="    ")
        return output.toprettyxml(indent="    ")

    def add_testsuite(self, testsuite, input_type='file'):
        """Append testsuite junit to project junit"""
        if input_type == 'file':
            suites = ET.parse(testsuite)
            suite_root = suites.getroot()
            suite = suite_root.find('testsuite')
        elif input_type == 'string':
            suite = ET.fromstring(testsuite)

        self.errors += int(suite.get('errors'))
        self.failures += int(suite.get('failures'))
        self.skipped += int(suite.get('skipped'))
        self.tests += int(suite.get('tests'))
        self.time += float(suite.get('time'))
        self.root.append(suite)

    def output_junit(self):
        """Output the result to project junit file"""
        self.root.set('errors', str(self.errors))
        self.root.set('skipped', str(self.skipped))
        self.root.set('tests', str(self.tests))
        self.root.set('failures', str(self.failures))
        self.root.set('time', str(self.time))
        tree = ET.ElementTree(self.root)
        tree.write(self.filename)
