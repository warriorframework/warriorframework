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

"""This is the actions file, keywords are programmed here """

#===============================================================
# Import any python library you want to use below this line"""
#===============================================================
import time
import pexpect

#=====================================================================
# """ Import Warrior Framework Utilities below this line"""
#===========================================================================
# import Framework
import Framework.Utils as Utils

#++++++++++++++++++++++++++++++++++++++++
#WARRIOR KEYWORD TEMPLATE AND RULES
#++++++++++++++++++++++++++++++++++++++++

""" Warrior uses standard Python programming for its keyword development, however Warrior requires
the users to adhere to the following rules: """

""" Supported Keyword types
1. The keywords can be methods of a class or they can be a independent function in a library

2. When using classes for keywords:
    a. Users should always use the default __init__  for a class as shown below, and can
        extend it to add more attributes within __init__
    b. Multiple classes are allowed in a single file
    c. Class inheritance is not supported for keyword classes
    d. In Warrior, method names are keywords and hence the method names
        should be unique within the driver's packages.
    e. Users are allowed to use a mix of classes and independent functions
        in a single actions file as long as their names are unique.
    f. Static methods with decorators are not currently supported by the
        Warrior framework for the Action classes."""

"""Each keyword (along with its driver) is a step in the warrior test case.
   A keyword can have multiple sub-steps that are implemented in the code """


