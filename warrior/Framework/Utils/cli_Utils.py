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
from Framework.Utils.print_Utils import print_info, print_warning
from Framework.ClassUtils import WNetwork, ssh_utils_class
from WarriorCore.Classes.warmock_class import mocked
from WarriorCore.Classes.war_cli_class import WarriorCliClass

try:
    import pexpect
except ImportError:
    print_info("{0}: pexpect module is not installed".format(os.path.abspath(__file__)))
    print_info("Warrior framework by default uses pexpect for all cli related activites")
    print_info("All default methods/functions that use cli will fail"
               "without pexpect module. Users can however create"
               "their own custom libraries for cli interaction \n")


def pexpect_spawn_with_env(pexpect_obj, command, timeout, escape=False, env=None):
    """ spawn a pexpect object with environment variable """

    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    child = wc_obj.pexpect_spawn_with_env(pexpect_obj, command, timeout,
                                          escape, env)

    return child


@mocked
def connect_ssh(ip, port="22", username="", password="", logfile=None, timeout=60,
                prompt=".*(%|#|\$)", conn_options="", custom_keystroke="", escape="", **kwargs):
    """
    Initiates SSH connection via a specific port. Creates log file.
    :Arguments:
        1. ip = destination ip
        2. port(string) = telnet port
        3. username(string) = username
        4. password(string) = password
        5. logfile(string) = logfile name
        6. timeout(int) = timeout duration
        7. prompt(string) = destination prompt
        8. conn_options(string) = extra arguments that will be used when
                                  sending the ssh/telnet command
        9. custom_keystroke(string) = keystroke(to be given after initial timeout)
        10. escape(string) = true/false(to set TERM as dump)

    :Returns:
        1. session_object(pexpect session object)
        2. conn_string(pre and post login message)
    """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'connect_ssh' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/WNetwork/warrior_cli_class.py'")

    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    session_object, conn_string = wc_obj.connect_ssh(
        ip=ip, port=port, username=username, password=password, logfile=logfile, timeout=timeout,
        prompt=prompt, conn_options=conn_options, custom_keystroke=custom_keystroke, escape=escape)

    return session_object, conn_string


@mocked
def connect_telnet(ip, port="23", username="", password="",
                   logfile=None, timeout=60, prompt=".*(%|#|\$)",
                   conn_options="", custom_keystroke="", escape="", **kwargs):
    """
    Initiates Telnet connection via a specific port. Creates log file.

    :Arguments:
        1. ip = destination ip
        2. port(string) = telnet port
        3. username(string) = username
        4. password(string) = password
        5. logfile(string) = logfile name
        6. timeout(int) = timeout duration
        7. prompt(string) = destination prompt
        8. conn_options(string) = extra arguments that will be used when
                                  sending the ssh/telnet command
        9. custom_keystroke(string) = keystroke(to be given after initial timeout)
        10. escape(string) = true/false(to set TERM as dump)

    :Returns:
        1. session_object(pexpect session object)
        2. conn_string(pre and post login message)
    """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'connect_telnet' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/WNetwork/warrior_cli_class.py'")

    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    session_object, conn_string = wc_obj.connect_telnet(
        ip=ip, port=port, username=username, password=password, logfile=logfile, timeout=timeout,
        prompt=prompt, conn_options=conn_options, custom_keystroke=custom_keystroke, escape=escape)

    return session_object, conn_string


def disconnect_telnet(child):
    """Disconnects a telnet session """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'disconnect_telnet' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/WNetwork/warrior_cli_class.py'")

    if isinstance(child, WNetwork.warrior_cli_class.WarriorCli):
        child = child.disconnect_telnet()
    elif isinstance(child, pexpect.spawn):
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = child
        wc_obj.disconnect_telnet()

    return child


def disconnect(child):
    """
    - Disconnects warrior_cli_class session object(pexpect/paramiko)
    - Returns session object(same child)
    """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'disconnect' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/WNetwork/warrior_cli_class.py'")

    if isinstance(child, WNetwork.warrior_cli_class.WarriorCli):
        child = child.disconnect()
    elif isinstance(child, pexpect.spawn):
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = child
        wc_obj.disconnect()

    return child


