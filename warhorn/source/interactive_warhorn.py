#!/usr/bin/env python

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

"""This file prompts the user to enter information about the repositories and
dependencies that s/he wants to clone into her/his machine.
This is the interactive mode of warhorn."""
import os
import shutil
import subprocess
import xml.etree.ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element
import re
import sys

from utils import get_firstlevel_children, create_dir, get_repository_name, \
    get_subfiles, delete_read_only, get_relative_path, get_parent_dir


def confirm_url(question, attrib_value):
    """ This function recursively checks whether a given url is a valid
    repository or not. If it isn't, it promps the user to enter a new url and
    checks that.

    :Arguments:

    1. question (xml.etree.ElementTree.Element) = The question tag from data.xml
    2. attrib_value (str) = the url to be checked

    :Returns:

    1. attrib_value (str) = valid url

    """
    if not check_url_is_a_valid_repo(attrib_value):
        attrib_value = raw_input("Please enter a valid URL: ")
        attrib_value = confirm_url(question, attrib_value)
    return attrib_value


def validate_input(question, attrib_name, answer):
    """ This function validates the input values for tags in the data.xml
    that will eventually become attributes in the new xml file

    :Arguments:

    1. question (xml.etree.ElementTree.Element) = The question tag from data.xml
    2. attrib_name (str) = name of the tags from data.xml that will
    eventually become attribute names
    3. answer (str) = user response associated with that particular tag name


    :Returns:

    1. answer (str) = valid user response


    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    if attrib_name == "dependency":
        if aff_pattern.match(answer):
            return "yes"
        elif neg_pattern.match(answer):
            return "no"
        else:
            print "The command was not recognized. Please answer 'yes' or 'no'."
            answer = raw_input(question.text)
            answer = validate_input(question, attrib_name, answer)
    if attrib_name == "clone":
        if aff_pattern.match(answer):
            global STATE
            STATE = "yes"
            return "yes"
        elif neg_pattern.match(answer):
            global STATE
            STATE = "no"
            return "no"
        else:
            print "The command was not recognized. Please answer 'yes' or 'no'."
            answer = raw_input(question.text)
            answer = validate_input(question, attrib_name, answer)
    elif attrib_name == "destination":
        answer = validate_path(answer)
    elif attrib_name == "clean_install":
        if aff_pattern.match(answer):
            return "yes"
        elif neg_pattern.match(answer):
            return "no"
        else:
            print "The command was not recognized. Please answer 'yes' or 'no'."
            answer = raw_input(question.text)
            answer = validate_input(question, attrib_name, answer)
    return answer


def show_suggestion_get_answer(node, attrib_value, suggestion):
    """ This function 'suggests' a tentative url of the git repository that
    the user wants to clone. The user has the ability to accept the suggested
    url or reject it and give a url of his own

    :Arguments:

    1. node (xml.etree.ElementTree.Element) = the parent node of the
    suggestion tag from data.xml
    2. attrib_value (str) = contains the name of the repository that the user
    wants to clone
    3. suggestion (xml.etree.ElementTree.Element) = suggestion tag from data.xml

    :Returns:

    1. suggestion_content (str) = The complete, suggested url
    2. answer (str) = valid user response

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    suggestion_content = suggestion.text
    if node.attrib["name"] == 'repository':
        suggestion_content = suggestion_content + attrib_value + ".git"
        print "The suggested URL is: " + suggestion_content
    else:
        print "The suggested URL is: " + suggestion_content
    answer = raw_input("Do you want to use this URL? (yes[Enter]/no):")
    if not (aff_pattern.match(answer) or neg_pattern.match(answer)):
        print "The command was not recognized. Please answer yes or no."
        suggestion_content, answer = show_suggestion_get_answer(node,
                                                                attrib_value,
                                                                suggestion)
    return suggestion_content, answer


def check_url_is_a_valid_repo(url):
    """ This function checks if the url is a valid git repository or not

    :Arguments:

    1. url (str) = url of a repository

    :Returns:

    1. bool (True/False) = True is url is a valid repository, False if not

    """
    try:
        _ = subprocess.check_output(["git", "ls-remote", url])
    except:
        print url + " is not a valid git repository"
        return False
    print url + " is available"
    return True


