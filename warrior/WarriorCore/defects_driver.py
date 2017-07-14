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

"""jira utils library which has functions related to
interaction of Warrior framework with jira rest api and other related actions."""

import os
import Tools
import json
import time
from WarriorCore.Classes.jira_rest_class import Jira
from Framework.Utils.print_Utils import print_error, print_info, print_warning
from Framework.Utils import xml_Utils, file_Utils

class DefectsDriver(object):
    """ Defects Driver Class """

    def __init__(self, data_repository):
        """Constructor for Defects Driver"""
        self.xmlfile = data_repository['wt_resultfile']
        self.defectsdir = data_repository['wt_defectsdir']
        self.logsdir = data_repository['wt_logsdir']
        self.resultfile = data_repository['wt_resultfile']
        self.testcase_filepath = data_repository['wt_testcase_filepath']
        self.jiraproj = data_repository['jiraproj']
        self.w_jira_object = None

    def create_failing_kw_json(self):
        """Create a json file each failing keyword """

        status = False
        result_filename = file_Utils.getNameOnly(os.path.basename(self.xmlfile))
        tc_name = result_filename.split("_results")[0]
        #tc_name = file_Utils.getNameOnly(os.path.basename(self.xmlfile))
        #tree = xml_Utils.get_tree_from_file(self.xmlfile)
        tree = xml_Utils.getRoot(self.xmlfile)
        data_filepath = tree.find("Datafile").text
        failed = 0
        #get_tc_details_frm_resultxml
        keyword_list = tree.findall("Keyword")

        if len(keyword_list) == 0:
            print_error('No Keywords found in resultfile of testcase {0}'.format(tc_name))
            status = False
        else:
            for keyword in tree.findall("Keyword"):
                fail_list = []
                if keyword.find("KeywordStatus").text.upper() in ['FAIL', 'EXCEPTION', 'ERROR']:
                    step_num = keyword.find("Step").get('step_num')
                    kw_resultfile = keyword.find("Resultfile").text
                    kw_resultfile_nameonly = file_Utils.getNameOnly(os.path.basename(kw_resultfile))
                    failed += 1
                    #addd testcase details to json of failed keyowrds
                    fail_list.append({'tc_name':tc_name})
                    fail_list.append({'step_num':str(step_num)})
                    fail_list.append({'testcase_filepath':str(self.testcase_filepath)})
                    fail_list.append({'data_filepath':str(data_filepath)})
                    fail_list.append({'defectsdir':str(self.defectsdir)})
                    fail_list.append({'logsdir':str(self.logsdir)})
                    fail_list.append({'resultfile':str(self.resultfile)})
                    for node in keyword.iter():
                        text = self._get_text_forjson(node)
                        if text: 
                            fail_list.append({node.tag: text}) 
                        else: continue
                if len(fail_list) > 0:
                    json_file_name = "{0}{1}{2}_{3}.json".format(self.defectsdir, os.sep,
                                                                 tc_name, kw_resultfile_nameonly)
#                     json_file_name = self.defectsdir + os.sep + tc_name +\
#                                     '_step-'+str(step_num)+'_' + keyword.text +'.json'
                    j_file = open(json_file_name, 'w')
                    j_file.write(json.dumps(fail_list, indent=4))
                    j_file.close()
                    status = True
            if failed == 0:
                print_warning("There are no failed keywords in the testcase result xml file")
                status = False
            return status
    
    def _get_text_forjson(self, node):
        """Process the text and attributes of a node
        into a text, this text will be used in the defect json file"""
        text = ""        
        excl_list = ["Name", "Arguments"]

        if node.tag == "Keyword":
            text = node.find("Name").text
        elif node.tag == "argument":
            text = self._get_argument_text(node)
        elif node.tag in excl_list:
            text = ""
        else:
            text = node.text
        return text

    def _get_argument_text(self, arg):
        """Get test for arguemnt nod ein the form 
        name="name", value="value" """
        
        name = str(arg.get("name"))
        value = str(arg.get("value"))
        text =  "name={0}, value={1}".format(name, value) 
        return text

    def get_defect_json_list(self):
        """Gets the list of defect json files for the testcase execution """
        defects_list = []

        for j_file in os.listdir(self.defectsdir):
            if j_file.endswith(".json"):
                defect_file = os.path.abspath(self.defectsdir + os.sep+ j_file)
                print_info("Defect file location is :{0}".format(defect_file))
                defects_list.append(defect_file)
        return defects_list

    def connect_warrior_jira(self):
        """Creates a Warrior Jira object """
        self.w_jira_object = Jira(self.jiraproj)
        return self.w_jira_object.status

    def create_jira_issues(self, defects_json_list):
        """Creates issues in jira """
        issue_list = []
        if self.w_jira_object is not None:
            if self.w_jira_object.status is not False:
                issue_list = self.w_jira_object.create_issues_from_jsonlist(defects_json_list,
                                                                            self.xmlfile,
                                                                            issue_type='Bug')
                for issue in issue_list:
                    self.attach_logs_to_jira_issues(issue)
                    time.sleep(3)
            elif self.w_jira_object.status is False:
                print_error("could not obtain jira credentials!! "\
                            "check jira config file ")

        return issue_list

    def attach_logs_to_jira_issues(self, issue):
        """Attach logs to jira issues """
        logs_zipfile = file_Utils.create_zipdir('logs', self.logsdir)
        self.w_jira_object.upload_logfile_to_jira_issue(issue, logs_zipfile)
        time.sleep(3)
        self.w_jira_object.upload_logfile_to_jira_issue(issue, self.resultfile,
                                                        'full_resultfile.xml')
        time.sleep(3)
        self.w_jira_object.upload_logfile_to_jira_issue(issue, self.testcase_filepath,
                                                        'tescase.xml')
        time.sleep(3)
