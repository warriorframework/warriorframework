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

"""
Iterative testsuite:
An iterative suite is one where the  exectype="iterative_sequential" or "iterative_parallel".

- For an iterative suite it is mandatory to provide a value for <InputDataFile> in the details
section of the suite.

- All cases in the suite will use the <InputDataFile> provided in the details section of the
suite for execution i.e. the values of <InputDataFile> provided in for each case in the suite
or the value of <InputDataFile> provided in the case details will be overwritten with the value
of <InputDataFile> provided in the details section of the suite.

- In case of an iterative suite user will not be able to provide an input datafile to each
testcase in the suite. If using katana the option will not be available to the user, if user
uses an xml editor ad provides a value for <input_data_file> for a case in the suite then this
value will be ignored.

- If the suite is of exectype=iterative_parallel or iterative_sequential then all the testcases
in the suite should have datatype=Iterative and not custom. If any testcase in an iterative
suite has datatype=custom then the testcase execution will be skipped.

iterative_sequential:
If the suite exectype="iterative_sequential" then the cases in the suite will be executed against
each system in the <InputDataFile> in a sequential fashion.

For Eg:
Suite-1 has exectype="iterative_sequential", <InputDataFile> provided in the suite details has 2
systems say sys-1, sys-2. Suite-1 has three cases say case-1, case-2, case-3.

For the eg the execution would be as follows.
1. case-1 will be executed on sys-1 then,
2. case-2 will be executed on sys-1 then,
3. case-3 will be executed on sys-1 then,
4. case-1 will be executed on sys-2 then,
5. case-2 will be executed on sys-2 then,
6. case-3 will be executed on sys-2.

iterative_parallel:
If the suite exectype="iterative_parallel" then the cases in the suite will be executed against
each system in the <InputDataFile> in a parallel fashion.

For Eg:
Suite-1 has exectype="iterative_parallel", <InputDataFile> provided in the suite details has 2
systems say sys-1, sys-2. Suite-1 has three cases say case-1, case-2, case-3.

For the eg the execution would be as follows.
case-1, case-2, case-3  will be executed on sys-1 sequentially,
at the same time case-1, case-2, case-3  will be executed on sys-2 sequentially.
So the case executions will take place in parallel on all the systems at the same time.

"""

from Framework.Utils import data_Utils
from Framework.Utils.testcase_Utils import pNote
from WarriorCore import sequential_testcase_driver, iterative_parallel_testcase_driver

class IterativeTestsuite(object):
    """
    Class for Iterative Suite
    """
    def __init__(self, testcase_list, suite_repository, data_repository,
                 from_project, auto_defects):
        """
        Constructor
        """
        self.testcase_list = testcase_list
        self.suite_repository = suite_repository
        self.data_repository = data_repository
        self.from_project = from_project
        self.auto_defects = auto_defects
        self.ts_datafile = self.suite_repository['data_file']

        # get the list of system names and system nodes (as xml elements) from the <InputDataFile>
        # provided in the suite details
        self.system_name_list, self.system_node_list = data_Utils.get_system_list(self.ts_datafile,
                                                                                  node_req=True)
        # get the list of systems (names, nodes) that has iter=yes.
        self.iter_sysnamelist,\
        self.iter_sysnode_list = data_Utils.get_iteration_syslist(self.system_node_list,
                                                                  self.system_name_list)

    def execute_iterative_sequential(self):
        """
        Execute the cases in a suite in iterative
        sequential fashion
        """
        ts_status = True
        if self.iter_sysnamelist == []:
            pNote("Testsuite exec_type=iterative_sequential but there are no systems "\
                  "in the datafile={0} that can be iterated upon, please check the "\
                  "iter parameter os the systems in the datafile".format(self.ts_datafile),
                  "error")
            ts_status = False
        for system in self.iter_sysnamelist:
            ts_result = sequential_testcase_driver.main(self.testcase_list, self.suite_repository,
                                                        self.data_repository, self.from_project,
                                                        self.auto_defects, iter_ts_sys=system)
            if ts_result == 'ERROR':
                ts_status = 'ERROR'
            else:
                ts_status = ts_result and ts_status
        return ts_status

    def execute_iterative_parallel(self):
        """
        Execute the testcases in a testsuite in a iterative
        parallel fashion
        """
        ts_status = True
        if self.iter_sysnamelist == []:
            pNote("Testsuite exec_type=iterative_sequential but there are no systems "\
                  "in the datafile= {0} that can be iterated upon, please check the "\
                  "iter parameter os the systems in the datafile".format(self.ts_datafile),
                  "error")
            ts_status = False
        else:
            ts_status = iterative_parallel_testcase_driver.main(self.iter_sysnamelist,
                                                                self.testcase_list,
                                                                self.suite_repository,
                                                                self.data_repository,
                                                                self.from_project,
                                                                True, self.auto_defects)
        return ts_status