@mocked
def send_command_and_get_response(sessionobj, prompt1, prompt2, command):
    """"Sends a command to a terminal expects a completion prompt
    If completion prompt was found, returns the response of the command """

    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'send_command' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/WNetwork/warrior_cli_class.py'")

    if isinstance(sessionobj, WNetwork.warrior_cli_class.WarriorCli):
        _, response = sessionobj.send_command(prompt1, prompt2, command)
    elif isinstance(sessionobj, pexpect.spawn):
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = sessionobj
        _, response = wc_obj.send_command(prompt1, prompt2, command)
    else:
        response = ""
        print_warning("Unable to send the command since the sessionobj is not "
                      "supported by warrior_cli_class, status will be marked as ERROR."
                      "Please use warrior_cli_class for session establishment.")

    return response


def smart_analyze(prompt, testdatafile=None):
    """
        retrieve the correspond smart testdata file for smart cmd
        from either Tools/connection or testcase testdata file
        :param prompt:
            The string that will be analyzed in order to find the device system
        :param testdatafile:
            optional arg to provide a pre-defined device system in the test datafile
        :return:
            the smart datafile that contains the smart cmd to be sent
    """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    smart_datafile = wc_obj.smart_analyze(prompt, testdatafile)

    return smart_datafile


def send_smart_cmd(connect_testdata, session_object, tag_value, call_system_name, pre_tag):
    """
        The beacons of Gondor are lit
        send out the smart command
        :param connect_testdata:
            the smart testdata file that contains the smart cmd
        :param session_object:
            use this pexpect object to send out command
        :param tag_value:
            specify the testdata block of commands that get sent out
        :param call_system_name:
            in order to get passed the substitutions, a system name must be provided
        :param pre_tag:
            Distinguish if it is a connect smart action or disconnect smart action
    """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    wc_obj.send_smart_cmd(connect_testdata, session_object, tag_value, call_system_name, pre_tag)


def smart_action(datafile, call_system_name, raw_prompt, session_object, tag_value,
                 connect_testdata=None):
    """
        entry function for sending smart command
        :param datafile:
            the testcase datafile
        :param call_system_name:
            in order to get passed the substitutions, a system name must be provided
        :param raw_prompt:
            The string that will be analyzed in order to find the device system
        :param session_object:
            use this pexpect object to send out command
        :param tag_value:
            specify the testdata block of commands that get sent out
        :param connect_testdata:
            the smart testdata file that contains the smart cmd, optional in here
        :return:
            the smart testdata file that contains the smart cmd
    """

    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    smart_testdatafile = wc_obj.smart_action(datafile, call_system_name, raw_prompt,
                                             session_object, tag_value, connect_testdata)
    return smart_testdatafile


def get_connection_port(conn_type, inpdict):
    """Gets the port for ssh or telnet connections
    1. ssh :
        - looks if ssh_port is present in  inpdict.
        - if not checks for conn_port
        - if both not present returns None
    """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    inpdict = wc_obj.get_connection_port(conn_type, inpdict)
    return inpdict


@mocked
def send_command(session_object, start_prompt, end_prompt, command,
                 timeout=60):
    """
    Sends command to warrior_cli_class session object(pexpect/paramiko)
    and returns the status of the command sent.
    - Checks for the availability of the start_prompt.
    - if start prompt was available sends the command
    - if failure response is not None and failure response found in
    response then returns False.
    - else if failure response was not found
    and end prompt also not found returns False.
    - else if failure response was not found and end prompt found,
    then returns true.
    """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'send_command' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/WNetwork/warrior_cli_class.py'")

    if isinstance(session_object, WNetwork.warrior_cli_class.WarriorCli):
        status, response = session_object.send_command(start_prompt, end_prompt,
                                                       command, timeout)
    elif isinstance(session_object, pexpect.spawn):
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = session_object
        status, response = wc_obj.send_command(start_prompt, end_prompt, command, timeout)
    else:
        status, response = "ERROR", ""
        print_warning("Unable to send the command since the session_object is not an "
                      "instance of warrior_cli_class, status will be marked as ERROR. "
                      "Please use warrior_cli_class for session establishment.")

    return status, response