class CliActions(object):

    """" Default __init__ field must be used when using classes for keywords """
    def __init__(self):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

    """ Sample method (keyword)  with a single substep and
    some of the most commonly used functions from the data_Utils is given below
    *** Please remember this is only a sample keyword to help a beginner
    in Warrior Framework, and may not work exactly ****"""

    def connect_ssh(self, system_name, session_name=None, expected_prompt='.*'):
        """ KEYWORD DOCUMENTATION: A recommended style for keyword documentation is given below
        Connects to the ssh port of the the given system or subsystems

        :Datafile usage:

            Tags or attributes to be used in input datafile for the system or subsystem
            If both tag and attribute is provided the attribute will be used.
            
            1. ip = IP address of the system/subsystem
            2. username = username for the ssh session
            3. password = password for the ssh session
            4. timeout = use if you want to set timeout while connecting
            5. prompt = the prompt expected when the connection is successful
            6. ssh_port = use this tag to provide a ssh port to connect to,\
                if not provided default ssh port 22 will be used.

        :Arguments:
            1. system_name (string) = This can be name of the\
                system or a subsystem.
                
                    To connect to a system provided system_name=system_name.
                    
                    To connect to a single subsystem provide
                    system_name=system_name[subsystem_name].
                    
                    To connect to multiple subsystems provide
                    system_name=system_name[subsystem1_name,subsystem2_name..etc..].
                    
                    To connect to all subsystems under a system provide
                    system_name="system_name[all]".
            2. session_name(string) = name of the session to the system/subsystem.
            3. prompt(string) = prompt expected in the terminal
            4. int_timeout(int) = use this to set timeout value for commands\
                issued in this session.


        :Returns:
            1. status(bool)= True / False.
            2. session_id (dict element)= an id is generated for each connection\
                and each connection is stored in the framework's data_repository.\
                session_id=system_name+subsystem_name+session_name.
            3. response dictionary(dict): an empty dictionary to store the responses of all\
                commands sent to the particular system or subsystem.\
                This dictionary is available in warrior frameworks global data_repository\
                and can be retrieved using the key= "session_id + _td_response".

        """

        """ THE DESCRIPTION (optional):

        - All keywords can have a description variable that gives details
            of what is being performed by the keyword
        - It should be a string enclosed within double or single quotes, no variable
            substitutions to be used here as it is used as just a text for reporting purpose
        - This string will be used in result file for reporting a step.
        - If this variable is missing warrior will just report  the
            keyword name in step description of the result file
        """

        WDesc = "Connect to the ssh port of the system and creates a session"

        """ PSUBSTEP (optional) :

        All keywords can start with the below function-call to
        pSubStep with a single argument describing in short the sub-step's functionality
        If this function-call is missing warrior will not
        report any sub-step in the test case result file"""
        Utils.testcase_Utils.pSubStep('Connect to ssh of {0}'.format(system_name))


        """ Some useful Information:
        Warrior provides a data repository within a test case and a test suite.
		- The data repository within a test case contains all the data returned
		by a keyword stored as dictionary entry.

		- The data returned by the keywords is stored automatically
		in the data repository and is accessible to the other keywords within the test case.

		- The process by which keywords can access the data returned by other keywords is
		    described in item #4 below.

		- Warrior also provides a data repository within a test suite.
		- The data repository within a test suite contains all the data returned by
		the keywords of the test cases within the suite stored as dictionary entry.

		- The data returned by the keywords is stored automatically in the
		data repository and is accessible to the other keywords within the test suite.

		- The process by which keywords can access the data returned by other
		keywords is described in item #4 below.

        """
        """ 1. Custom Logfile for a Keyword:
        ---------------------------------
        - Warrior framework creates a logfile by default with the name of the testcase
            located in 'Warriorspace/Execution/DateTime/logs'.
        - If the keyword is written as class method then it is available as self.logfile.
        - If the keyword is written as a independent function
            then it is available for the user in the test case data repository.

        - However user may want to create a separate logfile for each keyword,
            to create a custom logfile for a keyword use the below function from file_Utils

        logfile = Utils.file_Utils.getCustomLogFile(self.filename, self.logsdir,
                                                    'NE_TL1_{0}'.format(system_name))

        """

        """ 2. Adding Notes to test case result file:
        ---------------------------------------------
        Use testcase_Utils.pNote, pNote does the following 3 operations.
        1. Adds notes to the result xml file
        2. Print the same note to the console.
        3. Writes the notes to the console log file.
        refer to testcase_Utils.py for more functions related to testcase result file reporting

        Utils.testcase_Utils.pNote("Logfile= %s" % logfile)

        """
        Utils.testcase_Utils.pNote(WDesc)

        """3. Get details from input datafile:
        --------------------------------------
        - Warrior supports the use of a system input datafile.
        - A sample system data file is located in Warriorspace/Data.
        - get_credentials method from data_Utils can be used to retrieve data
        from an xml tag in the system file.

        For eg: In-order to get the ip, ssh_port, username, password,
        prompt of a system called 'dpoe03' from the input datafile.

        credentials = Utils.data_Utils.get_credentials(self.datafile, 'dpoe03',
                                                        ['ip', 'ssh_port', 'username',
                                                        'password', 'prompt'])
        """

        """ 4. Sharing data between keywords:
        ------------------------------------
        - In Warrior Framework all data to be returned by a keyword should be returned
        in a python dictionary, and this data will be stored in the test case
        or test suite data repository as a key-value pair.

        - Keywords will have to access the test case data repository to get the
        data returned from a previous keyword.

        For eg:
        Lets say a previous keyword has returned ne_location(string), session_id(pexpect object)
        to the test case data repository,in order to use these values in the next keyword
        use 'Utils.data_Utils.get_object_from_datarepository' and pass the key to it.

        ne_location = Utils.data_Utils.get_object_from_datarepository('ne_location')
        session_id = Utils.data_Utils.get_object_from_datarepository('session_id')
        """


        """A sample code of the keyword"""

        WDesc = "Connect to the ssh port of the system and creates a session"

        Utils.testcase_Utils.pSubStep('Connect to ssh of {0}'.format(system_name))

        output_dict = {}
        logfile = Utils.file_Utils.getCustomLogFile(self.filename, self.logsdir,
                                                    'NE_TL1_{0}'.format(system_name))
        Utils.testcase_Utils.pNote(system_name)
        Utils.testcase_Utils.pNote(logfile)
        Utils.testcase_Utils.pNote(Utils.file_Utils.getDateTime())

        if session_name is None:
            session_id = system_name
        elif session_name is not None:
            session_id = system_name + session_name

        credentials = Utils.data_Utils.get_credentials(self.datafile, system_name,
                                                       ['ip', 'ssh_port', 'username',
                                                        'password', 'prompt'])
        ne_location = Utils.data_Utils.get_object_from_datarepository('ne_location')
        Utils.testcase_Utils.pNote(ne_location)
        time.sleep(10)
        if credentials is False:
            status = credentials
        else:
            if credentials['prompt'] is not None:
                expected_prompt = credentials['prompt']
                session_object = Utils.cli_Utils.connect_ssh(credentials['ip'],
                                                            credentials['ssh_port'],
                                                            credentials['username'],
                                                            credentials['password'], logfile,
                                                            prompt_expected=expected_prompt)
                if isinstance(session_object, pexpect.spawn):
                    output_dict[session_id] = session_object
                    status = True
                else:
                    status = False

        """Reporting status of a sub step:
        ---------------------------------
        After executing a sub step in a keyword, use Utils.testcase_Utils.report_substep_status(status)
        to report the status of that substep to the result file.

        If a keyword has multiple sub-steps use this for each sub step in the keyword.
        """
        Utils.testcase_Utils.report_substep_status(status)


        """ Returning Keyword status and data:
        ---------------------------------------
        Each keyword should return the status of the keyword in the return command.

        - Any Data generated in the keyword can also be returned
        as a key-value pair in a python dictionary.

		- This key-value pair will be stored in the  data repository for use by other keywords.

        """

        """RETURN TYPES
        1. Supported return types from keywords.
            a. Only status: True or False only
            b. Only dictionary.
            c. status, dictionary
            d. dictionary, status

        2. If a keyword does not return a status,
        it will be declared as failure in the test case results.

        3. When a keyword returns a dictionary the test case data repository
        will be updated with the dictionary returned by the keyword.

        4. If a keyword returns any unsupported value the keyword will be declared as failure. """

        """ Sample Return statement"""
        return status, output_dict
    