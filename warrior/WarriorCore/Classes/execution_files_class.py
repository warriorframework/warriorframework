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

"""Execution files driver """


import os
import  Tools
from Framework.Utils import file_Utils as file_Utils
from Framework.Utils import xml_Utils as xml_Utils
from Framework.Utils.print_Utils import print_info, print_warning, print_error, print_exception
from Framework.Utils.data_Utils import get_credentials

class ExecFilesClass(object):
    """Execution Files class """
    def __init__(self, filepath, filetype, res_startdir=None, logs_startdir=None):
        """Constructor """
        self.filepath = filepath
        self.filetype = filetype
        self.res_startdir = res_startdir
        self.logs_startdir = logs_startdir
        self.ws_execution = None
        #calculate filename and nameonly from file path
        self.filename = os.path.basename(filepath)
        self.nameonly = file_Utils.getNameOnly(self.filename)

        #resultsdir, resultfile, results_location
        self.resultfile, self.resultsdir, self.results_execdir = self.get_result_files()

        #logsdir, logfile, logs_location
        self.logfile, self.logsdir, self.logs_execdir = self.get_log_files()

    def create_ws_execution(self):
        """Create execution dir in Warriorspace """
        curr_file_locn = os.path.realpath(__file__)
        war_locn = os.sep.join(curr_file_locn.split(os.sep)[:-3]) + os.sep + "Warrior"
        warriorspace = os.path.dirname(war_locn) + os.sep + "Warriorspace"
        #check_create_warriorspace(warriorspace)
        ws_execution = warriorspace + os.sep + "Execution"

        try:
            if not file_Utils.pathExists(ws_execution):
                os.makedirs(ws_execution)
            execution_dir = ws_execution
            self.ws_execution = file_Utils.createDir_addtimestamp(execution_dir, self.nameonly)
        except OSError as exception:
            print_error("Unable to create directory/file(s) under Warriorspace "\
                        "'{0}', hence aborting".format(ws_execution))
            print_exception(exception)
            exit(0)
        else:
            return self.ws_execution

    def create_def_exec_dir(self):
        """Create the default result execution directory """
        if self.ws_execution is None:
            execdir = self.create_ws_execution()
        else:
            execdir = self.ws_execution
        return execdir


    def get_result_files(self):
        """Get execution results dir and files """

        if self.res_startdir is not None:
            results_execdir = file_Utils.createDir_addtimestamp(self.res_startdir, self.nameonly)
            rfile = self.get_exec_file_by_type("Results", results_execdir)
        elif self.res_startdir is None:
            results_location = xml_Utils.getChildTextbyParentTag(self.filepath,
                                                                 'Details', 'Resultsdir')

            #get default results directory
            default_xml = Tools.__path__[0] + os.sep + 'w_settings.xml'
            default_resultsdir = get_credentials(default_xml, 'def_dir', ['Resultsdir'], 'Setting')
            #use the default directory if user didn't define it in test case/test suite/project
            if results_location is None or results_location is False:
                if default_resultsdir['Resultsdir'] is not None:
                    results_location = default_resultsdir['Resultsdir']

            if results_location is None or results_location is False\
            or str(results_location).strip() == "":
                results_execdir = self.create_def_exec_dir() #proj_exec_dir
                rfile = self.get_exec_file_by_type("Results", results_execdir)

            elif results_location is not None and results_location is not False:
                results_location_rel = str(results_location).strip()
                results_location = file_Utils.getAbsPath(results_location_rel,
                                                         os.path.dirname(self.filepath))
                rfile, results_execdir = self.checkdir_create_file(results_location, "Results")

        # print "printing results_execdir: ", results_execdir
        resultfile = file_Utils.getNewExtension(rfile, "xml")
        resultsdir = os.path.dirname(resultfile)
        return resultfile, resultsdir, results_execdir

    def get_log_files(self):
        """Get execution logs dir and results """

        if self.logs_startdir is not None:
            if self.logs_startdir == self.res_startdir:
                logs_execdir = self.results_execdir
            else:
                logs_execdir = file_Utils.createDir_addtimestamp(self.logs_startdir, self.nameonly)
            logfile = self.get_exec_file_by_type("Logs", logs_execdir)

        elif self.logs_startdir is None:
            colocate = False
            logs_location = xml_Utils.getChildTextbyParentTag(self.filepath, 'Details', 'Logsdir')
            results_location = xml_Utils.getChildTextbyParentTag(self.filepath,
                                                                 'Details', 'Resultsdir')
            #get default logs and results directory
            default_xml = Tools.__path__[0] + os.sep + 'w_settings.xml'        
            default_logsdir = get_credentials(default_xml, 'def_dir',['Logsdir'], 'Setting')
            default_resultsdir = get_credentials(default_xml, 'def_dir',['Resultsdir'], 'Setting')
            #use the default directory if user didn't define it in test case/test suite/project
            if results_location is None or results_location is False :
                if default_resultsdir['Resultsdir'] is not None :
                    results_location = default_resultsdir['Resultsdir']
            
            if logs_location is None or logs_location is False :
                if default_logsdir['Logsdir'] is not None :
                    logs_location = default_logsdir['Logsdir']

            if logs_location is None or logs_location is False\
            or str(logs_location).strip() == "":
                logs_execdir = self.create_def_exec_dir()
                logfile = self.get_exec_file_by_type('Logs', logs_execdir)

            elif logs_location is not None and logs_location is not False:
                logs_location_rel = str(logs_location).strip()
                logs_location = file_Utils.getAbsPath(logs_location_rel,
                                                      os.path.dirname(self.filepath))
                results_location_rel = str(results_location).strip()
                results_location = file_Utils.getAbsPath(results_location_rel,
                                                         os.path.dirname(self.filepath))
                if logs_location == results_location:
                    colocate = True

                logfile, logs_execdir = self.checkdir_create_file(logs_location, 'Logs', colocate)

        # print "printing logs_execdir: ", logs_execdir
        logsdir = os.path.dirname(logfile)
        return logfile, logsdir, logs_execdir

    def get_defect_files(self):
        """get execution defects dir and results """
        defectsdir = file_Utils.createDir_addtimestamp(os.path.dirname(self.resultsdir), 'Defects')
        return defectsdir


    def checkdir_create_file(self, inpdir, dirname, colocate=False):
        """Check if dir is present, if dir present create subdir nd files
        if dir not present try to create dir, subdir and files
        if not able to create dir use Warrior frameworks default dir structure."""

        dir_status = file_Utils.check_and_create_dir(inpdir) # creates tc_results dir
        if dir_status:
            try:
                if colocate:
                    execdir = self.results_execdir
                else:
                    execdir = file_Utils.createDir_addtimestamp(inpdir, self.nameonly)
                rfile = self.get_exec_file_by_type(dirname, execdir)
            except OSError:
                dir_status = False
            except Exception as exception:
                print_exception(exception)
                dir_status = False
        if dir_status is False:
            print_warning("Creating directory/file(s) in provided path {0} failed. "
                          "\n Hence Warrior Framework's default directory structure will be used "
                          "for this execution.".format(inpdir))
            execdir = self.create_def_exec_dir() # proj_exec_dir
            rfile = self.get_exec_file_by_type(dirname, execdir)
        return rfile, execdir


    def get_exec_file_by_type(self, dirname, exec_dir):
        """Get execution files by file type """
        if self.filetype == "tc":
            rfile = get_testcase_execution_files(self.filepath, exec_dir, dirname)
        elif self.filetype == "ts" or self.filetype == "proj":
            rfile = get_execution_files(self.filepath, exec_dir, 'xml')
        return rfile

    def get_data_files(self):
        """Get datafiles for testcase and testuite """
        data_type = "CUSTOM"
        if self.filetype == "tc":
            datafile = self.check_get_datafile()
            data_type = self.check_get_datatype(datafile)
        elif self.filetype == "ts" or self.filetype == "proj":
            datafile = self.check_get_datafile()
        return datafile, data_type

    def check_get_datafile(self):
        """Check InputDatFile tag in the xml file and
        based on the values return the datafile to be used for the testcase/testsuite
            - If user provided a datafile, will use it.
            - If user specified 'Default' will use the default datafile
            - If user did not provide any value will use default datafile
            - If user specified 'NODATA' will print a msg saying so.
        """

        datafile = xml_Utils.getChildTextbyParentTag(self.filepath,
                                                     'Details', 'InputDataFile')
        if datafile is None or datafile is False or \
        str(datafile).strip() == "":
            if self.filetype == "tc":
                #print "get default datatype for testcase"
                datafile = get_default_xml_datafile(self.filepath)
            if self.filetype == "ts":
                # Check if test suite datatype starts with iterative.
                # If yes then get default datafile else set it as false
                # this is because at testsuite level input datafile is
                # supported only if the suite datatype is iterative seq/parallel
                datatype = self.check_get_datatype(False)
                if str(datatype).lower().startswith("iterative"):
                    datafile = get_default_xml_datafile(self.filepath)
                else:
                    datafile = False
            elif self.filetype == "proj":
                datafile = False
        elif str(datafile).strip().upper() == "DEFAULT":
            print_info("This testcase will be executed using the default InputDataFile")
            datafile = get_default_xml_datafile(self.filepath)
        elif str(datafile).strip().upper() == 'NO_DATA':
            print_info('This test case will be run without any InputDataFile')
            datafile = "NO_DATA"

        elif datafile is not None and datafile is not False:
            datafile_rel = str(datafile).strip()
            datafile = file_Utils.getAbsPath(datafile_rel, os.path.dirname(self.filepath))

        if str(datafile).strip().upper() != 'NO_DATA' and datafile is not False:
            if not file_Utils.fileExists(datafile):
                print_info('\n')
                print_error("!!! *** InputDataFile does not exist in provided path:"\
                            "{0} *** !!!".format(datafile))
        return datafile

    def check_get_datatype(self, datafile):
        """Check and get the datatype for testcase
        """

        data_type = xml_Utils.getChildTextbyParentTag(self.filepath, 'Details', 'Datatype')
        if str(datafile).upper().strip() == 'NO_DATA':
            data_type = 'CUSTOM'
            print_info('This test case will be run without any InputDataFile')

        elif data_type is None or data_type is False or\
        str(data_type).strip() == "":
            data_type = 'CUSTOM'

        elif data_type is not None and data_type is not False:
            data_type = str(data_type).strip()
            supported_values = ['iterative', 'custom', 'hybrid']
            if data_type.lower() not in supported_values:
                print_warning("unsupported value '{0}' provided for data_type,"
                              " supported values are "\
                              "'{1}' and case-insensitive".format(data_type, supported_values))
                print_info("Hence using default value for data_type which is 'custom'")
                data_type = 'CUSTOM'
        return data_type

    #def to get runtype of the testcase from xml
    def check_get_runtype(self):
        """Check and get the runtype for testcase
        """
        if xml_Utils.nodeExists(self.filepath, 'Runtype'):
            run_type = xml_Utils.getChildTextbyParentTag(self.filepath, 'Details', 'Runtype')
            if run_type is not None and run_type is not False:
               run_type = str(run_type).strip()
               supported_values = ['sequential_keywords', 'parallel_keywords']
               if run_type.lower() not in supported_values:
                   print_warning("unsupported value '{0}' provided for run_type,"
                                 "supported values are "\
                                "'{1}' and case-insensitive".format(run_type, supported_values))
                   print_info("Hence using default value for run_type which is 'sequential_keywords'")
                   run_type = 'SEQUENTIAL_KEYWORDS'
        else:
            run_type = "SEQUENTIAL_KEYWORDS"
        return run_type