def sendPing(hostname, count, fname):
    """Sends a ping command
    :Arguments:
        1. count(string) = no of pings to be sent
        2. src_iface(string) = source interface from whihc ping messages
                                are to be sent.
        3. destip(string) = the destination ip address to ping.
        4. fname = logfile to log ping response.
    :Returns:
        status = boolean
    """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    status = wc_obj.sendPing(hostname, count, fname)

    return status


def sendSourcePing(count, src_iface, destip, fname):
    """Sends a source based ping command
    i.e. if multiple interfaces are configured and available,
    sends pings from the src_iface provided
    :Arguments:
        1. count(string) = no of pings to be sent
        2. src_iface(string) = source interface from whihc ping messages
                                are to be sent.
        3. destip(string) = the destination ip address to ping.
        4. fname = logfile to log ping response.
    :Returns:
        status = boolean
    """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    status = wc_obj.sendSourcePing(count, src_iface, destip, fname)

    return status


def send_commands_from_testdata(testdatafile, obj_session, **args):
    """
    - Parses the testdata file and gets the command details
    for rows marked execute=yes and row=str_rownum.
    - Sends the obtained commands to the warrior_cli_class session object(obj_Session).
    - If the commands have verification attribute set,
    then verifies the verification text for presence/absence as defined
    in the respective found attribute in the testdatfile.

    :Arguments:
        1. testdatafile = the xml file where command details are available
        2. obj_session = pexpect or warrior_cli_class session object
        3. logfile = logfile of the pexpect session object.
        4. varconfigfile=  xml file from which the values will be taken for subtitution
        5. var_sub(string) = the pattern [var_sub] in the testdata commands,
                                 start_prompt, end_prompt, verification search
                                 will substituted with this value.
        6. args = Optional filter to specify title/rownum
    :Returns:
        1. finalresult = boolean
    """
    if isinstance(obj_session, WNetwork.warrior_cli_class.WarriorCli):
        finalresult, td_resp_dict = obj_session.send_commands_from_testdata(testdatafile, **args)
    else:
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = obj_session
        finalresult, td_resp_dict = wc_obj.send_commands_from_testdata(testdatafile, **args)

    return finalresult, td_resp_dict


@mocked
def _send_cmd(obj_session, **kwargs):
    """method to send command based on the type of object """

    if isinstance(obj_session, WNetwork.warrior_cli_class.WarriorCli):
        result, response = obj_session._send_cmd(**kwargs)
    elif isinstance(obj_session, pexpect.spawn):
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = obj_session
        result, response = wc_obj._send_cmd(**kwargs)
    elif isinstance(obj_session, ssh_utils_class.SSHComm):
        command = kwargs.get('command')
        result, response = obj_session.get_response(command)
        print_info(response)
    else:
        print_warning('session object type is not supported')

    return result, response


def _get_response_dict(details_dict, index, response, response_dict):
    """Get the response dict for a command. """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    status, resp_key_list = \
        wc_obj._get_response_dict(details_dict, index, response, resp_key_list=[])
    return status, resp_key_list


def start_threads(started_thread_for_system, thread_instance_list, same_system,
                  unique_log_verify_list, system_name):
    """ This function iterates over unique_log_verify_list which consists of unique values
    gotten from monitor attributes and verify_on attributes

    If a system_name has a * against it, it indicates that the system is the
    same as the one on which the testcase is running. Thread would not be
    started for that system.

    :Returns:

    started_thread_for_system (list[str]) = Stores the system names for which
    threads were succesfully created

    thread_instance_list (list[str]) = stores the instances of thread created
    for corresponding system in the started_thread_for_system list,

    same_system (list[str]) = stores the system name which was the same as the
    system on which the TC is running without the trailing *,

    """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    started_thread_for_system, thread_instance_list, same_system = \
        wc_obj.start_threads(started_thread_for_system, thread_instance_list,
                             same_system, unique_log_verify_list, system_name)

    return started_thread_for_system, thread_instance_list, same_system