def get_driver_list(pd_file_names):
    """

    :Arguments:

    1. pd_file_names (list[str]) = All the files names obtained from the
    ProductDrivers directory of the repository that is temporarily cloned
    into the user's machine

    :Returns:

    2. driver_list (list[str]) = This list contains serial numbers and the
    driver names alternately

    eg: [1, driver_name_1, 2, driver_name_2, 3, driver_name_3]

    """
    subfiles = []
    driver_list = []
    for subfile in pd_file_names:
        if subfile.endswith('.py'):
            subfiles.append(subfile)
    for i, subfile in zip(range(0, len(subfiles)), subfiles):
        driver_list.append(str(i+1))
        driver_list.append(subfile)
    return driver_list


def get_corresponding_numbers():
    """This function validates the string of numbers entered by the user. Any
    alphabet, characters that may be found are elimintaed. a single 0 is also
     eliminated here. The string is converted into a list of int. space is used
     as a separator.

    :Returns:

    1. number_list (list[int]) = list of numbers

    """
    number_set = set()
    answer = raw_input("Please enter the corresponding number of the drivers "
                       "you want to clone. Separate the numbers with a space: ")
    pattern = re.compile("^[0-9]*$")

    for characters in answer.split():
        if pattern.match(characters):
            if characters == '0':
                print characters + " does not have a corresponding driver."
            else:
                number_set.add(int(characters))
        else:
            print characters + " is not a valid number"

    return list(number_set)


def add_drivers_to_tags(tag, drivers, driver_numbers):
    """ This function appends the driver tags sets the attributes and
    attribute names to the corresponding driver tag

    :Arguments:

    1. tag (xml.etree.ElementTree.Element) = Current tag to which the newly
    formed driver tags may be appended
    2. drivers (list[str]) = list of driver names available to the user
    3. driver_numbers (list[int]) = list of the numbers which correspond to
    the driver names that the user wants.

    """
    print "Selected drivers:"
    for driver_number in driver_numbers:
        driver_number = driver_number * 2 - 1
        if driver_number > len(drivers):
            print "Corresponding driver for " + str((driver_number+1)/2) +\
                  " not found."
            continue
        print str((driver_number+1)/2) + ". " + drivers[driver_number]
        driver_tag = Element("driver")
        driver_tag.set("name", drivers[driver_number])
        tag.append(driver_tag)


def transform_response(answer):
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    if aff_pattern.match(answer):
        return "yes"
    if neg_pattern.match(answer):
        return "no"


def clone_kw_repo(root, question, attrib_value, tag):
    """ This function clones the keyword repository if the user wants
    individual drivers of that repository. Otherwise, it just sets the
    attribute "all_drivers" of that repository tag as 'yes'

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = parent node of the current tag
    from data.xml
    2. question (xml.etree.ElementTree.Element) = question tag nested under
    the current tag from data.xml
    3. attrib_value (str) = url of the repository in question
    4. tag (xml.etree.ElementTree.Element) = current tag to which the
    repository tags would be appended.

    :Returns:

    1. attrib_value (str) = valid url

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    if not check_url_is_a_valid_repo(attrib_value):
        attrib_value = raw_input("Please enter a valid url: ")
        attrib_value = clone_kw_repo(root, question, attrib_value, tag)
    else:
        if root.tag == "drivers":
            name = get_repository_name(attrib_value)
            answer = raw_input("Do you want to clone all the drivers? "
                               "(yes[Enter]/no): ")
            answer = transform_response(answer)
            tag.set("all_drivers", answer)
            if neg_pattern.match(answer):
                current_dir = os.path.dirname(os.path.realpath(__file__))
                path = os.path.join(current_dir, "temp")
                create_dir(path)
                os.chdir(path)
                subprocess.call(["git", "clone", attrib_value])
                os.chdir(current_dir)
                temp, _ = get_subfiles(os.path.join(path, name,
                                                    'ProductDrivers'))
                drivers = get_driver_list(temp)

                for i in range(1, len(drivers), 2):
                    print drivers[i-1] + ". " + drivers[i]

                driver_numbers = get_corresponding_numbers()
                add_drivers_to_tags(tag, drivers, driver_numbers)
                shutil.rmtree(path, onerror=delete_read_only)
            elif not aff_pattern.match(answer):
                print "The command was not recognized. Please answer yes or no."
                attrib_value = clone_kw_repo(root, question, attrib_value, tag)
    return attrib_value


def populate_repo_tags(root, current_element, attrib_value, node, tag):
    """ This function retrieves information from data.xml and asks user for
    input. It also sets the attributes and their corresponding values of the
    tag in question.

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = parent of the current tag
    2. current_element (xml.etree.ElementTree.Element) = current tag that is
    being evaluated from data.xml
    3. attrib_value (str) = user response
    4. node (xml.etree.ElementTree.Element) = node used to create the tag
    5. tag (xml.etree.ElementTree.Element) = tag created using the node

    :Returns:

    1. attrib_value (str) = valid user response

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    answer = "no"
    suggestion_content = ""
    info = current_element.find("info")
    if info is not None:
        print info.text
    suggestion = current_element.find("suggestion")
    if suggestion is not None:
        suggestion_content = suggestion.text + attrib_value + ".git"
        print "The suggested URL is: " + suggestion_content
        answer = raw_input("Do you want to use this URL? (yes[Enter]/no): ")
        if not (aff_pattern.match(answer) or neg_pattern.match(answer)):
            print "The command was not recognized. Please answer yes or no."
            suggestion_content, answer = \
                show_suggestion_get_answer(node, attrib_value, suggestion)
    question = current_element.find("question")
    if question is not None:
        if aff_pattern.match(answer):
            attrib_value = suggestion_content
            if current_element.attrib["name"] == "url":
                attrib_value = clone_kw_repo(root, question, attrib_value, tag)
        else:
            attrib_value = raw_input(question.text)
            if current_element.attrib["name"] == "url":
                attrib_value = clone_kw_repo(root, question, attrib_value, tag)
            else:
                attrib_value = validate_input(question,
                                              current_element.attrib["name"],
                                              attrib_value)
        tag.set(current_element.attrib["name"], attrib_value)

    return attrib_value


