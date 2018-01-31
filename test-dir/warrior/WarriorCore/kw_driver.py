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

"""Driver utils module which handles gathers the argument
information about the keywords, executes the keywords and reports the
keyword status back to the product driver """
from Framework import Utils
from WarriorCore.Classes.kw_driver_class import ModuleOperations, KeywordOperations,\
skip_and_report_status
from Framework.Utils.print_Utils import print_info

def get_package_name_list(package_list):
    """Take a list of package loaders and returns
    a list of package names """

    package_name_list = []
    for package in package_list:
        package_name_list.append(package.__name__)
    return package_name_list

def execute_keyword(keyword, data_repository, args_repository, package_list):
    """ Executes the keyword provided by product driver
    1. searches for class methods in the package list
    2. searches for independent functions in the package list
    3. If class method matching the keyword is found in the actions package executes it
        else searches for independent fucntions matching the keyword name and executes it
    """
    package_name_list = get_package_name_list(package_list)

    drv_obj = ModuleOperations(package_list, keyword)
    if len(drv_obj.matching_method_list) == 1:
        method_call = drv_obj.matching_method_list[0]
        wdesc = Utils.testcase_Utils.get_wdesc_string(method_call)
        Utils.testcase_Utils.pStep(wdesc)
        kw_obj = KeywordOperations(keyword, method_call, args_repository, data_repository)
        #print_info('found a class method(%s) corresponding to keyword(%s)'%(method_call, keyword))
        return kw_obj.execute_method_for_keyword()

    # if function not found in package skip current step and report status to Warrior
    elif len(drv_obj.matching_method_list) == 0:
        if len(drv_obj.matching_function_list) == 0:
            msg = "could not find any function/class method corresponding to "\
            "keyword '{0}' in package(s) '{1}'".format(keyword, package_name_list)
            Utils.testcase_Utils.pStep()
            return skip_and_report_status(data_repository, msg)

        elif len(drv_obj.matching_function_list) == 1:
            function_call = drv_obj.matching_function_list[0]
            wdesc = Utils.testcase_Utils.get_wdesc_string(function_call)
            Utils.testcase_Utils.pStep(wdesc)
            kw_obj = KeywordOperations(keyword, function_call, args_repository, data_repository)
            return kw_obj.execute_function_for_keyword()

        elif len(drv_obj.matching_function_list) > 1:
            print_info("more than one function with same name {0} "\
                       "exists in the  packages '{1}' ".format(keyword, package_name_list))
            Utils.testcase_Utils.pStep()
            return skip_and_report_status(data_repository, msg)

    elif len(drv_obj.matching_method_list) > 1:
        msg = "More than one method with same name '{0}' "\
        "exists in the classes of package '{1}' ".format(keyword, package_name_list)
        Utils.testcase_Utils.pStep()
        return skip_and_report_status(data_repository, msg)

