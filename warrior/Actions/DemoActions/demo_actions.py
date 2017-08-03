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

"""This is demo_actions module that has all demo test case related keywords """
import base64
import json
import urllib2
import os

import Framework.Utils as Utils
from Framework.Utils.testcase_Utils import pNote, pSubStep
from Framework.Utils.data_Utils import getSystemData, get_credentials
from Framework.Utils.print_Utils import print_info, print_warning,\
print_error, print_debug, print_exception
from Framework.Utils import file_Utils as file_Utils


class DemoActions(object):
    """DemoActions class which has methods(keywords)
    related to actions used in demo KW """

    def __init__(self):
        """
        constructor
        """
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

    def check_lab_equipment(self, system_name):
        """
        Call the pc_replacement or testset_calibration KW to validate
        lab PC or test set calibration are up-to-date or not.
        """
        wdesc = "Check lab PC replacement or test set calibration status"
        pNote(wdesc)
        #Resolve system_name and subsystem_list
        system_name, subsystem_list = Utils.data_Utils.resolve_system_subsystem_list(self.datafile, system_name)
        output_dict = {}
        status = True
        attempt = 1 if subsystem_list == None else len(subsystem_list)
        for i in range(attempt):
            result = False
            subsystem_name = subsystem_list[i] if subsystem_list != None else None
            #Put system_name in system_name[subsystem] format before calling
            #checking function
            call_system_name = system_name if subsystem_name is None \
            else "{0}[{1}]".format(system_name, subsystem_name)
            eqpt_type = getSystemData(self.datafile, call_system_name, "eqpt_type")

            if eqpt_type is not False:
                if eqpt_type == "lab_pc":
                    result, output_dict = self.pc_replacement(call_system_name)
                elif eqpt_type == "lab_testset":
                    result, output_dict = self.testset_calibration(call_system_name)
                else:
                    pNote("<eqpt_type>={0} provided for '{1}' is  not "\
                          "supported".format(eqpt_type, call_system_name), "error")
            else:
                pNote("eqpt_type not provided for system={0}"\
                      .format(call_system_name), "warn")
            status = status and result

        return status, output_dict

    def pc_replacement(self, system_name):
        """
        Verify lab PC is current if less than 4 years old, otherwise
        a replacement is required.
        """
        wdesc = "Check if lab PC is current or need replacement"
        #Resolve system_name and subsystem_list
        system_name, subsystem_list = Utils.data_Utils.resolve_system_subsystem_list(self.datafile, system_name)
        output_dict = {}
        status = True
        attempt = 1 if subsystem_list == None else len(subsystem_list)
        for i in range(attempt):
            Utils.testcase_Utils.pSubStep(wdesc)
            #Get name from the list when it's not 'None', otherwise, set it to 'None'
            subsystem_name = subsystem_list[i] if subsystem_list != None else None
            call_system_name = system_name if subsystem_name is None \
            else "{0}[{1}]".format(system_name, subsystem_name)
            credentials = get_credentials(self.datafile, call_system_name,
                                          ['dom', 'user', 'os', 'testdata'])
            pNote("system={0}".format(call_system_name))
            #Demo Framework testdata capability
            testdatafile = file_Utils.getAbsPath(credentials["testdata"], os.path.dirname(self.datafile))
            add_info = Utils.xml_Utils.getElementWithTagAttribValueMatch(testdatafile, \
                       'add_info', 'name', 'testdata')
            if add_info is not None:
                info_text = Utils.xml_Utils.get_text_from_direct_child(add_info, 'info')
                pNote(info_text)
                pNote(testdatafile)

            if credentials is not None and credentials is not False:
                num_of_year = 4
                date_of_mfg = credentials["dom"]
                pass_msg = "Lab PC {0} is current, it's less than 4 years old."\
                           " A replacement is NOT required."\
                           .format(call_system_name)
                fail_msg = "Lab PC {0} is NOT current, it's more than than 4 "\
                           "years old. Please schedule for a replacement."\
                           .format(call_system_name)
                result = Utils.demo_utils.lab_eqpt_status(date_of_mfg, num_of_year, pass_msg, fail_msg)

            Utils.data_Utils.update_datarepository(output_dict)
            Utils.testcase_Utils.report_substep_status(result)
            status = status and result

        return status, output_dict


    def testset_calibration(self, system_name):
        """
        Check if the test set calibration is current if less than 1 year old,
        otherwise, re-calibration is required.
        """
        wdesc = "Check if Lab Test set calibration is current."
        #Resolve system_name and subsystem_list
        system_name, subsystem_list = Utils.data_Utils.resolve_system_subsystem_list(self.datafile, system_name)
        output_dict = {}
        status = True
        attempt = 1 if subsystem_list == None else len(subsystem_list)
        for i in range(attempt):
            Utils.testcase_Utils.pSubStep(wdesc)
            #Get name from the list when it's not 'None', otherwise, set it to 'None'
            subsystem_name = subsystem_list[i] if subsystem_list != None else None
            call_system_name = system_name if subsystem_name is None \
            else "{0}[{1}]".format(system_name, subsystem_name)
            credentials = get_credentials(self.datafile, call_system_name, \
                                ['calibration', 'user', 'location', 'testdata'])
            pNote("system={0}".format(call_system_name))
            #Demo Framework testdata capability
            testdatafile = file_Utils.getAbsPath(credentials["testdata"], os.path.dirname(self.datafile))
            add_info = Utils.xml_Utils.getElementWithTagAttribValueMatch(testdatafile, \
                       'add_info', 'name', 'testdata')
            if add_info is not None:
                info_text = Utils.xml_Utils.get_text_from_direct_child(add_info, 'info')
                pNote(info_text)
                pNote(testdatafile)

            if credentials is not None and credentials is not False:
                calibrated_date = credentials["calibration"]
                num_of_year = 1
                pass_msg = "Lab Test set {0} calibration is current, "\
                           "re-calibration is NOT required."\
                           .format(call_system_name)
                fail_msg = "Lab Test set {0} calibration is NOT current, it's "\
                           "more than than 1 year old. Re-calibration is "\
                           "required".format(call_system_name)
                result = Utils.demo_utils.lab_eqpt_status(calibrated_date, num_of_year, pass_msg, fail_msg)

            Utils.data_Utils.update_datarepository(output_dict)
            Utils.testcase_Utils.report_substep_status(result)
            status = status and result

        return status, output_dict

    def local_data_test(self, desired_status):
        """For testing/demo/placeholder
        return true/false/exception based on input
        :Argument:
            desired_status = user desired status
            input pass->true, fail->false and everything else ->exception
        """
        # print "desired_status: " + desired_status

        print_error("Please use the one in ci_regression_actions")
        if desired_status == "pass":
            return True
        elif desired_status == "fail":
            return False
        else:
            raise Exception("This is raised in demo_actions.local_data_test")

    def create_jira_issue(self, server_url, username, password, issue_summary, issue_description, project_key, issue_type='Bug'):
        """
            connect to jira server and create an issue under a specific project
        """
        status = True
        output_dict = {}
        wdesc = "Creates a JIRA issue"
        pSubStep(wdesc)
        issue_summary = issue_summary.replace('"', " ")
        issue_description = issue_description.replace('"', "-")
        fetchuri = server_url
        postdata_url=fetchuri+'/rest/api/2/issue/'
        postdata = """
        {
            "fields": {
                "project":
                {
                    "key": \""""+project_key+"""\"
                },
                "summary": \""""+issue_summary+"""\",
                "description": \""""+issue_description+"""\",
                "issuetype": {
                    "name": \""""+issue_type+"""\"
                }
            }
        }
        """
        credential_handler=urllib2.HTTPPasswordMgrWithDefaultRealm()
        credential_handler.add_password(None, postdata_url, username, password)
        auth = urllib2.HTTPBasicAuthHandler(credential_handler)
        userpassword = username + ":" + password
        password = base64.b64encode(userpassword)
        #Create an Authentication handler
        opener = urllib2.build_opener(auth)
        urllib2.install_opener(opener)
        opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
        #Create a POST request
        headers={"Authorization" : "Basic "+password,"Content-Type": "application/json"}
        request=urllib2.Request(str(postdata_url),postdata,headers)
        try:
            handler = urllib2.urlopen(request)
            extension = json.loads(handler.read())
            issue_id = str(extension['key'])
            pNote("JIRA Issue Created. Issue-Id: {0}".format(issue_id))
            output_dict["issue_id"] = issue_id
        except Exception as e:
            status = False
            pNote("Problem creating JIRA issue." , "error")
            pNote("JIRA Error Code: ({0})".format(e) , "error")

        Utils.data_Utils.update_datarepository(output_dict)
        Utils.testcase_Utils.report_substep_status(status)
        return status
