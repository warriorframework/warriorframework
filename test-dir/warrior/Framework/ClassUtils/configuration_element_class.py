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
    This module create a tree of ConfigurationElements from xml documents or elements of
    ElementTrees
"""

import xml.etree.ElementTree as ElementTree
import re
import decimal
from Framework.Utils.print_Utils import print_error
import Framework.Utils as Utils

class ConfigurationElement(object):
    """
        Configuration element to support arbitrary xml object depth
    """

    def __init__(self, name='base', start_pat="${", end_pat="}"):
        """ Constructor """
        self.name = name
        self.attributes = {}
        self.children = {}
        self.start_pat = start_pat
        self.end_pat = end_pat

    def __find_match(self, string):
        """
            Internal ufunction to match against a regular expression
        :param string:
        :return:
        """
        # Create a regex search object which contains
        # a group object with the text within the start and end pattern
        # and another group object with the text and start/end pattern
        # if the regex pattern doesn't match with the string, it return None
        # .* matches everything
        # ? matches until the first occurence of the next pattern, in this case
        # it matches the first occurence of the end pattern
        text_between_pattern = r"(.*?)"
        return re.search(r".*(" + re.escape(self.start_pat) + text_between_pattern +\
            re.escape(self.end_pat) + r").*", string)

    def expand_variables(self, string):
        """
            Replaces embedded variables in the string with their values.  Works with $(var) or
            ${var}.  These can be nested to any level
        :param string:
        :return:
        """
        new_string = self.__expand_variables(string)
        return new_string

    def __expand_variables(self, string):
        """
            Replaces embedded variables in the string with their values.  Can handle multiple levels
            of such as ${${node.some_var}.node.${some_other_var}}.  All occurrences of variables
            will be replaced
        :param string:
        :return:
        """
        # The string that is currently being processed
        return_value = string
        # When end_pat_index == -1, which means end_pattern is not found in the return_value string
        # Get the regex match object of the substring
        # which looks for text between start and endpattern
        match = self.__find_match(return_value)
        # Only substitued the string when there is a match
        while match is not None:
            # match.group(2) contains the pre-sub value
            # substitued value is the actual value after parsing the pre-sub value
            substitued_value = self.get_value(match.group(2))
            # match.group(1) contains start_pattern, pre-sub value and end_pattern
            # for default pattern, it looks like ${PRESUB_VALUE}
            # this step replace the pre_sub value
            return_value = return_value.replace(match.group(1), substitued_value, 1)
            # Call other substitute functions
            return_value = Utils.data_Utils.sub_from_env_var(
                return_value, self.start_pat, self.end_pat)
            return_value = Utils.data_Utils.sub_from_data_repo(
                return_value, self.start_pat, self.end_pat)

            # Doing another search for the next value to substitue
            match = self.__find_match(return_value)

        return return_value

    def get_list_direct(self, string):
        """
            entry function for __get_list
        :param string:
        :return:
            a dictionary
            if nothing wrong with list range
                return a dict with orignal list/range as key "1..4,5,6..7:0.5"
                parsed list as value [1,2,3,4,5,6,6.5,7]
            if invalid range found
                return a dict {'Error':False}
            if no list/range found
                return a dict {'False':False}
        """
        return_value = string
        result = {}
        check = self.end_pat
        match = self.__find_match(return_value[:return_value.find(check) + len(check)])
        while match is not None:
            try:
                parsed_value = self.__parse_list("{" + match.group(2) + "}")
            except (ValueError, TypeError, AttributeError):
                print_error("Invalid list range found")
                return {'Error':False}
            if parsed_value:
                result[match.group(2)] = parsed_value
            return_value = return_value.replace(return_value[:return_value.find(check) + len(check)], '')
            match = self.__find_match(return_value[:return_value.find(check) + len(check)])
        if result == {}:
            return {'False':False}
        return result

    def get_list(self, string):
        """
            entry function for __get_list
        :param string:
        :return:
            a dictionary
            if nothing wrong with list range
                return a dict with orignal list/range as key "1..4,5,6..7:0.5"
                parsed list as value [1,2,3,4,5,6,6.5,7]
            if invalid range found
                return a dict {'Error':False}
            if no list/range found
                return a dict {'False':False}
        """
        new_string = self.__get_list(string)
        return new_string

    def __get_list(self, string):
        """
            Get the list of variable from the string (can have multiple ${list} )
        :param string:
        :return:
            a dictionary
            if nothing wrong with list range
                return a dict with orignal list/range as key "1..4,5,6..7:0.5"
                parsed list as value [1,2,3,4,5,6,6.5,7]
            if invalid range found
                return a dict {'Error':False}
            if no list/range found
                return a dict {'False':False}
        """
        return_value = string
        result = {}
        check = self.end_pat
        match = self.__find_match(return_value[:return_value.find(check) + len(check)])
        while match is not None:
            try:
                parsed_value = self.__parse_list(self.get_value(match.group(2)))
            except (ValueError, TypeError, AttributeError):
                print_error("Invalid list range found")
                return {'Error':False}
            if parsed_value:
                result[match.group(2)] = parsed_value
            return_value = return_value.replace(return_value[:return_value.find(check) + len(check)], '')
            match = self.__find_match(return_value[:return_value.find(check) + len(check)])
        if result == {}:
            return {'False':False}
        return result

    def __parse_list(self, string):
        """
            Parsed a string of value list, extract values and put it in a list
        :param string:
        :return:
            a list of string - list of values that is extracted from original string or original string
        """
        if string.startswith("{") and string.endswith("}"):
            result = []
            parsed = string[1:-1].split(',')
            for var in parsed:
                if '..' in var and ':' in var:
                    indexes = re.split('\.\.|:', var)
                    x = self.__frange(indexes[0], indexes[1], indexes[2])
                    for index in x:
                        result.append(str(index))
                elif '..' in var and ':' not in var:
                    indexes = re.split('\.\.', var)
                    x = self.__frange(indexes[0], indexes[1])
                    for index in x:
                        result.append(str(index))
                else:
                    result.append(var)
            return result
        else:
            return False

    def __frange(self, x, y, jump=None):
        """
            Customized range function to support floating point step in/decrement
        :param x:
        :param y:
        :param jump:
        :return:
            a generator with each value in the range
        """
        # Find the floating number that has the longest exponents part
        x_dec = abs(decimal.Decimal(x).as_tuple().exponent)
        y_dec = abs(decimal.Decimal(y).as_tuple().exponent)
        if jump is None:
            jump = 1 if float(x) < float(y) else -1
        jump_dec = abs(decimal.Decimal(jump).as_tuple().exponent)
        dec_offset = max([x_dec, y_dec, jump_dec])
        if dec_offset == 0:
            x, y, jump = (int(x), int(y), int(jump))
        else:
            x, y, jump = (float(x), float(y), float(jump))

        if jump == 0:
            raise ValueError("step value cannot be 0")
        if (x > y and jump > 0) or (x < y and jump < 0):
            raise ValueError("sign of step value must not be the same as difference between comparing values")

        if x < y:
            while x <= y:
                yield x
                x += jump
                if dec_offset > 0:
                    x = round(x, int(dec_offset))
        else:
            while x >= y:
                yield x
                x += jump
                if dec_offset > 0:
                    x = round(x, int(dec_offset))

    def get_list_of_values(self, *args):
        """
            Looks up all values requested and returns a list in the order requested
        :param args:
        :return:
        """
        values = []
        for data in args:
            values.append(self.get_value(data))

        return values

    def get_dictionary_of_values(self, *args):
        """
            Looks up all values requested and returns a dictionary of key value pairs
        :param args:
        :return:
        """
        values = {}
        for data in args:
            values[data] = self.get_value(data)

        return values

    def get_value(self, value):
        """
            Returns requested value or None if not found and prints an error
        :param value:
        :return:
        """
        try:
            if len(value.split('.')) > 1:
                child = value.split('.')[0].strip()
                return self.children[child].get_value(value.split('.', 1)[1].strip())
            else:
                return self.attributes[value]
        except KeyError:
            print_error("Key error node " + self.name + " does not have sub node "
                  + value.split('.')[0] + ". Cannot complete remainder of search for " + value)
            return None

    def set_value(self, key, value):
        """
            Adds or changes the key value pair in the tree
        :param key:
        :param value:
        :return:
        """
        try:
            if len(key.split('.')) > 1:
                child = key.split('.')[0]
                self.children[child].set_value(key.split('.', 1)[1], value)
            else:
                self.attributes[key] = value
        except KeyError:
            print_error("Key error node " + self.name + " does not have sub node "
                  + key.split('.')[0] + ". Cannot complete remainder of search for " + key)

    def get_node(self, value):
        """
            Returns a ConfigurationElement that is the tree rooted at the requested node
        :param value:
        :return:
        """
        if len(value.split('.')) > 1:
            child = value.split('.')[0]
            return self.children[child].get_node(value.split('.', 1)[1])
        else:
            return self.children[value]

    def parse_data(self, *arg, **kwargs):
        """
            parse_data constructs a tree of ConfigurationElements from a list of xml files or a list
            of ElementTrees. The name attribute is the primary key for each node, so if there is any
            repetition of names at the same tree level, the two nodes will be merged with the second
            occurrence over writing the first when there is conflict.  This is also true across
            files if two files/ElementTrees passed in share the same node name structure second file
            will  over write any shared values.  The attribute xml_tag comes from the xml structure
            so any attribute named xml_tag will be over written by the xml structure tag name
        :param arg:
        :param kwargs:
                root is a bool default is True
                    this drives filepath(True) or ElementTree(False) parsing
        :return:
        """

        for xml in arg:
            # when the elem_type is xml_object(root xml object)
            if 'elem_type' in kwargs and kwargs['elem_type'] == "xml_object":
                config_tree = xml
            elif 'root' in kwargs and not kwargs['root']:
                config_tree = xml
            else:
                tree = ElementTree.parse(xml)
                config_tree = tree.getroot()

            self.parse_tree(config_tree)

    def parse_tree(self, node):
        """
            Method to parse ElementTree to ConfigurationElement Tree
        :param node:
        :return:
        """
        for key in node.attrib:
            self.attributes[key] = node.attrib[key]
        self.attributes['xml_tag'] = node.tag
        # self.attributes['xml_element'] = node

        for child in node:
            try:
                if not child.attrib['name'] in self.children:
                    child_config = ConfigurationElement(child.attrib['name'])
                    child_config.parse_data(child, root=False)
                    self.children[child.attrib['name']] = child_config
                else:
                    self.children[child.attrib['name']].parse_tree(child)
            except KeyError:
                print_error("No name attribute for node " + child.tag + ". Tree with root "
                            "at node " + child.tag + " not parsed.")

    @staticmethod
    def __tabs(number):
        """
            Supports str method
        :param number:
        :return:
        """
        data = ''
        num = 0
        while num < number:
            data += '\t'
            num += 1

        return data

    def print_me(self, depth=0):
        """
            To String implementation
        :param depth:
        :return:
        """
        data = "name: '" + self.name + "' atributes: "
        data += str(self.attributes) + " children:"
        for child in self.children:
            data += '\n' + self.__tabs(depth + 1) + child + ": "
            data += self.children[child].print_me(depth + 1)
        if len(self.children) == 0:
            data += ' None'
        return data

    def __str__(self):
        """ Prints the string representation of the object """
        return self.print_me()
