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

"""API for operations related to REST Interfaces
Packages used = Requests (documentation available at http://docs.python-requests.org/) """
import re
import time
import os
import os.path
import json as JSON
from xml.dom.minidom import parseString
from Framework.Utils.testcase_Utils import pNote
import Framework.Utils as Utils
from Framework.ClassUtils.json_utils_class import JsonUtils
from Framework.Utils.print_Utils import print_error
from Framework.Utils import string_Utils


class WRest(object):
    """WRest class has methods required to interact
    with REST interfaces"""

    def __init__(self):
        """constructor for WRest """
        self.req = None
        self.import_requests()
        self.json_utils = JsonUtils()

    def import_requests(self):
        """Import the requests module """
        try:
            import requests
        except ImportError:
            pNote("Requests module is not installed"\
                       "Please install requests module to"\
                       "perform any activities related to REST interfaces", "error")

        else:
            self.req = requests

    def post(self, url, expected_response=None, data=None, auth=None, **kwargs):
        """ performs a http post method
        Please refer to the python-requests docs for parameter type support.
        api reference: https://github.com/kennethreitz/requests/blob/master/requests/api.py

        expected_response is an additional parameter that accepts a string as an input
        and also a list of strings
        Eg: "204"
            ["201", "202", "404", "302"]
        """
        pNote("Perform a http post", "info")
        try:
            response = self.req.post(url, data=data, auth=auth, **kwargs)
        except Exception as e:
            status, response = self.catch_expection_return_error(e, url)
        else:
            status = self.report_response_status(response.status_code, expected_response, 'post')
        return status, response

    def get(self, url, expected_response=None, params=None, auth=None, **kwargs):
        """performs a http get method
        Please refer to the python-requests docs for parameter type support.
        api reference: https://github.com/kennethreitz/requests/blob/master/requests/api.py

        expected_response is an additional parameter that accepts a string as an input
        and also a list of strings
        Eg: "204"
            ["201", "202", "404", "302"]
        """
        pNote("Perform a http get", "info")
        try:
            response = self.req.get(url, params=params, auth=auth, **kwargs)
        except Exception as e:
            status, response = self.catch_expection_return_error(e, url)
        else:
            status = self.report_response_status(response.status_code, expected_response, 'get')
        return status, response

    def put(self, url, expected_response=None, data=None, auth=None, **kwargs):
        """ performs a http put method
        Please refer to the python-requests docs for parameter type support.
        api reference: https://github.com/kennethreitz/requests/blob/master/requests/api.py

        expected_response is an additional parameter that accepts a string as an input
        and also a list of strings
        Eg: "204"
            ["201", "202", "404", "302"]
        """
        pNote("Perform a http put", "info")
        try:
            response = self.req.put(url, data=data, auth=auth, **kwargs)
        except Exception as e:
            status, response = self.catch_expection_return_error(e, url)
        else:
            status = self.report_response_status(response.status_code, expected_response, 'put')
        return status, response

    def patch(self, url, expected_response=None, data=None, auth=None, **kwargs):
        """ performs a http patch method
        Please refer to the python-requests docs for parameter type support.
        api reference: https://github.com/kennethreitz/requests/blob/master/requests/api.py

        expected_response is an additional parameter that accepts a string as an input
        and also a list of strings
        Eg: "204"
            ["201", "202", "404", "302"]
        """
        pNote("Perform a http patch", "info")
        try:
            response = self.req.patch(url, data=data, auth=auth, **kwargs)
        except Exception as e:
            status, response = self.catch_expection_return_error(e, url)
        else:
            status = self.report_response_status(response.status_code, expected_response, 'patch')
        return status, response

    def delete(self, url, expected_response=None, auth=None, **kwargs):
        """ performs a http delete method
        Please refer to the python-requests docs for parameter type support.
        api reference: https://github.com/kennethreitz/requests/blob/master/requests/api.py

        expected_response is an additional parameter that accepts a string as an input
        and also a list of strings
        Eg: "204"
            ["201", "202", "404", "302"]
        """
        pNote("Perform a http delete", "info")
        try:
            response = self.req.delete(url, auth=auth, **kwargs)
        except Exception as e:
            status, response = self.catch_expection_return_error(e, url)
        else:
            status = self.report_response_status(response.status_code, expected_response, 'delete')
        return status, response

    def options(self, url, expected_response=None, auth=None, **kwargs):
        """ performs a http options method
        Please refer to the python-requests docs for parameter type support.
        api reference: https://github.com/kennethreitz/requests/blob/master/requests/api.py

        expected_response is an additional parameter that accepts a string as an input
        and also a list of strings
        Eg: "204"
            ["201", "202", "404", "302"]
        """
        pNote("Perform a http options", "info")
        try:
            response = self.req.options(url, auth=auth, **kwargs)
        except Exception as e:
            status, response = self.catch_expection_return_error(e, url)
        else:
            status = self.report_response_status(response.status_code, expected_response, 'options')
        return status, response

    def head(self, url, expected_response=None, auth=None, **kwargs):
        """ performs a http head method
        Please refer to the python-requests docs for parameter type support.
        api reference: https://github.com/kennethreitz/requests/blob/master/requests/api.py

        expected_response is an additional parameter that accepts a string as an input
        and also a list of strings
        Eg: "204"
            ["201", "202", "404", "302"]
        """
        pNote("Perform a http head", "info")
        try:
            response = self.req.head(url, auth=auth, **kwargs)
        except Exception as e:
            status, response = self.catch_expection_return_error(e, url)
        else:
            status = self.report_response_status(response.status_code, expected_response, 'head')
        return status, response

    def cmp_response(self, response, expected_api_response,
                     expected_response_type, output_file,
                     generate_output_diff_file=True):
        """
            Performs the comparison between api response
            and expected_api_response

            arguments:
              1.response: API response getting from the data repository
              2.expected_api_response : expected response which needs
              to be compared given by the user.
              3.expected_response_type: The type of the expected response.
              It can be xml or json or text.
              4.output_file: The file in which the difference will be written
              if the responses are not equal.
              5.generate_output_diff_file: If the responses does not match,
              then generates an output file by writing the difference
              to the file by default and if it set to False then doesnot
              generate any file.
            returns:
                Returns True if the response matches with
                the expected response else False.
        """
        if response is not None and expected_api_response is not None:
            if expected_response_type in response.headers['Content-Type']:
                extracted_response = response.content
                extension = Utils.rest_Utils.get_extension_from_path(expected_api_response)
                if 'xml' in response.headers['Content-Type']:
                    try:
                        f = open(expected_api_response, 'r')
                    except IOError as exception:
                        if ".xml" == extension:
                            pNote("File does not exist in the"
                                  " provided file path", "error")
                            return False
                    status, sorted_file1, sorted_file2, output_file = \
                    Utils.xml_Utils.compare_xml(extracted_response, expected_api_response,
                                                output_file, sorted_json=False)

                elif 'json' in response.headers['Content-Type']:
                    try:
                        expected_api_response = JSON.load(open(expected_api_response, 'r'))
                        for key, value in expected_api_response.items():
                            # replacing the environment variable with value in the verify json
                            if "${" in value:
                                s_out = value.split("}")[0]
                                env_var = s_out.split(".")[-1]
                                env_value = os.getenv(env_var)
                                if env_value is None:
                                    print_error("The env var {} is not presented in environment variables so unable to "
                                                "fetch the value ".format(env_var))
                                    return False
                                pattern = r'(\$\{.*\})'
                                line = re.sub(pattern, env_value, value)
                                expected_api_response[key] = line
                    except IOError as exception:
                        if ".json" == extension:
                            pNote("File does not exist in the"
                                  " provided file path", "error")
                            return False
                        expected_api_response = JSON.loads(expected_api_response)
                    extracted_response = JSON.loads(extracted_response)
                    status = self.json_utils.write_json_diff_to_file(
                        extracted_response, expected_api_response, output_file)

                elif 'text' in response.headers['Content-Type']:
                    try:
                        f = open(expected_api_response, 'r')
                        expected_api_response = f.read()
                        f.close()
                    except IOError as exception:
                        if ".txt" == extension:
                            pNote("File does not exist in the"
                                  " provided file path", "error")
                            return False
                    status = Utils.string_Utils.text_compare(
                        extracted_response, expected_api_response, output_file)
                if not status:
                    if not generate_output_diff_file:
                        os.remove(output_file)
                    else:
                        pNote("api_response and expected_api_response do not match", "error")
                        pNote("The difference between the responses is saved here:{0}".format(output_file), "info")
                return status
            else:
                type_of_response = Utils.rest_Utils.\
                get_type_of_api_response(response)
                pNote("Expected response type is {0}".
                      format(expected_response_type), "info")
                pNote("API response type is {0}".
                      format(type_of_response), "info")
                pNote("api_response and expected_api_response"
                      " types do not match", "error")
                return False
        else:
            return False
            
    def cmp_content_response(self, datafile, system_name, response, 
                             expected_api_response, expected_response_type,
                             comparison_mode):
        """
            Performs the comparison between api response
            and expected_api_response

            arguments:
              1. datafile: Datafile of the test case
              2. system_name: Name of the system from the datafile

                  Pattern: String Pattern
                  Multiple Values: No
                  Max Numbers of Values Accepted: 1
                  Characters Accepted: All Characters
                  Other Restrictions: Should be valid system name
                  from the datafile
                  eg: http_system_1
              3. response: API response getting from the data repository
              4. expected_api_response : expected response which needs
                 to be compared given by the user.
              5. expected_response_type: The type of the expected response.
                 It can be xml or json or text.
              6. comparison_mode:
                 This is the mode in which you wish to compare
                 The supported comparison modes are
                 file, string, regex=expression, jsonpath=path, xpath=path
                 If you have given comparison_mode as file or string then 
                 whole comparison will take place
                 If you wish to check content of expected response and
                 if it is only one value_check pass it in either data file
                 or test case file 
                 If it is more than one value_check
                 then pass it in data file in comparison_mode and expected_api_response
                 tags under system
                 If it is xml response then you need to give xpath=path to it
                 If it is string response then you can pass regex=expressions
                 and you can leave expected_api_response empty
                 Ex for passing values in data file if it is json response
                 <comparison_mode>
                      <response_path>jsonpath=1.2.3</response_path>
                      <response_path>jsonpath=1.2</response_path>
                 </comparison_mode>
                 <expected_api_response>
                      <response_value>4</response_value>
                      <response_value>5</response_value>
                 </expected_api_response>
            returns:
                Returns True if the response matches with
                the expected response else False.
        """
        if expected_response_type in response.headers['Content-Type']:
            extracted_response = response.content
            if comparison_mode:
                path_list = [comparison_mode]
                responses_list = [expected_api_response]
            else:
                path_list, responses_list = Utils.xml_Utils.\
                   list_path_responses_datafile(datafile, system_name)
            if path_list:
                if "xml" in response.headers['Content-Type']:
                    status = Utils.xml_Utils.compare_xml_using_xpath(extracted_response,
                                                                     path_list, responses_list)
                elif "json" in response.headers['Content-Type']:
                    status = self.json_utils.compare_json_using_jsonpath(extracted_response,
                                                                         path_list, responses_list)
                else:
                    status = Utils.string_Utils.compare_string_using_regex(extracted_response,
                                                                           path_list)
            else:
                print_error("Please provide the values for comparison_mode and "
                            "expected_api_response")
                status = False
        else:
            type_of_response = Utils.rest_Utils.\
            get_type_of_api_response(response)
            pNote("Expected response type is {0}".
                  format(expected_response_type), "info")
            pNote("API response type is {0}".
                  format(type_of_response), "info")
            pNote("api_response and expected_api_response"
                  " types do not match", "error")
            status = False
        return status


    @classmethod
    def report_response_status(cls, status, expected_response, action):
        """Reports the response status of http
        actions with a print message to the user"""
        result = False
        if expected_response is None or expected_response is False or \
                expected_response == [] or expected_response == "":
            pattern = re.compile('^2[0-9][0-9]$')
            if pattern.match(str(status)) is not None:
                pNote("http {0} successful".format(action), "info")
                result = True
        elif isinstance(expected_response, list):
            for i in range(0, len(expected_response)):
                if str(status) == expected_response[i]:
                    pNote("http {0} successful".format(action), "info")
                    result = True
        elif str(status) == expected_response:
                pNote("http {0} successful".format(action), "info")
                result = True
        if not result:
            pNote("http {0} failed".format(action), "error")
        return result

    def catch_expection_return_error(self, exception_name, url):
        """ Function for catching expections thrown by REST operations
        """
        if exception_name.__class__.__name__ == self.req.exceptions.ConnectionError.__name__:
            pNote("Max retries exceeded with URL {0}. Failed to establish a new connection.".
                  format(url), "error")
            status = False
            response = None
        elif exception_name.__class__.__name__ == self.req.exceptions.InvalidURL.__name__:
            pNote("Could not process the request. {0} is somehow invalid.".format(url), "error")
            status = "ERROR"
            response = None
        elif exception_name.__class__.__name__ == self.req.exceptions.URLRequired.__name__:
            pNote("Could not process the request. A valid URL is required to make a request.".
                  format(url), "error")
            status = "ERROR"
            response = None
        elif exception_name.__class__.__name__ == self.req.exceptions.MissingSchema.__name__:
            pNote("Could not process the request. The URL schema (e.g. http or https) is missing.".
                  format(url), "error")
            status = "ERROR"
            response = None
        elif exception_name.__class__.__name__ == ValueError.__name__:
            pNote("Could not process the request. May be the value provided for timeout is "
                  "invalid or the schema is invalid.", "error")
            status = "ERROR"
            response = None
        elif exception_name.__class__.__name__ == self.req.exceptions.ConnectTimeout.__name__:
            pNote("The request timed out while trying to connect to the remote server.", "error")
            status = False
            response = None
        elif exception_name.__class__.__name__ == self.req.exceptions.ReadTimeout.__name__:
            pNote("The server did not send any data in the allotted amount of time.", "error")
            status = False
            response = None
        else:
            pNote("An Error Occurred: {0}".format(exception_name), "error")
            status = False
            response = None
        return status, response

    def check_connection(self, url, auth=None, **kwargs):
        """Internally uses the http options to check connection status.
        i.e.
         - If connection is successfull return a true
         - if any ConnectionError is detected returns a False."""

        try:
            status = False
            api_response = self.req.options(url, auth=auth, **kwargs)
            if not str(api_response).startswith('2') or \
            str(api_response).startswith('1'):
                pNote("Connection was successful, but there was"\
                      "problem accessing the resource: {0}".format(url), "info")
                status = False
        except self.req.ConnectionError:
            pNote("Connection to url is down: {0}".format(url), "debug")
        except self.req.HTTPError:
            pNote("Problem accessing resource: {0}".format(url), "debug")
        else:
            pNote("Connection to resource successfull: {0}".format(url), "debug")
            status = True
        return status

    def update_output_dict(self, system_name, api_response, request_id, status, i):
        """
            updates the output dictionary with status code and response object and text response
            and placing another dictionary inside output dict and updating it with status code and content type
            and extracted content from object and response object
        """
        output_dict = {}

        pNote("Total number of requests in this step: {0}".format(i))
        pNote("This is request number: {0}".format(i))
        pNote("status: {0}".format(status), "debug")
        pNote("api_response: {0}".format(api_response), "debug")

        output_dict["{0}_api_response".format(system_name)] = api_response
        output_dict["{0}_api_response_object".format(system_name)] = api_response

        if api_response is not None:
            text = api_response.text
            status_code = api_response.status_code
            headers = api_response.headers
            output_response = self.get_output_response(api_response)
            history = api_response.history
        else:
            text = None
            status_code = None
            headers = None
            output_response = None
            history = None

        output_dict["{0}_status".format(system_name)] = status_code
        pNote("api_response_history: {0}".format(history), "debug")

        if request_id is not None:
            output_dict["{0}_{1}_api_response_object_{2}".format(system_name, request_id, i)] = api_response
            output_dict["{0}_{1}_api_response_text_{2}".format(system_name, request_id, i)] = text
            output_dict["{0}_{1}_api_response_status_{2}".format(system_name, request_id, i)] = status_code
            output_dict["{0}_{1}_api_response_headers_{2}".format(system_name, request_id, i)] = headers
            output_dict["{0}_{1}_api_response_content_{2}".format(system_name, request_id, i)] = output_response

            output_dict["{0}_{1}_api_response_object".format(system_name, request_id)] = api_response
            output_dict["{0}_{1}_api_response_text".format(system_name, request_id)] = text
            output_dict["{0}_{1}_api_response_status".format(system_name, request_id)] = status_code
            output_dict["{0}_{1}_api_response_headers".format(system_name, request_id)] = headers
            output_dict["{0}_{1}_api_response_content".format(system_name, request_id)] = output_response
        else:
            output_dict["{0}_api_response_object_{1}".format(system_name, i)] = api_response
            output_dict["{0}_api_response_text_{1}".format(system_name, i)] = text
            output_dict["{0}_api_response_status_{1}".format(system_name, i)] = status_code
            output_dict["{0}_api_response_headers_{1}".format(system_name, i)] = headers
            output_dict["{0}_api_response_content_{1}".format(system_name, i)] = output_response

            output_dict["{0}_api_response_object".format(system_name)] = api_response
            output_dict["{0}_api_response_text".format(system_name)] = text
            output_dict["{0}_api_response_status".format(system_name)] = status_code
            output_dict["{0}_api_response_headers".format(system_name)] = headers
            output_dict["{0}_api_response_content".format(system_name)] = output_response

        return output_dict

    @staticmethod
    def get_output_response(api_response):
        """
        This method is used to convert the given api_response in the form of text / xml / json
        Params:
            api_response : api_response
        Returns:
            ouptut_response in the form of text/xml/json
        """
        if api_response is not None:
            try:
                output_response = parseString("".join(api_response.text))
            except:
                try:
                    JSON.loads(api_response.text)
                except:
                    output_response = api_response.text.encode('ascii', 'ignore')
                    pNote("api_response Text: \n {0}".format(output_response))
                else:
                    output_response = api_response.json()
                    pNote("api_response (JSON format): \n {0}".
                          format(JSON.dumps(output_response, indent=4)))
            else:
                pNote("api_response (XML format): \n {0}".
                      format(output_response.toprettyxml(newl='\n')))
        else:
            output_response = None
        return output_response

    def try_until_resource_status(self, url, auth=None, status="up", trials=5, **kwargs):
        """  Tries to connect to the resource until resource
        reaches the specified status. Tries for the number mentioned in the
        trials parameter (default=5)
        waits for a time of 30 seconds between trials
        """
        final_status = False
        if status.upper() == "UP":
            expected_result = True
        elif status.upper() == "DOWN":
            expected_result = False

        i = 1
        while i <= trials:
            pNote("Trial: {0}".format(i), "info")
            result = self.check_connection(url, auth, **kwargs)
            if result == expected_result:
                final_status = True
                break
            i += 1
            time.sleep(10)
        return final_status