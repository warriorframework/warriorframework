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
import os
import platform
import shutil
import stat
from xml.etree import ElementTree
import re
import imp
import subprocess
import datetime
import sys
import urllib
from war_print_class import print_main
"""
Utility functions for warhorn.py
"""


def check_url_is_a_valid_repo(url, repo_name, logfile, print_log_name):
    """ Check if the url stated in the .xml file is a repository or not

    :Arguments:

    1. print_log_name (str) = Contains the name of the print_log file.
    2. logfile (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'
    3.repo_name (str) = Name of the repository
    4. url (str) = url provided by the user in the .xml file

    :Returns:

    bool = True/False.

    """
    print_info("Verifying if {0} is a valid git repository.".format(url), logfile, print_log_name)
    if subprocess.call(["git", "ls-remote", url],
                       stdout=logfile, stderr=subprocess.STDOUT) != 0:
        print_error("{0} is not a valid git repository.".format(url),
                    logfile, print_log_name)
        setDone(1)
        print_info("{0} not cloned.".format(repo_name), logfile, print_log_name)
        return False
    print_info("{0} is available".format(url), logfile, print_log_name)
    return True


def print_info(message, con_log, pr_log_name, *args):
    """ Prints an info message to the terminal

    :Arguments:

    1. pr_log_name (str) = Contains the name of the print_log file.
    2. con_log (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'
    3. message (object) = message that needs to be printed

    :Returns:

    message (object) = message that needs to be printed

    """
    print_type = "-I-"
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    color_message = None
    print_main(message, print_type, con_log, pr_log_name, color_message)
    return message


def print_error(message, con_log, pr_log_name, *args):
    """ Prints an error message to the terminal

    :Arguments:

    1. pr_log_name (str) = Contains the name of the print_log file.
    2. con_log (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'
    3. message (object) = message that needs to be printed

    :Returns:

    message (object) = message that needs to be printed

    """
    print_type = "-E-"
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    color_message = None
    print_main(message, print_type, con_log, pr_log_name, color_message)
    return message


def print_warning(message, con_log, pr_log_name, *args):
    """ Prints a warning message to the terminal

    :Arguments:

    1. pr_log_name (str) = Contains the name of the print_log file.
    2. con_log (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'
    3. message (object) = message that needs to be printed

    :Returns:

    message (object) = message that needs to be printed

    """
    print_type = "-W-"
    if len(args) > 0:
        for arg in args:
            message += arg + ", "
    color_message = None
    print_main(message, print_type, con_log, pr_log_name, color_message)
    return message


def words(import_actions):
    """ This function gives out the words by splitting the lines

    :Arguments:

    1. import_actions (list) = list of the lines starting from 'import'

    :Returns:

    list = list of words in the line

    """
    line_stream = iter(import_actions)
    for line in line_stream:
        for word in line.split():
            yield word


def get_repository_name(url):
    """ This function returns the name of the repository for splitting the
    url of the repository.

    :Arguments:

    1. url (str) = url of the repository as stated by the user in
    the xml file

    :Returns:

    string = name of the repository
    """
    li_temp_1 = url.rsplit('/', 1)
    return li_temp_1[1][:-4] if \
        li_temp_1[1].endswith(".git") else li_temp_1[1]


def get_attribute_value(tag_name, attrib_name):
    """ Retrieves the attribute value for the specified node name or tag name

    :Arguments:

    1. attrib_name (str) = Name of the attribute whose value has to be
    retrieved
    2. tag_name (str) = Name of the tag or node which has thee aforementioned
    attrib_name as an attribute

    :Returns:

    value (str) = value of the attribute

    """
    if attrib_name in tag_name.attrib:
        value = tag_name.attrib[attrib_name]
    else:
        value = ""
    return value


def get_all_leaf_dirs(path, paths):
    """ Retrieves all the leaf directories of the specified directory

    :Arguments:

    1. paths (list) = paths of all the leaf directories obtained.
    2. path (str)= path of the root directory

    :Returns:

    """
    _, subdirs = get_subfiles(path)
    if len(subdirs) != 0:
        for subdir in subdirs:
            paths.append(os.path.join(path, subdir))
            get_all_leaf_dirs(os.path.join(path, subdir), paths)


