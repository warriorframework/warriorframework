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
import shutil
import subprocess
import sys
from distutils import dir_util
from source.utils import (check_installed_python_version, print_info, verify_python_version,
                          check_packages, print_warning, print_error, get_subfiles, create_dir,
                          get_node, get_firstlevel_children, get_attribute_value,
                          check_url_is_a_valid_repo, delete_directory, delete_read_only,
                          get_paths, get_all_leaf_dirs, words, get_repository_name,
                          get_date_and_time, get_relative_path, set_file_names, get_dependencies,
                          setDone, getDone, get_parent_dir, get_all_direct_child_nodes,
                          remove_extra_list_elements, git_clone_repository, get_latest_tag,
                          git_checkout_label, get_dest, install_depen, embed_user_cred_in_url)

"""

warhorn.py is an installer that runs from a cli interface.
warhorn.py takes arguments - the first argument: the name of the .xml file
that contains the data necessary for this installer to run and the second
argument - the path to the aforementioned file.
If the path is not given, warhorn.py automatically searches through
config/user_generated directory for the file.
If no arguments are passed, warhorn.py uses the default .xml file -
default_config.xml.

warhorn.py checks if the system satisfies basic requirements that Warrior
recommends, installs them if necessary. Currently, it creates a Warrior .egg
which is basically a Warrior package. Though, at this point in time,
unnecessary, it is a foundation provided to warhorn.py for when Warrior
would be distributed as a package instead of a git repository.

It clones the Warrior repository.
Depending upon the .xml file, warhorn.py can:
Clone the master, clone any existing branch, tag, or commit id, delete
existing Warrior to clone a fresh Warrior, pull Warrior if the user does not
want a fresh start but wants the files s/he is missing, switch branches
in the existing local Warrior, and clone the latest version of Warrior if
nothing is specified.

It clones the drivers:
As per the instruction set provided in the config directory, the .xml file
can be used to tell warrior which drivers the user needs. warhorn.py can
successfully clone only those particular drivers, clone the associated actions
and Framework. Older and existing drivers, framework and actions get replaced if
the .xml states so, otherwise are left untouched. Older and "extra" drivers
and actions are not deleted.

It clones Warriorspace:
All the Warriorspaces mentioned in the .xml get cloned. The older and
existing Warriorspace get overwritten. Older and "extra" testcases, suites, and
projects in Warriorspace are not deleted.

"""


def check_basic_requirements(logfile, config_file_name, console_log_name,
                             print_log_name, python_executable):
    """ Checks the version of python Warrior is running on. Checks if pip,
    setuptools, and git have been installed.
    Exits if setuptools or git have not been installed.
    Throws warning if the python version is not what is recommended but
    continues with the program.
    Installs pip for the user if it hasn't already been installed.

    :Arguments:

    1. console_log_name(str) = Contains the name of the console_log file.
    2. print_log_name(str) = Contains the name of the print_log file.
    3. config_file_name(str) = Contains the name of the console_log file.
    4. logfile (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'

    :Returns:

    """
    str_version = check_installed_python_version(logfile, print_log_name)
    print_info("Warrior requires Python 2.7.0 - till the latest release in the "
               "2.7 family.", logfile, print_log_name)
    verify_python_version(str_version, r"^(2\.7)",
                          logfile, print_log_name)

    str_package = 'pip'
    bool_found = check_packages(str_package)
    if not bool_found:
        print_warning("Pip not found.", logfile, print_log_name)
        install_pip(logfile, print_log_name, python_executable)
    else:
        print_info("Pip is available.", logfile, print_log_name)

    str_package = 'setuptools'
    bool_found = check_packages(str_package)
    if not bool_found:
        print_error("Please install setuptools, and then restart this "
                    "installation.", logfile, print_log_name)
        delete_temp_files_and_folders(logfile=logfile,
                                      config_file_name=config_file_name,
                                      console_log_name=console_log_name,
                                      print_log_name=print_log_name)
        setDone(1)
        getDone(logfile, print_log_name)
    else:
        print_info("Setuptools package is available.", logfile, print_log_name)

    try:
        null = open("/dev/null", "w")
        sp_output = subprocess.Popen("git", stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE, shell=True)
        null.close()
        output = sp_output.stdout.read()
        print_info(output, logfile, print_log_name)
        print_info("Git is available", logfile, print_log_name)
    except OSError:
        print_error("Git is not installed on the system. "
                    "Please install git and restart this installation.",
                    logfile, print_log_name)
        delete_temp_files_and_folders(logfile=logfile,
                                      config_file_name=config_file_name,
                                      console_log_name=console_log_name,
                                      print_log_name=print_log_name)
        setDone(1)
        getDone(logfile, print_log_name)