def get_multiple_repos(root, node, attrib_value, temp_values_list):
    """ This function lets the user fill in details for multiple repositories.

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = parent of the current tag
    2. node (xml.etree.ElementTree.Element) = current tag from data.xml
    3. attrib_value (str) = user response
    4. temp_values_list (list[xml.etree.ElementTree.Element]) = list of nodes
    that need to be filled out each time the user wants to add a new repository.

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    response = raw_input("Do you want to clone another repository? "
                         "(yes[Enter]/no): ")
    if aff_pattern.match(response):
        tag = Element(node.attrib["name"])
        root.append(tag)
        for i in range(0, len(temp_values_list)):
            attrib_value = populate_repo_tags(root, temp_values_list[i],
                                              attrib_value, node, tag)
        get_multiple_repos(root, node, attrib_value, temp_values_list)
    elif not neg_pattern.match(response):
        print "The command was not recognized. Please answer yes or no."
        get_multiple_repos(root, node, attrib_value, temp_values_list)


def install_all_dependencies(root, node, tag, attribute, values, answer):
    """ This function can set the value of the attribute 'install' of all the
    dependencies to 'yes' or 'no' by prompting the user for an input.

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = parent of the current tag
    2. node (xml.etree.ElementTree.Element) = current tag from data.xml
    3. tag (xml.etree.ElementTree.Element) = current tag that is being
    changed and updated for the new xml file
    4. attribute (xml.etree.ElementTree.Element) = The current attribure tag
    5. values (list[xml.etree.ElementTree.Element]) = complete list of
    value tags in that particular nesting from data.xml
    6. answer (str) = user response

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    if aff_pattern.match(answer):
        print "All dependencies will get installed"
    else:
        print "No dependencies will get installed"
    answer = transform_response(answer)
    for i in range(0, len(values)):
        if i != 0:
            newnode = Element(node.attrib["name"])
            root.append(newnode)
        if i == 0:
            tag.set("install", answer)
            tag.set(attribute.attrib["name"], values[i].attrib["name"])
        else:
            newnode.set("install", answer)
            newnode.set(attribute.attrib["name"], values[i].attrib["name"])


def install_select_dependencies(root, node, tag, attribute, values):
    """This function can set the value of the attribute 'install' of selected
    dependencies to 'yes' or 'no' by prompting the user for an input for each
    dependency.

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = parent of the current tag
    2. node (xml.etree.ElementTree.Element) = current tag from data.xml
    3. tag (xml.etree.ElementTree.Element) = current tag that is being
    changed and updated for the new xml file
    4. attribute (xml.etree.ElementTree.Element) = The current attribure tag
    5. values (list[xml.etree.ElementTree.Element]) = complete list of
    value tags in that particular nesting from data.xml

    """
    for i in range(0, len(values)):
        if i != 0:
            newnode = Element(node.attrib["name"])
            root.append(newnode)
        question = values[i].find("question")
        if question is not None:
            attrib_value = raw_input(question.text)
            attrib_value = validate_input(question, node.attrib["name"],
                                          attrib_value)
            if i == 0:
                tag.set("install", attrib_value)
                tag.set(attribute.attrib["name"], values[i].attrib["name"])
            else:
                newnode.set("install", attrib_value)
                newnode.set(attribute.attrib["name"], values[i].attrib["name"])


