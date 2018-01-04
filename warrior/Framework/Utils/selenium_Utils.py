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

"""This libraryprovides functionality for Selnium KW related data"""
import json
import os
import xml.etree.ElementTree as ET
from Framework.Utils import xml_Utils
from Framework.Utils import data_Utils
from Framework.Utils import config_Utils
from Framework.ClassUtils.WSelenium.browser_mgmt import BrowserManagement
from Framework.Utils.print_Utils import print_error, print_info
from Framework.Utils import file_Utils as file_Utils


def evaluate_argument_value(xpath_or_tagname, datafile):
    """This function takes checks if the given xpath_or_tagname exists in the
    datafile and returns its value. Else returns None."""
    tree = ET.parse(datafile)
    root = tree.getroot()
    if xpath_or_tagname.startswith(root.tag + "/"):
        xpath_or_tagname = xpath_or_tagname[len(root.tag + "/"):]
        try:
            xpath_or_tagname = root.find(xpath_or_tagname).text
        except Exception:
            print_error("Invalid xpath: {0}".format(root.tag + "/" + xpath_or_tagname))
            xpath_or_tagname = None
    else:
        print_error("Invalid xpath: {0}".format(xpath_or_tagname))
        xpath_or_tagname = None
    return xpath_or_tagname


def save_screenshot_onerror(status, current_browser):
    """ To get the filename, directory name and to take screenshot of the current browser window """
    if status != True:
        browser_object = BrowserManagement()
        data_repository = config_Utils.data_repository
        tc_name = data_repository['wt_testcase_filepath'].split("/")[-1].split('.xml')[0]
        step_number = data_repository['step_num']
        kw_name = data_repository['wt_keyword']
        filename = tc_name + "_" + "step-{0}".format(step_number) + "_" + kw_name
        browser_object.save_screenshot(current_browser, filename, data_repository['wt_defectsdir'])


def get_json_value_from_path(path, file, default):
    """This function returns the value of json key (it can also be a path)
    obtained from the json file."""
    data_dict = None
    flag = False
    try:
        data_dict = json.load(open(file, 'r'))
    except ValueError:
        if not default:
            print_error("Seems like the Configuration file: {0} is malformed".format(file))
    else:
        path_list = path.split("/")
        for key in path_list:
            if not key.endswith("]"):
                try:
                    if isinstance(data_dict, dict):
                        data_dict = data_dict[key]
                    elif isinstance(data_dict, list):
                        for i in range(0, len(data_dict)):
                            if key in data_dict[i]:
                                data_dict = data_dict[i][key]
                                flag = True
                                break
                        if not flag:
                            data_dict = None
                    else:
                        data_dict = None
                except KeyError:
                    if not default:
                        print_error("Key '{0}' not found in json of the {1}. "
                                    "{2} seems to be an invalid path".
                                    format(key, file, path))
                    data_dict = None
            else:
                key_list = key.split("[")
                try:
                    data_dict = data_dict[key_list[0]]
                except KeyError:
                    if not default:
                        print_error("Key '{0}' not found in json of the {1}. "
                                    "{2} seems to be an invalid path".
                                    format(key_list[0], file, path))
                    data_dict = None
                key_list[1] = key_list[1][:-1]
                try:
                    data_dict = data_dict[int(key_list[1])]
                except KeyError:
                    if not default:
                        print_error("Element '{0}' of key {1} not found in "
                                    "json of the {2}. {3} seems to be an "
                                    "invalid path".format(key_list[1],
                                                          key_list[0],
                                                          file, path))
                    data_dict = None
    return data_dict


def execute_script(browser_instance, user_script):
    """To exceute a user provided script """
    status = True
    print_info("executing user provided script")
    try:
        browser_instance.execute_script(user_script)
    except:
        print_error("Provide the correct input to execute a script")
        status = False
    return status


def split_kwargs_on_tag_equalto(kwargs, datafile, browser):
    """
    This function splits kwargs on tag=
    If the value is an xpath, then it follows the xpath and returns the value
    Else, if is it a singular tag name, then it searched for a tag with that
    name under the current <browser>
    """
    idf_data_dict = {}
    final_dict = {}
    for element in kwargs:
        if isinstance(kwargs[element], str) and kwargs[element] is not None and\
        kwargs[element] is not False:
            if kwargs[element].startswith("tag") and "=" in kwargs[element] \
                    and datafile is not None:
                temp_list = kwargs[element].split("=")
                temp_var = temp_list[1]
                for i in range(2, len(temp_list)):
                    temp_var = temp_var + "=" + temp_list[i]
                temp_var = temp_var.strip()
                if "/" in temp_var:
                    root = xml_Utils.getRoot(datafile)
                    idf_data_dict[element] = root.find(temp_var).text
                else:
                    if browser.get(temp_var, None) is None:
                        if browser.find(temp_var) is not None:
                            idf_data_dict[element] = browser.find(temp_var).text
                    else:
                        idf_data_dict[element] = browser.get(temp_var, None)
            else:
                final_dict[element] = kwargs[element]
        else:
            final_dict[element] = kwargs[element]

    return final_dict, idf_data_dict