def get_response_dict(started_thread_for_system, thread_instance_list,
                      same_system, response):
    """This function iterates over thread_instance_list and gets the data that
    the threads have stored in its data variable. Updates the remote_resp_dict
    with the system name and the corresponding data collected.

    The system names in same_system also get stored in the remote_resp_dict but
    their value is the same as the response that was obtained through the
    _send_cmd function

    :Returns:

    remote_resp_dict (dict) with collected logs as value to the system_name key
    """

    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    remote_resp_dict = wc_obj.get_response_dict(started_thread_for_system,
                                                thread_instance_list,
                                                same_system, response)

    return remote_resp_dict


def get_unique_log_and_verify_list(log_list, verify_on_list, system_name):
    """This function loops through the log_list and the verify_on_list
    and returns a unique list containing unique sustem names fromboth the lists
    """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    final_list = wc_obj.get_unique_log_and_verify_list(log_list, verify_on_list, system_name)

    return final_list


def _send_cmd_get_status(obj_session, details_dict, index, system_name=None):
    """Sends a command, verifies the response and returns
    status of the command """
    if isinstance(obj_session, WNetwork.warrior_cli_class.WarriorCli):
        result, response = obj_session._send_cmd_get_status(details_dict,
                                                            index, system_name)
    else:
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = obj_session
        result, response = wc_obj._send_cmd_get_status(details_dict,
                                                       index, system_name)

    return result, response


def _get_obj_session(details_dict, obj_session, kw_system_name, index):
    """If system name is provided in testdata file
    get the session of that system name and use it or
    use the current obj_session"""
    if isinstance(obj_session, WNetwork.warrior_cli_class.WarriorCli):
        value, kw_system_name, details_dict = obj_session._get_obj_session(
            details_dict, kw_system_name, index)
    else:
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = obj_session
        value, kw_system_name, details_dict = wc_obj._get_obj_session(
            details_dict, kw_system_name, index)

    return value, kw_system_name, details_dict


@mocked
def _send_command_retrials(obj_session, details_dict, index, **kwargs):
    """ Sends a command to a session, if a user provided pattern
    is found in the command response then tries to resend the command multiple
    times.
    retry_timer = time interval between subsequent retries
    retry_onmatch = the pattern to be matched in the response
                    in order to retry the command.
    retry_count = no of times to retry.
    """
    if isinstance(obj_session, WNetwork.warrior_cli_class.WarriorCli):
        result, response = obj_session._send_command_retrials(details_dict, index, **kwargs)
    else:
        wc_obj = WNetwork.warrior_cli_class.WarriorCli()
        wc_obj.conn_obj = WNetwork.warrior_cli_class.PexpectConnect()
        wc_obj.conn_obj.target_host = obj_session
        result, response = wc_obj._send_command_retrials(details_dict, index, **kwargs)

    return result, response


def _get_match_status(retry_onmatch, response):
    """ Searchs retry_onmatch value in response """
    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    status = wc_obj._get_match_status(retry_onmatch, response)
    return status


def _send_cmd_by_type(session_object, command):
    """Determine the command type and send accordingly
    """

    wc_obj = WNetwork.warrior_cli_class.WarriorCli()
    wc_obj._send_cmd_by_type(session_object, command)

##################
# Uses telnet_Utils.Tnet_Comm object as input
# def send_telnet_command(telnet_session, command, start_prompt='',
#                         end_prompt='', failure_resp=''):
#     """ Takes a telnet session object created using
#     telnet_Utils.Tnet_Comm object as input
#     Sends a tl1 command to the telnet session and verifies the end
#     prompt/failure response
#     :Returns:
#         1. True, response = if end prompt is encountered
#         2. False, response = if failure_resp is encountered
#     """
#     #print "start prompt is : {0}".format(start_prompt)
#     msg = 'Send Command:{0}'.format(command)
#     pNote(msg)
#     try:
#         response = telnet_session.get_response(command, end_prompt)
#         print_info("Response:{0}".format(response))
#     except Exception as exception:
#         print_debug("Could not find the end prompt %s or failure "
#                     "response %s "% (end_prompt, failure_resp))
#         err = print_exception(exception)
#         return False, str(err)
#
#     e_prompt = re.compile(end_prompt, re.DOTALL)
#     f_resp = re.compile(failure_resp, re.DOTALL)
#
#
#     if re.search(f_resp, response):
#         return (False, response)
#     elif re.search(e_prompt, response):
#         return (True, response)
#     else:
#         return (False, response)
