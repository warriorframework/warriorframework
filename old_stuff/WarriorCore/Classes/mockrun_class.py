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

"""This is the library called mockrun which checks the
script errors in the xml files"""

from Framework.Utils.print_Utils import print_info, print_exception

class MockRun(object):
    """ mockRun Class"""

    def __init__(self):
        """ Contructor """
        self.tab = "    "

    def print_summary(self, output):
        """This is to print the summary of the executed files"""
        level = 0
        details = {}
        self.print_suite_summary(output, level, details)


    def print_suite_summary(self, output, level, details):
        """This is to print the summary of the executed suite files"""
        suites = output.split("Executing testsuite '")[1:]
        if suites:
            print_info("Suites")
            print_info("-"*6)
        else:
            self.print_testcase_summary(output, level, details)
        suite_names = [suite.split("'")[0] for suite in suites]
        for (suite, suite_name) in zip(suites, suite_names):
            print_info(self.tab*level+suite_name)
            details[suite_name] = {}
            self.print_testcase_summary(suite, level+1, details[suite_name])

    def print_testcase_summary(self, output, level, details):
        """This is to print the summary of the executed test case files"""
        testcases = output.split("Starting execution of Test case: ")[1:]
        if testcases:
            testcase_files = [testcase.split(">>>>")[0] for testcase in testcases]
        else:
            testcases = output.split("Abosulete path")[1:]
            tc_files = [testcase.split('\n')[0] for testcase in testcases]
            testcase_files = [testcase.split(': ')[1] for testcase in tc_files]
        details['testcases'] = testcases
        details['testcase_files'] = testcase_files
        print_info(self.tab*level+'Testcases')
        print_info(self.tab*level+'---------')
        for (testcase, testcase_file) in zip(testcases, testcase_files):
            details[testcase_file] = {}
            keywords = testcase.split("Keyword:")[1:]
            details[testcase_file]['keywords'] = keywords
            details[testcase_file]['statuses'] = []
            for keyword in keywords:
                status = keyword.split("Keyword status ***")[1].split('\n')[1].split('- ')[1].split(':')[2]
                details[testcase_file]['statuses'].append(status)
            errors = ''.join(details[testcase_file]['statuses'])
            nerrs = errors.count('ERROR')+errors.count('FAIL')
            details[testcase_file]['errors'] = nerrs
            print_info(self.tab*level+testcase_file)
            print_info(self.tab*level+' - %3d errors' % nerrs)