def get_answer_for_depen(root, node, tag, attribute, values):
    """This function allows the user to say yes to installing all
    dependencies, or no to installing all dependencies, or the user can type
    in select to choose which dependencies to install.

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = parent of the current tag
    2. node (xml.etree.ElementTree.Element) = current tag from data.xml
    3. tag (xml.etree.ElementTree.Element) = current tag that is being
    changed and updated for the new xml file
    4. attribute (xml.etree.ElementTree.Element) = The current attribure tag
    5. values (list[xml.etree.ElementTree.Element]) = complete list of
    value tags in that particular nesting from data.xml

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    sel_pattern = re.compile("^(select)$", re.IGNORECASE)
    print ""
    answer = raw_input("Please enter 'yes' if you want to install all the "
                       "dependencies, 'no' if you don't want to install any "
                       "of the dependency, and 'select' if you would like to "
                       "choose which dependency to install. "
                       "(yes[Enter]/no/select): ")
    if aff_pattern.match(answer) or neg_pattern.match(answer):
        install_all_dependencies(root, node, tag, attribute, values, answer)
    elif sel_pattern.match(answer):
        install_select_dependencies(root, node, tag, attribute, values)
    else:
        print "The command was not recognized. Please answer yes or no or " \
              "select."
        get_answer_for_depen(root, node, tag, attribute, values)


def diff_attributes_values(root, node, tag, attribute, values):
    """ This function creates tags in the new xml file which contain
    information about the value tags from data.xml

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = parent of the current node from
    data.xml
    2. node (xml.etree.ElementTree.Element) = current node from data.xml
    3. tag (xml.etree.ElementTree.Element) = current node that would be added
    to the new xml file
    4. attribute (xml.etree.ElementTree.Element) = The current attribure tag
    5. values (list[xml.etree.ElementTree.Element]) = complete list of
    value tags in that particular nesting from data.xml

    """
    for i in range(0, len(values)):
        info = values[i].find("info")
        if info is not None:
            print info.text
    print "Warrior recommends that all these dependencies be installed on" \
          " your machine."
    get_answer_for_depen(root, node, tag, attribute, values)


def get_and_validate_response(response, repo_type):
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    if aff_pattern.match(response) or neg_pattern.match(response):
        return response
    else:
        print "Command not recognized. Please type 'yes' or 'no'."
        response = raw_input("Do you want to clone a " + repo_type +
                             "repository? (yes[Enter]/no): ")
        response = get_and_validate_response(response, repo_type)
    return response


def get_final_attrib_value(question, answer, suggestion_content, attribute):
    """
    This functions validates the final attribute value that would be written
    into the xml file
    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    if aff_pattern.match(answer):
        attrib_value = suggestion_content
    else:
        attrib_value = raw_input(question.text)
        if attribute.attrib["name"] == "url":
            attrib_value = confirm_url(question, attrib_value)
        else:
            attrib_value = validate_input(question, attribute.attrib["name"], attrib_value)
    return attrib_value


