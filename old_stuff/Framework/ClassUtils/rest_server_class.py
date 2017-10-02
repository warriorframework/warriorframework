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

from Framework.OSS.bottle import Bottle, run, request, response, ServerAdapter
from wsgiref.simple_server import make_server
import threading
from time import sleep
from Framework.Utils import data_Utils, file_Utils
from Framework.Utils.file_Utils import getAbsPath, getDirName
import json
from ast import literal_eval
import xml.etree.ElementTree as ET
from Framework.Utils.xml_Utils import getChildElementWithSpecificXpath, compare_xml

request_verify_list = ["request_verify_data", "request_param", "request_verify"]
on_fail_response_list = ["on_fail_response_value", "on_fail_response_status_code"]
response_list = ["response_status_code", "response_value", 
"async_response_value", "async_response_timer", "async_response_status_code"] + on_fail_response_list
data_tags = ["request_method"] + request_verify_list + response_list

class ServerHandler(ServerAdapter):
    """
        A wsgiref server that can be shutdown manually
        so the bottle server can be terminated peacefully
        Once bottle is capable of terminating itself this can go away
    """
    server = None

    def run(self, app):
        self.server = make_server(self.host, self.port, app)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()

class RestServer(object):
    """
        A Rest server that is powered by the Python Bottle framework
    """
    def __init__(self):
        self.server = None

    def verify_param(self, incoming_params, respond_obj):
        """
            Verify all request param matched with the expect param
            :param:
                incoming_params: the incoming params in a list of tuple form
                                 eg. [(key1, value1), (key2, value2)]
                respond_obj: contains the verification detail from datafile
            :return:
                True if all incoming params match the veri param
                False if any incoming params fail to match
        """
        provided_param_dict = {}
        for param_pair in respond_obj["request_param"]:
            provided_param_dict.update({param_pair.split("=")[0]:param_pair.split("=")[1]})

        for incoming_param_pair in incoming_params:
            if incoming_param_pair[0] not in provided_param_dict:
                return False
            elif incoming_param_pair[1] != provided_param_dict[incoming_param_pair[0]]:
                return False

        return True

    def verify_forms(self, incoming_forms, respond_obj):
        """
            Verify all items in form/dict match the expect param
            :param:
                incoming_forms: the incoming form in a list of tuple form
                                 eg. [(key1, value1), (key2, value2)]
                respond_obj: contains the verification detail from datafile
            :return:
                True if all items in form/dict match the veri param
                False if any of the items fail to match
        """
        provided_form_dict = {}
        for form_pair in respond_obj["request_verify"]:
            provided_form_dict.update({form_pair.split(",")[0][4:]:form_pair.split(",")[1][6:]})

        for incoming_pair in incoming_forms:
            if incoming_pair[0] not in provided_form_dict:
                return False
            elif incoming_pair[1] != provided_form_dict[incoming_pair[0]]:
                return False

        if incoming_forms == []:
            return False
        return True

    def verify_xml(self, incoming_xml, respond_obj, file=False):
        """
            Verify the incoming_xml data with either
            a. whole xml file
            b. tag text pairs
            :param:
                incoming_xml: an xml string
                respond_obj: contains the verification detail from datafile
                file: indicate if comparing whole file or just pairs
            :return:
                True if whole file match/all pairs match
                False if not match
        """
        if file:
            status = False
            for expect_xml_file in respond_obj["request_verify_data"]:
                expect_xml_file = getAbsPath(expect_xml_file, getDirName(self.datafile))
                status, _, _, _ = compare_xml(incoming_xml, expect_xml_file, 
                    output_file=False, sorted_json=False, remove_namespaces=True)
            return status
        else:
            incoming_xml = ET.fromstring(incoming_xml, parser=ET.XMLParser(encoding="utf-8"))
            for element_pair in respond_obj["request_verify"]:
                xpath = element_pair.split(",")[0][4:]
                value = element_pair.split(",")[1][6:]
                incoming_value = getChildElementWithSpecificXpath(incoming_xml, xpath)
                if incoming_value is None or value != incoming_value.text:
                    return False

        return True

    def verify_json(self, incoming_json, respond_obj, file=False):
        """
            Verify the incoming_json data with either
            a. whole json file
            b. key value pairs
            :param:
                incoming_json: a json string/json obj
                respond_obj: contains the verification detail from datafile
                file: indicate if comparing whole file or just pairs
            :return:
                True if whole file match/all pairs match
                False if not match
        """
        if isinstance(incoming_json, str):
            incoming_json = json.loads(incoming_json)
        if file:
            for expect_json_file in respond_obj["request_verify_data"]:
                expect_json_file = getAbsPath(expect_json_file, getDirName(self.datafile))
                expect_json = json.load(open(expect_json_file))
                if sorted(incoming_json.items()) == sorted(expect_json.items()):
                    return True
            return False
        else:
            for json_pair in respond_obj["request_verify"]:
                json_keys = json_pair.split(",")[0][4:].split("[")
                # Since datafile is xml and it only have string
                # must have a way to process different object type in json
                json_value = literal_eval(json_pair.split(",")[1][6:])
                # travesing to get the child element value
                incoming_json_index = incoming_json
                for json_key in json_keys:
                    json_key = json_key.replace("]", "")
                    if json_key not in incoming_json_index:
                        return False
                    else:
                        incoming_json_index = incoming_json_index[json_key]
                if incoming_json_index != json_value:
                    return False
        return True

    def async_response(self, response_val, async, async_response_value, async_status):
        """
            Bottle framework support async response using yield
            simulate a semi-async response
            :param:
                response_val: the original response value
                async: time between original response and 2nd response
                async_response_value: async response value
                async_status: the async status code
        """
        if response_val.startswith("$PATH:"):
            yield open(response_val[6:], "r").readlines()
        else:
            yield response_val + "\n\r"
        sleep(async)
        response.status = int(async_status)
        if async_response_value.startswith("$PATH:"):
            yield open(async_response_value[6:], "r").readlines()
        else:
            yield async_response_value + "\n\r"

    def form_response(self, res_obj, status=True):
        """
            Take in a response object and generate response based on its status
            :param:
                res_obj: object that contains all the response info
        """
        response.status = int(res_obj["response_status_code"][0]) if "response_status_code" in res_obj else 200
        if status:
            response_val = res_obj["response_value"][0] if "response_value" in res_obj else "Default pass response"
        else:
            response_val = res_obj["response_value"][0] if "response_value" in res_obj else "Default fail response"
            response.status = int(res_obj["on_fail_response_status_code"][0]) if "on_fail_response_status_code" in res_obj else response.status
            response_val = res_obj["on_fail_response_value"][0] if "on_fail_response_value" in res_obj else response_val
        
        async = int(res_obj["async_response_timer"][0]) if "async_response_timer" in res_obj else 0
        async_response_value = res_obj["async_response_value"][0] if "async_response_value" in res_obj else "Default async response"
        async_status = int(res_obj["async_response_status_code"][0]) if "async_response_status_code" in res_obj else 200

        if not async:
            if response_val.startswith("$PATH:"):
                return open(response_val[6:], "r").readlines()
            else:
                return response_val
        else:
            return self.async_response(response_val, async, async_response_value, async_status)

    def build_route(self, route, method, specific_res_list, general_res):
        """
            Take in route, method and its request/response
            build a route with the corresponded method
            loaded with request/response condition
            return the route method
            :param:
                route: the route name, eg. /att /verizon
                method: the route method type, eg. GET POST
                specific_res_list: a list of tuple (verify info, response)
                general_res: the general response if no specific response is present
        """
        if specific_res_list is not None:
            # Cond 1: special request
            def inner_method():
                print "Content type: " + str(request.content_type)
                # This is paramaters
                print "Query: " + str(request.query.items())
                # This is form data
                print "Forms: " + str(request.forms.items())
                print "Body: " + str(request.body.getvalue())
                print "Json: " + str(request.json)
                print "File: " + str(request.files.items())

                # Extract request type and values
                # Look for specific type comparison for value
                status = False
                if request.query.items():
                    # request param comparison
                    # All param must match
                    for specific_res in specific_res_list:
                        if "request_param" in specific_res:
                            status = self.verify_param(request.query.items(), specific_res)

                        if status:
                            break
                elif "json" in request.content_type:
                    # request body json comparison
                    # compare whole file
                    # search for all json path
                    for specific_res in specific_res_list:
                        if "request_verify_data" in specific_res:
                            status = self.verify_json(request.json, specific_res, file=True)
                        elif "request_verify" in specific_res:
                            status = self.verify_json(request.json, specific_res, file=False)

                        if status:
                            break
                elif "xml" in request.content_type:
                    # request body xml comparison
                    # compare whole file
                    # search for all xpath
                    for specific_res in specific_res_list:
                        if "request_verify_data" in specific_res:
                            status = self.verify_xml(request.body.getvalue(), specific_res, file=True)
                        elif "request_verify" in specific_res:
                            status = self.verify_xml(request.body.getvalue(), specific_res, file=False)

                        if status:
                            break
                else:
                    # request body form comparison
                    # compare whole form
                    # search for all provided key, value pair
                    for specific_res in specific_res_list:
                        if "request_verify" in specific_res:
                            status = self.verify_forms(request.forms.items(), specific_res)

                        if status:
                            break

                if status:
                    return self.form_response(specific_res)
                return self.form_response(general_res, False)

        elif general_res is not None:
            # Cond 2: general request
            # response with general response
            def inner_method():
                print "Content type: " + str(request.content_type)
                # This is paramaters
                print "Query: " + str(request.query.items())
                # This is form data
                print "Forms: " + str(request.forms.items())
                print "Body: " + str(request.body.getvalue())
                print "Json: " + str(request.json)
                print "File: " + str(request.files.items())

                return self.form_response(general_res)
        else:
            # Default action
            def inner_method():
                return "Not verifying anything, please check if datafile is correct"

        print "\nBuild a " + method + " route with this route: " + route
        import pprint
        print "Special request: "
        pprint.pprint(specific_res_list)
        print "General request: "
        pprint.pprint(general_res)

        inner_method.__doc__ = route + "_" + method + " is the method name"
        inner_method.__name__ = route + "_" + method
        return inner_method

    def build_server(self, datafile, system_name):
        """
            Take in a system and read all its routes
            Load the routes into Bottle server object
            Start a thread with the bottle server

            return the bottle server adapter and server thread
        """
        app = Bottle()
        # Get system and routes
        system_data = data_Utils.get_credentials(datafile, system_name)
        self.datafile = datafile

        route_file = system_data['mapping_file']
        if route_file:
            route_file = getAbsPath(route_file, getDirName(datafile))
        # Loop through each route
        for route in data_Utils.get_all_system_or_subsystem(route_file):
            route_name = route.get('name')
            if route_name[0] != '/':
                route_name = '/' + route_name

            # Group request condition with the same method together
            route_methods = {}
            for request in route:
                request_method = request.find('request_method').text.upper()
                if request_method not in route_methods:
                    route_methods[request_method] = [request]
                else:
                    route_methods[request_method].append(request)

            # Build route with the grouped conditions
            for method_type, same_type_methods in route_methods.items():
                # A route can have general response and conditional response
                specific_res = []
                general_res = {}

                for method in same_type_methods:
                    dict_of_info = {}
                    method_req = {}
                    method_res = {}

                    # Get all info from the condition
                    for info in iter(method):
                        if info.tag in dict_of_info:
                            dict_of_info[info.tag].append(info.text)
                        else:
                            dict_of_info[info.tag] = [info.text]

                    # Extract request/response related info
                    for key, value in dict_of_info.items():
                        if key in request_verify_list:
                            method_req = {key:value}
                        elif key in response_list:
                            method_res[key] = value

                    if any([key in request_verify_list for key in dict_of_info.keys()]):
                        # this condition has request/response pair
                        method_combine = method_req
                        method_combine.update(method_res)
                        specific_res.append(method_req)
                        # this ensure when all verification fail and no general response given
                        # there will be some responses
                        if any([key in on_fail_response_list for key in dict_of_info.keys()]):
                            general_res.update(method_res)
                    else:
                        # this condition only has general response
                        general_res.update(method_res)

                app.route(route_name, method_type, self.build_route(route_name, method_type, specific_res, general_res))

        # Build a class to hold the server so it can be closed easily
        port = 5000 if "port" not in system_data else int(system_data["port"])
        server = ServerHandler(host="0.0.0.0", port=port)
        server_thread = threading.Thread(target=run, kwargs={"app": app, "server": server, "debug": True})
        server_thread.daemon = True
        server_thread.start()
        sleep(2)

        if server_thread.is_alive():
            return True, {"server":server, "server_thread":server_thread}
        else:
            return False, {}
