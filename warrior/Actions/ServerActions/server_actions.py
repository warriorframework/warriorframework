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
Implementation of the Bottle web socket server related keywords
"""

import Framework.Utils as Utils
from Framework.ClassUtils.rest_server_class import RestServer
# Written by Sourav
# from Framework.Utils import rest_server
# from Framework.Utils.rest_server import b_start_server, b_stop_server, \
#     b_create_route, b_get_request, b_get_response

class ServerActions(object):
    """
    Class for Bottle Web socket server
    """
    def __init__(self):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        # self.users = [{"user": "admin", "password": "admin", "auth_header":
        # 'Basic ' + base64.b64encode('admin:admin')}] 
        # self.jsonobj = JsonUtils()

    def start_server(self, system_name):
        """
        Start Bottle Web Socket Server
        :param server_name:
        :return: Binary True or False and dictionary {socket_obj: object}
        """
        wdesc = "Starting Bottle web socket server."
        Utils.testcase_Utils.pSubStep(wdesc)
        rest_server = RestServer()
        status, server_dict = rest_server.build_server(self.datafile, system_name)
        if status:
            output_dict = {"{}_server_controller".format(system_name): server_dict["server"],
                           "{}_server_thread".format(system_name): server_dict["server_thread"],
                           "{}_server_object".format(system_name): rest_server}
            return status, output_dict
        return status

    def stop_server(self, system_name):
        """
        Stop Bottle Web server all application
        :param server_name:
        :return: Binary True or False
        """
        wdesc = "Closing Bottle web socket server."
        Utils.testcase_Utils.pSubStep(wdesc)
        server_controller = Utils.data_Utils.get_object_from_datarepository("{}_server_controller".format(system_name))
        server_controller.stop()
        server_thread = Utils.data_Utils.get_object_from_datarepository("{}_server_thread".format(system_name))
        
        if server_thread.is_alive():
            print "Server doesn't shutdown correctly"
            return False
        else:
            return True

    """
        The below methods are written by Sourav
        Keeping here for reference as some of the code maybe reusable in the future
    """

    # def initilize_route(self, system_name, route_param):
    #     """
    #     Initilize The Route parameters
    #     :return: True
    #     """
    #     wdesc = "Initilize route"
    #     Utils.testcase_Utils.pSubStep(wdesc)
    #     op_dict = {}
    #     inputdata_child = Utils.data_Utils.get_child_tag_value_list(self.datafile, system_name, [route_param])
    #     print "inputdata_child", inputdata_child
    #     __app = Utils.data_Utils.get_object_from_datarepository("{}_socket_obj".format(system_name))
    #     __route = inputdata_child[1][0]  ##UNDER a same route different JSON file could come.
    #     __method = inputdata_child[1][1]
    #     __stat, __json = self.jsonobj.load_path_json(inputdata_child[1][2])
    #     func = functools.partial(self.__receive_notification, system_name=system_name)
    #     b_create_route(__app, __route, __method, func)
    #     #__app.route(path=__route, method=__method, callback=self.__receive_notification)
    #     testcase_Utils.pNote('Initilize Route List {}'.format(__app.routes))
    #     if __stat:
    #         op_dict = {"Verify_Data_{}".format(__route):__json}
    #         print "op_dict", op_dict
    #     else:
    #         testcase_Utils.pNote("Json file not found!")
    #     return True, op_dict

    # def add_users(self, uname, password):
    #     """

    #     :param uname:
    #     :param password:
    #     :return:
    #     """
    #     self.users.append({"user": uname, "password": password, "auth_header":
    #     'Basic ' + base64.b64encode(uname+':'+password)})

    # def __receive_notification(self, **kargs):
    #     """
    #     The callback method
    #     """
    #     wdesc = "Receive and verify notification."
    #     Utils.testcase_Utils.pSubStep(wdesc)
    #     request = b_get_request()
    #     response = b_get_response()
    #     match = re.search("(http.*:[0-9]+)(/.*$)+", request.url, re.DOTALL)
    #     __route = match.group(2)
    #     __app = Utils.data_Utils.get_object_from_datarepository("{}_socket_obj".format(kargs["system_name"]))
    #     __json = Utils.data_Utils.get_object_from_datarepository("Verify_Data".format(__route))
    #     self.__log_request(request)
    #     if request.auth is not None and len(request.auth) >= 2 and \
    #             self.__check_credentials(request.auth[0], request.auth[1]): ##for Virura any request will come with some authentication
    #         if request.content_type == 'application/json':
    #             status, _list = self.jsonobj.diff_json_objects(json.loads(request.body.getvalue()), __json)
    #             if status:
    #                 response.status = 200 ## Response status will fetch from data file. TBD
    #                 testcase_Utils.pNote('Incomming json Match')
    #             else:
    #                 response.status = 401
    #                 testcase_Utils.pNote('Incomming json Does not Match', "warning")
    #         self.__log_response(response)
    #         return {'title': 'sucess'}
    #     else:
    #         response.status = 401
    #         return {'title': 'Failure'}

    # def __log_request(self, request):
    #     """
    #     TBD
    #     :param request:
    #     :return:None
    #     """
    #     testcase_Utils.pNote('request.url {}'.format( request.url))
    #     testcase_Utils.pNote( 'request.method {}'.format(request.method))
    #     testcase_Utils.pNote('request.auth {}'.format(request.auth))
    #     testcase_Utils.pNote( 'request content-type: {}'.format(request.content_type))
    #     if request.content_type == 'application/json': #should also support application text and application xml
    #         testcase_Utils.pNote('request body contents: {}'.format(json.dumps(json.loads(
    #             request.body.getvalue()), indent=4)))
    #     else:
    #         pass

    # def __log_response(self, response):
    #     """
    #     TBD
    #     :param response:
    #     :return:None
    #     """
    #     testcase_Utils.pNote('Response.status {}'.format(response.status))
    #     testcase_Utils.pNote('Response.status_code {}'.format(
    #     response.status_code))
    #     testcase_Utils.pNote('Response.status_line {}'.format(
    #     response.status_line))

    # def __check_credentials(self, uname, password):
    #     """
    #     TBD
    #     :param user:
    #     :param password:
    #     :return:
    #     """
    #     status = False
    #     for user_record in self.users:
    #         if user_record['user'] == uname and user_record['password'] == password:
    #             status = True
    #             break
    #     return status
