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

""" Module contains database related classes and its methods """
import os
import xml.etree.ElementTree as ET

import Tools
from Framework.Utils import xml_Utils
from Framework.Utils.print_Utils import print_warning, print_info


def create_database_connection(server_type="resultservers", dbsystem=None):
    """ To create object for the database class based on the dbsystem:dbtype
    value of server_type in Tools/database/database_config.xml """
    db_config_fpath = 'database/database_config.xml'
    db_config_xml = os.path.join(Tools.__path__[0],
                                 db_config_fpath)

    db_type_list = get_database_details(db_config_xml, server_type,
                                        dbsystem, ['dbtype'])

    if db_type_list is False:
        db_type = False
    else:
        db_type = db_type_list['dbtype']

    db_conn = False
    if db_type == "mongodb":
        details_dict = get_database_details(db_config_xml,
                                            server_type, dbsystem,
                                            ['host', 'port', 'uri', 'dbname'])
        if details_dict is not False:
            details_dict.update({'server_type': server_type,
                                 'dbsystem': dbsystem})
            db_conn = WMongodb(details_dict)
            db_conn = db_conn if db_conn.status is True else False

    return db_conn


def get_database_details(config_file, server_type, system_name, info_list):
    """ To get the database system details from database config file """

    system = server_type + "/system"
    if system_name is not None:
        element = xml_Utils.getElementWithTagAttribValueMatch(config_file,
                                                              system,
                                                              'name',
                                                              system_name)
    else:
        element = xml_Utils.getElementWithTagAttribValueMatch(config_file,
                                                              system,
                                                              'default',
                                                              "true")
        if element is None:
            node_value = xml_Utils.getNodeValuebyAttribute(config_file,
                                                           system,
                                                           'name')
            element = xml_Utils.getElementWithTagAttribValueMatch(
                        config_file, system, 'name', node_value)

    if element is not None and element is not False:
        output_dict = {}
        for item in info_list:
            output_dict[item] = xml_Utils.get_text_from_direct_child(
                                element, item)
        return output_dict
    else:
        if system_name is not None:
            msg = "There is no system with name: '{0}' under '{1}' in " \
                  "the database config file: '{2}'".format(system_name,
                                                           server_type,
                                                           config_file)
            print_warning(msg)
        elif server_type == "dataservers":
            msg = "Value for td_system/var_system tag is not provided in " \
                  "the datafile and there is no system listed in database " \
                  "config file under dataservers block to be used as default"
            print_warning(msg)

        return False


