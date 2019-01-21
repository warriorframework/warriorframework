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
import re
import sys
import Tools
from Framework.Utils import file_Utils
from Framework.Utils.data_Utils import get_credentials
from Framework.Utils.print_Utils import print_error, print_info
import Framework.Utils.encryption_utils as Encrypt
from WarriorCore.Classes import war_cli_class
"""Handle all the cli command, new functions may be added later"""


def decide_runcat_actions(w_cli_obj, namespace):
    """Decide the actions to be taken for runcat tag """
    filepath = namespace.filepath

    if namespace.tcdir is not None and len(namespace.tcdir) == 0:
        namespace.tcdir = None

    if namespace.runcat and namespace.suitename is None:
        namespace.cat = namespace.runcat
        filepath = w_cli_obj.check_tag(namespace.cat, namespace.tcdir)

    elif namespace.runcat and namespace.suitename is not None and len(namespace.runcat) != 0:
        namespace.cat = namespace.runcat
        filepath = w_cli_obj.examine_create_suite(namespace)
        print_info("suite created in ", filepath[0])

    if len(filepath) == 0:
        print_error("No matching Testcases found for the provided category(ies)")
        exit(1)
    print_info("file path for runcat actions is ", filepath)
    return filepath


def decide_createsuite_actions(w_cli_obj, namespace):
    """Decide the actions for -createsuite tag """
    filepath = namespace.filepath

    # already check namespace.create here, no need to double check
    if namespace.filepath is not None and len(namespace.filepath) == 0:
        namespace.filepath = None

    if all([namespace.suitename, namespace.filepath]):
        filepath = w_cli_obj.examine_create_suite(namespace)
        print_info("suite created in ", filepath[0])
        exit(0)

    if all([namespace.suitename, namespace.cat]):
        filepath = w_cli_obj.examine_create_suite(namespace)
        print_info("suite created in ", filepath[0])
        exit(0)

    elif not namespace.cat and not all([namespace.suitename, namespace.filepath]):
        print_error("Invalid combination... Use -createsuite with -suitename, "
                    "filepath(s) (i.e. list of testcase xml files. "
                    "Use -h or --help for more command line options")
        exit(1)
    elif namespace.cat and not namespace.suitename:
        print_error("Invalid combination... Use -creatsuite + -category "
                    "with -suitename")
        exit(1)

    return filepath


def decide_ujd_actions(w_cli_obj, namespace):
    """Decide upload jira objects actions """
    if namespace.ujd and any([namespace.ddir, namespace.djson]):
        if namespace.ddir is not None and namespace.djson is None:
            w_cli_obj.manual_defects("dir", namespace.ddir, jiraproj=namespace.jiraproj)
        elif namespace.djson is not None and namespace.ddir is None:
            w_cli_obj.manual_defects("files", namespace.djson, jiraproj=namespace.jiraproj)
        elif namespace.ddir is not None and namespace.djson is not None:
            print_error("Use -ujd with one of -ddir or -djson  not both")
        exit(0)
    elif namespace.ujd and not any([namespace.ddir, namespace.djson]):
        print_error("Use -ujd with one of -ddir or -djson")
        exit(1)


def decide_overwrite_var(namespace):
    """options provided in cli get preference over the ones provided inside tests
    """
    overwrite = {}
    if namespace.datafile:
        if namespace.datafile[0] != os.sep:
            namespace.datafile = os.getcwd() + os.sep + namespace.datafile
        overwrite['ow_datafile'] = namespace.datafile
    #namespace for wrapperfile
    if namespace.wrapperfile:
        if namespace.wrapperfile[0] != os.sep:
            namespace.wrapperfile = os.getcwd() + os.sep + namespace.wrapperfile
        overwrite['ow_testwrapperfile'] = namespace.wrapperfile
    if namespace.resultdir:
        if namespace.resultdir[0] != os.sep:
            namespace.resultdir = os.getcwd() + os.sep + namespace.resultdir
        overwrite['ow_resultdir'] = namespace.resultdir
    if namespace.logdir:
        if namespace.logdir[0] != os.sep:
            namespace.logdir = os.getcwd() + os.sep + namespace.logdir
        overwrite['ow_logdir'] = namespace.logdir
    if namespace.outputdir:
        if namespace.outputdir[0] != os.sep:
            namespace.outputdir = os.getcwd() + os.sep + namespace.outputdir
        overwrite['ow_resultdir'] = namespace.outputdir
        overwrite['ow_logdir'] = namespace.outputdir
    if all([namespace.outputdir, any([namespace.resultdir, namespace.logdir])]):
        print_error("outputdir shouldn't be used with resultdir or logdir")
        exit(1)
    if namespace.jobid:
        settings_xml = Tools.__path__[0] + os.sep + 'w_settings.xml'
        job_url = get_credentials(settings_xml, 'job_url', ['url'], 'Setting')
        if job_url['url'] is not None:
            url = job_url['url']
        else:
            print_info("jobid is specified but no job url found in w_settings")
            print_info("Using jobid only in JUnit file")
            url = ""
        overwrite['jobid'] = url + str(namespace.jobid)
    return overwrite