def get_default_tags_from_datafile(kwargs, idf_data_dict, browser):
    """
    This function checks for default tags under the current <browser>
    """
    for element in kwargs:
        if browser.get(element, None) is None:
            if browser.find(element) is not None:
                idf_data_dict[element] = browser.find(element).text
        else:
            idf_data_dict[element] = browser.get(element, None)

    return idf_data_dict


def get_mappers_for_all_elements(final_dict, def_name_tuple):
    """
    This function gets the user defined mappings for tags and stores them in a
    mapper dictionary
    """
    mapper = {}
    for element in final_dict:
        if final_dict[element] is not None and final_dict[element] is not False and "=" in final_dict[element]:
            temp_list_1 = final_dict[element].split("=")
            if temp_list_1[0] in final_dict:
                if "=" in final_dict[temp_list_1[0]]:
                    temp_list_2 = final_dict[temp_list_1[0]].split("=")
                    mapper[element] = [temp_list_2[0], temp_list_1[0]]
                else:
                    mapper[element] = [temp_list_1[0], None]
            else:
                mapper[element] = [def_name_tuple[0], def_name_tuple[1]]
        else:
            mapper[element] = [def_name_tuple[0], def_name_tuple[1]]

    return mapper


def get_mapped_to_elements(mapper):
    """
    The mapper list contains all the element names that have been mapped to by
    other elements
    """
    mapper_list = []
    for element in mapper:
        for list_element in mapper[element]:
            if list_element not in mapper_list:
                mapper_list.append(list_element)
    return mapper_list


def update_final_dict_to_have_no_mappings(final_dict):
    """
    This function removes all mappings from the dictionary and only element
    values are retained
    """
    for element in final_dict:
        if final_dict[element] is not None and final_dict[element] is not False and "=" in final_dict[element]:
            temp_list = final_dict[element].split("=")
            if temp_list[0] in final_dict:
                temp_var = temp_list[1]
                for i in range(2, len(temp_list)):
                    temp_var = temp_var + "=" + temp_list[i]
                final_dict[element] = temp_var

    return final_dict


def get_final_json_values(element, final_dict, mapper, def_name_tuple):
    """
    This gets JSON values for every element and updates the dictionary
    """
    locator_types = {"locator_type": "locator",
                     "source_locator_type": "source_locator",
                     "target_locator_type": "target_locator"}
    reference = {"xpath": "xpath", "id": "id", "css_selector": "css",
                 "link_text": "link", "partial_link_text": "partial_link",
                 "tag_name": "tag", "class_name": "class",
                 "name_of_element": "name"}
    flag = False
    for key in locator_types:
        if element == locator_types[key]:
            flag = True
            break
    if element.lower() in reference:
        if mapper[element][0] == def_name_tuple[0] and mapper[element][1] == def_name_tuple[1]:
            value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                 final_dict[mapper[element][1]],
                                                 reference[element.lower()],
                                                 default=True)
        else:
            if mapper[element][1] is not None:
                value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                     final_dict[mapper[element][1]],
                                                     reference[element.lower()])
            else:
                value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                     None,
                                                     reference[element.lower()])
        final_dict[element] = value
    elif element.lower() in locator_types:
        if mapper[element][0] == def_name_tuple[0] and mapper[element][1] == def_name_tuple[1]:
            value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                 final_dict[mapper[element][1]],
                                                 final_dict[element],
                                                 is_locator_type="yes",
                                                 default=True)
        else:
            if mapper[element][1] is not None:
                value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                     final_dict[mapper[element][1]],
                                                     final_dict[element],
                                                     is_locator_type="yes")
            else:
                value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                     None, final_dict[element],
                                                     is_locator_type="yes")
        final_dict[element] = value[0]
        final_dict[locator_types[element]] = value[1]
    elif flag:
        pass
    else:
        if mapper[element][0] == def_name_tuple[0] and mapper[element][1] == def_name_tuple[1]:
            value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                 final_dict[mapper[element][1]],
                                                 element, default=True)
        else:
            if mapper[element][1] is not None:
                value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                     final_dict[mapper[element][1]],
                                                     element)
            else:
                value = get_element_from_config_file(final_dict[mapper[element][0]],
                                                     None, element)
        final_dict[element] = value
    return final_dict