def get_paths(path, li_names):
    """ Concatenates existing path with the names of the folders and gives
    out the paths to each of the stated folder

    :Arguments:

    1. path(str) = base path.
    2. li_names (list) = list of the folder_names that need to be
    concatenated with the base path

    :Returns:

    path (str) = contatenated paths

    """
    for folder_name in li_names:
        path = os.path.join(path, folder_name)
    return path


def get_first_level_dirs(path):
    """ Gives out paths to the next level directories of the stated
    directory.

    :Arguments:

    1. path (str) = path to the root directory

    :Returns:

    list[str] = list of str with paths to the next level directories
    of the root directory

    """
    return os.walk(path).next()[1]


def delete_directory(path, logfile, print_log_name):
    """ Deletes the specified directory.
    Calls delete_read_only if error arises due to 'read only' files

    :Arguments:

    1. path (str) = deletes the stated directory

    :Returns:

    """
    try:
        shutil.rmtree(path, onerror=delete_read_only)
    except IOError:
        print_error("Warhorn was unable to delete read-only files!",
                    logfile, print_log_name)
        setDone(1)
    except OSError:
        print_error("Warhorn could not find the file that was asked to "
                    "be deleted!", logfile, print_log_name)
        setDone(1)
    except:
        print_error("Warhorn was unable to accomplish certain necessary "
                    "deletions.", logfile, print_log_name)
        setDone(1)


def delete_read_only(action, name, exc):
    """ Deletes read-only files by changing permissions.

    :Arguments:

    1. name (str) = name of the file

    :Returns:

    """
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


def get_subfiles(src):
    """ Gets all the directories and files listed under the specified directory.
    Separates the directories from standalone files.
    Directory names get appended in li_dirs. File names get appended in li_files
    return type: list, list.

    :Arguments:

    1. src (str) = path to the source file

    :Returns:

    li_files (list) = list of files.
    li_dirs (list) = list of files.

    """
    li_files = []
    li_dirs = []
    all_files = os.listdir(src)
    for files in all_files:
        if os.path.isfile(os.path.join(src, files)):
            li_files.append(files)
        else:
            li_dirs.append(files)
    return li_files, li_dirs


def create_dir(path):
    """ Checks if a directory already exists.
    If not, creates one with the specified name.

    :Arguments:

    1. path (str) = path to the needed directory

    :Returns:

    """
    if not os.path.exists(path):
        os.makedirs(path)


def check_packages(str_package):
    """ Checks if the specified python package is installed.
    return type: boolean

    :Arguments:

    1. str_package (str) = name of the package to be checked

    :Returns:

    bool = True/False

    """
    try:
        imp.find_module(str_package)
        bool_found = True
    except ImportError:
        bool_found = False
    return bool_found


def get_node(filename, node_name):
    """ Searches for the specified node in the xml tree.
    return type: xml.etree.ElementTree.Element

    :Arguments:

    1. node_name (str) = Name of the node to be searched
    2. filename (str) = path of the .xml that has to be searched.

    :Returns:

    node = xml.etree.ElementTree.Element/boolean False

    """
    root = ElementTree.parse(filename).getroot()
    node = root.find(node_name)
    if node is not None:
        return node
    else:
        return False


def get_firstlevel_children(node, child_tag):
    """ Searches for the specified children of a node in the xml tree.
    Returns only first level children.

    :Arguments:

    1. child_tag (str) = Name of the child tag
    2. node (xml.etree.ElementTree.Element) = node that needs to be
    searched

    :Returns:

    list = list of all child nodes of the given node

    """
    child_list = node.findall(child_tag)
    return child_list


def check_installed_python_version(logfile, print_log_name):
    """ Returns version of python that Warrior is running on.

    :Arguments:

    1. print_log_name (str) = Name of the print_log file
    2. logfile (file object) = Contains the file object for the
    console_log file. This file object is the 'opened' console_log
    file with mode set to 'a'

    :Returns:

    str = python version

    """
    print_info("The current python version installed is: " +
               platform.python_version(), logfile, print_log_name)
    return platform.python_version()


