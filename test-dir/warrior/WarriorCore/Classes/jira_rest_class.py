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

import json
import os

import Tools
from Framework.Utils.print_Utils import print_error, print_info, print_warning
from Framework.Utils import xml_Utils

try:
    import requests
except ImportError:
    print_warning("{0}: 'requests' module is not installed".format(os.path.abspath(__file__)))
    print_warning("WarriorFramework uses 'requests' module for all Jira related activites")


""" jira utils library which has functions related to interaction
of Warrior framework with jira rest api and other related actions."""


class Jira(object):
    """Warrior Jira class """

    def __init__(self, jiraproj):
        """Constructor"""
        jira_dir = Tools.__path__[0] + os.sep + 'jira' + os.sep
        self.jira_template_xml = jira_dir + os.sep + 'jira_config.xml'
        self.jiraproj = jiraproj
        credentials = self.get_jira_system_creds(self.jira_template_xml, self.jiraproj,
                                                 ['url', 'username', 'password',
                                                  'assignee', 'project_key', 'append_log'])
        if credentials is False:
            self.status = False
            return None

        self.server = credentials['url']
        self.username = credentials['username']
        self.password = credentials['password']
        self.auth = (self.username, self.password)
        self.append = True if str(credentials['append_log']).lower().strip() == "true" else False
        self.status = True
        self.project_key = credentials['project_key']
        self.assignee = credentials['assignee']

    def check_jira_issue(self, issue_summary):
        """
            check jira server for any existing issue with the same summary(title)
            :Arguments,:
                1. issue_summary(str) - issue title
            :Returns:
                1. issue_id(str/boolean) - existing issue key or False if not found
        """
        issue_id = False
        parsed_summary = issue_summary.replace("[", "\\\\[")
        parsed_summary = parsed_summary.replace("]", "\\\\]")
        postdata_url = (self.server + '/rest/api/2/search/?jql=summary~' +
                        '\"' + parsed_summary + '\"')
        response = requests.get(postdata_url, auth=self.auth)

        if response:
            resp_dict = response.json()
            for issue in resp_dict["issues"]:
                if issue_summary[:-2].strip() == issue["fields"]["summary"].strip():
                    issue_id = issue["key"]
                else:
                    # partially match title
                    pass
        else:
            print_error("Problem checking JIRA issues with same issue summary")
            print_error("JIRA Error code: ({0}), Error message: ({1})".
                        format(response.status_code, response.reason))
        return issue_id

    def update_jira_issue(self, jiraid, status):
        """
        Update the jira issue using the jiraid
        Transition to correct issue status based on warrior status
        :Arguments:
            1. jiraid(str) - Jira issue ID
            2. status(str/boolean) - warrior execution status
        :Returns:
            1. oper_status(Boolean) - True/False
        """

        print_info("Updating the status of the Jira issue '{0}'".format(jiraid))
        issue_type = self.get_jira_issue_type(jiraid)
        if not issue_type:
            # when failed to get the type of the Jira issue
            return False

        oper_status = False
        status_map = {"true": "pass", "false": "fail"}
        status = status_map[str(status).lower()] if str(status).lower() in \
            status_map else str(status).lower()

        # Find the correct jira system from the jira_config.xml
        if self.jiraproj is not None:
            jiraproj = self.jiraproj
            sys_elem = xml_Utils.getElementWithTagAttribValueMatch(self.jira_template_xml,
                                                                   'system', 'name', jiraproj)
        else:
            jiraproj = "default"
            sys_elem = xml_Utils.getElementWithTagAttribValueMatch(self.jira_template_xml,
                                                                   'system', jiraproj, "true")

        # Find the correct issue type and status
        if sys_elem is not None and sys_elem is not False:
            sys_data = xml_Utils.get_children_as_dict(sys_elem)

            type_matched = None
            for t in sys_data["issue_type"]:
                if t["type"] == [issue_type]:
                    type_matched = t
                    break
            if type_matched is None:
                for t in sys_data["issue_type"]:
                    if t["type"] == ["default"]:
                        type_matched = t

            if type_matched is not None and status in type_matched.keys():
                # Change the jira issue status
                if type_matched[status][0]:
                    to_status = type_matched[status][0].lower()
                    oper_status = self.set_jira_issue_status(jiraid, to_status)
                else:
                    print_error("No value provided for the tag '{0}' under issue_type "
                                "'{1}' of project '{2}' in jira_config file '{3}'.".
                                format(status, issue_type, jiraproj,
                                       "Tools/jira/jira_config.xml"))
            else:
                print_error("Cannot find the correct issue type in "
                            "jira_config file, unable to update jira status")
        else:
            print_error("There is no project with name: '{0}' in the jira config "
                        "file: '{1}'".format(self.jiraproj, "Tools/jira/jira_config.xml"))

        return oper_status

    def create_jira_issue(self, issue_summary, issue_description, issue_type='Bug'):
        """
        Function to Create jira Ticket using JIRA rest API
        :Arguments:
            1. issue_summary(str) - Jira issue ID
            2. issue_description(str) - warrior execution status
            3. issue_type(str) - Jira issue type(Ex. Story/Bug/Task)
        :Returns:
            1. issue_id(str/boolean) - (a) issue_key if created
                                       (b) False if not created
                                       (c) issue_key if already exists and the append_log is True
                                       (d) False if already exists and the append_log is not True
        """
        issue_id = False
        issue_summary = issue_summary.replace('"', " ")
        issue_description = issue_description.replace('"', "-")
        postdata_url = self.server + '/rest/api/2/issue/'
        headers = {"Content-Type": "application/json"}
        postdata = """
        {
            "fields": {
                "project":
                {
                    "key": \""""+self.project_key+"""\"
                },
                "summary": \""""+issue_summary+"""\",
                "description": \""""+issue_description+"""\",
                "issuetype": {
                    "name": \""""+issue_type+"""\"
                }
            }
        }
        """

        existed = self.check_jira_issue(issue_summary)
        if not existed:
            # POST request to create new Jira issue
            response = requests.post(postdata_url, auth=self.auth,
                                     headers=headers, data=postdata)
            if response:
                resp_dict = response.json()
                issue_id = str(resp_dict['key'])
                print_info("JIRA Issue Created. Issue-Id: {0}".format(issue_id))
            else:
                print_error("Problem creating JIRA issue")
                print_error("JIRA Error code: ({0}), Error message: ({1})".
                            format(response.status_code, response.reason))
        else:
            if self.append:
                print_info("Issue '{0}' already exists and the execution logs "
                           "will be uploaded since the 'append_log' option is "
                           "set to True in jira config file".format(str(existed)))
                issue_id = existed
            else:
                print_info("Issue '{0}' already exists and the execution logs "
                           "will not be uploaded since the 'append_log' option is "
                           "not set to True in jira config file".format(str(existed)))

        return issue_id

    def upload_logfile_to_jira_issue(self, issue_id, logfile, attachment_name="Log file"):
        """
        Function to attach logs to jira Ticket using JIRA rest API
        :Arguments:
            1. issue_id(str) - Jira issue ID
            2. logfile(str) - File(path) to be attached
            3. attachment_name(str) - Name of the file to be attached
        """

        status = False
        postdata_url = self.server + '/rest/api/2/issue/' + issue_id + '/attachments'
        print_info("logfile is : {0}".format(logfile))
        fileobj = open(logfile, 'rb').read()
        logfile_name = os.path.basename(logfile)
        headers = {"X-Atlassian-Token": "nocheck"}
        files = {"file": (logfile_name, fileobj)}
        response = requests.post(postdata_url, auth=self.auth,
                                 files=files, headers=headers)

        if response:
            status = True
            print_info("{0} - '{1}' uploaded to Jira issue '{2}'"
                       .format(attachment_name, logfile_name, issue_id))
        else:
            print_error("Problem attaching logs to Jira issue '{0}'".format(issue_id))
            print_error("JIRA Error code: ({0}), Error message: ({1})".
                        format(response.status_code, response.reason))
        return status

    def create_issues_from_jsonlist(self, json_file_list,
                                    result_xml_file, issue_type='Bug'):
        """Takes a list of json files as input and creates
        jira ticket for each json file"""

        issue_id_list = []
        for json_file in json_file_list:
            issue_summary, issue_description, step_num = self.get_issue_description(json_file)
            if issue_summary is not None:
                issue_id = self.create_jira_issue(issue_summary,
                                                  issue_description,
                                                  issue_type)
                self.update_issue_in_resultxml(result_xml_file, issue_id, step_num)
                if issue_id:
                    # The cases when issue_id is False/None are 1) error
                    # 2) issue exist and user chose not to append log
                    issue_id_list.append(issue_id)

        print_info("Issue List: {0}".format(issue_id_list))
        return issue_id_list

    @classmethod
    def get_issue_description(cls, json_file):
        """Takes a warrior issue json file as input and
        forms the summary, description for the jira issue to be created"""

        tc_name, keyword, step_num, issue_summary = (None,)*4
        step = keyword
        desc = '-'*18 + ' Description ' + '-'*18 + '\\n'
        p_header = '-'*18 + 'Problem Details' + '-'*18 + '\\n'

        with open(json_file) as issue_file:
            json_data = json.load(issue_file)

        for attr in json_data:
            if 'Keyword' in attr:
                keyword = attr['Keyword']
            elif 'tc_name' in attr:
                tc_name = attr['tc_name']
            elif 'Step' in attr:
                step = attr['Step']
            elif 'step_num' in attr:
                step_num = attr['step_num']
        if not all([tc_name, keyword, step_num]):
            print_error("all/one of tc_name, keyword, step_num is missing.."
                        "could not create jira ticket without these details")
        else:
            issue_summary = ("TC-" + str(tc_name).strip() + ":" + "Keyword-" +
                             str(keyword).strip() + ":" + "Step{0}.".format(str(step_num)) +
                             str(step).strip() + "[FAILED]" + '\\n')

            desc = desc + '\\n' + issue_summary + '\\n' + '\\n' + p_header + '\\n'
            for attr in json_data:
                for key, value in attr.items():
                    key = key.replace('\n', "\\n")
                    value = value.replace('\n', "\\n")
                    desc = desc + str(key) + ':' + str(value) + '\\n'

            desc = ('\\n' + desc + '\\n' + "-Attached logfiles" + '\\n' +
                    "-Attached actual testcase for steps to reproduce" + '\\n')
        return issue_summary, desc, str(step_num)

    @classmethod
    def update_issue_in_resultxml(cls, result_xml_file, issue_id, step_num):
        """ Update the issue-id under the corresponding step
        in the testcase result xml file """

        tree = xml_Utils.get_tree_from_file(result_xml_file)
        keywords = tree.findall('Keyword')
        for keyword in keywords:
            step = keyword.find('Step')
            if step is not None:
                ts_num = step.get('step_num')
                if ts_num == str(step_num):
                    defect = xml_Utils.create_subelement(step, 'Defect', {})
                    defect.text = str(issue_id)
                    tree.write(result_xml_file)

    @staticmethod
    def get_jira_system_creds(datafile, system_name, list_my_info):
        """Returns a python dictionary containing key value pairs of
        requested info and their values for the provided system name from the datafile """
        if system_name is not None:
            element = xml_Utils.getElementWithTagAttribValueMatch(datafile,
                                                                  'system',
                                                                  'name',
                                                                  system_name)
        else:
            element = xml_Utils.getElementWithTagAttribValueMatch(datafile, 'system',
                                                                  'default', "true")
            if element is None:
                node_value = xml_Utils.getNodeValuebyAttribute(datafile, 'system', 'name')
                element = xml_Utils.getElementWithTagAttribValueMatch(datafile, 'system',
                                                                      'name',
                                                                      node_value)
        if element is not None and element is not False:
            output_dict = {}
            for item in list_my_info:
                output_dict[item] = xml_Utils.get_text_from_direct_child(element, item)
            return output_dict
        else:
            msg = ("There is no project with name: '{0}' in the jira config "
                   "file: '{1}'".format(system_name, "Tools/jira/jira_config.xml"))
            print_warning(msg)
            return False

    def get_jira_issue_type(self, jiraid):
        """
        Returns the type of the Jira Issue in lower case.
        :Arguments:
            1. jiraid(str) - Jira issue ID
        :Returns:
            1. issue_type(str) or False(Bool)
        """

        issue_type = False
        issue_url = self.server + '/rest/api/2/issue/' + jiraid
        # Get the details of the the Jira ticket to find the issue type
        response = requests.get(issue_url, auth=self.auth)
        if response:
            issue_details = response.json()
            issue_type = issue_details['fields']['issuetype']['name'].lower()
        else:
            print_error("Problem getting type of the Jira issue '{0}'".format(jiraid))
            print_error("JIRA Error code: ({0}), Error message: ({1})".
                        format(response.status_code, response.reason))

        return issue_type

    def get_jira_issue_status(self, jiraid):
        """
        Returns the current status of the Jira Issue
        :Arguments:
            1. jiraid(str) - Jira issue ID
        :Returns:
            1. issue_status(str) or False(Bool)
        """

        issue_status = False
        issue_url = self.server + '/rest/api/2/issue/' + jiraid
        # Get the details of the the Jira ticket to find the issue status
        response = requests.get(issue_url, auth=self.auth)
        if response:
            issue_details = response.json()
            issue_status = issue_details['fields']['status']['name']
        else:
            print_error("Problem getting status of the Jira issue '{0}'".format(jiraid))
            print_error("JIRA Error code: ({0}), Error message: ({1})".
                        format(response.status_code, response.reason))

        return issue_status

    def set_jira_issue_status(self, jiraid, status):
        """
        Change the status of the jiraid
        :Arguments:
            1. jiraid(str) - Jira issue ID
            2. status(str/boolean) - Transition status(Ex. Resolved/Closed/Reopened)
        :Returns:
            1. oper_status(Boolean) - True/False
        """
        oper_status = True
        postdata = None
        headers = {"Content-Type": "application/json"}
        issue_trans_url = self.server + '/rest/api/2/issue/' + jiraid + "/transitions"
        resp_get_trans = requests.get(issue_trans_url, auth=self.auth)
        transitions = resp_get_trans.json()['transitions']
        for trans in transitions:
            if trans["to"]["name"].lower() == status.lower():
                postdata = """
                            {
                                "transition":{
                                    "id":""" + trans["id"] + """
                                }
                            }
                            """
        if postdata is None:
            print_warning("Cannot change status to " + str(status))
            available_statuses = str([trans["to"]["name"] for trans in transitions])
            print_warning("The available statuses are: {}".format(available_statuses))
            oper_status = False

        if oper_status is True:
            # Change the Jira issue status
            resp_change_trans = requests.post(issue_trans_url, auth=self.auth,
                                              headers=headers, data=postdata)
            if resp_change_trans and resp_change_trans.status_code == 204:
                print_info("Successfully changed the Jira issue status to "
                           "'{0}'".format(trans["to"]["name"]))
            else:
                print_error("Error while changing Jira issue status")
                print_error("JIRA Error code: ({0}), Error message: "
                            "({1})".format(resp_change_trans.status_code,
                                           resp_change_trans.reason))
                oper_status = False

        return oper_status