def get_url_for_main_repos(suggestion, node):
    """
    This function gets the value of the url for warrior_main and katana.
    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    suggestion_content = suggestion.text
    repo_name = suggestion_content.rsplit('/', 1)[-1]
    repo_name = repo_name.split(".")[0]
    print "For " + repo_name + ": "
    print "The suggested URL is: " + suggestion_content
    answer = raw_input("Do you want to use this URL? (yes[Enter]/no): ")
    if not (aff_pattern.match(answer) or neg_pattern.match(answer)):
        print "The command was not recognized. Please answer yes or no."
        suggestion_content, answer = show_suggestion_get_answer(node, "", suggestion)
    return suggestion_content, answer


def same_attributes_values(root, node, tag, attributes, repo_type):
    """ This function  creates tags in the new xml file which contain
    information about the any tags that are not value tags from data.xml

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = parent of the current node from
    data.xml
    2. node (xml.etree.ElementTree.Element) = current node from data.xml
    3. tag (xml.etree.ElementTree.Element) = current node that would be added
    to the new xml file
    4. attributes (list[xml.etree.ElementTree.Element]) = complete list of
    attribute tags in that particular nesting from data.xml

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    attrib_value = ""
    temp_values_list = []
    for i in range(0, len(attributes)):
        answer = "no"
        suggestion_content = ""
        if node.attrib["name"] == 'repository':
            if not temp_values_list:
                response = raw_input("Do you want to clone a " + repo_type +
                                     " repository? (yes[Enter]/no): ")
                response = get_and_validate_response(response, repo_type)
            if aff_pattern.match(response):
                temp_values_list.append(attributes[i])
                attrib_value = populate_repo_tags(root, attributes[i],
                                                      attrib_value, node, tag)
                if i == len(attributes)-1:
                    get_multiple_repos(root, node, attrib_value, temp_values_list)
            elif neg_pattern.match(response):
                break
        else:
            info = attributes[i].find("info")
            if info is not None:
                global STATE
                if "warrior" not in tag.tag and STATE == "no":
                        pass
                else:
                    print info.text
            suggestion = attributes[i].find("suggestion")
            if suggestion is not None:
                global STATE
                if "warrior" not in tag.tag and STATE == "no":
                        suggestion_content = suggestion.text
                        answer = "yes"
                else:
                    suggestion_content, answer = get_url_for_main_repos(suggestion, node)
            question = attributes[i].find("question")
            if question is not None:
                global STATE
                if "warrior" not in tag.tag and STATE == "no":
                    attrib_value = suggestion_content
                    attrib_value = validate_input(question, attributes[i].attrib["name"], attrib_value)
                else:
                    attrib_value = get_final_attrib_value(question,
                                                              answer,
                                                              suggestion_content,
                                                              attributes[i])
                tag.set(attributes[i].attrib["name"], attrib_value)


def populate_xml(root, nodes, identifier=""):
    """ This function recursively goes through data.xml and uses information
    stored in that file to create nodes in the new file.

    :Arguments:

    1. root (xml.etree.ElementTree.Element) = This is the parent node from
    data.xml
    2. node (xml.etree.ElementTree.Element) = This is the current node from
    data.xml

    """
    for node in nodes:
        tag = Element(node.attrib["name"])
        root.append(tag)
        children = node.findall("child")
        populate_xml(tag, children, node.attrib["name"])
        attributes = node.findall("attribute")
        if identifier == "drivers":
            repo_type = "Keyword"
        elif identifier == "warriorspace":
            repo_type = "Warriorspace"
        else:
            repo_type = ""
        same_attributes_values(root, node, tag, attributes, repo_type)
        for j in range(0, len(attributes)):
            values = attributes[j].findall("value")
            if values:
                diff_attributes_values(root, node, tag, attributes[j], values)


def validate_new_file_name(path, new_file_name):
    """ This function checks if a file with the same name already exists in
    the path that the user gave. If it does, it promps the user to enter a
    new file name.

    :Arguments:

    1. path (str) = Validated path to the directory
    2. new_file_name (str) = user given file name

    :Returns:

    1. new_file_path (str) = validated file name

    """
    if not os.path.exists(os.path.join(path, new_file_name)):
        new_file_path = os.path.join(path, new_file_name)
    else:
        answer = raw_input("A file with the same name already exists in the "
                           "given directory. Please enter a new name "
                           "for the file: ")
        if answer.endswith(".xml"):
            new_file_name = answer
        else:
            new_file_name = answer + ".xml"
        new_file_path = validate_new_file_name(path, new_file_name)
    return new_file_path


def validate_path(path):
    """ This function validates the path to the directory provided bby the
    user. The default is the current working directory.

    :Arguments:

    1. path (str) = user input that contains path to the directory.

    :Returns:

    1. path (str) = Validated path to the directory.

    """
    if path == "":
        current_dir = get_parent_dir(os.path.realpath(__file__))
        print "Path: " + current_dir
        return current_dir
    if not os.path.exists(path):
        path = raw_input("Invalid path! Please provide a correct path to "
                         "the folder: ")
        path = validate_path(path)
    return path