class WMongodb(object):
    """ Class to handle mongodb operations to add html results """

    def __init__(self, details_dict=False):
        """ constructor """

        self.status = False
        if details_dict is not False:
            try:
                self.pymongo = __import__('pymongo')
                self.conn = self.connect_mongodb(details_dict)
                self.dbname = details_dict['dbname']
                if self.conn is not False:
                    # no need to check the existence of database when the
                    # purpose is to store results, new database will be
                    # created if it is not there in the server
                    if details_dict['server_type'] == 'resultservers':
                        self.status = True
                    else:
                        if self.dbname in self.conn.database_names():
                            # print_info("database - '{}' is found in MongoDB "
                            #            "server".format(self.dbname))
                            self.status = True
                        else:
                            print_warning("database - '{}' is not in MongoDB "
                                          "server".format(self.dbname))
                    self.db = self.conn[self.dbname]
            except ImportError:
                print_warning("pymongo module is not installed and Warrior "
                              "Framework uses it for establishing "
                              "connection with MongoDB server")

    def connect_mongodb(self, details_dict):
        """ Establish connection with the mongodb server.
        URI or IP/port combination is supported in mongodb config file,
        URI will have higher precedence over IP/Port """

        conn = False
        try:
            if details_dict:
                if details_dict['uri'] is not False:
                    conn = self.pymongo.MongoClient(details_dict['uri'])
                else:
                    ip = details_dict['host'] if details_dict['host'] \
                        is not False else "localhost"
                    port = details_dict['port'] if details_dict['port'] \
                        is not False else "27017"
                    conn = self.pymongo.MongoClient(ip, port)
                # This will raise ServerSelectionTimeoutError when no server
                # is available for an operation
                conn.server_info()
                # print_info("Connection to MongoDB server - '{}' is "
                #            "successful".format(details_dict['dbsystem']))
        except Exception as e:
            conn = False
            print_warning("Unable to establish connection with MongoDB server "
                          "- '{0}' : {1}".format(details_dict['dbsystem'], e))
        return conn

    def close_connection(self):
        """ To close database connection """

        self.conn.close()

    def get_file_type(self, root):
        """ To get the type of warrior execution file - case/suite/project """

        proj_attrib = root.attrib
        # Project
        if proj_attrib['name'] != \
           "customProject_independant_testcase_execution":
            file_type = "project"
        else:
            suite_elem = root.findall('testsuite')
            # Suite
            if suite_elem[0].attrib['name'] != \
               "customTestsuite_independant_testcase_execution":
                file_type = "suite"
            # Case
            else:
                file_type = 'case'

        return file_type

    def get_html_results(self, file_type, root):
        """ To get the results from the junit root element """

        if file_type == 'case':
            case_elem = root.findall('testsuite')[0].\
             findall('testcase')[0]
            results_dict = self.get_details_from_case_element(case_elem)
        elif file_type == 'suite':
            suite_elem = root.findall('testsuite')[0]
            results_dict = self.get_details_from_suite_element(suite_elem)
        elif file_type == 'project':
            results_dict = self.get_details_from_project_element(root)

        return results_dict

    def get_details_from_case_element(self, case_elem):
        """ To get the details from JUnit case element(xml) """

        case_dict = case_elem.attrib
        kw_list = case_elem.findall('keyword')
        case_dict['kw_results'] = {}
        for num, kw_element in enumerate(kw_list, 1):
            case_dict['kw_results'][str(num)] = kw_element.attrib

        return case_dict

    def get_details_from_suite_element(self, suite_elem):
        """ To get the details from JUnit suite element(xml) """

        suite_dict = suite_elem.attrib
        case_list = suite_elem.findall('testcase')
        suite_dict['case_results'] = {}
        for num, case_elem in enumerate(case_list, 1):
            suite_dict['case_results'][str(num)] = \
             self.get_details_from_case_element(case_elem)

        return suite_dict

    def get_details_from_project_element(self, proj_elem):
        """ To get the details from JUnit project element(xml) """

        proj_dict = proj_elem.attrib
        suite_list = proj_elem.findall('testsuite')
        proj_dict['suite_results'] = {}
        for num, suite_elem in enumerate(suite_list, 1):
            proj_dict['suite_results'][str(num)] = \
             self.get_details_from_suite_element(suite_elem)

        return proj_dict

    def add_html_result_to_mongodb(self, input_xml):
        """ To add case/suite/project results as a document to MongoDB
        database collections, here collection names are case/suite/project """

        root = xml_Utils.getRoot(input_xml)
        file_type = self.get_file_type(root)
        results_dict = self.get_html_results(file_type, root)

        coll_dict = {'case': 'case_html_results',
                     'suite': 'suite_html_results',
                     'project': 'project_html_results'}

        collection = self.db[coll_dict.get(file_type)]

        # create a new document with _id as case/suite/project name
        if collection.find({'_id': results_dict['name']}).count() == 0:
            collection.insert({'_id': results_dict['name']})

        collection.update({'_id': results_dict['name']},
                          {'$push': {'results': results_dict}})
        print_info("Successfully added html results in MongoDB database")

    # ToDo - This method has to be modified after XML schema update
    # This will work only for the current testcase xml format - 25/01/2017
    def get_details_from_case_xml_element(self, case_xml_elem):
        """ To get the details from testcase xml element """

        child_list = xml_Utils.\
            getChildElementsListWithSpecificXpath(case_xml_elem, "*")
        child_dict = {}
        for child in child_list:
            value = self.get_details_from_case_xml_element(child)
            if child.tag not in child_dict:
                if child.tag not in ['Note', 'SubStep', 'Requirement',
                                     'argument']:
                    child_dict[child.tag] = [value] if value != {} \
                     else child.text
                elif child.tag == "argument":
                    child_dict[child.tag] = [value] if value != {} \
                     else {child.attrib['name']: child.attrib['value']}
                else:
                    child_dict[child.tag] = [value] if value != {} \
                     else [child.text]
            else:
                if child.tag != 'argument':
                    child_dict[child.tag].append(value if value != {}
                                                 else child.text)
                else:
                    child_dict[child.tag].update({child.attrib['name']:
                                                  child.attrib['value']})
        return child_dict

    def add_xml_result_to_mongodb(self, input_xml):
        """ To add case xml results as a document to the MongoDB database
        collection - 'case' """

        root = xml_Utils.getRoot(input_xml)
        collection = self.db['case_xml_results']
        results_dict = self.get_details_from_case_xml_element(root)
        case_name = os.path.basename(os.path.splitext(input_xml)[0])

        # create a new document with _id as case_xml_results
        if collection.find({'_id': case_name}).count() == 0:
            collection.insert({'_id': case_name})

        collection.update({'_id': case_name},
                          {'$push': {'results': results_dict}})

        print_info("Successfully added case xml results in MongoDB database")

    def get_doc_from_db(self, collection_name, document_name):
        """ To get the document from the database by matching document_name
        with '_id' field of each document. It will return False if the document
        doesn't exist """

        tddoc = False
        if collection_name in self.db.collection_names():
            # print_info("collection - '{}' is found in the MongoDB "
            #            "server".format(collection_name))
            collection = self.db[collection_name]
            testdata = collection.find({'_id': document_name})
            if testdata.count() == 1:
                tddoc = testdata[0]
            #     print_info("Document - '{}' is found in the MongoDB "
            #                "server".format(document_name))
            else:
                print_warning("Document - '{}' is not found in the MongoDB "
                              "server".format(document_name))
        else:
            print_warning("collection - '{}' is not found in the MongoDB "
                          "server".format(collection_name))

        return tddoc

    def convert_tddict_to_xmlobj(self, root, tddict):
        """
        To Convert the testdata dictionary into a xml object.

        Testdata dictionary can have following combinations :
            1. dict within dict
            2. list within dict
            3. dict within list

        """

        for element in tddict:
            if isinstance(tddict[element], dict):
                self.convert_tddict_to_xmlobj(ET.SubElement(root, element),
                                              tddict[element])
            elif isinstance(tddict[element], list):
                for list_elem in tddict[element]:
                    # here list can only have dictionary in it
                    if isinstance(list_elem, dict):
                        self.convert_tddict_to_xmlobj(ET.SubElement(root,
                                                                    element),
                                                      list_elem)
            else:
                root.set(element, tddict[element])

    def get_tdblock_as_xmlobj(self, db_details):
        """ To get the testdata blocks from the database as xml object """

        rootobj = False
        td_collection = db_details.get('td_collection')
        td_document = db_details.get('td_document')

        if td_collection is not None and td_document is not None:
            tddoc = self.get_doc_from_db(td_collection, td_document)
        else:
            tddoc = False

        if tddoc is not False:
            root = ET.Element('data')
            self.convert_tddict_to_xmlobj(root, tddoc['data'])
            rootobj = root

        return rootobj

    def get_globalblock_as_xmlobj(self, db_details):
        """ To get the global block from the database as xml object """

        globalobj = False
        global_collection = db_details.get('global_collection')
        global_document = db_details.get('global_document')

        if global_collection is not None and global_document is not None:
            globaldoc = self.get_doc_from_db(global_collection,
                                             global_document)
        else:
            globaldoc = False

        if globaldoc is not False:
            global_root = ET.Element('global')
            self.convert_tddict_to_xmlobj(global_root, globaldoc['global'])
            globalobj = global_root

        return globalobj

    def get_varblock_as_xmlobj(self, db_details):
        """ To get the variable config details from the
        database as xml object """

        varobj = False
        var_collection = db_details.get('var_collection')
        var_document = db_details.get('var_document')

        if var_collection is not None and var_document is not None:
            vardoc = self.get_doc_from_db(var_collection, var_document)
        else:
            vardoc = False

        if vardoc is not False:
            var_root = ET.Element('configuration')
            self.convert_tddict_to_xmlobj(var_root, vardoc['configuration'])
            varobj = var_root

        return varobj
