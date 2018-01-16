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

try:
    import os
    import re
    import sys
    import shutil
    import Framework.Utils.email_utils as email
    import Framework.Utils as Utils
    import Framework.Utils.encryption_utils as Encrypt
    from Framework.Utils import xml_Utils, file_Utils
    from Framework.Utils.print_Utils import print_error, print_info
    from Framework.ClassUtils import database_utils_class
    from WarriorCore import testcase_driver, testsuite_driver, project_driver
    from WarriorCore import ironclaw_driver, mockrun_driver, framework_detail
    from WarriorCore.Classes import war_cli_class
    from WarriorCore.Classes.jira_rest_class import Jira
except:
    raise

def update_jira_by_id(jiraproj, jiraid, exec_dir, status):
    """ If jiraid is provided, upload the log and result file to jira """
    if jiraid is not False:
        jira_obj = Jira(jiraproj)
        if jira_obj.status is True:
            zip_file = shutil.make_archive(exec_dir, 'zip', exec_dir)
            jira_obj.upload_logfile_to_jira_issue(jiraid, zip_file)
            jira_obj.update_jira_issue(jiraid, status)

    else:
        print_info("jiraid not provided, will not update jira issue")


def add_live_table_divs(livehtmllocn, file_list):
    """
    add the divs for the live html table
    """

    root_attribs = {'id': 'liveTables'}
    root = xml_Utils.create_element("div", "", **root_attribs)

    # for each iteration create a div with id = the iteration number
    # the table for tis iteration will be added
    # under this div

    for i in range(0, len(file_list)):
        marker_start = 'table-{0}starts'.format(str(i))
        marker_end = 'table-{0}ends'.format(str(i))
        div_attribs = {'id': str(i)}
        elem = xml_Utils.create_subelement(root, 'div', div_attribs)
        start_comment = xml_Utils.create_comment_element(marker_start)
        end_comment = xml_Utils.create_comment_element(marker_end)
        elem.append(start_comment)
        elem.append(end_comment)
        # write the tree to the file
        xml_Utils.write_tree_to_file(root, livehtmllocn)

def file_execution(parameter_list, cli_args, abs_filepath, default_repo):
    """
        Call the corresponded driver of each file type
    """
    result = False
    mockrun = cli_args.mockrun
    a_defects = cli_args.ad
    jiraproj = cli_args.jiraproj
    jiraid = cli_args.jiraid

    if mockrun:
        result = mockrun_driver.main(abs_filepath, len(parameter_list))
    elif Utils.xml_Utils.getRoot(abs_filepath).tag == 'Testcase':
        default_repo['war_file_type'] = "Case"
        result, _, data_repository = testcase_driver.main(
            abs_filepath, data_repository=default_repo,
            runtype='SEQUENTIAL_KEYWORDS',
            auto_defects=a_defects, jiraproj=jiraproj)
        update_jira_by_id(jiraproj, jiraid, os.path.dirname(
            data_repository['wt_resultsdir']), result)
        email.compose_send_email("Test Case: ", abs_filepath,
                                 data_repository['wt_logsdir'],
                                 data_repository['wt_resultsdir'], result)
    elif Utils.xml_Utils.getRoot(abs_filepath).tag == 'TestSuite':
        default_repo['war_file_type'] = "Suite"
        result, suite_repository = testsuite_driver.main(
            abs_filepath, auto_defects=a_defects,
            jiraproj=jiraproj, data_repository=default_repo)
        update_jira_by_id(jiraproj, jiraid,
                          suite_repository['suite_execution_dir'], result)
        email.compose_send_email("Test Suite: ", abs_filepath,
                                 suite_repository['ws_logs_execdir'],
                                 suite_repository['ws_results_execdir'], result)
    elif Utils.xml_Utils.getRoot(abs_filepath).tag == 'Project':
        default_repo['war_file_type'] = "Project"
        result, project_repository = project_driver.main(
            abs_filepath, auto_defects=a_defects,
            jiraproj=jiraproj, data_repository=default_repo)
        update_jira_by_id(jiraproj, jiraid,
                          project_repository['project_execution_dir'], result)
        email.compose_send_email("Project: ", abs_filepath,
                                 project_repository['wp_logs_execdir'],
                                 project_repository['wp_results_execdir'], result)
    else:
        print_error("Unrecognized root tag in the input xml file ! exiting!!!")

    return result