def get_dir_path_to_save_file(new_file_name):
    """ This function prompts the user to enter the path to the directory in
    which he wants to save the newly created xml file.

    :Arguments:

    1. new_file_name (str) = This is the new name of the xml file

    :Returns:

    1. new_file_path (str) = This is the path of the xml file to where it
    will be saved

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    answer = raw_input("Would you like to store " +
                       new_file_name +
                       " in the user_generated folder? (yes[Enter]/no): ")
    if aff_pattern.match(answer):
        dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        rel_path = get_relative_path(os.path.dirname(dir_path),
                                     "user_generated", new_file_name)
        new_file_path = os.path.join(rel_path)
    elif neg_pattern.match(answer):
        path = raw_input("Please enter a new path. If nothing is entered, " +
                         new_file_name +
                         " will get stored in the home folder: ")
        path = validate_path(path)
        new_file_path = validate_new_file_name(path, new_file_name)
    else:
        print "The command was not recognized. Please answer 'yes' or 'no'."
        new_file_path = get_dir_path_to_save_file(new_file_name)
    return new_file_path


def get_filename(temp_xml):
    """ This function lets the user give a new name to the newly created
    xml file.

    :Arguments:

    1. temp_xml (str) = This is name of the newly created xml file

    :Returns:

    1. new_file_name (str) = This is the new name of the xml file

    """
    answer = raw_input("Please enter a name for this file: ")
    if answer == "":
        print "You cannot save a file without a name."
        new_file_name = get_filename(temp_xml)
    elif answer.endswith(".xml"):
        new_file_name = answer
    else:
        new_file_name = answer + ".xml"
    return new_file_name


def check_if_writable(new_file_name, new_file_path):
    try:
        shutil.copy(new_file_name, new_file_path)
        print "File saved as: " + new_file_name + \
              " in " + os.path.dirname(new_file_path)
        os.remove(new_file_name)
    except:
        print "Oops! Warhorn doesn't have the necessary permissions to write " \
              "in" + new_file_path + " !"
        new_file_path = get_dir_path_to_save_file(new_file_name)
        check_if_writable(new_file_name, new_file_path)


def save_file(temp_xml):
    """ This function saves the xml file created using this program.

    :Arguments:

    1. temp_xml (str) = This is name of the newly created xml file
    2. counter (int) = Counter set to 0 indicates that the file has not been
    run. Counter set to 1 indicates that warhorn.py has been run using this
    file.

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    answer = raw_input("Do you want to save this file? (yes[Enter]/no):")
    if aff_pattern.match(answer):
        new_file_name = get_filename(temp_xml)
        shutil.copy(temp_xml, new_file_name)
        os.remove(temp_xml)
        new_file_path = get_dir_path_to_save_file(new_file_name)
        check_if_writable(new_file_name, new_file_path)
        run_file(new_file_path, 1)
    elif neg_pattern.match(answer):
        print "File won't be saved."
        run_file(temp_xml, 0)
        os.remove(temp_xml)
    else:
        print "The command was not recognized. Please answer 'yes' or 'no'."
        save_file(temp_xml)


def run_file(filename, counter):
    """ This function runs warhorn.py using the newly created xml file.

    :Returns:

    1. counter (int) = Counter value changes to 1 if the user decides to run
     warhorn.py; otherwise remains 0.

    """
    aff_pattern = re.compile("^(|y|yes)$", re.IGNORECASE)
    neg_pattern = re.compile("^(n|no)$", re.IGNORECASE)
    answer = raw_input("Do you want to run this file now? (yes[Enter]/no): ")
    if aff_pattern.match(answer):
        print "Running Warhorn"
        dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        rel_path = get_relative_path(os.path.dirname(dir_path), "warhorn.py")
        subprocess.call(["python", rel_path, filename])
        if counter == 0:
            print "You can view the config file in the logs folder."
    elif neg_pattern.match(answer):
        if counter == 0:
            print "File discarded."
        elif counter == 1:
            print "File saved for later use."
    else:
        print "The command was not recognized. Please answer 'yes' or 'no'."
        run_file(filename, counter)


def main():
    """ This function basically creates the xml file by calling various other
     functions, runs the file and then saves it.

    """
    root = Element('data')
    dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    rel_path = get_relative_path(dir_path, "data.xml")
    tree = xml.etree.ElementTree.parse(rel_path)
    input_root = tree.getroot()
    nodes = get_firstlevel_children(input_root, "tag")

    populate_xml(root, nodes)

    temp_xml = 'temp.xml'
    pretty_xml = minidom.parseString(xml.etree.ElementTree.tostring(root))\
        .toprettyxml(indent="   ")
    with open(temp_xml, "w") as config_file:
        config_file.write(pretty_xml)
        config_file.flush()
    config_file.close()

    save_file(temp_xml)


if __name__ == "__main__":
    global STATE
    STATE = ""
    main()
