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

import multiprocessing


def create_and_start_process_with_queue(target_module, args_dict, jobs_list, output_q, p_name=''):
    """Creates python multiprocesses for the provided target module with the
    provided arguments and  starts them

    Arguments:
    1. target_module = module for which multiple processes has to be started
    2. args_list = list of arguments to be passed to the target module
    3. jobs_list = list of process created
    4. output_q  = multiprocessing.Queue object to handle returns from the target module
    """

    # THis is to handle the first process when
    # output_q wll be none,create a new q and use the
    # same q for all instances of process started
    if output_q is None:
        # output_q = multiprocessing.JoinableQueue()
        output_q = multiprocessing.Manager().Queue()

    args_dict["output_q"] = output_q

    # now we need to convert the args_dict into
    # a tuple so first create a listout of the dict
    # and then convert the list into a tuple
    args_list = []
    for _, value in args_dict.iteritems():
        args_list.append(value)
    args_tuple = tuple(args_list)

    process = multiprocessing.Process(name=p_name, target=target_module, args=args_tuple)
    jobs_list.append(process)

    process.start()

    return process, jobs_list, output_q


def get_results_from_queue(queue):
    """Get the result form the provided multiprocessing queue object """
    result_list = []
    for _ in range(queue.qsize()):
        # print type(queue), queue.qsize()
        result_list.append(queue.get())
    return result_list


def update_ts_junit_resultfile(ts_junit_obj, tc_junit_list, ts_timestamp):
    """loop through tc_junit object and attach testcase result to testsuite
    Arguments:
    1. ts_junit_obj = target testsuite
    2. tc_junit_list = list of testcase junit objects
    """

    for master_ts in ts_junit_obj.root.iter('testsuite'):
        # make sure we are modifying the correct testsuite
        if master_ts.get('timestamp') == ts_timestamp:
            for tc_junit_obj in tc_junit_list:
                for ts_part in tc_junit_obj.root.iter('testsuite'):
                    # make sure we are obtaining only the wanted testcases
                    if ts_part.get('timestamp') == ts_timestamp:
                        # add testcase element to testsuite, update count
                        for tc in ts_part.iter('testcase'):
                            master_ts.append(tc)
                            master_ts.attrib = update_attribute(master_ts.attrib, ts_part.attrib)

    return ts_junit_obj


def update_pj_junit_resultfile(pj_junit_obj, ts_junit_list):
    """loop through ts_junit object and attach suite result to project(testsuites)
    :Arguments:
        1. pj_junit_obj = target project
        2. ts_junit_list = list of suite junit objects
    """
    for ts_junit_obj in ts_junit_list:
        for ts in ts_junit_obj.root.iter('testsuite'):
            # append suite result to testsuites
            pj_junit_obj.root.append(ts)
        # update the count in testsuites attribute
        pj_junit_obj.attrib = update_attribute(pj_junit_obj.root.attrib,
                                               ts_junit_obj.root.attrib)
    return pj_junit_obj


def update_attribute(dict1, dict2):
    """merge the count for 2 attribute dictionary
    Arguments:
    1. dict1 = target dict
    2. dict2 = obtain count from this dict and put in dict1
    """
    keys = ["errors", "failures", "skipped", "passes", "exceptions",
            "keywords", 'tests', 'suites']
    for key in keys:
        if key in dict1 and key in dict2:
            dict1[key] = str(int(dict1[key])+int(dict2[key]))
    return dict1


def update_tc_junit_resultfile(tc_junit_obj, kw_junit_list, tc_timestamp):
    """loop through kw_junit object and attach keyword result to testcase
    Arguments:
    1. tc_junit_obj = target testcase
    2. kw_junit_list = list of keyword junit objects
    3. tc_timestamp = target testcase timestamp
    """
    for master_tc in tc_junit_obj.root.iter('testcase'):
        # make sure we are modifying the correct testcase
        if master_tc.get('timestamp') == tc_timestamp:
            for kw_junit_obj in kw_junit_list:
                for tc_part in kw_junit_obj.root.iter('testcase'):
                    # make sure we are obtaining only the wanted keywords
                    if tc_part.get('timestamp') == tc_timestamp:
                        # add keyword element to testcase, add property result
                        # to properties, update count
                        for result in tc_part.find('properties').iter('property'):
                            if result.get('type') == "keyword":
                                master_tc.find('properties').append(result)
                        master_tc.attrib = update_attribute(master_tc.attrib, tc_part.attrib)

    return tc_junit_obj
