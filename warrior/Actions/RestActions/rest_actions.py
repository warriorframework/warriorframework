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

import os
import re
import json
import Framework.Utils as Utils
from Framework.Utils.file_Utils import getAbsPath
from Framework.Utils import config_Utils, file_Utils, print_Utils
from Framework.Utils.data_Utils import get_object_from_datarepository
from Framework.ClassUtils.rest_utils_class import WRest
from Framework.Utils.testcase_Utils import pNote, pSubStep, \
    report_substep_status
# pylint: disable-msg=too-many-arguments

"""This is the actions file, keywords are programmed here
"""


class RestActions(object):
    """ Rest class"""

    def __init__(self):
        """ constructor """
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.tc_path = Utils.config_Utils.tc_path
        self.rest_object = WRest()

    def perform_http_post(self, system_name, variable_config=None,
                          request_id=None, url=None, data=None,
                          expected_response=None,
                          headers=None, user=None, password=None,
                          allow_redirects=None, timeout=None,
                          json=None, cookies=None, files=None, proxies=None,
                          verify=None, stream=None, cert=None, var_sub=None):
        """Perform a http post actions and get the response
        This keyword uses the warrior recommended Input datafile format for rest

        GLOSSARY

        ** string pattern **
        This pattern basically accepts every alphabet,
        number, and special character.
        Multiple values are accepted only where specified.
        Separator would be specified if multiple values are accepted.
        Other restrictions would be specified wherever needed


        ** dictionary pattern **

        This pattern does not accept multiple
        values for a single key.
        Key-Value pairs are separated by ;
        Key and the corresponding value is separated by =

        Eg. key1=value1; key2=value2; key3=value3


        ** dict-tuple pattern **

        This pattern accepts multiple values for every key.
        Key-Value pairs are separated by ,
        Key and the corresponding value/s is/are separated by =
        Values are separated by ;

        Eg. key1=value1;value2;value3, key2=value4;value5;value6, key3=value6;value7


        ** tuple pattern **

        This pattern accepts groups of elements.
        Groups are separated by commas
        Elements inside the group are separated by ;
        Groups are enclosed inside parenthesis
        Maximum number of elements inside a group: 2

        (element_11; element_12),(element_21; element_22),(element_31; element_32)


        ** dict-in-tuple pattern **
        This pattern accepts groups of elements.
        Only in the 3rd position, a dictionary patten is accepted.
        Maximum number of elements inside a group: 3
        Maximum number of elements inside the dictionary patten: No restrictions
        The first two place do not accept dictionary pattern.
        Groups are separated by ,
        Groups are enclosed inside parenthesis
        The dictionary patten inside the group is also enclosed in a parenthesis
        Elements inside a group are separated by ;
        Dictionary pattern accepted in the third position follows the specified
        dictionary pattern

        (element_11;element_12;(key_11=value_11; key_12:value_12)),
        (element_21;element_22;(key_21=value_21)),
        (element_31;element_32;(key_31=value_31; key_32:value_32; key_33=value_33; key_34:value_34))

        :Arguments:
            1. system_name: Name of the system from the datafile

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Other Restrictions: Should be valid system name from the datafile

                eg: http_system_1

            2. url: Represents URL/ip address that is supposed to be tested

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: http://httpbin.org

            3. params: Represents parameters that need to be sent along with the URL

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: postId=1; comments=5

            4. data: Represents data to be posted. HTTP GET does NOT accept this argument.

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Encoding: Unicode

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: userId=1;id=1;title=Changed Post;body=New Comment
                    \\u0075\\u0073\\u0065\\u0072\\u0049\\u0064\\u003d\\u0031\\u003b\\u0069
                    \\u0064\\u003d\\u0031\\u003b\\u0074
                    path/to/file/containing/data

            5. json: Represents the JSON data that goes into the body of the request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Format: Valid JSON format

                eg: {"postId":"1", "comments":"This is a new comment"}

            6. headers: Represents the headers sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: Content-Type=text; Date=04/21/2016; Allow=whatever_you_want_to_allow

            7. cookies: Represents the cookies sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: cookie=cookie_name; details=more_details_abput_the_cookie
                    path/to/file/containing/cookie/details

            8. files: Lets User accomplish multipart encoding upload

                Pattern: string pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="path_to_file1, path_to_file2, path_to_file3"/>

                Pattern: dict-tuple pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="file_group_name=path_to_file1, path_to_file2,
                                                                  path_to_file4, path_to_file5"/>

                Pattern: tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="(path_to_file1;content_type),
                                                  (path_to_file2;content_type),
                                                  (path_to_file3;content_type)"/>

                Pattern: dict-in-tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values inside the Dictionary Pattern: No Restrictions
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files"
                              value="(path_to_file1;content_type;(custom_header_1=value1;
                                                                  custom_header_2:value2)),
                                     (path_to_file2;content_type;(custom_header_1=value1)),
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3))"/>

                eg: <argument name="files"
                              value="(path_to_file1;content_type),
                                     path_to_file2,
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2),
                                     (path_to_file4;content_type),
                                     (path_to_file5;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3)),
                                     path_to_file6, path_to_file_7"/>

            9. user: Represents the username that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: Sanika

            10. password: Represents the password that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: password

            11. timeout: Represents the time barrier in which the request should be completed
                         If 2 values are given, the first value would be treated as a constraint for
                         sending the request, the second would be treated as a constraint for
                         receiving the response. If only one value is given, it would be treated as
                         constraint for sending the request and receiving a response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: Numerical Characters - Int or Float

                eg: 0.5, 0.75
                    0.6

            12. allow_redirects: Allows or disallows redirection

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                eg: yes

            13. proxies: Allows the User to set up proxies for ip addresses

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: http=157.126.12.196:8081; https:157.126.12.144:80

            14. verify: Allows user to enable or disable authentication

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path to a .pem file

                eg: path/to/CA_BUNDLE
                    no

            15. stream: Allows user to enable or disable immediate data downloading

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'no'

                eg: yes

            16. cert: Allows user to send  his/her own certificate

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: All Characters

                Other Restrictions:
                Both the inputs should be valid file paths.
                Input 1 should be a file path to the certificate file
                If the file specified in Input 1 contains the key, Input 2 is not necessary
                If the key is stored in a different file, Input 2 should contain the path
                to that file.

                eg: path/to/certificate/file, path/to/key/file
                    path/to/certificate/file/which/contains/the/key

            17. expected_response: User specified expected response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: Numerical Characters - Integers only
                Default: The entire 200 series of HTTP Responses

                eg: 200, 302, 404
                    200

            18. request_id:  A unique request ID for this request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: 01

            19. variable_config: The variable config file that contains
                variables that need to be substituted into the json that is
                being passed to this request. This can either be a relative or
                an absolute path.

                Eg: ../Config_files/var_config.xml
                    /home/user/warrior_main/Warrior/Warriorspace/Config_files/var_config.xml

            20. var_sub: the pattern [var_sub] in the json will get substituted
                with this value.

        :Returns:
            1. <system_name>_status(boolean) = status code of the http post
            2. <system_name>_api_response = the entire response object of the
               http request

            Note: The Request Number is applicable when variable substitution in
            JSON is being used. As variables get substituted in JSON, multiple
            JSONs are formed and each JSON is sent as a separate request. These
            requests are differentiated by adding add "request_number" which is
            basically the serial number of those requests.

            3. The entire response object of the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_object
               <system_name>_api_response_object_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_object
               <system_name>_<request_id>_api_response_object_<request_number>

            4. The response text (in text format) returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_text
               <system_name>_api_response_text_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_text
               <system_name>_<request_id>_api_response_text_<request_number>

            5. The status code returned by the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_status
               <system_name>_api_response_status_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_status
               <system_name>_<request_id>_api_response_status_<request_number>

            6. The content_type of the response returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_content_type
               <system_name>_api_response_content_type_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content_type
               <system_name>_<request_id>_api_response_content_type_<request_number>

            7. The extracted response returned from the response object (stored
               in the format that it is returned in - JSON, XML, Text) is stored
               as:

            If request_id has not been provided:
               <system_name>_api_response_content
               <system_name>_api_response_content_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content
               <system_name>_<request_id>_api_response_content_<request_number>
        """
        arguments = {'system_name': system_name, 'variable_config': variable_config,
                     'request_id': request_id, 'url': url, 'data': data,
                     'expected_response': expected_response, 'headers': headers,
                     'user': user, 'password': password, 'allow_redirects': allow_redirects,
                     'timeout': timeout, 'json': json, 'cookies': cookies,
                     'files': files, 'proxies': proxies, 'verify': verify,
                     'stream': stream, 'cert': cert, 'var_sub': var_sub}
        wdesc = "Perform a http post"
        pSubStep(wdesc)
        pNote(system_name)
        output_dict = {}
        result = True

        for element in arguments:
            if element in ["json", "data", "variable_config"] and \
                    arguments[element] and arguments[element] is not None:
                arguments[element] = Utils.rest_Utils.\
                    check_ext_get_abspath(arguments[element], self.tc_path)

        credentials = Utils.data_Utils.\
            get_user_specified_tag_values_in_tc(self.datafile, **arguments)

        if credentials["variable_config"] and  \
           credentials["variable_config"] is not None:
            credentials["variable_config"] = Utils.rest_Utils.\
                check_ext_get_abspath(credentials["variable_config"],
                                      os.path.dirname(self.datafile))

        for element in credentials:
            credentials = Utils.rest_Utils.\
                resolve_credentials_for_rest(credentials, element,
                                             self.datafile, system_name)
        credentials["auth"] = (credentials['user'], credentials['password'])

        credentials, popped_args = Utils.rest_Utils.\
            remove_invalid_req_args(credentials, ["user", "password",
                                                  "request_id",
                                                  "variable_config",
                                                  "var_sub", "json"])

        pNote("url is: {0}".format(credentials['url']))
        for i in range(0, len(popped_args["json"])):
            if popped_args["json"][i] != "Error":
                credentials["json"] = popped_args["json"][i]
                for key in credentials:
                    pNote("Sending argument '{0}': {1}"
                          .format(key, credentials[key]))
                status, api_response = self.rest_object.post(**credentials)
                result = result and status
                output_dict.update(self.rest_object.
                                   update_output_dict(system_name,
                                                      api_response, request_id, status, i+1))
            else:
                pNote("Request not sent.", "error")
                status = False
                result = result and status
        if result:
            msg = "http post successful"
        else:
            msg = "http post failed"
        pNote(msg)
        report_substep_status(result)
        return result, output_dict

    def perform_http_get(self, system_name, variable_config=None,
                         request_id=None, url=None,
                         params=None, expected_response=None,
                         headers=None, user=None, password=None,
                         allow_redirects=None, timeout=None,
                         json=None, cookies=None, files=None, proxies=None,
                         verify=None, stream=None, cert=None, var_sub=None):
        """
        Perform a http post actions and get the response
        This keyword uses the warrior recommended Input datafile format for rest

        Please refer to perform_http_post keyword documentation to understand all
        patterns

        :Arguments:
            1. system_name: Name of the system from the datafile

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Other Restrictions: Should be valid system name from the datafile

                eg: http_system_1

            2. request_id: A unique request ID for this request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: 01

            3. url: Represents URL/ip address that is supposed to be tested

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: http://httpbin.org

            4. params: Represents parameters that need to be sent along with the URL

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: postId=1; comments=5

            5. json: Represents the JSON data that goes into the body of the request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Format: Valid JSON format

                eg: {"postId":"1", "comments":"This is a new comment"}

            6. headers: Represents the headers sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: Content-Type=text; Date=04/21/2016; Allow=whatever_you_want_to_allow

            7. cookies: Represents the cookies sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: cookie=cookie_name; details=more_details_abput_the_cookie
                    path/to/file/containing/cookie/details

            8. files: Lets User accomplish multipart encoding upload

                Pattern: string pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="path_to_file1, path_to_file2, path_to_file3"/>

                Pattern: dict-tuple pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="file_group_name=path_to_file1,
                                                    path_to_file2, path_to_file4, path_to_file5"/>

                Pattern: tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="(path_to_file1;content_type),
                                                  (path_to_file2;content_type),
                                                  (path_to_file3;content_type)"/>

                Pattern: dict-in-tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values inside the Dictionary Pattern: No Restrictions
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files"
                              value="(path_to_file1;content_type;(custom_header_1=value1;
                                                                  custom_header_2:value2)),
                                     (path_to_file2;content_type;(custom_header_1=value1)),
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3))"/>

                eg: <argument name="files"
                              value="(path_to_file1;content_type),
                                     path_to_file2,
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2),
                                     (path_to_file4;content_type),
                                     (path_to_file5;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3)),
                                     path_to_file6, path_to_file_7"/>

            9. user: Represents the username that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: Sanika

            10. password: Represents the password that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: password

            11. timeout: Represents the time barrier in which the request should be completed
                         If 2 values are given, the first value would be treated as a constraint for
                         sending the request, the second would be treated as a constraint for
                         receiving the response. If only one value is given, it would be treated as
                         constraint for sending the request and receiving a response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: Numerical Characters - Int or Float

                eg: 0.5, 0.75
                    0.6

            12. allow_redirects: Allows or disallows redirection

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                eg: yes

            13. proxies: Allows the User to set up proxies for ip addresses

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: http=157.126.12.196:8081; https:157.126.12.144:80

            14. verify: Allows user to enable or disable authentication

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path to a .pem file

                eg: path/to/CA_BUNDLE
                    no

            15. stream: Allows user to enable or disable immediate data downloading

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'no'

                eg: yes

            16. cert: Allows user to send  his/her own certificate

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: All Characters

                Other Restrictions:
                Both the inputs should be valid file paths.
                Input 1 should be a file path to the certificate file
                If the file specified in Input 1 contains the key, Input 2 is not necessary
                If the key is stored in a different file, Input 2 should contain the path
                to that file.

                eg: path/to/certificate/file, path/to/key/file
                    path/to/certificate/file/which/contains/the/key

            17. expected_response: User specified expected response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: Numerical Characters - Integers only
                Default: The entire 200 series of HTTP Responses

                eg: 200, 302, 404
                    200

            18. variable_config: The variable config file that contains
                variables that need to be substituted into the json that is
                being passed to this request. This can either be a relative or
                an absolute path.

                Eg: ../Config_files/var_config.xml
                    /home/user/warrior_main/Warrior/Warriorspace/Config_files/var_config.xml

            19. var_sub: the pattern [var_sub] in the json will get substituted
                with this value.

        :Returns:
            1. <system_name>_status(boolean) = status code of the http get
            2. <system_name>_api_response = the entire response object of the
               http request

            Note: The Request Number is applicable when variable substitution in
            JSON is being used. As variables get substituted in JSON, multiple
            JSONs are formed and each JSON is sent as a separate request. These
            requests are differentiated by adding add "request_number" which is
            basically the serial number of those requests.

            3. The entire response object of the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_object
               <system_name>_api_response_object_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_object
               <system_name>_<request_id>_api_response_object_<request_number>

            4. The response text (in text format) returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_text
               <system_name>_api_response_text_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_text
               <system_name>_<request_id>_api_response_text_<request_number>

            5. The status code returned by the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_status
               <system_name>_api_response_status_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_status
               <system_name>_<request_id>_api_response_status_<request_number>

            6. The content_type of the response returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_content_type
               <system_name>_api_response_content_type_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content_type
               <system_name>_<request_id>_api_response_content_type_<request_number>

            7. The extracted response returned from the response object (stored
               in the format that it is returned in - JSON, XML, Text) is stored
               as:

            If request_id has not been provided:
               <system_name>_api_response_content
               <system_name>_api_response_content_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content
               <system_name>_<request_id>_api_response_content_<request_number>

        """
        arguments = {'system_name': system_name, 'variable_config': variable_config,
                     'request_id': request_id, 'url': url, 'params': params,
                     'expected_response': expected_response, 'headers': headers,
                     'user': user, 'password': password, 'allow_redirects': allow_redirects,
                     'timeout': timeout, 'json': json, 'cookies': cookies,
                     'files': files, 'proxies': proxies, 'verify': verify,
                     'stream': stream, 'cert': cert, 'var_sub': var_sub}
        wdesc = "Perform a http get to the url"
        pSubStep(wdesc)
        pNote(system_name)
        output_dict = {}
        result = True

        for element in arguments:
            if element in ["json", "data", "variable_config"] and \
                    arguments[element] and arguments[element] is not None:
                arguments[element] = Utils.rest_Utils.\
                    check_ext_get_abspath(arguments[element], self.tc_path)

        credentials = Utils.data_Utils.\
            get_user_specified_tag_values_in_tc(self.datafile, **arguments)

        if credentials["variable_config"] and  \
           credentials["variable_config"] is not None:
            credentials["variable_config"] = Utils.rest_Utils.\
                check_ext_get_abspath(credentials["variable_config"],
                                      os.path.dirname(self.datafile))

        for element in credentials:
            credentials = Utils.rest_Utils.\
                resolve_credentials_for_rest(credentials, element,
                                             self.datafile, system_name)
        credentials["auth"] = (credentials['user'], credentials['password'])

        credentials, popped_args = Utils.rest_Utils.\
            remove_invalid_req_args(credentials, ["user", "password",
                                                  "request_id",
                                                  "variable_config",
                                                  "var_sub", "json"])

        pNote("url is: {0}".format(credentials['url']))
        for i in range(0, len(popped_args["json"])):
            if popped_args["json"][i] != "Error":
                credentials["json"] = popped_args["json"][i]
                for key in credentials:
                    pNote("Sending argument '{0}': {1}"
                          .format(key, credentials[key]))
                status, api_response = self.rest_object.get(**credentials)
                result = result and status
                output_dict.update(self.rest_object.
                                   update_output_dict(system_name,
                                                      api_response, request_id, status, i+1))
            else:
                pNote("Request not sent.", "error")
                status = False
                result = result and status
        if result:
            msg = "http get successful"
        else:
            msg = "http get failed"
        pNote(msg)
        report_substep_status(result)
        return result, output_dict

    def perform_http_put(self, system_name, variable_config=None,
                         request_id=None, data=None,
                         url=None, expected_response=None,
                         headers=None, user=None, password=None,
                         allow_redirects=None, timeout=None,
                         json=None, cookies=None, files=None, proxies=None,
                         verify=None, stream=None, cert=None, var_sub=None):
        """
        Perform a http post actions and get the response
        This keyword uses the warrior recommended Input datafile format for rest

        Please refer to perform_http_post keyword documentation to understand all
        patterns

        :Arguments:
            1. system_name: Name of the system from the datafile

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Other Restrictions: Should be valid system name from the datafile

                eg: http_system_1

            2. request_id: A unique request ID for this request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: 01

            3. url: Represents URL/ip address that is supposed to be tested

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: http://httpbin.org

            4. params: Represents parameters that need to be sent along with the URL

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: postId=1; comments=5

            5. data: Represents data to be posted. HTTP GET does NOT accept this argument.

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Encoding: Unicode

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: userId=1;id=1;title=Changed Post;body=New Comment
                    \\u0075\\u0073\\u0065\\u0072\\u0049\\u0064\\u003d\\u0031\\u003b\\u0069
                    \\u0064\\u003d\\u0031\\u003b\\u0074
                    path/to/file/containing/data

            6. json: Represents the JSON data that goes into the body of the request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Format: Valid JSON format

                eg: {"postId":"1", "comments":"This is a new comment"}

            7. headers: Represents the headers sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: Content-Type=text; Date=04/21/2016; Allow=whatever_you_want_to_allow

            8. cookies: Represents the cookies sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: cookie=cookie_name; details=more_details_abput_the_cookie
                    path/to/file/containing/cookie/details

            9. files: Lets User accomplish multipart encoding upload

                Pattern: string pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="path_to_file1, path_to_file2, path_to_file3"/>

                Pattern: dict-tuple pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="file_group_name=path_to_file1,
                                                    path_to_file2, path_to_file4, path_to_file5"/>

                Pattern: tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="(path_to_file1;content_type),
                                                  (path_to_file2;content_type),
                                                  (path_to_file3;content_type)"/>

                Pattern: dict-in-tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values inside the Dictionary Pattern: No Restrictions
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files"
                              value="(path_to_file1;content_type;(custom_header_1=value1;
                                                                  custom_header_2:value2)),
                                     (path_to_file2;content_type;(custom_header_1=value1)),
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3))"/>

                eg: <argument name="files"
                              value="(path_to_file1;content_type),
                                     path_to_file2,
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2),
                                     (path_to_file4;content_type),
                                     (path_to_file5;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3)),
                                     path_to_file6, path_to_file_7"/>

            10. user: Represents the username that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: Sanika

            11. password: Represents the password that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: password

            12. timeout: Represents the time barrier in which the request should be completed
                         If 2 values are given, the first value would be treated as a constraint for
                         sending the request, the second would be treated as a constraint for
                         receiving the response. If only one value is given, it would be treated as
                         constraint for sending the request and receiving a response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: Numerical Characters - Int or Float

                eg: 0.5, 0.75
                    0.6

            13. allow_redirects: Allows or disallows redirection

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                eg: yes

            14. proxies: Allows the User to set up proxies for ip addresses

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: http=157.126.12.196:8081; https:157.126.12.144:80

            15. verify: Allows user to enable or disable authentication

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path to a .pem file

                eg: path/to/CA_BUNDLE
                    no

            16. stream: Allows user to enable or disable immediate data downloading

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'no'

                eg: yes

            17. cert: Allows user to send  his/her own certificate

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: All Characters

                Other Restrictions:
                Both the inputs should be valid file paths.
                Input 1 should be a file path to the certificate file
                If the file specified in Input 1 contains the key, Input 2 is not necessary
                If the key is stored in a different file, Input 2 should contain the path
                to that file.

                eg: path/to/certificate/file, path/to/key/file
                    path/to/certificate/file/which/contains/the/key

            18. expected_response: User specified expected response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: Numerical Characters - Integers only
                Default: The entire 200 series of HTTP Responses

                eg: 200, 302, 404
                    200

            19. variable_config: The variable config file that contains
                variables that need to be substituted into the json that is
                being passed to this request. This can either be a relative or
                an absolute path.

                Eg: ../Config_files/var_config.xml
                    /home/user/warrior_main/Warrior/Warriorspace/Config_files/var_config.xml

            20. var_sub: the pattern [var_sub] in the json will get substituted
                with this value.

        :Returns:
            1. <system_name>_status(boolean) = status code of the http put
            2. <system_name>_api_response = the entire response object of the
               http request

            Note: The Request Number is applicable when variable substitution in
            JSON is being used. As variables get substituted in JSON, multiple
            JSONs are formed and each JSON is sent as a separate request. These
            requests are differentiated by adding add "request_number" which is
            basically the serial number of those requests.

            3. The entire response object of the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_object
               <system_name>_api_response_object_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_object
               <system_name>_<request_id>_api_response_object_<request_number>

            4. The response text (in text format) returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_text
               <system_name>_api_response_text_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_text
               <system_name>_<request_id>_api_response_text_<request_number>

            5. The status code returned by the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_status
               <system_name>_api_response_status_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_status
               <system_name>_<request_id>_api_response_status_<request_number>

            6. The content_type of the response returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_content_type
               <system_name>_api_response_content_type_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content_type
               <system_name>_<request_id>_api_response_content_type_<request_number>

            7. The extracted response returned from the response object (stored
               in the format that it is returned in - JSON, XML, Text) is stored
               as:

            If request_id has not been provided:
               <system_name>_api_response_content
               <system_name>_api_response_content_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content
               <system_name>_<request_id>_api_response_content_<request_number>
        """
        arguments = {'system_name': system_name, 'variable_config': variable_config,
                     'request_id': request_id, 'url': url, 'data': data,
                     'expected_response': expected_response, 'headers': headers,
                     'user': user, 'password': password, 'allow_redirects': allow_redirects,
                     'timeout': timeout, 'json': json, 'cookies': cookies,
                     'files': files, 'proxies': proxies, 'verify': verify,
                     'stream': stream, 'cert': cert, 'var_sub': var_sub}
        wdesc = "Perform a http put to the url"
        pSubStep(wdesc)
        pNote(system_name)
        output_dict = {}
        result = True

        for element in arguments:
            if element in ["json", "data", "variable_config"] \
                    and arguments[element] and arguments[element] is not None:
                arguments[element] = Utils.rest_Utils.\
                    check_ext_get_abspath(arguments[element], self.tc_path)

        credentials = Utils.data_Utils.\
            get_user_specified_tag_values_in_tc(self.datafile, **arguments)

        if credentials["variable_config"] and  \
           credentials["variable_config"] is not None:
            credentials["variable_config"] = Utils.rest_Utils.\
                check_ext_get_abspath(credentials["variable_config"],
                                      os.path.dirname(self.datafile))

        for element in credentials:
            credentials = Utils.rest_Utils.\
                resolve_credentials_for_rest(credentials, element,
                                             self.datafile, system_name)
        credentials["auth"] = (credentials['user'], credentials['password'])

        credentials, popped_args = Utils.rest_Utils.\
            remove_invalid_req_args(credentials, ["user", "password",
                                                  "request_id",
                                                  "variable_config",
                                                  "var_sub", "json"])

        pNote("url is: {0}".format(credentials['url']))
        for i in range(0, len(popped_args["json"])):
            if popped_args["json"][i] != "Error":
                credentials["json"] = popped_args["json"][i]
                for key in credentials:
                    pNote("Sending argument '{0}': {1}"
                          .format(key, credentials[key]))
                status, api_response = self.rest_object.put(**credentials)
                result = result and status
                output_dict.update(self.rest_object.
                                   update_output_dict(system_name,
                                                      api_response, request_id, status, i+1))
            else:
                pNote("Request not sent.", "error")
                status = False
                result = result and status
        if result:
            msg = "http put successful"
        else:
            msg = "http put failed"
        pNote(msg)
        report_substep_status(result)
        return result, output_dict

    def perform_http_patch(self, system_name, variable_config=None,
                           request_id=None, data=None,
                           url=None, expected_response=None,
                           headers=None, user=None, password=None,
                           allow_redirects=None, timeout=None,
                           json=None, cookies=None, files=None, proxies=None,
                           verify=None, stream=None, cert=None, var_sub=None):
        """
        Perform a http post actions and get the response
        This keyword uses the warrior recommended Input datafile format for rest

        Please refer to perform_http_post keyword documentation to understand all
        patterns

        :Arguments:
            1. system_name: Name of the system from the datafile

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Other Restrictions: Should be valid system name from the datafile

                eg: http_system_1

            2. request_id: A unique request ID for this request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: 01

            3. url: Represents URL/ip address that is supposed to be tested

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: http://httpbin.org

            4. params: Represents parameters that need to be sent along with the URL

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: postId=1; comments=5

            5. data: Represents data to be posted. HTTP GET does NOT accept this argument.

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Encoding: Unicode

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: userId=1;id=1;title=Changed Post;body=New Comment
                    \\u0075\\u0073\\u0065\\u0072\\u0049\\u0064\\u003d\\u0031\\u003b\\u0069
                    \\u0064\\u003d\\u0031\\u003b\\u0074
                    path/to/file/containing/data

            6. json: Represents the JSON data that goes into the body of the request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Format: Valid JSON format

                eg: {"postId":"1", "comments":"This is a new comment"}

            7. headers: Represents the headers sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: Content-Type=text; Date=04/21/2016; Allow=whatever_you_want_to_allow

            8. cookies: Represents the cookies sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: cookie=cookie_name; details=more_details_abput_the_cookie
                    path/to/file/containing/cookie/details

            9. files: Lets User accomplish multipart encoding upload

                Pattern: string pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="path_to_file1, path_to_file2, path_to_file3"/>

                Pattern: dict-tuple pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="file_group_name=path_to_file1,
                                                    path_to_file2, path_to_file4, path_to_file5"/>

                Pattern: tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="(path_to_file1;content_type),
                                                  (path_to_file2;content_type),
                                                  (path_to_file3;content_type)"/>

                Pattern: dict-in-tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values inside the Dictionary Pattern: No Restrictions
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files"
                              value="(path_to_file1;content_type;(custom_header_1=value1;
                                                                  custom_header_2:value2)),
                                     (path_to_file2;content_type;(custom_header_1=value1)),
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3))"/>

                eg: <argument name="files"
                              value="(path_to_file1;content_type),
                                     path_to_file2,
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2),
                                     (path_to_file4;content_type),
                                     (path_to_file5;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3)),
                                     path_to_file6, path_to_file_7"/>

            10. user: Represents the username that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: Sanika

            11. password: Represents the password that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: password

            12. timeout: Represents the time barrier in which the request should be completed
                         If 2 values are given, the first value would be treated as a constraint for
                         sending the request, the second would be treated as a constraint for
                         receiving the response. If only one value is given, it would be treated as
                         constraint for sending the request and receiving a response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: Numerical Characters - Int or Float

                eg: 0.5, 0.75
                    0.6

            13. allow_redirects: Allows or disallows redirection

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                eg: yes

            14. proxies: Allows the User to set up proxies for ip addresses

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: http=157.126.12.196:8081; https:157.126.12.144:80

            15. verify: Allows user to enable or disable authentication

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path to a .pem file

                eg: path/to/CA_BUNDLE
                    no

            16. stream: Allows user to enable or disable immediate data downloading

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'no'

                eg: yes

            17. cert: Allows user to send  his/her own certificate

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: All Characters

                Other Restrictions:
                Both the inputs should be valid file paths.
                Input 1 should be a file path to the certificate file
                If the file specified in Input 1 contains the key, Input 2 is not necessary
                If the key is stored in a different file, Input 2 should contain the path
                to that file.

                eg: path/to/certificate/file, path/to/key/file
                    path/to/certificate/file/which/contains/the/key

            18. expected_response: User specified expected response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: Numerical Characters - Integers only
                Default: The entire 200 series of HTTP Responses

                eg: 200, 302, 404
                    200

            19. variable_config: The variable config file that contains
                variables that need to be substituted into the json that is
                being passed to this request. This can either be a relative or
                an absolute path.

                Eg: ../Config_files/var_config.xml
                    /home/user/warrior_main/Warrior/Warriorspace/Config_files/var_config.xml

            20. var_sub: the pattern [var_sub] in the json will get substituted
                with this value.

        :Returns:
            1. <system_name>_status(boolean) = status code of the http patch
            2. <system_name>_api_response = the entire response object of the
               http request

            Note: The Request Number is applicable when variable substitution in
            JSON is being used. As variables get substituted in JSON, multiple
            JSONs are formed and each JSON is sent as a separate request. These
            requests are differentiated by adding add "request_number" which is
            basically the serial number of those requests.

            3. The entire response object of the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_object
               <system_name>_api_response_object_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_object
               <system_name>_<request_id>_api_response_object_<request_number>

            4. The response text (in text format) returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_text
               <system_name>_api_response_text_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_text
               <system_name>_<request_id>_api_response_text_<request_number>

            5. The status code returned by the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_status
               <system_name>_api_response_status_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_status
               <system_name>_<request_id>_api_response_status_<request_number>

            6. The content_type of the response returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_content_type
               <system_name>_api_response_content_type_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content_type
               <system_name>_<request_id>_api_response_content_type_<request_number>

            7. The extracted response returned from the response object (stored
               in the format that it is returned in - JSON, XML, Text) is stored
               as:

            If request_id has not been provided:
               <system_name>_api_response_content
               <system_name>_api_response_content_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content
               <system_name>_<request_id>_api_response_content_<request_number>
        """
        arguments = {'system_name': system_name, 'variable_config': variable_config,
                     'request_id': request_id, 'url': url, 'data': data,
                     'expected_response': expected_response, 'headers': headers,
                     'user': user, 'password': password, 'allow_redirects': allow_redirects,
                     'timeout': timeout, 'json': json, 'cookies': cookies,
                     'files': files, 'proxies': proxies, 'verify': verify,
                     'stream': stream, 'cert': cert, 'var_sub': var_sub}
        wdesc = "Perform a http patch to the url"
        pSubStep(wdesc)
        pNote(system_name)
        output_dict = {}
        result = True

        for element in arguments:
            if element in ["json", "data", "variable_config"] and \
                    arguments[element] and arguments[element] is not None:
                arguments[element] = Utils.rest_Utils.\
                    check_ext_get_abspath(arguments[element], self.tc_path)

        credentials = Utils.data_Utils.\
            get_user_specified_tag_values_in_tc(self.datafile, **arguments)

        if credentials["variable_config"] and  \
           credentials["variable_config"] is not None:
            credentials["variable_config"] = Utils.rest_Utils.\
                check_ext_get_abspath(credentials["variable_config"],
                                      os.path.dirname(self.datafile))

        for element in credentials:
            credentials = Utils.rest_Utils.\
                resolve_credentials_for_rest(credentials, element,
                                             self.datafile, system_name)
        credentials["auth"] = (credentials['user'], credentials['password'])

        credentials, popped_args = Utils.rest_Utils.\
            remove_invalid_req_args(credentials, ["user", "password",
                                                  "request_id",
                                                  "variable_config",
                                                  "var_sub", "json"])

        pNote("url is: {0}".format(credentials['url']))
        for i in range(0, len(popped_args["json"])):
            if popped_args["json"][i] != "Error":
                credentials["json"] = popped_args["json"][i]
                for key in credentials:
                    pNote("Sending argument '{0}': {1}"
                          .format(key, credentials[key]))
                status, api_response = self.rest_object.patch(**credentials)
                result = result and status
                output_dict.update(self.rest_object.
                                   update_output_dict(system_name,
                                                      api_response, request_id, status, i+1))
            else:
                pNote("Request not sent.", "error")
                status = False
                result = result and status
        if result:
            msg = "http patch successful"
        else:
            msg = "http patch failed"
        pNote(msg)
        report_substep_status(result)
        return result, output_dict

    def perform_http_delete(self, system_name, variable_config=None,
                            request_id=None, data=None,
                            url=None, expected_response=None,
                            headers=None, user=None, password=None,
                            allow_redirects=None, timeout=None,
                            json=None, cookies=None, files=None, proxies=None,
                            verify=None, stream=None, cert=None, var_sub=None):
        """
        Perform a http post actions and get the response
        This keyword uses the warrior recommended Input datafile format for rest

        Please refer to perform_http_post keyword documentation to understand all
        patterns

        :Arguments:
            1. system_name: Name of the system from the datafile

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Other Restrictions: Should be valid system name from the datafile

                eg: http_system_1

            2. request_id: A unique request ID for this request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: 01

            3. url: Represents URL/ip address that is supposed to be tested

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: http://httpbin.org

            4. params: Represents parameters that need to be sent along with the URL

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: postId=1; comments=5

            5. data: Represents data to be posted. HTTP GET does NOT accept this argument.

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Encoding: Unicode

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: userId=1;id=1;title=Changed Post;body=New Comment
                    \\u0075\\u0073\\u0065\\u0072\\u0049\\u0064\\u003d\\u0031\\u003b\\u0069
                    \\u0064\\u003d\\u0031\\u003b\\u0074
                    path/to/file/containing/data

            6. json: Represents the JSON data that goes into the body of the request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Format: Valid JSON format

                eg: {"postId":"1", "comments":"This is a new comment"}

            7. headers: Represents the headers sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: Content-Type=text; Date=04/21/2016; Allow=whatever_you_want_to_allow

            8. cookies: Represents the cookies sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: cookie=cookie_name; details=more_details_abput_the_cookie
                    path/to/file/containing/cookie/details

            9. files: Lets User accomplish multipart encoding upload

                Pattern: string pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="path_to_file1, path_to_file2, path_to_file3"/>

                Pattern: dict-tuple pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="file_group_name=path_to_file1,
                                                    path_to_file2, path_to_file4, path_to_file5"/>

                Pattern: tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="(path_to_file1;content_type),
                                                  (path_to_file2;content_type),
                                                  (path_to_file3;content_type)"/>

                Pattern: dict-in-tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values inside the Dictionary Pattern: No Restrictions
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files"
                              value="(path_to_file1;content_type;(custom_header_1=value1;
                                                                  custom_header_2:value2)),
                                     (path_to_file2;content_type;(custom_header_1=value1)),
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3))"/>

                eg: <argument name="files"
                              value="(path_to_file1;content_type),
                                     path_to_file2,
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2),
                                     (path_to_file4;content_type),
                                     (path_to_file5;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3)),
                                     path_to_file6, path_to_file_7"/>

            10. user: Represents the username that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: Sanika

            11. password: Represents the password that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: password

            12. timeout: Represents the time barrier in which the request should be completed
                         If 2 values are given, the first value would be treated as a constraint for
                         sending the request, the second would be treated as a constraint for
                         receiving the response. If only one value is given, it would be treated as
                         constraint for sending the request and receiving a response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: Numerical Characters - Int or Float

                eg: 0.5, 0.75
                    0.6

            13. allow_redirects: Allows or disallows redirection

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                eg: yes

            14. proxies: Allows the User to set up proxies for ip addresses

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: http=157.126.12.196:8081; https:157.126.12.144:80

            15. verify: Allows user to enable or disable authentication

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path to a .pem file

                eg: path/to/CA_BUNDLE
                    no

            16. stream: Allows user to enable or disable immediate data downloading

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'no'

                eg: yes

            17. cert: Allows user to send  his/her own certificate

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: All Characters

                Other Restrictions:
                Both the inputs should be valid file paths.
                Input 1 should be a file path to the certificate file
                If the file specified in Input 1 contains the key, Input 2 is not necessary
                If the key is stored in a different file, Input 2 should contain the path
                to that file.

                eg: path/to/certificate/file, path/to/key/file
                    path/to/certificate/file/which/contains/the/key

            18. expected_response: User specified expected response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: Numerical Characters - Integers only
                Default: The entire 200 series of HTTP Responses

                eg: 200, 302, 404
                    200

            19. variable_config: The variable config file that contains
                variables that need to be substituted into the json that is
                being passed to this request. This can either be a relative or
                an absolute path.

                Eg: ../Config_files/var_config.xml
                    /home/user/warrior_main/Warrior/Warriorspace/Config_files/var_config.xml

            20. var_sub: the pattern [var_sub] in the json will get substituted
                with this value.

        :Returns:
            1. <system_name>_status(boolean) = status code of the http delete
            2. <system_name>_api_response = the entire response object of the
               http request

            Note: The Request Number is applicable when variable substitution in
            JSON is being used. As variables get substituted in JSON, multiple
            JSONs are formed and each JSON is sent as a separate request. These
            requests are differentiated by adding add "request_number" which is
            basically the serial number of those requests.

            3. The entire response object of the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_object
               <system_name>_api_response_object_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_object
               <system_name>_<request_id>_api_response_object_<request_number>

            4. The response text (in text format) returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_text
               <system_name>_api_response_text_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_text
               <system_name>_<request_id>_api_response_text_<request_number>

            5. The status code returned by the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_status
               <system_name>_api_response_status_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_status
               <system_name>_<request_id>_api_response_status_<request_number>

            6. The content_type of the response returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_content_type
               <system_name>_api_response_content_type_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content_type
               <system_name>_<request_id>_api_response_content_type_<request_number>

            7. The extracted response returned from the response object (stored
               in the format that it is returned in - JSON, XML, Text) is stored
               as:

            If request_id has not been provided:
               <system_name>_api_response_content
               <system_name>_api_response_content_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content
               <system_name>_<request_id>_api_response_content_<request_number>
        """
        arguments = {'system_name': system_name, 'variable_config': variable_config,
                     'request_id': request_id, 'url': url, 'data': data,
                     'expected_response': expected_response, 'headers': headers,
                     'user': user, 'password': password, 'allow_redirects': allow_redirects,
                     'timeout': timeout, 'json': json, 'cookies': cookies,
                     'files': files, 'proxies': proxies, 'verify': verify,
                     'stream': stream, 'cert': cert, 'var_sub': var_sub}
        wdesc = "Perform a http delete to the url"
        pSubStep(wdesc)
        pNote(system_name)
        output_dict = {}
        result = True

        for element in arguments:
            if element in ["json", "data", "variable_config"] and \
                    arguments[element] and arguments[element] is not None:
                arguments[element] = Utils.rest_Utils.\
                    check_ext_get_abspath(arguments[element], self.tc_path)

        credentials = Utils.data_Utils.\
            get_user_specified_tag_values_in_tc(self.datafile, **arguments)

        if credentials["variable_config"] and  \
           credentials["variable_config"] is not None:
            credentials["variable_config"] = Utils.rest_Utils.\
                check_ext_get_abspath(credentials["variable_config"],
                                      os.path.dirname(self.datafile))

        for element in credentials:
            credentials = Utils.rest_Utils.\
                resolve_credentials_for_rest(credentials, element,
                                             self.datafile, system_name)
        credentials["auth"] = (credentials['user'], credentials['password'])

        credentials, popped_args = Utils.rest_Utils.\
            remove_invalid_req_args(credentials, ["user", "password",
                                                  "request_id",
                                                  "variable_config",
                                                  "var_sub", "json"])

        pNote("url is: {0}".format(credentials['url']))
        for i in range(0, len(popped_args["json"])):
            if popped_args["json"][i] != "Error":
                credentials["json"] = popped_args["json"][i]
                for key in credentials:
                    pNote("Sending argument '{0}': {1}"
                          .format(key, credentials[key]))
                status, api_response = self.rest_object.delete(**credentials)
                result = result and status
                output_dict.update(self.rest_object.
                                   update_output_dict(system_name,
                                                      api_response, request_id, status, i+1))
            else:
                pNote("Request not sent.", "error")
                status = False
                result = result and status
        if result:
            msg = "http delete successful"
        else:
            msg = "http delete failed"
        pNote(msg)
        report_substep_status(result)
        return result, output_dict

    def perform_http_options(self, system_name, variable_config=None,
                             request_id=None, data=None,
                             url=None, expected_response=None,
                             headers=None, user=None, password=None,
                             allow_redirects=None, timeout=None,
                             json=None, cookies=None, files=None, proxies=None,
                             verify=None, stream=None, cert=None, var_sub=None):
        """
        Perform a http post actions and get the response
        This keyword uses the warrior recommended Input datafile format for rest

        Please refer to perform_http_post keyword documentation to understand all
        patterns

        :Arguments:
            1. system_name: Name of the system from the datafile

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Other Restrictions: Should be valid system name from the datafile

                eg: http_system_1

            2. request_id: A unique request ID for this request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: 01

            3. url: Represents URL/ip address that is supposed to be tested

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: http://httpbin.org

            4. params: Represents parameters that need to be sent along with the URL

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: postId=1; comments=5

            5. data: Represents data to be posted. HTTP GET does NOT accept this argument.

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Encoding: Unicode

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: userId=1;id=1;title=Changed Post;body=New Comment
                    \\u0075\\u0073\\u0065\\u0072\\u0049\\u0064\\u003d\\u0031\\u003b\\u0069
                    \\u0064\\u003d\\u0031\\u003b\\u0074
                    path/to/file/containing/data

            6. json: Represents the JSON data that goes into the body of the request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Format: Valid JSON format

                eg: {"postId":"1", "comments":"This is a new comment"}

            7. headers: Represents the headers sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: Content-Type=text; Date=04/21/2016; Allow=whatever_you_want_to_allow

            8. cookies: Represents the cookies sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: cookie=cookie_name; details=more_details_abput_the_cookie
                    path/to/file/containing/cookie/details

            9. files: Lets User accomplish multipart encoding upload

                Pattern: string pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="path_to_file1, path_to_file2, path_to_file3"/>

                Pattern: dict-tuple pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="file_group_name=path_to_file1,
                                                    path_to_file2, path_to_file4, path_to_file5"/>

                Pattern: tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="(path_to_file1;content_type),
                                                  (path_to_file2;content_type),
                                                  (path_to_file3;content_type)"/>

                Pattern: dict-in-tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values inside the Dictionary Pattern: No Restrictions
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files"
                              value="(path_to_file1;content_type;(custom_header_1=value1;
                                                                  custom_header_2:value2)),
                                     (path_to_file2;content_type;(custom_header_1=value1)),
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3))"/>

                eg: <argument name="files"
                              value="(path_to_file1;content_type),
                                     path_to_file2,
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2),
                                     (path_to_file4;content_type),
                                     (path_to_file5;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3)),
                                     path_to_file6, path_to_file_7"/>

            10. user: Represents the username that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: Sanika

            11. password: Represents the password that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: password

            12. timeout: Represents the time barrier in which the request should be completed
                         If 2 values are given, the first value would be treated as a constraint for
                         sending the request, the second would be treated as a constraint for
                         receiving the response. If only one value is given, it would be treated as
                         constraint for sending the request and receiving a response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: Numerical Characters - Int or Float

                eg: 0.5, 0.75
                    0.6

            13. allow_redirects: Allows or disallows redirection

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                eg: yes

            14. proxies: Allows the User to set up proxies for ip addresses

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: http=157.126.12.196:8081; https:157.126.12.144:80

            15. verify: Allows user to enable or disable authentication

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path to a .pem file

                eg: path/to/CA_BUNDLE
                    no

            16. stream: Allows user to enable or disable immediate data downloading

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'no'

                eg: yes

            17. cert: Allows user to send  his/her own certificate

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: All Characters

                Other Restrictions:
                Both the inputs should be valid file paths.
                Input 1 should be a file path to the certificate file
                If the file specified in Input 1 contains the key, Input 2 is not necessary
                If the key is stored in a different file, Input 2 should contain the path
                to that file.

                eg: path/to/certificate/file, path/to/key/file
                    path/to/certificate/file/which/contains/the/key

            18. expected_response: User specified expected response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: Numerical Characters - Integers only
                Default: The entire 200 series of HTTP Responses

                eg: 200, 302, 404
                    200

            19. variable_config: The variable config file that contains
                variables that need to be substituted into the json that is
                being passed to this request. This can either be a relative or
                an absolute path.

                Eg: ../Config_files/var_config.xml
                    /home/user/warrior_main/Warrior/Warriorspace/Config_files/var_config.xml

            20. var_sub: the pattern [var_sub] in the json will get substituted
                with this value.

        :Returns:
            1. <system_name>_status(boolean) = status code of the http options
            2. <system_name>_api_response = the entire response object of the
               http request

            Note: The Request Number is applicable when variable substitution in
            JSON is being used. As variables get substituted in JSON, multiple
            JSONs are formed and each JSON is sent as a separate request. These
            requests are differentiated by adding add "request_number" which is
            basically the serial number of those requests.

            3. The entire response object of the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_object
               <system_name>_api_response_object_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_object
               <system_name>_<request_id>_api_response_object_<request_number>

            4. The response text (in text format) returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_text
               <system_name>_api_response_text_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_text
               <system_name>_<request_id>_api_response_text_<request_number>

            5. The status code returned by the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_status
               <system_name>_api_response_status_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_status
               <system_name>_<request_id>_api_response_status_<request_number>

            6. The content_type of the response returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_content_type
               <system_name>_api_response_content_type_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content_type
               <system_name>_<request_id>_api_response_content_type_<request_number>

            7. The extracted response returned from the response object (stored
               in the format that it is returned in - JSON, XML, Text) is stored
               as:

            If request_id has not been provided:
               <system_name>_api_response_content
               <system_name>_api_response_content_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content
               <system_name>_<request_id>_api_response_content_<request_number>
        """
        arguments = {'system_name': system_name, 'variable_config': variable_config,
                     'request_id': request_id, 'url': url, 'data': data,
                     'expected_response': expected_response, 'headers': headers,
                     'user': user, 'password': password, 'allow_redirects': allow_redirects,
                     'timeout': timeout, 'json': json, 'cookies': cookies,
                     'files': files, 'proxies': proxies, 'verify': verify,
                     'stream': stream, 'cert': cert, 'var_sub': var_sub}
        wdesc = "Perform a http options to the url"
        pSubStep(wdesc)
        pNote(system_name)
        output_dict = {}
        result = True

        for element in arguments:
            if element in ["json", "data", "variable_config"] and \
                    arguments[element] and arguments[element] is not None:
                arguments[element] = Utils.rest_Utils.\
                    check_ext_get_abspath(arguments[element],
                                          self.tc_path)

        credentials = Utils.data_Utils.\
            get_user_specified_tag_values_in_tc(self.datafile, **arguments)

        if credentials["variable_config"] and \
           credentials["variable_config"] is not None:
            credentials["variable_config"] = Utils.rest_Utils.\
                check_ext_get_abspath(credentials["variable_config"],
                                      os.path.dirname(self.datafile))

        for element in credentials:
            credentials = Utils.rest_Utils.\
                resolve_credentials_for_rest(credentials, element,
                                             self.datafile, system_name)
        credentials["auth"] = (credentials['user'], credentials['password'])

        credentials, popped_args = Utils.rest_Utils.\
            remove_invalid_req_args(credentials, ["user", "password",
                                                  "request_id",
                                                  "variable_config",
                                                  "var_sub", "json"])

        pNote("url is: {0}".format(credentials['url']))
        for i in range(0, len(popped_args["json"])):
            if popped_args["json"][i] != "Error":
                credentials["json"] = popped_args["json"][i]
                for key in credentials:
                    pNote("Sending argument '{0}': {1}"
                          .format(key, credentials[key]))
                status, api_response = self.rest_object.options(**credentials)
                result = result and status
                output_dict.update(self.rest_object.
                                   update_output_dict(system_name,
                                                      api_response, request_id, status, i+1))
            else:
                pNote("Request not sent.", "error")
                status = False
                result = result and status
        if result:
            msg = "http options successful"
        else:
            msg = "http options failed"
        pNote(msg)
        report_substep_status(result)
        return result, output_dict

    def perform_http_head(self, system_name, variable_config=None,
                          request_id=None, data=None,
                          url=None, expected_response=None,
                          headers=None, user=None, password=None,
                          allow_redirects=None, timeout=None,
                          json=None, cookies=None, files=None, proxies=None,
                          verify=None, stream=None, cert=None, var_sub=None):
        """
        Perform a http post actions and get the response
        This keyword uses the warrior recommended Input datafile format for rest

        Please refer to perform_http_post keyword documentation to understand all
        patterns

        :Arguments:
            1. system_name: Name of the system from the datafile

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Other Restrictions: Should be valid system name from the datafile

                eg: http_system_1

            2. request_id: A unique request ID for this request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: 01

            3. url: Represents URL/ip address that is supposed to be tested

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: http://httpbin.org

            4. params: Represents parameters that need to be sent along with the URL

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: postId=1; comments=5

            5. data: Represents data to be posted. HTTP GET does NOT accept this argument.

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Encoding: Unicode

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: userId=1;id=1;title=Changed Post;body=New Comment
                    \\u0075\\u0073\\u0065\\u0072\\u0049\\u0064\\u003d\\u0031\\u003b\\u0069
                    \\u0064\\u003d\\u0031\\u003b\\u0074
                    path/to/file/containing/data

            6. json: Represents the JSON data that goes into the body of the request

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters
                Format: Valid JSON format

                eg: {"postId":"1", "comments":"This is a new comment"}

            7. headers: Represents the headers sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: Content-Type=text; Date=04/21/2016; Allow=whatever_you_want_to_allow

            8. cookies: Represents the cookies sent along with the request

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path

                eg: cookie=cookie_name; details=more_details_abput_the_cookie
                    path/to/file/containing/cookie/details

            9. files: Lets User accomplish multipart encoding upload

                Pattern: string pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="path_to_file1, path_to_file2, path_to_file3"/>

                Pattern: dict-tuple pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="file_group_name=path_to_file1,
                                                    path_to_file2, path_to_file4, path_to_file5"/>

                Pattern: tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files" value="(path_to_file1;content_type),
                                                  (path_to_file2;content_type),
                                                  (path_to_file3;content_type)"/>

                Pattern: dict-in-tuple pattern
                Multiple Values: As specified in Glossary
                Separators: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Max Numbers of Values inside a Group: As specified in Glossary
                Max Numbers of Values inside the Dictionary Pattern: No Restrictions
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: <argument name="files"
                              value="(path_to_file1;content_type;(custom_header_1=value1;
                                                                  custom_header_2:value2)),
                                     (path_to_file2;content_type;(custom_header_1=value1)),
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3))"/>

                eg: <argument name="files"
                              value="(path_to_file1;content_type),
                                     path_to_file2,
                                     (path_to_file3;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2),
                                     (path_to_file4;content_type),
                                     (path_to_file5;content_type;(custom_header_1=value1;
                                                                  custom_header_2=value2;
                                                                  custom_header_3=value3)),
                                     path_to_file6, path_to_file_7"/>

            10. user: Represents the username that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: Sanika

            11. password: Represents the password that would be required for authentication.

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: All Characters

                eg: password

            12. timeout: Represents the time barrier in which the request should be completed
                         If 2 values are given, the first value would be treated as a constraint for
                         sending the request, the second would be treated as a constraint for
                         receiving the response. If only one value is given, it would be treated as
                         constraint for sending the request and receiving a response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: Numerical Characters - Int or Float

                eg: 0.5, 0.75
                    0.6

            13. allow_redirects: Allows or disallows redirection

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                eg: yes

            14. proxies: Allows the User to set up proxies for ip addresses

                Pattern: Dictionary Pattern
                Multiple Values: As specified in Glossary
                Separator: As specified in Glossary
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: All Characters

                eg: http=157.126.12.196:8081; https:157.126.12.144:80

            15. verify: Allows user to enable or disable authentication

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'yes'

                OR

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Other Restrictions: Should be a valid file path to a .pem file

                eg: path/to/CA_BUNDLE
                    no

            16. stream: Allows user to enable or disable immediate data downloading

                Pattern: String Pattern
                Multiple Values: No
                Max Numbers of Values Accepted: 1
                Characters Accepted: 'yes' and 'no'
                Default: 'no'

                eg: yes

            17. cert: Allows user to send  his/her own certificate

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: 2
                Characters Accepted: All Characters

                Other Restrictions:
                Both the inputs should be valid file paths.
                Input 1 should be a file path to the certificate file
                If the file specified in Input 1 contains the key, Input 2 is not necessary
                If the key is stored in a different file, Input 2 should contain the path
                to that file.

                eg: path/to/certificate/file, path/to/key/file
                    path/to/certificate/file/which/contains/the/key

            18. expected_response: User specified expected response.

                Pattern: String Pattern
                Multiple Values: Yes
                Separator: ,
                Max Numbers of Values Accepted: No Restrictions
                Characters Accepted: Numerical Characters - Integers only
                Default: The entire 200 series of HTTP Responses

                eg: 200, 302, 404
                    200

            19. variable_config: The variable config file that contains
                variables that need to be substituted into the json that is
                being passed to this request. This can either be a relative or
                an absolute path.

                Eg: ../Config_files/var_config.xml
                    /home/user/warrior_main/Warrior/Warriorspace/Config_files/var_config.xml

            20. var_sub: the pattern [var_sub] in the json will get substituted
                with this value.

        :Returns:
            1. <system_name>_status(boolean) = status code of the http head
            2. <system_name>_api_response = the entire response object of the
               http request

            Note: The Request Number is applicable when variable substitution in
            JSON is being used. As variables get substituted in JSON, multiple
            JSONs are formed and each JSON is sent as a separate request. These
            requests are differentiated by adding add "request_number" which is
            basically the serial number of those requests.

            3. The entire response object of the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_object
               <system_name>_api_response_object_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_object
               <system_name>_<request_id>_api_response_object_<request_number>

            4. The response text (in text format) returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_text
               <system_name>_api_response_text_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_text
               <system_name>_<request_id>_api_response_text_<request_number>

            5. The status code returned by the http request is stored as:

            If request_id has not been provided:
               <system_name>_api_response_status
               <system_name>_api_response_status_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_status
               <system_name>_<request_id>_api_response_status_<request_number>

            6. The content_type of the response returned by the http request
               is stored as:

            If request_id has not been provided:
               <system_name>_api_response_content_type
               <system_name>_api_response_content_type_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content_type
               <system_name>_<request_id>_api_response_content_type_<request_number>

            7. The extracted response returned from the response object (stored
               in the format that it is returned in - JSON, XML, Text) is stored
               as:

            If request_id has not been provided:
               <system_name>_api_response_content
               <system_name>_api_response_content_<request_number>

            If request_id has been provided:
               <system_name>_<request_id>_api_response_content
               <system_name>_<request_id>_api_response_content_<request_number>

        """
        arguments = {'system_name': system_name, 'variable_config': variable_config,
                     'request_id': request_id, 'url': url, 'data': data,
                     'expected_response': expected_response, 'headers': headers,
                     'user': user, 'password': password, 'allow_redirects': allow_redirects,
                     'timeout': timeout, 'json': json, 'cookies': cookies,
                     'files': files, 'proxies': proxies, 'verify': verify,
                     'stream': stream, 'cert': cert, 'var_sub': var_sub}
        wdesc = "Perform a http head to the url"
        pSubStep(wdesc)
        pNote(system_name)
        output_dict = {}
        result = True

        for element in arguments:
            if element in ["json", "data", "variable_config"] and \
                    arguments[element] and arguments[element] is not None:
                arguments[element] = Utils.rest_Utils.\
                    check_ext_get_abspath(arguments[element], self.tc_path)

        credentials = Utils.data_Utils.\
            get_user_specified_tag_values_in_tc(self.datafile, **arguments)

        if credentials["variable_config"] and  \
           credentials["variable_config"] is not None:
            credentials["variable_config"] = Utils.rest_Utils.\
                check_ext_get_abspath(credentials["variable_config"],
                                      os.path.dirname(self.datafile))

        for element in credentials:
            credentials = Utils.rest_Utils.\
                resolve_credentials_for_rest(credentials, element,
                                             self.datafile, system_name)
        credentials["auth"] = (credentials['user'], credentials['password'])

        credentials, popped_args = Utils.rest_Utils.\
            remove_invalid_req_args(credentials, ["user", "password",
                                                  "request_id",
                                                  "variable_config",
                                                  "var_sub", "json"])

        pNote("url is: {0}".format(credentials['url']))
        for i in range(0, len(popped_args["json"])):
            if popped_args["json"][i] != "Error":
                credentials["json"] = popped_args["json"][i]
                for key in credentials:
                    pNote("Sending argument '{0}': {1}"
                          .format(key, credentials[key]))
                status, api_response = self.rest_object.head(**credentials)
                result = result and status
                output_dict.update(self.rest_object.
                                   update_output_dict(system_name,
                                                      api_response, request_id, status, i+1))
            else:
                pNote("Request not sent.", "error")
                status = False
                result = result and status
        if result:
            msg = "http head successful"
        else:
            msg = "http head failed"
        pNote(msg)
        report_substep_status(result)
        return result, output_dict

    def verify_response(self, system_name, expected_api_response,
                        expected_response_type, comparison_mode,
                        request_id=None, generate_output_diff_file="Yes"):
        """
            Verifies the api response with the expected response
            and returns True or False

            Arguments:

                1. system_name: Name of the system from the datafile

                    Pattern: String Pattern
                    Multiple Values: No
                    Max Numbers of Values Accepted: 1
                    Characters Accepted: All Characters
                    Other Restrictions: Should be valid system name
                    from the datafile

                    eg: http_system_1

                2. request_id: A unique request ID for this request

                    Pattern: String Pattern
                    Multiple Values: No
                    Max Numbers of Values Accepted: 1
                    Characters Accepted: All Characters

                    eg: 01

                3. expected_api_response: expected api response given by
                   the user.

                    pattern: can be string or file name and response can be
                    simple text or xml or json
                    Multiple Values: No
                    Max Number of values accepted: 1

                4. expected_response_type: The type of expected response
                    Can be xml or json or text
                    For jsonpath & xpath comparison_modes, verify status will
                    be marked as pass if anyone the below operations is successful:
                        1. Equality match: Check if the expected response is
                        equal to API response
                        2. Regex search: Check if the expected
                        response(pattern) is in API response
                    Use 'regex=expression' as comparison_mode to support
                    python regular expression for text response.

                5. comparison_mode:
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
                6. generate_output_diff_file: If the responses doesn't match,
                    then saves the difference between
                    the responses in a file by default and if this sets to
                    'no', doesn't save any difference.

            returns:
                    If api response matches with expected_api_response
                    then returns True else False.

        """
        arguments = {'system_name': system_name,
                     'expected_api_response': expected_api_response,
                     'expected_response_type': expected_response_type,
                     'comparison_mode': comparison_mode,
                     'request_id': request_id,
                     'generate_output_diff_file': generate_output_diff_file}
        wdesc = "Verify API response with the expected API response"
        pNote(wdesc)
        output_file = self.logsdir+"/difference_output.log"
        output_file = Utils.file_Utils.addTimeDate(output_file)
        generate_output_diff_file = Utils.rest_Utils.\
            resolve_value_of_verify(generate_output_diff_file)

        try:
            arguments["expected_api_response"] = Utils.rest_Utils.\
                      check_ext_get_abspath(arguments["expected_api_response"],
                                            self.tc_path)

            credentials = Utils.data_Utils.\
                get_user_specified_tag_values_in_tc(self.datafile, **arguments)

            credentials["expected_api_response"] = Utils.rest_Utils.\
                check_ext_get_abspath(credentials["expected_api_response"],
                                      os.path.dirname(self.datafile))

            if request_id:
                response = Utils.data_Utils.get_object_from_datarepository(
                    "{0}_{1}_api_response_object".format(system_name,
                                                         credentials['request_id']))
            else:
                response = Utils.data_Utils.get_object_from_datarepository(
                    "{0}_api_response_object".format(system_name))
        except Exception as exception:
            pNote(exception, "error")
            return False
        if any([x in credentials["comparison_mode"] for x in ["xpath=", "jsonpath=", "regex="]]) \
           or credentials["comparison_mode"] == "":
            status = self.rest_object.cmp_content_response(self.datafile, system_name, response,
                                                           credentials['expected_api_response'],
                                                           credentials['expected_response_type'],
                                                           credentials['comparison_mode'])
        else:
            status = self.rest_object.cmp_response(response,
                                                   credentials['expected_api_response'],
                                                   credentials['expected_response_type'],
                                                   output_file,
                                                   credentials['generate_output_diff_file'])
        return status

    def verify_response_in_console_log(self, dict_expected_event_content=None,
                                       expected_event_content_filepath=None):
        """
            This method is used to verify the api response or event output in the console log
            Arguments:
                dict_expected_event_content (optional) : api response or event output in the format
                                                   of json/dictionary.
                expected_event_content_filepath (optional) : path of the json file which contains
                 the api response or event output in the format of json
            Returns:
                    If api response or event output found in the console log turns True else False.

        """
        wdesc = "Verify the given API response in the console log"
        pNote(wdesc)
        data_repository = config_Utils.data_repository
        tc_name = os.path.splitext(data_repository["wt_filename"])[0]
        log_file_name = "{}_consoleLogs.log".format(tc_name)
        log_file_path = os.path.join(self.logsdir, log_file_name)
        file_desc = file_Utils.open_file(log_file_path, "r")
        lines = file_desc.read()

        def verify_in_the_console_logs(data):
            """
            This method is used to verify the given dictionary is available in the console log or
            not.If all the keys and values are presented in the console log it will return True,
            if any one of the key or value is not presented in the console log it will return False
            Params:
                data : the data to verify in the console log it must be dictionary
            Return :
                Boolean value : True/False
            """
            wdesc = "Verify the json content in the console log"
            pNote(wdesc)
            for key, value in data.items():
                if isinstance(value, dict):
                    if re.search(key, lines):
                        ret_value = verify_in_the_console_logs(value)
                        if not ret_value:
                            return ret_value
                    else:
                        print_Utils.print_warning("The key {} is not presented".format(key))
                        return False
                else:
                    value = ''.join(e if e.isalnum() or e.isspace() else r"{}".format(e)
                                    for e in str(value))
                    if "${" in value:
                        s_out = value.split("}")[0]
                        env_var = s_out.split(".")[-1]
                        env_value = os.getenv(env_var)
                        if env_value is None:
                            print_Utils.print_warning("The env variable {} is not presented .so unable to "
                                                      "fetch the value ".format(env_var))
                            return False
                        pat = r'(\$\{.*\})'
                        value = re.sub(pat, env_value, value)
                    if re.search(key, lines) and re.search(value, lines):
                        pass
                    else:
                        print_Utils.print_warning("The {}/{} are not presented in the console log"
                                                  .format(key, value))

                        return False
            return True

        if dict_expected_event_content:

            status = verify_in_the_console_logs(dict_expected_event_content)
            if status:
                print_Utils.print_info("The expected json event is found in the console log")
                return True
            print_Utils.print_warning("The expected json event is not found in the console log")
            return False

        if expected_event_content_filepath:

            testcasefile_path = get_object_from_datarepository('wt_testcase_filepath')
            filepath = getAbsPath(expected_event_content_filepath,
                                  os.path.dirname(testcasefile_path))

            with open(filepath) as file_obg:
                data = json.load(file_obg)
                status = verify_in_the_console_logs(data)
                if status:
                    print_Utils.print_info("The expected json(file content) event is found in the console log")
                    return True
                print_Utils.print_warning("The expected json (file content) event is not found "
                                          "in the console log")
                return False