def verify_python_version(str_version, regex_str, logfile, print_log_name):
    """Checks if the version of Python is correct or not.
    Throws a warning and continues with the rest of the program if not.

    :Arguments:

    1. print_log_name (str) = Name of the print_log file
    2. regex_str (Regular Expression) = Regular Expression for comparison
    3. logfile (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode
    set to 'a'
    4. str_version (str) = Version of python that warhorn.py is running on

    :Returns:

    """
    pattern = re.compile(regex_str)
    if not pattern.match(str_version):
        print_error("You are currently using Python " + str_version + ". It is strongly "
                    "recommended that you install the correct version of Python (2.7.0 or "
                    "above in the 2.7 family).", logfile, print_log_name)
        setDone(1)
        getDone(logfile, print_log_name)
    else:
        print_info("Python version satisfies requirements.", logfile, print_log_name)


def get_latest_tag(base_path="", current_dir=""):
    """This function returns the latest tag set in a repository. If tags cannot
    be determined, then check is set to 1 and 'master' is returned. If the'
    repository has no tags, 'master' is returned, but check is set to 0
    """
    check = 0
    try:
        if base_path != "":
            os.chdir(base_path)
        latest_tag = subprocess.check_output(["git", "tag"])
        if current_dir != "":
            os.chdir(current_dir)
    except:
        check = 1
        latest_tag = "master"
        if current_dir != "":
            os.chdir(current_dir)
    else:
        # If at least one or more tags found in the latest_tag
        # Do split and return the latest
        if latest_tag:
            try:
                li_tags = str.splitlines(latest_tag)
            except TypeError:
                latest_tag = "master"
            else:
                latest_tag = ""
                pattern = re.compile("^([0-9]|v)")
                remove_tags = []
                # Taking out any tags that are not in pattern 3.1 or v3.1
                for tag in li_tags:
                    if not pattern.match(tag):
                        remove_tags.append(tag)
                for tag in remove_tags:
                    li_tags.remove(tag)
                # Comparing tags to get the highest
                for tag in li_tags:
                    flag = False
                    if tag.startswith("v"):
                        temp = tag[1:]
                        flag = True
                    else:
                        temp = tag
                    lt_flag = False
                    if latest_tag == "":
                        lt_flag = flag
                        latest_tag = temp
                    if latest_tag.startswith("v"):
                        latest_tag = latest_tag[1:]
                        lt_flag = True
                    if latest_tag < temp:
                        if flag:
                            temp = "v" + temp
                        latest_tag = temp
                    elif lt_flag:
                        latest_tag = "v" + latest_tag
        # else there is no tag in repo. return master
        else:
            latest_tag = "master"
    return latest_tag, check


def git_clone_repository(url, base_path="", current_dir=""):
    """This function clones a git repository in a given location (base_path).
    If base_path is empty, the repository is cloned in the current working
    directory"""
    try:
        if base_path != "":
            os.chdir(base_path)
        subprocess.check_output(["git", "clone", url])
        check = True
        if current_dir != "":
            os.chdir(current_dir)
    except:
        check = False
        if current_dir != "":
            os.chdir(current_dir)
    return check