def get_browser_details(browser, datafile=None, br_name="browser_name",
                        def_name_tuple=("DEF_ecf", "DEF_et"),
                        bw_comp=("element_config_file", "element_tag"), **kwargs):
    """This function returns the correct browser details by evaluating the data
    files and the element config files"""

    # Gets all tags from the data file and adds it to idf_data_dict.
    # kwargs remains intact

    final_dict, idf_data_dict = split_kwargs_on_tag_equalto(kwargs, datafile, browser)

    # Gets all default tags from the data file and adds it to idf_data_dict.
    # idf_data_dict maintains all the data gotten from the data file
    idf_data_dict = get_default_tags_from_datafile(kwargs, idf_data_dict, browser)

    final_dict.update(idf_data_dict)

    # To maintain backward compatibilty
    for dnt_el, bwc_el in zip(def_name_tuple, bw_comp):
        if (dnt_el not in final_dict or final_dict[dnt_el] is None) and bwc_el in final_dict:
            final_dict[dnt_el] = final_dict[bwc_el]

    # gets mappings of all elements
    mapper = get_mappers_for_all_elements(final_dict, def_name_tuple)
    mapper_list = get_mapped_to_elements(mapper)

    # final_dict updated to contain only element values and no mappings
    final_dict = update_final_dict_to_have_no_mappings(final_dict)

    # All mapping dependent values get updated from json file
    for element in final_dict:
        if element not in mapper_list:
            final_dict = get_final_json_values(element, final_dict, mapper, def_name_tuple)

    # All the mapped-to elements get updated from the json file
    for element in final_dict:
        if element in mapper_list:
            final_dict = get_final_json_values(element, final_dict, mapper, def_name_tuple)

    # since data file has priority, vales from data file get imposed on the
    # json values
    for element in final_dict:
        if element in idf_data_dict and idf_data_dict[element] is not None and idf_data_dict[element] is not False:
            final_dict[element] = idf_data_dict[element]

    # Finally, if arguments are still None, the defaults and alues from the
    # testcases are applied
    for element in final_dict:
        if final_dict[element] is None:
            if element in kwargs:
                final_dict[element] = kwargs[element]

    # Browser name matching
    if kwargs[br_name] != "all" and final_dict[br_name] != kwargs[br_name]:
        return None

    final_dict = data_Utils.sub_from_env_var(final_dict)

    return final_dict


def get_default_tag_for_locs(config_file, element_tag, locator_types):
    """This function gets the default value of the locator_type from the
    element config file."""
    output = [None, None]
    with open(config_file) as data_file:
        data = json.load(data_file)
    try:
        locator = data[element_tag]
    except KeyError:
        print_error("No tag with the name {0} found!".format(element_tag))
    else:
        counter = 0
        for element in locator:
            for key in element:
                if key.strip().lower() == "default" and \
                                element[key].strip().lower() == "yes":
                    for locator_type in locator_types:
                        if locator_type in element:
                            output = [locator_type, element[locator_type]]
                            counter = 1
                            break
                if counter == 1:
                    # Flag helps break out of loop to avoid unnecessary
                    # computations
                    break
            if counter == 1:
                # Flag helps break out of loop to avoid unnecessary
                # computations
                break
        # Flag helps identify if match was found earlier
        if counter == 0:
            # Iterates through the list
            for element in locator:
                # Iterates through the dictionary in each list
                for key in element:
                    # Checks if key exists in locator types
                    if key in locator_types:
                        output = [key, element[key]]
                        # Sets flag to 1 if match is found
                        counter = 1
                        break
                if counter == 1:
                    # Flag helps break out of loop to avoid unnecessary
                    # computations
                    break
    return output


def get_element_from_config_file(config_file, element_tag, child_tag,
                                 is_locator_type="no", default=False):
    """
    Gets default locators from json file
    """
    locator_types = ("xpath", "id", "css", "link", "partial_link", "tag",
                     "class", "name")
    wt_datafile = data_Utils.get_object_from_datarepository('wt_datafile') 
    if wt_datafile: 
        config_file = file_Utils.getAbsPath(config_file, os.path.dirname(wt_datafile))
    if config_file is not None and config_file is not False:
        if child_tag in locator_types:
            if element_tag is not None:
                final_value = get_json_value_from_path(element_tag + "/" + child_tag, config_file, default)
            else:
                final_value = get_json_value_from_path(child_tag, config_file, default)
            if is_locator_type == "yes":
                final_value = [child_tag, final_value]
        else:
            if child_tag is not None:
                if element_tag is not None:
                    final_value = get_json_value_from_path(element_tag + "/" + child_tag, config_file, default)
                else:
                    final_value = get_json_value_from_path(child_tag, config_file, default)
            else:
                if element_tag is not None:
                    final_value = get_default_tag_for_locs(config_file, element_tag, locator_types)
                else:
                    final_value = get_default_tag_for_locs(config_file, child_tag, locator_types)
    else:
        if is_locator_type == "yes":
            final_value = [None, None]
        else:
            final_value = None
    return final_value

def create_display():
    """
        Create a virtual display
        Default size is 1920x1080 as smaller resolution
        may cause problem in firefox
    """
    status = True
    if data_Utils.get_object_from_datarepository("headless_display"):
        return status
    try:
        from pyvirtualdisplay import Display
        # Selenium has problem with firefox in virtualdisplay if resolution is low
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        print_info("Running in headless mode")
    except ImportError:
        print_error("pyvirtualdisplay is not installed in order "
                    "to launch the browser in headless mode")
        status = False
    except Exception as err:
        print_error("Encountered Exception: {0}, while trying to launch the browser"
                    " in headless mode".format(err))
        status = False
    return status