def decide_action(w_cli_obj, namespace):
    """Prepare filepath and other arguments for Warrior main to use"""
    # First level, sleep
    if namespace.target_time:
        w_cli_obj.gosleep(namespace.target_time)

    # Second level, decide filepath
    cli_args = [namespace.kwparallel, namespace.kwsequential,
                namespace.tcparallel, namespace.tcsequential,
                namespace.RMT, namespace.RUF]
    filepath = namespace.filepath

    # runcat related actions
    if namespace.runcat:
        filepath = decide_runcat_actions(w_cli_obj, namespace)

    elif namespace.create:
        filepath = decide_createsuite_actions(w_cli_obj, namespace)

    elif namespace.encrypt:
        status = True
        encoded_key = False
        if namespace.secretkey:
            # Checks if User has given a string for creating a secret key
            status, encoded_key = Encrypt.set_secret_key(namespace.secretkey)
        else:
            # If secret key has not been given, checks for the existence of the
            # secret.key file
            path = file_Utils.get_parent_dir(os.path.realpath(__file__),
                                             "WarriorCore")
            path = os.path.join(path, "Tools", "admin", "secret.key")
            if not os.path.exists(path):
                print_error("Could not find the secret.key file in Tools/Admin!"
                            " Please use '-secretkey your_key_text' in the "
                            "-encrypt command for creating the file!")
                status = False
        if status:
            # sends secret key and plain text password for encryption
            message = Encrypt.encrypt(namespace.encrypt[0], encoded_key)
            # Checks if message is not hexadecimal
            if re.match(r".*[g-z].*", message):
                print_error(message)
            else:
                print_info("The encrypted text for '{0}' is: {1}".
                           format(namespace.encrypt[0], message))
        else:
            print_error("Encrypted text could not be generated.")
        exit(1)

    elif namespace.decrypt:
        status = True
        encoded_key = False
        if namespace.secretkey:
            # Checks if User has given a string for creating a secret key
            status, encoded_key = Encrypt.set_secret_key(namespace.secretkey)
        else:
            # If secret key has not been given, checks for the existence of the
            # secret.key file
            path = file_Utils.get_parent_dir(os.path.realpath(__file__),
                                             "WarriorCore")
            path = os.path.join(path, "Tools", "admin", "secret.key")
            if not os.path.exists(path):
                print_error("Could not find the secret.key file in Tools/Admin!"
                            " Please use '-secretkey your_key_text' in the "
                            "-encrypt command for creating the file!")
                status = False
        if status:
            # sends secret key and encrypted text password for decryption
            message = Encrypt.decrypt(namespace.decrypt[0], encoded_key)
            # Checks if message is not hexadecimal
            print_info("The decrypted text for '{0}' is: {1}".
                       format(namespace.decrypt[0], message))
        else:
            print_error("Decrypted text could not be generated.")
        exit(1)

    elif any(cli_args):
        filepath = w_cli_obj.examine_cli_args(cli_args, namespace)

    elif namespace.ujd:
        decide_ujd_actions(w_cli_obj, namespace)

    def append_path(path_list, path):
        """Append appropriate paths for testcase/suite/project in test folder
        """
        temp_list = []
        for file_name in path_list:
            file_name = path + file_name
            temp_list.append(file_name)
        filepath.extend(temp_list)

    if namespace.tc_name is not None:
        append_path(namespace.tc_name, "Warriorspace/Testcases/")

    if namespace.ts_name is not None:
        append_path(namespace.ts_name, "Warriorspace/Suites/")

    if namespace.proj_name is not None:
        append_path(namespace.proj_name, "Warriorspace/Projects/")

    # overwrite layer
    overwrite = decide_overwrite_var(namespace)

    if filepath is None:
        print_error("No input filepath: {0}".format(namespace.filepath))
        exit(1)
    else:
        for index, file_name in enumerate(filepath):
            if len(file_name.split('.')) == 1:
                filepath[index] = file_name + '.xml'

    # print filepath
    return (filepath, namespace.ad, namespace.version,
            namespace.ironclaw, namespace.jiraproj, overwrite,
            namespace.jiraid, namespace.dbsystem, namespace.headless)


def main(args):
    """init a Warrior Cli Class object, parse its arguments and run it"""
    w_cli_obj = war_cli_class.WarriorCliClass()
    parsed_args = w_cli_obj.parser(args)
    return decide_action(w_cli_obj, parsed_args)

if __name__ == "__main__":
    print re.match(r"[g-z]", raw_input("Enter: "))
    main(sys.argv[1:])
