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

"""This is the library which holds api's related to operations on csv files"""
import csv
import json
from Framework.Utils import data_Utils, xml_Utils, file_Utils
from Framework.Utils.print_Utils import print_exception, print_info
import os
from collections import OrderedDict
try:
    import xlrd
except ImportError:
    print_info("{0}: xlrd module is not installed".format(os.path.abspath(__file__)))
    print_info("Install xlrd module in order to perform Excel to CSV or"\
               " Excel to XML file conversion")
    print_info("Please follow the instructions in "
               " http://xlrd.readthedocs.io/en/latest/installation.html"
               " to install the xlrd")


def convert_csv_to_list_of_dict(input_csv_file):
    """
        Takes the CSV file path as input and
        converts it to list of dictionaries

        Arguments:
            input_csv_file: it takes CSV file path as input

        Returns:
            Returns list of dictionaries where keys are
            column names and values are respective column values
    """
    list_of_dict = []
    try:
        if type(input_csv_file) == str:
            input_csv_file = open(input_csv_file, 'r')
        else:
            input_csv_file.seek(0)
        reader = csv.DictReader(input_csv_file)
        title = reader.fieldnames
        for row in reader:
            ordered_dict = OrderedDict()
            for i in xrange(len(title)):
                if not title[i]:
                    continue
                ordered_dict[title[i]] = row[title[i]]
            list_of_dict.append(ordered_dict)
        input_csv_file.close()

    except Exception as exception:
        print_exception(exception)
    
    return list_of_dict

def convert_excel_to_csv(input_excel_file,
                         output_csv_file_path=None, return_csv_file=False):

    """
        Takes the excel file path as input and converts
        into csv file and if we select return_csv_file as
        True returns csv file else
        returns csv file object

        Arguments:
            1. input_excel_file: It is a excel file path
               which is to be converted into csv file
            2. output_csv_file_path: If user gives the output csv path,
               then creating csv file at that path else creating a csv file
                in the directory from where he have given excel file.
            3. return_csv_file: If the user selects return_csv_file as True,
               returning the output csv file else returning the object.
        Returns:
            Returns the csv file path if user selects
            return_csv_file as True else returns the object.
    """
    try:
        if output_csv_file_path is None:
            if ".xlsx" in input_excel_file:
                ret_csv_file = input_excel_file.replace(".xlsx", ".csv")
            else:
                ret_csv_file = input_excel_file.replace(".xls", ".csv")
        else:
            ret_csv_file = output_csv_file_path

        wb = xlrd.open_workbook(input_excel_file)
        sh = wb.sheet_by_index(0)
        csv_file = open(ret_csv_file, 'wb+')
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        for rownum in xrange(sh.nrows):
            row_val = sh.row_values(rownum)
            for index, value in enumerate(row_val):
                if sh.cell(rownum, index).ctype == 3:
                    year, month, day, hour, minute, sec = xlrd.xldate_as_tuple(
                                                            value, wb.datemode)
                    date_format = "%02d/%02d/%04d" % (month, day, year)
                    row_val[index] = date_format
            wr.writerow(row_val)
        if return_csv_file:
            csv_file.close()
            csv_file = ret_csv_file
        else:
            csv_file = csv_file

    except Exception as exception:
        print_exception(exception)
        csv_file = None

    return csv_file