def get_date_and_time():
    """ Gets current date and time

    :Arguments:

    :Returns:

    str = strftime format of the retrieved current date and time

    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def get_relative_path(*args):
    """ This function builds the relative path

    :Arguments:

    1. *args (list[str]): List of paths that need to be joined

    :Returns:

    1. path (str): relative path
    """
    path = ""
    for arg in args:
        path = os.path.join(path, arg)
    return path


def get_dict_with_versions():
    """ This function carries the name and version of the depndencies

    :Returns:

    1. versions (dict) = Dictionary with name as Key and version as value
    """
    versions = {'jira': '1.0.3', 'lxml': '3.3.3', 'ncclient': '0.4.6',
                'paramiko': '2.4.1', 'pexpect': '4.2', 'pysnmp': '4.4.4',
                'requests': '2.9.1', 'selenium': '2.48.0', 'xlrd': '1.0.0',
                'cloudshell-automation-api':'7.1.0.34', 'pycryptodome': '3.6.1'}
    return versions


def install_depen(dependency, dependency_name, logfile, print_log_name,
                  user=None):
    """ This function checks if a dependency was installed. If not,
     then it raises an error.
    """
    counter = 0
    pip_cmds = ['pip', 'install', dependency]
    if user:
        print_info("Installing {} as user...".format(dependency), logfile, print_log_name)
        pip_cmds.insert(2, "--user")
    try:
        print_info("installing "+dependency, logfile, print_log_name)
        sp_output = subprocess.Popen(pip_cmds, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        output, error = sp_output.communicate()
        return_code = sp_output.returncode
        if return_code > 0:
            print_info(output, logfile, print_log_name, error)
    except IOError:
        counter = 1
        print_error("Warhorn was unable to install " + dependency_name + " because Warhorn "
                    "does not have write permissions. You need to have admin privileges to "
                    "install anything!", logfile, print_log_name)
        setDone(1)
    except:
        counter = 1
        print_error("Warhorn was unable to install " + dependency_name + ". Warhorn could not "
                    "determine the cause for this. This could have happened because probably the "
                    "system is not connected to internet.", logfile, print_log_name)
        setDone(1)
    if counter == 0:
        try:
            sp_output = subprocess.Popen(["pip", "show", dependency_name], stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = sp_output.stdout.read()
            if output == "":
                print_error(dependency_name + " could not be installed!!",
                            logfile, print_log_name)
                setDone(1)
            else:
                print_info(dependency_name + " installation complete!",
                           logfile, print_log_name)
        except:
            print_error("Warhorn wasn't able to determine if " + dependency_name + " was "
                        "installed successfully or not!", logfile, print_log_name)
            setDone(1)


def get_dependencies(logfile, print_log_name, config_file_name, venv=False):
    """ Function gets called from setup.py
    Gets the dependencies that need to be installed.
    Appends dependency name and version to a list if attribute 'install'
    is specified as yes.
    Throws an informational message if 'install' attribute set to no.
    Throws an error if 'install' attribute left blank or is absent and
    continues with the program.

    :Arguments:

    1. print_log_name (str) = Contains the name of the print_log file.
    2. config_file_name (str) = Contains the name of the console_log
    file.
    3. logfile (file object) = Contains the file object for the
    console_log file. This file object is the 'opened' console_log
    file with mode set to 'a'

    :Returns:

    1. install_reqs(list[str]) = a list of dependencies that the user
    has asked warhorn.py to install.
    install_reqs = [<dep_name>==<version>, <dep_name>==<version>]

    """
    node = get_node(config_file_name, 'warhorn')
    if node is False:
        print_error("Warhorn tag not found! Proceeding with the installation without installing "
                    "any of the recommended dependencies.", logfile, print_log_name)
        setDone(1)
    else:
        dependencies = get_firstlevel_children(node, "dependency")
        versions = get_dict_with_versions()
        for dependency in dependencies:
            if 'install' in dependency.attrib:
                if dependency.attrib["install"] == "yes":
                    print_info("Warhorn will try to install " + dependency.attrib["name"] + " as "
                               "it was set to 'yes' in the .xml file", logfile, print_log_name)
                    if (not venv and 'user' in dependency.attrib and
                            dependency.attrib["user"] == "yes"):
                        install_depen(dependency.attrib["name"] + "==" +
                                      versions.get(dependency.attrib["name"]),
                                      dependency.attrib["name"], logfile, print_log_name, True)
                    else:
                        install_depen(dependency.attrib["name"] + "==" +
                                      versions.get(dependency.attrib["name"]),
                                      dependency.attrib["name"], logfile, print_log_name)
                elif dependency.attrib["install"] == "no":
                    print_info("Warhorn will not install " + dependency.attrib["name"] + " as "
                               "it was set to 'no' in the .xml file.", logfile, print_log_name)
                else:
                    print_error("Warhorn will not install " + dependency.attrib["name"] + " as "
                                "the 'install' attribute in the .xml file was left blank.",
                                logfile, print_log_name)
                    setDone(1)
            else:
                print_error("Warhorn will not install " + dependency.attrib["name"] + " as "
                            "the 'install' attribute was not found.", logfile, print_log_name)
                setDone(1)


def get_dest(logfile, print_log_name, config_file_name):
    """ Function gets called from setup.py
    Find out if warhorn is assembling warrior in the same repo
    or in a different repo location

    :Arguments:

    1. print_log_name (str) = Contains the name of the print_log file.
    2. config_file_name (str) = Contains the name of the console_log
    file.
    3. logfile (file object) = Contains the file object for the
    console_log file. This file object is the 'opened' console_log
    file with mode set to 'a'

    :Returns:

    1. dest (str) = the path where warrior is being cloned to, if blank
                    it means on the same level of warhorn folder

    """
    node = get_node(config_file_name, 'warriorframework')
    if node is False:
        if "destination" in node.attrib:
            return get_attribute_value(node, "destination")
        else:
            print_error("Destination attrib not found! Installation cannot "
                        "continue", logfile, print_log_name)
            setDone(1)


def set_file_names():
    """ Function written so that setup.py can access these file names.

    :Returns:

    1. console_log_name (str) = name of the console_log file
    2. print_log_name (str) = name of the print_log file"

    """
    console_log_name = "console_log.txt"
    print_log_name = "print_log.txt"
    return console_log_name, print_log_name


def setDone(value):
    """This function sets the exit value of warhorn"""
    global DONE
    DONE = value


def getDone(logfile, print_log_name):
    """This function prints the exit value of warhorn"""
    print_info("DONE " + str(DONE), logfile, print_log_name)
    sys.exit(DONE)


def get_parent_dir(path, child="warhorn"):
    """ This function gets the parent directory of any a specified child folder
    from the given path
    """
    if path.rsplit(os.sep)[-1] == child:
        path = os.path.dirname(path)
    else:
        path = os.path.dirname(path)
        path = get_parent_dir(path, child)
    return path


def get_all_direct_child_nodes(config_file_name, parent=""):
    """This function gets all the direct (first-level) children
    of an xml node"""
    if parent == "":
        parent = ElementTree.parse(config_file_name).getroot()
    element_list = list(parent.iter())
    node_list = []
    for node in element_list:
        if parent.find(node.tag) is not None:
            node_list.append(node.tag)
    return node_list


def remove_extra_list_elements(input_list, *args):
    """This is a list util function tha removes extra elements passed through
    args that are in the list and returns the remaining list"""
    final_list = []
    for element in input_list:
        counter = 0
        for arg in args:
            if element == arg:
                counter = 1
                break
        if counter == 0:
            final_list.append(element)
    return final_list


def git_checkout_label(label, base_path="", current_dir=""):
    """ This function checks out a particular label in the git repository.
    Directory is switched to base_path if given and then switched back to
    current working directory.
    If base_path is not given, repo is cloned in the current working directory.
    check == True and current_tag == 0 is the success condition.
    check == True and current_tag != 0 is condition for invalid label
    check == False and current_tag != 0 is condition for problematic git
                                                        commands
    """
    check = True
    current_label = ""
    if base_path != "":
        os.chdir(base_path)
    try:
        # checking out label
        subprocess.check_call(["git", "checkout", label])
        # getting current commit id (%H) and label (%d)
        current_label = subprocess.check_output(["git", "show", '--format="%H%d"', "--no-patch"])
    except:
        check = False
    if label not in current_label:
        check = False
    if current_dir != "":
        os.chdir(current_dir)
    return check, current_label


def embed_user_cred_in_url(url, username, password):
    """
    Embed the username and password in the git url.
    It is applicable only for http or https url types.
    Input url format: https://path/to/repo (or) https://username@path/to/repo
    Output url format: https://username:password@path/to/repo
    If the username is already given in the url, that will be used.

    :Arguments:
        1. url(string) - url to be used for cloning
        2. username(string) - git username
        3. password(string) - git password
    :Returns:
        1. url(string) - url with username and password
    """
    url_parts = url.split("://", 1)
    # check if the url type is http or https
    if len(url_parts) == 2 and url_parts[0].upper() in ["HTTP", "HTTPS"]:
        url_type, url_path = url_parts[0], url_parts[1]
        # get the username from the URL
        if '@' in url_path:
            url_username, url_path = url_path.split('@', 1)
        else:
            url_username = ""

        if url_username != "":
            username = url_username
        # modify url to include username and password in it
        # format: http[s]://username:password@path/to/repo
        if username != "" and password != "":
            username = urllib.quote_plus(username)
            password = urllib.quote_plus(password)
            url = url_type + "://" + username + ":" + password + '@' + url_path
    return url