def overwrite_files(path, destination, overwrite, logfile, print_log_name):
    """ Overwrites existing files with new files if overwrite attribute is
    set to
    yes, empty or is absent.
    Excludes the Execution folder.

    :Arguments:

    1. overwrite (str) = Contains the associated value of the attribute
    'overwrite' for that particular tag extracted from the .xml file
    2. destination (str) = Contains path to the directory in which the files
    to be overwritten reside.
    3. path (str) = Contains path to the 'temp' folder in which the
    repository is initially cloned.

    :Returns:

    """
    sub_files, sub_folders = get_subfiles(path)
    for sub_folder in sub_folders:
        if sub_folder != "Execution":
            create_dir(os.path.join(destination, sub_folder))
            overwrite_files(os.path.join(path, sub_folder),
                            os.path.join(destination, sub_folder),
                            overwrite, logfile, print_log_name)
    for sub_file in sub_files:
        if os.path.exists(os.path.join(destination, sub_file)):
            if (not overwrite) or overwrite == "yes":
                try:
                    shutil.copy(os.path.join(path, sub_file),
                                os.path.join(destination, sub_file))
                except Exception, e:
                    print_error("Exception Trace: {0}".format(e),
                                logfile, print_log_name)
                    print_error("Error while copying {0}.".format(sub_file),
                                logfile, print_log_name)
        else:
            try:
                shutil.copy(os.path.join(path, sub_file),
                            os.path.join(destination, sub_file))
            except Exception, e:
                print_error("Exception Trace: {0}".format(e),
                            logfile, print_log_name)
                print_error("Error while copying {0}.".format(sub_file),
                            logfile, print_log_name)