def get_execution_files(filepath, execution_dir, extn):
    """Get the execution files like resultfile, logfile etc"""

    filename = file_Utils.getFileName(filepath)
    nameonly = file_Utils.getNameOnly(filename)
    if extn.lower() == "res":
        fullpath = execution_dir + os.sep + nameonly + "_results" +"." + extn
    else:
        fullpath = execution_dir + os.sep + nameonly + '.' + extn
    if file_Utils.fileExists(fullpath):
        fullpath = file_Utils.addTimeDate(fullpath)
    return fullpath

def get_testcase_execution_files(testcase_filepath, tc_execution_dir, dirname):
    """Create directories for Results, Logs for testcase execution
    and get related files """
    extension = file_Utils.getExtension(dirname)
    dirpath = file_Utils.createDir_addtimestamp(tc_execution_dir, dirname)
    fullpath = get_execution_files(testcase_filepath, dirpath, extension)
    return fullpath

def get_default_xml_datafile(filepath):
    """Get the default datafile for a testcase/testsuite file

    :Arguments:
        1. filepath   = full path of the input xml file
    """
    inpdir = os.path.split(filepath)[0]
    filename = file_Utils.getFileName(filepath)
    nameonly = file_Utils.getNameOnly(filename)
    data_dir = os.sep.join(inpdir.split(os.sep)[:-1]) + os.sep + 'Data'

    def_datafile_path = data_dir + os.sep + nameonly+'_Data.xml'
    return def_datafile_path