def convert_csv_or_excel_to_xml(input_file,
                                mapping_file=None, output_xml_file_path=None,
                                overwrite="yes"):
    """
        Takes file path as input
        1. If it is excel file, converts to csv and then converts
           csv file to xml
        2. If it is csv file, converts to xml file.
        3. Mapping file is used to map the column names in the excel sheet to
            a meaningful name as recognized by the code.

    Arguments:
        1. input_file: input_file which is either
           csv file path or excel file path
        2. mapping_file: If a mapping file path is given, it is used to map
           columns with the meaningful name as recognized by the user else
           the spaces in the column names will be replaced by "_" in
           the output xml
        3. output_xml_file_path: If user gives the output_xml_file_path,
           creating an xml file in that path else creating
           xml file in the path from where he have given csv or excel file.

    Returns:
        1. output_xml_file_path: Returns the output xml file path
        2  output_dict: Updates the output_dict with
           json string and with output xml.
    """
    output_dict = {}
    generate_csv = False
    try:
        if ".xls" in input_file:
            input_file = convert_excel_to_csv(input_file)
            generate_csv = True

        dict_response = convert_csv_to_list_of_dict(input_file)
        json_response = json.dumps(dict_response, sort_keys=False, indent=4,
                                   separators=(',', ': '), encoding="utf-8")

        if mapping_file:
            mapping_dict = data_Utils.get_credentials(mapping_file,
                                                      'mapping_scheme')

            mapping_dictionary = {v: k for k, v in mapping_dict.iteritems()}
        else:
            mapping_dictionary = {}

        result = []
        result.append(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<systems>\n")
        for i in xrange(len(dict_response)):
            result.append("  <system name="+"\""+str(i+1)+"\">\n")
            for key, value in dict_response[i].iteritems():
                if mapping_dictionary:
                    if key in mapping_dictionary and mapping_dictionary[key]:
                        result.append(
                            ("    <{0}>{1}</{0}>\n")
                            .format(mapping_dictionary[key], value))
                    else:
                        result.append(
                            ("    <{0}>{1}</{0}>\n").format(key, value))
                else:
                    result.append(
                        ("    <{0}>{1}</{0}>\n").format("_".join(key.split()),
                                                        value))

            result.append("  </system>\n")
        result.append("</systems>")

        xml_res = ''.join(result)
        if type(input_file) == file:
            input_file = input_file.name

        if generate_csv:
            os.remove(input_file)

        output_dict["{0}_json_response"
                    .format(input_file.replace(".csv", ''))] = json_response
        output_dict["{0}_xml_response"
                    .format(input_file.replace(".csv", ''))] = xml_res

        if output_xml_file_path:
            output_xml_file = output_xml_file_path
        else:
            output_xml_file = input_file.replace(".csv", ".xml")

        if overwrite == "no":
            output_xml_file = file_Utils.addTimeDate(output_xml_file)

        f = open(output_xml_file, "wb+")
        f.write(xml_res)
        f.close()

    except Exception as exception:
        print_exception(exception)
        output_xml_file = None
    
    return output_xml_file, output_dict


def convert_xml_to_csv(input_file, mapping_file=None,
                       output_csv_file_path=None, overwrite="yes"):
    """
        It takes xml file path as input and converts to csv.

        Arguments:
            1. input_file: Takes xml file path as input
            2. mapping_file: If a mapping file path is given, it is used to map
               columns with the meaningful name as recognized by the user else
               the tags in the xml file will be used as column names in
               the csv file.
            3. output_csv_file_path: If user gives the output_csv_file_path,
               creating an csv file in that path else creating
               csv file in the path from where he have given xml file.
        Returns:
            Returns output csv file path.
    """
    count = 0
    try:
        dict_response = xml_Utils.convert_xml_to_list_of_dict(input_file)
        if mapping_file:
            mapping_dict = data_Utils.get_credentials(mapping_file,
                                                      'mapping_scheme')

            mapping_dictionary = {v: k for k, v in mapping_dict.iteritems()}
        else:
            mapping_dictionary = {}

        if output_csv_file_path:
            output_csv_file = output_csv_file_path
        else:
            output_csv_file = input_file.replace(".xml", ".csv")

        if overwrite == "no":
            output_csv_file = file_Utils.addTimeDate(output_csv_file)

        f = open(output_csv_file, 'wb+')
        csvwriter = csv.writer(f)
        for element in dict_response:
            if count == 0:
                header = element.keys()
                for index, val in enumerate(header):
                    for key, value in mapping_dictionary.iteritems():
                        if val == value:
                            header[index] = key
                csvwriter.writerow(header)
                count += 1
            csvwriter.writerow(element.values())
        f.close()

    except Exception as exception:
        print_exception(exception)
        output_csv_file = None
    
    return output_csv_file
