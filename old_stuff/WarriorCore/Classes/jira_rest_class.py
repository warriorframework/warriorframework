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


import urllib2, urllib
import json,base64
import sys,re
import random
import Tools, os
from Framework.Utils.print_Utils import print_error, print_info, print_warning
from Framework.Utils import xml_Utils
from Framework.Utils.testcase_Utils import pNote

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
        self.append = True if str(credentials['append_log']).lower().strip() == "true" else False
        self.status = True
        self.project_key = credentials['project_key']
        self.assignee = credentials['assignee']

    def check_jira_issue(self, issue_summary, headers):
        """
            check jira server for any existing issue with the same summary(title)
            :para,:
                issue_summary: issue title
                headers: auth header
            :return:
                the existing issue key or False if not found
        """
        fetchuri = self.server
        parsed_summary = issue_summary.replace("[", "\\\\[")
        parsed_summary = parsed_summary.replace("]", "\\\\]")
        postdata_url=fetchuri+'/rest/api/2/search/?jql=summary~'+urllib.quote_plus('\"' + parsed_summary + '\"')
        request=urllib2.Request(str(postdata_url), None, headers)
        try:
            handler = urllib2.urlopen(request)
            extension=json.loads(handler.read())
            for issue in extension["issues"]:
                if issue_summary[:-2].strip() == issue["fields"]["summary"].strip():
                    return issue["key"]
                else:
                    # partially match title
                    pass
            return False

        except Exception as e:
            pNote("Problem checking JIRA issue.","error")
            pNote("JIRA Error Code: ({0})".format(e),"error")
            exit(1)

    def update_jira_issue(self, jiraid, status):
        """
            Update the jira issue using the jiraid
            Transition to correct issue status based on warrior status
        """
        issue_url = self.server + '/rest/api/2/issue/' + jiraid + "/transitions"
        status_map = {"true":"pass", "false":"fail"}
        status = status_map[str(status).lower()] if str(status).lower() in status_map else str(status).lower()

        # Build Auth information
        credential_handler=urllib2.HTTPPasswordMgrWithDefaultRealm()
        credential_handler.add_password(None, issue_url, self.username, self.password)
        auth = urllib2.HTTPBasicAuthHandler(credential_handler)
        userpassword=self.username+":"+self.password
        password=base64.b64encode(userpassword)
        # Create an Authentication handler
        opener = urllib2.build_opener(auth)
        urllib2.install_opener(opener)
        opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))

        # Find the correct jira system
        if self.jiraproj is not None:
            element = xml_Utils.getElementWithTagAttribValueMatch(self.jira_template_xml,
                                                                  'system',
                                                                  'name',
                                                                  self.jiraproj)
        else:
            element = xml_Utils.getElementWithTagAttribValueMatch(self.jira_template_xml, 'system',
                                                                  'default', "true")

        # Find the correct issue type and status
        if element is not None and element is not False:
            system_data = xml_Utils.get_children_as_dict(element)

            issue = None
            for x in system_data["issue_type"]:
                if x["type"] == ["test"]:
                    issue = x
            if issue is None:
                for x in system_data["issue_type"]:
                    if x["type"] == ["default"]:
                        issue = x

            postdata = None
            if issue is not None and status in issue.keys():
                # Get the correct transition for changing status
                headers = {"Authorization" : "Basic " + password}
                request = urllib2.Request(str(issue_url), None, headers)
                handler = urllib2.urlopen(request)
                transitions = json.loads(handler.read())
                for trans in transitions["transitions"]:
                    if trans["to"]["name"].lower() == issue[status][0].lower():
                        postdata = """
                                    {
                                        "transition":{
                                            "id":""" + trans["id"] + """
                                        }
                                    }
                                    """

                if postdata is None:
                    print_info("Cannot change status to " + str(issue[status][0]))
                    print_info("The available status are: " + str([trans["to"]["name"] for trans in transitions["transitions"]]))
                    return False
            else:
                print_error("Cannot find the correct issue type, unable to update jira status")
                return False

            # Update status
            headers = {"Authorization" : "Basic " + password,"Content-Type": "application/json"}
            request = urllib2.Request(str(issue_url), postdata, headers)
            try:
                handler = urllib2.urlopen(request)
                if handler.getcode() == 204:
                    print_info("Successfully update issue status")
                    return True
                else:
                    print_error("Error occurs while updating issue status, error code: " + str(handler.getcode()))
            except Exception as e:
                print_info("Error occurs while updating issue status")
                print_info(e)
        else:
            msg = "There is no project with name: '{0}' "\
            "in the jira config file: '{1}'".format(self.jiraproj, "Tools/jira/jira_config.xml")
            print_warning(msg)
        return False

    def create_jira_issue(self, issue_summary, issue_description, issue_type='Bug'):
        """Function to Create jira Ticket using JIRA rest API"""

        issue_summary=issue_summary.replace('"', " ")
        issue_description=issue_description.replace('"', "-")
        # if description has any \n in it, it will cause a 400 http bad request error and unable to upload the issue
        # issue_description=issue_description.replace('\n', "************")
        fetchuri = self.server
        postdata_url=fetchuri+'/rest/api/2/issue/'
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
        credential_handler=urllib2.HTTPPasswordMgrWithDefaultRealm()
        credential_handler.add_password(None,postdata_url,self.username,self.password)
        auth = urllib2.HTTPBasicAuthHandler(credential_handler)
        userpassword=self.username+":"+self.password
        password=base64.b64encode(userpassword)
        #Create an Authentication handler
        opener = urllib2.build_opener(auth)
        urllib2.install_opener(opener)
        opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
        #Create a POST request
        headers={"Authorization" : "Basic "+password,"Content-Type": "application/json"}
        existed = self.check_jira_issue(issue_summary, headers)
        if not existed:
            request=urllib2.Request(str(postdata_url),postdata,headers)
            try:
                handler = urllib2.urlopen(request)
                extension=json.loads(handler.read())
                issue_id = str(extension['key'])
                print_info("JIRA Issue Created. Issue-Id: {0}".format(issue_id))
                return issue_id
            except Exception as e:
                pNote("Problem creating JIRA issue.","error")
                pNote("JIRA Error Code: ({0})".format(e),"error")
                exit(1)
        else:
            if self.append:
                print_info("Issue already exist - " + str(existed) + ". Will update log")
                return existed
            else:
                print_info("Issue already exist - " + str(existed) + ". Will not update log")
                return None

    def upload_logfile_to_jira_issue(self, issue_id, logfile, attachment_name=None):
        """Function to attach logs to jira Ticket using JIRA rest API"""

        fetchuri = self.server
        postdata_url=fetchuri+'/rest/api/2/issue/'+issue_id+'/attachments'
        credential_handler=self.username+":"+self.password
        password=base64.b64encode(credential_handler)
        boundary = '----------%s' % ''.join(random.sample('0123456789abcdef', 15))
        post_data = []
        post_data.append('--%s' % boundary)
        post_data.append('Content-Disposition: form-data; name="file"; filename="%s"' % str(logfile.split("/")[-1]))
        post_data.append('Content-Type: %s' % 'text/plain')
        post_data.append('')
        post_data.append(open(logfile, 'r').read())
        post_data.append('--%s--' % boundary)
        post_data.append('')   
        body = '\r\n'.join(post_data)
        req = urllib2.Request(str(postdata_url), body)
        req.add_header("X-Atlassian-Token", "nocheck")
        req.add_header("Authorization","Basic "+password)
        req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
        try:
            handler = urllib2.urlopen(req)
            extension=json.loads(handler.read())
            print_info("Log File {0} uploaded to Issue-Id: {1}".format(logfile.split("/")[-1],issue_id))
        except urllib2.HTTPError, e:
            pNote("Problem attaching logs to JIRA issue {0}".format(issue_id),"error")
            pNote("JIRA Error code: ({0})".format(e.code),"error")
            exit(1)


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
                if issue_id is not None:
                    # The cases when issue_id is None are 1) error 2) issue exist and user chose not to append log
                    issue_id_list.append(issue_id)

        print_info("Issue List: {0}".format(issue_id_list))
        return issue_id_list

    @classmethod
    def get_issue_description(cls, json_file):
        """Takes a warrior issue json file as input and
        forms the summary, description for the jira issue to be created"""

        tc_name, keyword, step_num, issue_summary = (None,)*4
        step = keyword
        desc = '-'*18 +' Description '+'-'*18+  '\\n'
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
            print_error("all/one of tc_name, keyword, step_num is missing.."\
                        "could not create jira ticket without these details")
        else:
            issue_summary = "TC-"+ str(tc_name).strip() + ":" + "Keyword-" + str(keyword).strip()\
                     + ":" + "Step{0}.".format(str(step_num)) + str(step).strip() + "[FAILED]" + '\\n'

            desc = desc + '\\n' + issue_summary + '\\n'  + '\\n' + p_header + '\\n'
            for attr in json_data:
                for key, value in attr.items():
                    key = key.replace('\n', "\\n")
                    value = value.replace('\n', "\\n")
                    desc = desc + str(key) +':' + str(value) +'\\n'

            desc = '\\n' + desc + '\\n' +  "-Attached logfiles" + '\\n' +\
                    "-Attached actual testcase for steps to reproduce" + '\\n'
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
            msg = "There is no project with name: '{0}' "\
            "in the jira config file: '{1}'".format(system_name, "Tools/jira/jira_config.xml")
            print_warning(msg)
            return False