def group_execution(parameter_list, cli_args, abs_cur_dir, db_obj, overwrite, livehtmlobj):
    """
        Process the parameter list and prepare environment for file_execution
    """
    livehtmllocn = cli_args.livehtmllocn

    status = True

    iter_count = 0 ## this iter is used for live html results
    for parameter in parameter_list:
        result = False
        # check if the input parameter is an xml file
        if Utils.file_Utils.get_extension_from_path(parameter) == '.xml':
            filepath = parameter
            framework_detail.warrior_banner()
            abs_filepath = Utils.file_Utils.getAbsPath(filepath, abs_cur_dir)
            print_info('Absolute path: {0}'.format(abs_filepath))
            if Utils.file_Utils.fileExists(abs_filepath):
                if overwrite.items():
                    default_repo = overwrite
                else:
                    default_repo = {}

                if db_obj is not False and db_obj.status is True:
                    default_repo.update({'db_obj': db_obj})
                else:
                    default_repo.update({'db_obj': False})

                #pdate livehtmllocn to default repo
                if livehtmllocn or livehtmlobj is not None:
                    live_html_dict = {}
                    live_html_dict['livehtmllocn'] =\
                        livehtmllocn if livehtmlobj is None else livehtmlobj
                    live_html_dict['iter'] = iter_count

                    default_repo.update({'live_html_dict': live_html_dict})
                    if iter_count == 0 and livehtmlobj is None:
                        add_live_table_divs(livehtmllocn, parameter_list)
                    elif iter_count == 0 and livehtmlobj is not None:
                        add_live_table_divs(livehtmlobj, parameter_list)

                result = file_execution(parameter_list, cli_args, abs_filepath, default_repo)
            else:
                print_error("file does not exist !! exiting!!")
        else:
            print_error("unrecognized file format !!!")
        status = status and result
        iter_count += 1
    return status

# def execution(parameter_list, mockrun, a_defects, cse_execution, iron_claw,
#          jiraproj, overwrite, jiraid, dbsystem, livehtmllocn):
def execution(parameter_list, cli_args, overwrite, livehtmlobj):
    """Parses the input parameters (i.e. sys.argv)
        If the input parameter is an xml file:
            - check if file exists, if exists
                - if the input is a testcase xml file, execute the testcase
                - if the input is a testsuite xml file, excute the testsuite
                - if the input is a project xml file, excute the project

        If the input is not an xml file:
            - check if it is a json object/array respresenting a valid Warrior
            suite structure, if yes to execute a build
    Arguments:
        1. parameter_list = list of command line parameters supplied by
        the user to execute Warrior
    """
    if cli_args.version:
        framework_detail.warrior_framework_details()
        sys.exit(0)
    if not parameter_list:
        print_error("Provide at least one xml file to execute")
        sys.exit(1)

    iron_claw = cli_args.ironclaw
    dbsystem = cli_args.dbsystem

    status = False

    if iron_claw:
        status = ironclaw_driver.main(parameter_list)
    else:
        abs_cur_dir = os.path.abspath(os.curdir)
        db_obj = database_utils_class.create_database_connection(dbsystem=dbsystem)
        status = group_execution(parameter_list, cli_args, abs_cur_dir,
                                 db_obj, overwrite, livehtmlobj)

        if db_obj is not False and db_obj.status is True:
            db_obj.close_connection()

    return status

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
        overwrite['jobid'] = "http://pharlap.tx.fnc.fujitsu.com/share/logs/"+str(namespace.jobid)
    return overwrite


def append_path(filepath, path_list, path):
    """Append appropriate paths for testcase/suite/project in test folder
    """
    temp_list = []
    for file_name in path_list:
        file_name = path + file_name
        temp_list.append(file_name)
    if temp_list:
        filepath.extend(temp_list)
    return filepath


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

    elif any(cli_args):
        filepath = w_cli_obj.examine_cli_args(cli_args, namespace)

    elif namespace.ujd:
        decide_ujd_actions(w_cli_obj, namespace)

    # append additional path
    if namespace.tc_name is not None:
        filepath = append_path(filepath, namespace.tc_name, "Warriorspace/Testcases/")
    if namespace.ts_name is not None:
        filepath = append_path(filepath, namespace.ts_name, "Warriorspace/Suites/")
    if namespace.proj_name is not None:
        filepath = append_path(filepath, namespace.proj_name, "Warriorspace/Projects/")

    # overwrite layer
    overwrite = decide_overwrite_var(namespace)

    if filepath is None:
        print_error("No input filepath: {0}".format(namespace.filepath))
        exit(1)
    else:
        for index, file_name in enumerate(filepath):
            if len(file_name.split('.')) == 1:
                filepath[index] = file_name + '.xml'

    return (filepath, namespace, overwrite)

def main(args):
    """init a Warrior Cli Class object, parse its arguments and run it"""
    w_cli_obj = war_cli_class.WarriorCliClass()
    parsed_args = w_cli_obj.parser(args)
    return decide_action(w_cli_obj, parsed_args)

if __name__ == "__main__":
    print re.match(r"[g-z]", raw_input("Enter: "))
    main(sys.argv[1:])
