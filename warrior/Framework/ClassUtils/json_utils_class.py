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

"""API for json related operations """
import json
import re
from Framework.Utils.print_Utils import print_info, print_exception, print_error, print_warning
from Framework.Utils.testcase_Utils import pNote,pSubStep
import difflib

class JsonUtils(object):
    """class for json utils"""
    def __init__(self):
        """ constructor """
        pass

    def sort_json_object(self, json_object):
        """Recursively sort any lists/dictionaries in a json
        into (key, value) pairs so that they're sorted
        """
        if isinstance(json_object, dict):
            return sorted((k, self.sort_json_object(v)) for k, v in json_object.items())
        if isinstance(json_object, list):
            return sorted(self.sort_json_object(x) for x in json_object)
        else:
            return json_object

    def nested_json_object(self,json_object):
        """
        Param: Takes json_object as input
        json_object can be a dictionary or nested dictionary.
        Returns: It returns a frozenset which has a list and it contains tuples
        ((key,value) pairs in
        json_object)

        """
        if isinstance(json_object,dict):
            return frozenset((key,self.nested_json_object(value)) for key,value in json_object.items())
        elif isinstance(json_object,list):
            return tuple(self.nested_json_object(value) for value in json_object)
        return json_object

    def case_conversion_json(self, json_object, convert_to_lower=False):
        """Takes json object and converts to upper by default and if user selects convert_to_lower
            as True, then converts json object to lower

            Returns:
                Returns json object by converting either to lower or upper case."""

        if convert_to_lower == True:
            json_object = dict({str(k).lower(): str(v).lower() for k, v in json_object.iteritems()})
        else:
            json_object = dict({str(k).upper(): str(v).upper() for k, v in json_object.iteritems()})
        return json_object

    def diff_json_objects(self, json_object1, json_object2,case_conversion=False):
        """ Takes two json objects as inputs and calculates the difference between them.
        :Returns:
            Returns a status and a comparison result(tuple or None)
            1. No difference between two json objects.
               - status = True
               - comparison result = None.
            2. Difference found between two json objects.
               - status=False
               - comparison result = a tuple of two lists
                                     list1= items in json1  but not json2
                                         list2= items in json2 but not json1
            3. If any exception encountered during comparison:
                - status=False
                - comaprison result = None
        """
        result = False
        try:
            if case_conversion == True:
                json_object1 = self.case_conversion_json(json_object1)
                json_object2 = self.case_conversion_json(json_object2)

            json_object1 = self.nested_json_object(json_object1)
            json_object2 = self.nested_json_object(json_object2)

            list1 = list(json_object1.difference(json_object2))
            list2 = list(json_object2.difference(json_object1))

            if list1 or list2:
                print_info("Items in json 1 but not json 2: {0}".format(str(list1)))
                print_info("\nItems in json 2 but not json 1: {0} ".format(str(list2)))
                result_list = (list1, list2)
            else:
                result, result_list = (True, None)
        except Exception as exception:
            print_exception(exception)
            result_list = None
        return result, result_list


    def diff_json_files(self, json_file1, json_file2):
        """ Takes two json files as inputs and calculates the difference between them.
        :Note: This method does an unsorted (or raw) comparison of the input json files
               For a sorted comparison use compare_json_files.
        :Returns:
            Returns a status and a comparison result(tuple or None)
            1. No difference between two json objects.
               - status = True
               - comparison result = None.
            2. Difference found between two json objects.
               - status=False
               - comparison result = a tuple of two lists
                                     list1= items in json1  but not json2
                                         list2= items in json2 but not json1
            3. If any exception encountered during comparison:
                - status=False
                - comaprison result = None
        """
        try:
            json_object1 = json.load(open(json_file1, 'r'))
            json_object2 = json.load(open(json_file2, 'r'))
            result, result_list = self.diff_json_objects(json_object1, json_object2)
        except Exception as exception:
            print_exception(exception)
            result = False
            result_list = None
        return result, result_list

    def compare_json_objects(self, json_object1, json_object2, case_conversion=False,
                             write_diff_to_console=True, check_for_subset=False):
        """Compares two json objects and returns true or false
        This method recursively sorts all the lists and dictionaries in the
        json objects and then performs the comparison
        If user selects check_for_subset as True, then checks whether json_object2
        is a subset of json_object1 or not by recursively sorting the json objects
        """
        print_info("compare two json objects")
        result = False
        try:
            if case_conversion == True:
                json_object1 = self.case_conversion_json(json_object1)
                json_object2 = self.case_conversion_json(json_object2)
            if check_for_subset:
                json_object1 = self.sort_json_object(json_object1)
                json_object2 = self.sort_json_object(json_object2)
                result = all(item in json_object1.items() for item in json_object2.items())
            else:
                result = self.sort_json_object(json_object1) == self.sort_json_object(json_object2)
            if not result and write_diff_to_console:
                self.diff_json_objects(json_object1, json_object2)
        except Exception as exception:
            print_exception(exception)
        return result

    def compare_json_files(self, json_file1, json_file2):
        """Compares two json files and returns true or false
        This method recursively sorts all the lists and dictionaries in the
        json files into a sorted json object and then performs the comparison"""
        print_info("compare two json files")
        result = False
        try:
            json_object1 = json.load(open(json_file1, 'r'))
            json_object2 = json.load(open(json_file2, 'r'))
            result = self.sort_json_object(json_object1) == self.sort_json_object(json_object2)
            if not result:
                self.diff_json_objects(json_object1, json_object2)
        except Exception as exception:
            print_exception(exception)
        return result

    def write_json_to_file(self, json_object, file_path):
        """Writes the given json object to the provided file """

        with open(file_path, 'w') as outfile:
            json.dump(json_object, outfile, indent=4, ensure_ascii=False)

    def pretty_print_json(self, json_object, indent=4):
        """ Prints the input json object in readable format
        to the terminal, default indent=4"""

        print_info(json.dumps(json_object, indent=indent))

    def retrieve_data_from_json(self, json_file, search_pattern):
        """Retrieves and returns data from input json
        file which matches with search pattern"""

        json_object = json.load(open(json_file, 'r'))
        for k, v in json_object.items():
            if search_pattern == k:
                print_info("Search pattern found in json")
                return v
            else:
                if not any(k == search_pattern for k in v.keys()):
                    print_info("Search pattern not found")
                    return None
                else:
                    print_info("Search pattern found in json")
                    for key, value in v.items():
                        if key == search_pattern:
                            return value
                        else:
                            continue

    def load_path_json(self, path_login_testdata):
        """ Retrieves data from json file. Returns None if exception occurs."""
        result = False
        data = None
        try:
            with open(path_login_testdata) as json_file:
                data = json.load(json_file)
                result = True
        except Exception as exception:
            pNote(exception, "error")
        return result, data
    
    def write_json_diff_to_file(self, json_object1, json_object2, output_file):
        """
            Compares two json objects and if they does not match writes the
            difference into the output file
        """
        result = self.compare_json_objects(json_object1, json_object2,
                                           write_diff_to_console=False)
        status = True
        if not result:
            status = False
            sorted_json1 = self.sort_json_object(json_object1)
            sorted_json2 = self.sort_json_object(json_object2)
            json_obj1 = json.dumps(
                sorted_json1, indent=4, separators=(',', ':'),
                encoding="utf-8")
            json_obj2 = json.dumps(
                sorted_json2, indent=4, separators=(',', ':'),
                encoding="utf-8")
            te = open(output_file, 'w')
            diff = ("\n".join(
                difflib.ndiff(json_obj1.splitlines(), json_obj2.splitlines())))
            te.write(diff)
            te.close()
        return status
    
    def compare_json_using_jsonpath(self, response, list_of_jsonpath, list_of_expected_api_responses):
        """
            Will get each json_path in list of jsonpath and get the value of
            that jsonpath in json response
            Compares the value with the expected_api_response
            If all values matches returns True else False
        """
        status = True
        json_response = json.loads(response)
        for index, jsonpath in enumerate(list_of_jsonpath):
            json_path = jsonpath.strip().replace("jsonpath=", "")
            value = self.get_value_for_nested_key(json_response, json_path)
            # Equality_match: Check if the expected response is equal to API response
            match = True if value == list_of_expected_api_responses[index] else False
            # Perform Regex_search if equality match fails
            if match is False:
                try:
                    # Regex_search: Check if the expected response pattern is in API response
                    match = re.search(list_of_expected_api_responses[index], value)
                except Exception:
                    print_warning("Python regex search failed, invalid "
                                  "expected_response_pattern '{}' is "
                                  "provided".format(list_of_expected_api_responses[index]))
            if not match:
                status = False
                print_error("For the given '{0}' the expected response value is '{1}'. "
                            "It doesn't match or available in the actual response value "
                            "'{2}'".format(jsonpath, list_of_expected_api_responses[index],
                                           value))
        return status

    def get_value_for_nested_key(self, json_response, json_path):
        """
            Returns the value of the nested key in the dictionary
            Arguments:
                json_response = dictionary from which we get the value of the
                    nested key
                json_path = nested key to which we need to get the value
                For example: json_response = {"1":{"2":{"3":{"4":"5"}}}}
                If we wish to get the value of key '4', you need to give 
                the json_path as "1.2.3.4"
            Returns:
                returns the value of the nested key
            
        """
        keys = json_path.split(".")
        for index, key in enumerate(keys, 1):
            json_response = json_response.get(key)
            if index < len(keys) and isinstance(json_response, dict):
                continue
            else:
                break
        return json_response