def install_pip(logfile, print_log_name, python_executable):
    """ Installs pip.

    :Arguments:

    1. print_log_name (str) = Contains the name of the print_log file.
    2. logfile (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'

    :Returns:

    """
    print_info("Installing pip", logfile, print_log_name)
    command = python_executable + " source/get-pip.py"
    try:
        sp_output = subprocess.\
            Popen(command, shell=True, stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output = sp_output.stdout.read()
        print_info(output, logfile, print_log_name)
        output, error = sp_output.communicate()
        if sp_output.returncode != 0:
            print_error("An error occured while installing pip: {0}".format(error),
                        logfile, print_log_name)
            print_info("Exiting Warhorn.", logfile, print_log_name)
            setDone(1)
            getDone(logfile, print_log_name)
        print_info("Pip installed.", logfile, print_log_name)
    except IOError:
        print_error("Pip couldn't be installed! Seems like Warhorn does not "
                    "have write permissions.", logfile, print_log_name)
        setDone(1)
        getDone(logfile, print_log_name)
    except Exception as e:
        print_error("An error occured while installing pip: {0}".format(e),
                    logfile, print_log_name)
        print_info("Exiting Warhorn.", logfile, print_log_name)
        setDone(1)
        getDone(logfile, print_log_name)


def print_out_checkout_status(label, check, current_tag, repo_name, **kwargs):
    """Git checkout status reporting"""
    logfile = kwargs.get("logfile")
    print_log_name = kwargs.get("print_log_name")
    if check and label in current_tag:
        print_info("Checkout complete. " + repo_name + " version: " + label,
                   logfile, print_log_name)
    elif not check and label not in current_tag:
        print_error(label + " seems to be an invalid tag name\n" + repo_name +
                    " is now running: " + current_tag,
                    logfile, print_log_name)
        setDone(1)
    else:
        print_error("Checkout unsuccessful. " + repo_name +
                    " is now running: " + current_tag,
                    logfile, print_log_name)
        setDone(1)


def clone_warrior_and_tools(base_path, current_dir, repo_root, **kwargs):
    """ Clones Warrior into the specified directory.
    Does not give user the ability to change the name of the local repository.

    :Arguments:

    1. console_log_name (str) = Contains the name of the console_log file.
    2. print_log_name (str) = Contains the name of the print_log file.
    3. config_file_name (str) = Contains the path to the .xml file.
    4. logfile (file object) = Contains the file object for the console_log
    file. This file objectis the 'opened' console_log file with mode set
    to 'a'
    5. base_path (str) = Contains the path to the directory in which the user
    wants to clone Warrior.

    :Returns:

    """
    # Getting all variables from kwargs
    repo_name = kwargs.get("repo_name")
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    console_log_name = kwargs.get("console_log_name")
    print_log_name = kwargs.get("print_log_name")

    # Setting the path to the root of the repo
    path = os.path.join(base_path, repo_root)

    # Getting the node from the config file
    node = get_node(config_file_name, repo_name.lower())

    # Validating the URL
    url = get_attribute_value(node, "url")

    if repo_name == "tools":
        # for http/https url types, embed username & password in url
        username = get_attribute_value(node, "username")
        password = get_attribute_value(node, "password")
        url = embed_user_cred_in_url(url, username, password)

    if url == "":
        print_error("Can't clone repository without the url!",
                    logfile, print_log_name)
        setDone(1)
        if repo_name == "warrior":
            # Exiting the program if Warrior URL is empty
            delete_temp_files_and_folders(logfile=logfile,
                                          config_file_name=config_file_name,
                                          console_log_name=console_log_name,
                                          print_log_name=print_log_name)
            getDone(logfile, print_log_name)
        else:
            return
    if not check_url_is_a_valid_repo(url, repo_name, logfile, print_log_name):
        setDone(1)
        if repo_name == "warrior":
            # Exiting the program if Warrior URL is incorrect
            delete_temp_files_and_folders(logfile=logfile,
                                          config_file_name=config_file_name,
                                          console_log_name=console_log_name,
                                          print_log_name=print_log_name)
            getDone(logfile, print_log_name)
        else:
            return

        # Getting the clean_install attribute value
    if 'clean_install' in node.attrib:
        clean_install = get_attribute_value(node, "clean_install")
    else:
        # backward compatibility
        clean_install = get_attribute_value(node, "clean_install_warrior")
    label = get_attribute_value(node, "label")

    if clean_install == "yes":
        # Deleting exising repo is clean_install is set to 'yes'
        if os.path.exists(path):
            print_info("Deleting existing " + repo_name,
                       logfile, print_log_name)
            try:
                delete_directory(path, logfile, print_log_name)
            except Exception:
                print_error("Warhorn was unable to delete existing " + repo_name + ". " +
                            repo_name + " will be pulled.", logfile, print_log_name)
                setDone(1)
            else:
                print_info("Existing " + repo_name + " deleted successfully",
                           logfile, print_log_name)

    if os.path.exists(path):
        # Pulling repo if path exists
        print_info("Pulling " + repo_name + ".", logfile, print_log_name)
        os.chdir(path)
        try:
            sp_output = subprocess.Popen(["git", "pull", url], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            os.chdir(current_dir)
            output = sp_output.stdout.read()
            print_info(output, logfile, print_log_name)
        except Exception:
            os.chdir(current_dir)
            print_error("Pulling unsuccessful", logfile, print_log_name)
            setDone(1)
        if label != "":
            # Checking out a particular label
            print_info("Checking out: " + label, logfile, print_log_name)
            check, current_tag = git_checkout_label(label, path, current_dir)
            print_out_checkout_status(label, check, current_tag, repo_name,
                                      logfile=logfile, print_log_name=print_log_name)
        print_info("Pull complete", logfile, print_log_name)
    else:
        # Cloning repo if path does not exist
        print_info("Cloning " + repo_name + ".", logfile, print_log_name)
        check = git_clone_repository(url, base_path, current_dir)
        if check:
            # If cloning successful
            print_info(repo_name + " cloned successfully.",
                       logfile, print_log_name)
            if label != "":
                # Checking out label
                print_info("Checking out: " + label, logfile, print_log_name)
                check, current_tag = git_checkout_label(label, path, current_dir)
                print_out_checkout_status(label, check, current_tag, repo_name,
                                          logfile=logfile,
                                          print_log_name=print_log_name)
            else:
                # Getting latest tag
                latest_tag, check = get_latest_tag(path, current_dir)
                if latest_tag == "master" and check == 1:
                    print_error("Warhorn could not determine if there were any tags in {0} to "
                                "checkout. {0} would be set to the default (master) branch"
                                ".".format(repo_name), logfile, print_log_name)
                    setDone(1)
                elif latest_tag == "master" and check == 0:
                    print_info("No tags were found in " + repo_name +
                               ". It would be set to the default (master) "
                               "branch.", logfile, print_log_name)
                else:
                    print_info("Checking out: " + latest_tag, logfile,
                               print_log_name)
                    check, current_tag = git_checkout_label(latest_tag, path,
                                                            current_dir)
                    print_out_checkout_status(latest_tag, check, current_tag,
                                              repo_name,
                                              logfile=logfile,
                                              print_log_name=print_log_name)
        else:
            # If cloning unsuccessful
            print_error("Clone unsuccessful.", logfile, print_log_name)
            setDone(1)
            if repo_name == "warrior":
                # Exiting the program if Warrior clone is unsuccessful
                delete_temp_files_and_folders(logfile=logfile,
                                              config_file_name=config_file_name,
                                              console_log_name=console_log_name,
                                              print_log_name=print_log_name)
                getDone(logfile, print_log_name)


def remove_extra_drivers(drivers, path):
    """ This function basically compares the drivers that have been cloned
    into the temp folder and the drivers that the user wants, i.e, the driver
    names stated in the .xml file.

    The 'wanted' driver names are stored in the list called drivers and the
    names of all the drivers cloned are stored in the list called subfiles.

    The names are then compared and whichever driver name that exists in
    subfiles but not in drivers is deleted.

    :Arguments:

    1. path (str) = Contains the path to the temp folder where the repository
    is initially cloned
    2. drivers (list) = Contains a list of driver names that the user wants
    to clone.

    :Returns:

    """
    subfiles, _ = get_subfiles(os.path.join(path, 'ProductDrivers'))
    for driver in drivers:
        clone = get_attribute_value(driver, "clone")
        for subfile in subfiles:
            if clone == "yes" or clone == "":
                driver_name = driver.attrib["name"] if \
                    driver.attrib["name"].endswith(".py") else \
                    driver.attrib["name"] + ".py"
                if driver_name == subfile:
                    subfiles.remove(subfile)
                    break
    for subfile in subfiles:
        os.remove(os.path.join(path, 'ProductDrivers', subfile))


def get_docs_folder(path, repository, direc, destination):
    """ Function written to copy over the docs folders. A folder going by the
    name of the current repository is created inside the
    warrior_main/Warrior/Docs folder and only the html folder is copied over

    :Arguments:

    1. path (str) = Contains the path to the temp folder where the repository
    is initially cloned
    2. destination (str) = Contains path to the directory in which the files
    to be overwritten reside.
    3. direc (str) = contains the value "Docs"
    4. repository (xml.etree.ElementTree.Element) = node of the repository

    """
    url = get_attribute_value(repository, "url")
    name = get_repository_name(url)
    subfiles, subdirs = get_subfiles(os.path.join(path, direc))
    for subfile in subfiles:
        os.remove(os.path.join(path, direc, subfile))
    for subdir in subdirs:
        if subdir != "build":
            shutil.rmtree(os.path.join(path, direc, subdir),
                          onerror=delete_read_only)
        else:
            sub_subfiles, sub_subdirs = get_subfiles(os.path.join(path, direc, subdir))
            for sub_subfile in sub_subfiles:
                os.remove(os.path.join(path, direc, subdir, sub_subfile))
            for sub_subdir in sub_subdirs:
                if sub_subdir != "html":
                    shutil.rmtree(os.path.join(path, direc, subdir, sub_subdir),
                                  onerror=delete_read_only)
                else:
                    if os.path.exists(os.path.join(destination, direc, name, sub_subdir)):
                        shutil.rmtree(os.path.join(destination, direc, name, sub_subdir),
                                      onerror=delete_read_only)
                    shutil.copytree(os.path.join(path, direc, subdir, sub_subdir),
                                    os.path.join(destination, direc, name, sub_subdir))


def replace_folders(path, repository, destination, logfile, print_log_name):
    """ Function written mainly to 'replace' specified directories under the
    Actions directory and files under the
    ProductDrivers directory.
    Gracefully handles the absence of Framework directory.

    :Arguments:

    1. print_log_name (str) = Contains the name of the print_log file.
    2. logfile (file object) = Contains the file object for the console_log
    file. This file objectis the 'opened' console_log file with mode set to 'a'
    3. destination (str) = Contains path to the directory in which the files
    to be overwritten reside.
    4. path (str) = Contains the path to the temp folder where the repository
    is initially cloned

    :Returns:

    """

    # found_framework keeps a track of whether or not the Framework directory
    # exists.
    found_framework = 0

    # list_dirs contains the names of directories that need to be replaced in
    # the existing warrior.
    list_dirs = ["Actions", "Framework", "Docs", "ProductDrivers"]
    _, subdirs = get_subfiles(path)
    for subdir in subdirs:
        for list_dir in list_dirs:
            if subdir == list_dir:
                if subdir == "Framework":
                    found_framework = 1

                    # Framework directory needs to be overwritten and not
                    # replaced.
                    overwrite_files(path, destination, "yes", logfile,
                                    print_log_name)
                elif subdir == "Docs":
                    get_docs_folder(path, repository, subdir, destination)
                elif subdir == "Actions" or subdir == "ProductDriver":
                    _, sub_subdirs = \
                        get_subfiles(os.path.join(path, subdir))
                    for sub_subdir in sub_subdirs:
                        newpath = os.path.join(path, subdir, sub_subdir)
                        destpath = \
                            os.path.join(destination, list_dir, sub_subdir)
                        if os.path.exists(destpath):
                            # Removes existing directory/file, copies over
                            # the newly cloned one.
                            shutil.rmtree(destpath, onerror=delete_read_only)
                        shutil.copytree(newpath, destpath)

    # Throws an informational message that Framework directory was not cloned
    #  because it did not exist.
    if found_framework == 0:
        print_info("Framework directory not found, hence not cloned.",
                   logfile, print_log_name)


def remove_extra_actions(path, logfile, print_log_name):
    """ Removes the unneeded Actions packages that have been cloned into the
    temp folder.

    :Arguments:

    1. path (str) = Contains the path to the temp folder where the repository
    is initially cloned

    :Returns:

    """
    li_actions = []
    get_action_name_from_driver(li_actions, path)
    actions_dirs = []
    for actions in li_actions:
        temp = ""
        for folder in actions.split('.'):
            temp = os.path.join(temp, folder)
        folder_path = []
        get_action_folder_details(os.path.join(path, temp, ''), folder_path)
        temp = os.path.join(path, 'Actions')
        str_path = get_paths(temp, reversed(folder_path))
        if len(folder_path) > 1:
            for i in range(0, (len(folder_path) - 1)):
                temp = os.path.join(temp,
                                    folder_path[(len(folder_path) - 1) - i])
                if temp not in actions_dirs:
                    actions_dirs.append(temp)
        if str_path not in actions_dirs:
            actions_dirs.append(str_path)
    paths = []
    get_all_leaf_dirs(os.path.join(path, 'Actions'), paths)
    for actions_dir in actions_dirs:
        for p in paths:
            if p == actions_dir:
                paths.remove(p)
                break
    for p in reversed(paths):
        delete_directory(p, logfile, print_log_name)


def get_action_folder_details(path, destination):
    """ Gets all the folder inside the Actions folder

    :Arguments:

    1. destination (str) = Contains path to the directory in which
    the files to be overwritten reside.
    2. path (str) = Contains the path to the temp folder where the
    repository is initially cloned

    :Returns:

    """
    if os.path.basename(os.path.dirname(path)) != "Actions":
        destination.append(os.path.basename(os.path.dirname(path)))
        get_action_folder_details(os.path.dirname(path), destination)


def get_action_name_from_driver(li_actions, path):
    """ This functions peeks into the driver file, reads it and recognises
    which Actions packages are required by the driver.

    :Arguments:

    1. path (str) = Contains the path to the temp folder where the
    repository is initially cloned
    2. li_actions (list) = Contains list of action packages that are
    required by the driver in question.

    :Returns:

    """
    subfiles, _ = get_subfiles(os.path.join(path, 'ProductDrivers'))
    for subfile in subfiles:
        load_profile = open(os.path.join(path, 'ProductDrivers', subfile), "r")
        read_it = load_profile.read()
        import_actions = []
        for line in read_it.splitlines():
            if line.startswith("import"):
                import_actions.append(line)
        for word in words(import_actions):
            if word != "import":
                li_actions.append(word)


def clone_drivers(base_path, current_dir, **kwargs):
    """ This function has been written to clone Keywords, cherry pick the
    drivers as per the instructions in the .xml file,
    choose Actions accordingly, and overwrite existing Framework folder if it
    exists.

    :Arguments:

    1. print_log_name (str) = Contains the name of the print_log file.
    2. config_file_name (str) = Contains the path to the .xml file.
    3. logfile (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'
    4. base_path (str) = Contains the path to the directory in which the user
    wants to clone Warrior.

    :Returns:

    """
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    print_log_name = kwargs.get("print_log_name")
    internal_copy = kwargs.get("dest")
    if internal_copy == "":
        destination = os.path.join(base_path, 'warrior')
    else:
        destination = os.path.join(base_path, 'warrior')
    node = get_node(config_file_name, "drivers")
    if node is False:
        print_error("Drivers tag not found. No drivers cloned.",
                    logfile, print_log_name)
        setDone(1)
    else:
        repositories = get_firstlevel_children(node, "repository")
        for repository in repositories:
            if ('url' not in repository.attrib and 'label' not in repository.attrib and
                    'all_drivers' not in repository.attrib and 'clone' not in repository.attrib):
                continue
            url = get_attribute_value(repository, "url")
            name = get_repository_name(url)

            # for http/https url types, embed username & password in url
            username = get_attribute_value(repository, "username")
            password = get_attribute_value(repository, "password")
            url = embed_user_cred_in_url(url, username, password)

            # url validation
            if url == "":
                print_error("Can't clone repository without the url!",
                            logfile, print_log_name)
                setDone(1)
                print_info(name + " not cloned.", logfile, print_log_name)
                continue
            if not check_url_is_a_valid_repo(url, name, logfile,
                                             print_log_name):
                continue
            try:
                if internal_copy == "":
                    create_dir(os.path.join(base_path, 'temp'))
                else:
                    create_dir(os.path.join(base_path, 'temp'))
            except Exception:
                print_error("Warhorn does not have the required permissions "
                            "to clone " + name, logfile, print_log_name)
                setDone(1)
            else:
                if internal_copy == "":
                    path = os.path.join(base_path, 'temp', name)
                else:
                    path = os.path.join(base_path, 'temp', name)
                label = get_attribute_value(repository, "label")

                # current_dir stores the path in which warhorn.py is running
                print_info("Cloning " + name, logfile, print_log_name)

                # directory switch to where the drivers should be cloned.
                if internal_copy == "":
                    os.chdir(os.path.join(base_path, 'temp'))
                else:
                    os.chdir(os.path.join(base_path, 'temp'))
                try:
                    subprocess.check_output(["git", "clone", url])
                except Exception:
                    print_error(name + " could not be cloned.",
                                logfile, print_log_name)
                    setDone(1)
                    continue
                if label != "":
                    print_info("Checking out: " + label, logfile, print_log_name)
                    check, current_tag = git_checkout_label(label, path, current_dir)
                    print_out_checkout_status(label, check, current_tag, name, logfile=logfile,
                                              print_log_name=print_log_name)

                print_info("Cloning complete", logfile, print_log_name)

                clone = get_attribute_value(repository, "clone")
                if clone == "" or clone == "yes":
                    try:
                        clone_user_specified_drivers(path, repository,
                                                     destination, logfile,
                                                     print_log_name)
                    except:
                        print_error("Could not copy drivers/actions files "
                                    "from " + name + " into warrior_main",
                                    logfile, print_log_name)
                        setDone(1)

                # folder inside the temp folder that had the initial clone of
                # the repository get deleted here. This is done for every
                # iteration because if user wants to clone another repository
                # with the same name, it should not create a problem.
                if internal_copy == "":
                    tmp_path = os.path.join(base_path, 'temp', name)
                else:
                    tmp_path = os.path.join(base_path, 'temp', name)
                if os.path.exists(tmp_path):
                    delete_directory(tmp_path, logfile, print_log_name)


def clone_user_specified_drivers(path, repository, destination,
                                 logfile, print_log_name):
    """ This function, calls various functions to copy over only the required
    files and folders

    :Arguments:

    1. print_log_name (str) = Contains the name of the print_log file.
    2. logfile (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'
    3. destination (str) = Contains path to the directory in which the files
    to be replaced reside.
    4. repository (xml.etree.ElementTree.Element) = node of the repository
    in question
    5. path (str) = Contains the path to the temp folder where the
    repository is initially cloned

    :Returns:

    """
    drivers = get_firstlevel_children(repository, "driver")
    all_drivers = get_attribute_value(repository, "all_drivers")
    if all_drivers == "yes" or (all_drivers == "" and len(drivers) == 0):
        replace_folders(path, repository, destination, logfile, print_log_name)
    elif all_drivers == "no" or (all_drivers == "" and len(drivers) != 0):
        remove_extra_drivers(drivers, path)
        remove_extra_actions(path, logfile, print_log_name)
        replace_folders(path, repository, destination, logfile, print_log_name)


def clone_warriorspace(base_path, current_dir, **kwargs):
    """ Clones Warriorspace.

    :Arguments:

    1. config_file_name (str) = Contains the path to the .xml file.
    2. print_log_name (str) = Contains the name of the print_log file.
    3. logfile (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'
    4. base_path (str) = Contains the path to the directory in which the user
    wants to clone Warrior.

    :Returns:

    """
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    print_log_name = kwargs.get("print_log_name")
    node = get_node(config_file_name, "warriorspace")
    if node is False:
        print_error("warriorspace tag not found. No warriorspace cloned.",
                    logfile, print_log_name)
        setDone(1)
    else:
        repositories = get_firstlevel_children(node, "repository")

        for repository in repositories:
            if 'url' not in repository.attrib and\
                            'label' not in repository.attrib and\
                            'all_drivers' not in repository.attrib and\
                            'clone' not in repository.attrib:
                continue
            clone = get_attribute_value(repository, "clone")
            if clone == "" or clone == "yes":
                url = get_attribute_value(repository, "url")
                name = get_repository_name(url)

                # for http/https url types, embed username & password in url
                username = get_attribute_value(repository, "username")
                password = get_attribute_value(repository, "password")
                url = embed_user_cred_in_url(url, username, password)

                # url validation
                if url == "":
                    print_error("Can't clone repository without the url!",
                                logfile, print_log_name)
                    setDone(1)
                    print_info(name + " not cloned.", logfile, print_log_name)
                    continue
                if not check_url_is_a_valid_repo(url, name, logfile, print_log_name):
                    continue
                try:
                    create_dir(os.path.join(base_path, 'warrior', 'temp'))
                except:
                    print_error("Warhorn does not have the required permissions to clone " + name,
                                logfile, print_log_name)
                    setDone(1)
                else:
                    overwrite = get_attribute_value(repository, "overwrite")
                    label = get_attribute_value(repository, "label")
                    path = os.path.join(base_path, 'warrior', 'temp', name)

                    # current_dir stores the path of the directory in which
                    # warhorn.py is running
                    print_info("Cloning " + name + " warriorspace",
                               logfile, print_log_name)

                    # directory switch to where the warriorspace should be
                    # cloned.
                    os.chdir(os.path.join(base_path, 'warrior', 'temp'))
                    try:
                        subprocess.check_output(["git", "clone", url])
                    except:
                        print_error(name + " could not be cloned.",
                                    logfile, print_log_name)
                        setDone(1)
                        continue
                    if label != "":
                        print_info("Checking out: " + label, logfile,
                                   print_log_name)
                        check, current_tag = git_checkout_label(label, path,
                                                                current_dir)
                        print_out_checkout_status(label, check, current_tag,
                                                  name, logfile=logfile,
                                                  print_log_name=print_log_name)

                    # directory switch to where warhorn.py is running.
                    print_info("Cloning complete", logfile, print_log_name)
                    destination = os.path.join(base_path, 'warrior', 'Warriorspace')
                    dummy, root_repo_folder_list = get_subfiles(path)
                    if 'Warriorspace' not in root_repo_folder_list:
                        print_error('Could not find Warriorspace under the '
                                    'root of the repository')
                        setDone(1)
                    else:
                        try:
                            overwrite_files(os.path.join(path, 'Warriorspace'),
                                            destination, overwrite, logfile, print_log_name)
                        except:
                            print_error("Could not copy Warriorspace files from {} into "
                                        "warriorframework".format(name), logfile, print_log_name)
                            setDone(1)
                # folder inside the temp folder that had the initial clone of
                # the repository get deleted here. This is done for every
                # iteration because if user wants to clone another repository
                # with the same name, it should not create a problem
                tmp_path = os.path.join(base_path, 'warrior', 'temp', name)
                if os.path.exists(tmp_path):
                    delete_directory(tmp_path, logfile, print_log_name)


def delete_temp_files_and_folders(base_path="", current_dir="", **kwargs):
    """ Deletes the temporary folders created.
    Copies over the log files to their correct location.
    Deletes the temp log files

    :Arguments:
    1. console_log_name (str) = Contains the name of the console_log file.
    2. print_log_name (str) = Contains the name of the print_log file.
    3. config_file_name (str) = Contains the path to the .xml file.
    4. logfile (file object) = Contains the file object for the console_log
    file. This file object is the 'opened' console_log file with mode set to 'a'
    4. base_path (str) = path to the temp folders inside Warrior
    :Returns:
    """
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    console_log_name = kwargs.get("console_log_name")
    print_log_name = kwargs.get("print_log_name")
    # temp folder deletions.
    # .git and tests folder deletions.
    path_list = [os.path.join(base_path, 'warrior', 'temp'),
                 os.path.join(base_path, 'temp'),
                 os.path.join(base_path, 'warrior', '.git')]
    if base_path != "":
        for path in path_list:
            if os.path.exists(path):
                delete_directory(path, logfile, print_log_name)

    # console_log file object closed.
    logfile.close()

    # time stamped directory created.
    path = os.path.join(current_dir,
                        'logs', get_date_and_time())
    create_dir(path)

    try:
        # .xml file copied over.
        if config_file_name != "":
            shutil.copyfile(config_file_name, os.path.join(path, 'config.xml'))

        # log files copied over
        shutil.copyfile(print_log_name, os.path.join(path,
                        os.path.basename(os.path.normpath(print_log_name))))
        shutil.copyfile(console_log_name, os.path.join(path,
                        os.path.basename(os.path.normpath(console_log_name))))
    except:
        print_error("Unable to copy config/print_log/console_log file to correct location",
                    logfile, print_log_name)

    # log files deleted from the original directory.
    os.remove(print_log_name)
    os.remove(console_log_name)


def validate_base_path(base_path, repo_name="warrior", **kwargs):
    """ Validates user defined value for the destination attribute in the
    Warrior tag in the config file. If the user hasn't defined anything,
    the default value would be set to the current working directory.

    :Arguments:

    1. base_path (str) = user defined value for the destination attribute in the
    Warrior tag in the config file
    2. logfile (file object) = file object of the console_log file
    3. config_file_name (str) = name of the config xml file
    4. console_log_name (str) = Name of the console_log file
    5. print_log_name (str) = Name of the print_log file

    :Returns:

    1. base_path (str) = valid base_path

    """
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    console_log_name = kwargs.get("console_log_name")
    print_log_name = kwargs.get("print_log_name")
    if base_path == "":
        base_path = get_parent_dir(os.path.dirname(os.path.realpath(__file__)))
    try:
        create_dir(os.path.join(base_path, "temp"))
        delete_directory(os.path.join(base_path, "temp"), logfile,
                         print_log_name)
    except:
        print_error("You do not have permission to write in " + base_path +
                    ".", logfile, print_log_name)
        setDone(1)
        if repo_name == "warrior":
            delete_temp_files_and_folders(logfile=logfile,
                                          config_file_name=config_file_name,
                                          console_log_name=console_log_name,
                                          print_log_name=print_log_name)
            getDone(logfile, print_log_name)
        else:
            return None
    return base_path


def delete_older_logfiles(console_log_name, print_log_name):
    """ This function deletes existing older logfiles if they already exist.

    :Arguments:

    1. console_log_name (str) = Name of the console_log file
    2. print_log_name (str) = Name of the print_log file
    """
    if os.path.exists(os.path.join("source", print_log_name)):
        os.remove(os.path.join("source", print_log_name))
    if os.path.exists(os.path.join("source", console_log_name)):
        os.remove(os.path.join("source", console_log_name))
    if os.path.exists(os.path.join(print_log_name)):
        os.remove(os.path.join(print_log_name))
    if os.path.exists(os.path.join(console_log_name)):
        os.remove(os.path.join(console_log_name))


def check_if_tools_should_be_cloned(node, p_node, base_path, current_dir,
                                    **kwargs):
    """This functions checks if the clone attribute for all the repository tags
    that are not Warrior are set to 'yes' or not. If itis, only then that
    repository would be cloned, else it won't be."""
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    console_log_name = kwargs.get("console_log_name")
    print_log_name = kwargs.get("print_log_name")
    clone = get_attribute_value(node, "clone")
    url = get_attribute_value(node, "url")
    repo_root = get_repository_name(url)
    if clone == "yes":
        clone_warrior_and_tools(base_path, current_dir, repo_root, logfile=logfile,
                                config_file_name=config_file_name,
                                console_log_name=console_log_name,
                                print_log_name=print_log_name,
                                repo_name=p_node)
    else:
        print_info("Warhorn will not install " + p_node + " as the clone attribute "
                   "was not set to 'yes'.", logfile, print_log_name)


def clone_major_repositories(p_node, **kwargs):
    """This function calls the clone_warrior_and_tools function if p_node is
    set to 'warrior', else it calls the check_if_tools_should_be_cloned
    function if it is any other repository. It also gets the path of the
    directory that has been mentioned in the xml file as the value of the
    'destination' attribute"""
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    console_log_name = kwargs.get("console_log_name")
    print_log_name = kwargs.get("print_log_name")
    base_path, node = get_base_path(p_node, logfile=logfile,
                                    config_file_name=config_file_name,
                                    console_log_name=console_log_name,
                                    print_log_name=print_log_name)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if base_path is not None:
        check_if_tools_should_be_cloned(node, p_node, base_path, current_dir,
                                        logfile=logfile,
                                        config_file_name=config_file_name,
                                        console_log_name=console_log_name,
                                        print_log_name=print_log_name)


def get_base_path(node_name="warriorframework", **kwargs):
    """This function returns the base_path - the path where the git repository
    is supposed to be cloned."""
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    print_log_name = kwargs.get("print_log_name")
    console_log_name = kwargs.get("console_log_name")
    node = get_node(config_file_name, node_name)
    base_path = ""
    if node is not False:
        base_path = get_attribute_value(node, "destination")
    base_path = validate_base_path(base_path, logfile=logfile,
                                   config_file_name=config_file_name,
                                   console_log_name=console_log_name,
                                   print_log_name=print_log_name)
    return base_path, node


def activate_virtualenv(node, destination, logfile, print_log_name):
    '''Activate virtual environment to add dependencies
    '''
    ve_name = get_attribute_value(node, 'name')
    ve_loc = get_attribute_value(node, 'location')
    ve_dest = os.path.join(destination, ve_name)
    print_info("ve_name: "+ve_name, logfile, print_log_name)
    print_info("destination: "+ve_dest, logfile, print_log_name)
    try:
        venv_cmd = os.path.expanduser(ve_loc)
        subprocess.check_call([venv_cmd, "--system-site-packages", ve_dest])
        venv_file = "{}/bin/activate_this.py".format(ve_dest)
        execfile(venv_file, dict(__file__=venv_file))
        return True
    except Exception as e:
        print_error("Activating virtual env at {} resulted in exception {}".format(
                                                ve_dest, e), logfile, print_log_name)
        print_error("Check {} is a proper virtualenv binary".format(ve_loc),
                    logfile, print_log_name)
        setDone(1)
        return False


def replace_tools_from_product_repo(node_list, **kwargs):
    """ This will clone the tools from product repo and then replaces
        tools directory in warrior main with this tools repo.
    """
    logfile = kwargs.get("logfile")
    config_file_name = kwargs.get("config_file_name")
    console_log_name = kwargs.get("console_log_name")
    print_log_name = kwargs.get("print_log_name")
    if "tools" in node_list:
        tools_node = get_node(config_file_name, "tools")
        tools_url = get_attribute_value(tools_node, "url")
        tools_root = get_repository_name(tools_url)
        tools_clone = get_attribute_value(tools_node, "clone")
        tools_base_path = ""
        warrior_node = get_node(config_file_name, "warriorframework")
        warrior_base_path = get_attribute_value(warrior_node, "destination")
        if tools_url and tools_clone == "yes":
            tools_base_path = validate_base_path(
                tools_base_path, logfile=logfile,
                config_file_name=config_file_name,
                console_log_name=console_log_name,
                print_log_name=print_log_name)
            warrior_base_path = validate_base_path(
                warrior_base_path, logfile=logfile,
                config_file_name=config_file_name,
                console_log_name=console_log_name, print_log_name=print_log_name)
            warrior_tools_path = os.path.join(warrior_base_path,
                                                  "warrior", "Tools")
            product_tools_path = os.path.join(tools_base_path, tools_root, "Tools")
            dir_util.copy_tree(product_tools_path, warrior_tools_path, update=1)
            delete_directory(os.path.join(tools_base_path, tools_root), logfile, print_log_name)


def assemble_warrior():
    """Assembles Warrior by:
     - Installing dependencies
     - Cloning Warrior in the specified location
     - Cloning drivers, then cloning the corresponding Actions, and Framework in
     a temp folder
       and then copying the files over to their correct location.
     - Cloning Warriorspace in a temp folder and then copying the files over to
     their correct location.
     - Deleting the temp folders.

     :Arguments:

     1. sys.argv[0] (str) = path to warhorn.py - an unused argument
     2. sys.argv[1] (str) = optional argument as to when the user wants to run a
     different .xml file. The user must specify the complete path to .xml
     file if s/he has stored it in a folder different than the folder in which
     warhorn.py is running.

     :Returns:

    """
    setDone(0)
    virtualenv_activated = False
    if sys.executable is None or sys.executable == "":
        python_executable = "python"
    else:
        python_executable = sys.executable
    dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if len(sys.argv) > 1 and sys.argv[1] == "-interactive":
        rel_path = get_relative_path(dir_path, "source",
                                     "interactive_warhorn.py")
        subprocess.call(["python", rel_path])
        sys.exit()
    elif len(sys.argv) > 1 and sys.argv[1] != "-interactive":
        config_file_name = os.path.realpath(sys.argv[1])
    else:
        config_file_name = os.path.join(dir_path, "default_config.xml")

    console_log_name, print_log_name = set_file_names()
    delete_older_logfiles(console_log_name, print_log_name)
    console_log_name = os.path.join(dir_path, console_log_name)
    print_log_name = os.path.join(dir_path, print_log_name)

    logfile = open(console_log_name, 'a')

    # config file validation
    if not os.path.exists(config_file_name):
        print_error("Config file not found!", logfile, print_log_name)
        delete_temp_files_and_folders(logfile=logfile,
                                      config_file_name="",
                                      console_log_name=console_log_name,
                                      print_log_name=print_log_name)
        setDone(1)
        getDone(logfile, print_log_name)

    check_basic_requirements(logfile, config_file_name, console_log_name,
                             print_log_name, python_executable)
    node = get_node(config_file_name, 'virtualenv')
    if node is not False and get_attribute_value(node, 'name') != '':
        if get_attribute_value(node, 'install') == 'yes':
            install_depen('virtualenv', 'virtualenv', logfile, print_log_name)
        war_tag = get_node(config_file_name, 'warriorframework')
        if war_tag is False:
            print_error("warriorframework is a mandatory repo. Please add and rerun",
                        logfile, print_log_name)
            setDone(1)
            getDone(logfile, print_log_name)
        dest = os.getcwd()
        virtualenv_activated = activate_virtualenv(node, dest, logfile, print_log_name)

    get_dependencies(logfile, print_log_name, config_file_name, virtualenv_activated)
    internal_copy = get_dest(logfile, print_log_name, config_file_name)

    node_list = get_all_direct_child_nodes(config_file_name)
    node_list = remove_extra_list_elements(node_list, "warhorn", "drivers",
                                           "warriorspace", "virtualenv")
    for node in node_list:
        if node == "warriorframework":
            print_info("The ability to upgrade/downgrade wariorframework version would be available for use soon.", logfile, print_log_name)
        else:
            clone_major_repositories(node, logfile=logfile,
                                     config_file_name=config_file_name,
                                     console_log_name=console_log_name,
                                     print_log_name=print_log_name)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    base_path, _ = get_base_path("warriorframework", logfile=logfile,
                                 config_file_name=config_file_name,
                                 console_log_name=console_log_name,
                                 print_log_name=print_log_name)

    replace_tools_from_product_repo(node_list, logfile=logfile,
                                    config_file_name=config_file_name,
                                    console_log_name=console_log_name,
                                    print_log_name=print_log_name,
                                    dest=internal_copy)
    clone_drivers(base_path, current_dir, logfile=logfile,
                  config_file_name=config_file_name,
                  print_log_name=print_log_name,
                  dest=internal_copy)
    clone_warriorspace(base_path, current_dir, logfile=logfile,
                       config_file_name=config_file_name,
                       print_log_name=print_log_name,
                       dest=internal_copy)
    delete_temp_files_and_folders(base_path, current_dir, logfile=logfile,
                                  config_file_name=config_file_name,
                                  console_log_name=console_log_name,
                                  print_log_name=print_log_name,
                                  dest=internal_copy)

    getDone(logfile, print_log_name)


if __name__ == "__main__":
    assemble_warrior()
