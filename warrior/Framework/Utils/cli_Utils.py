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

"""Api for cli related operations """

import os
import sys
import time
import re
import subprocess
import Tools
import Framework.ClassUtils
from Framework.Utils import datetime_utils, data_Utils, xml_Utils
from Framework.Utils.data_Utils import get_object_from_datarepository
from Framework.Utils.print_Utils import print_debug, print_info,\
print_error, print_exception, print_warning
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.list_Utils import get_list_by_separating_strings
from Framework.ClassUtils.WNetwork.loging import ThreadedLog
from WarriorCore.Classes.war_cli_class import WarriorCliClass
from Framework.ClassUtils import database_utils_class

try:
    import pexpect
except ImportError:
    print_info("{0}: pexpect module is not installed".format(os.path.abspath(__file__)))
    print_info("Warrior framework by default uses pexpect for all cli related activites")
    print_info("All default methods/functions that use cli will fail"\
               "without pexpect module. Users can however create"\
               "their own custom libraries for cli interaction \n")

def cmdprinter(cmdfunc):
    """decorator"""
    def inner(*args, **kwargs):
        """routing different mock functions"""
        if WarriorCliClass.cmdprint:
            result = (True, "")
            if cmdfunc.__name__ == "_send_cmd_get_status":
                pNote(":CMD: %s"%(args[1]["command_list"][kwargs['index']]))
            elif cmdfunc.__name__ == "_send_command_retrials":
                pass
            elif cmdfunc.__name__ == "send_command":
                pNote(":CMD: %s"%(args[3]))
            elif cmdfunc.__name__ == "send_command_and_get_response":
                pNote(":CMD: %s"%(args[3]))
                result = ""
            elif cmdfunc.__name__ == "_send_cmd":
                pNote(":CMD: %s"%(kwargs['command']))
            else:
                pNote(":CMD: %s"%(args[3]))
        else:
            result = cmdfunc(*args, **kwargs)
        return result
    return inner

def pexpect_spawn_with_env(pexpect_obj, command, timeout, escape=False, env=None):
    """
        spawn a pexpect object with environment variable
    """
    if env is None:
        env = {}
    if str(escape).lower() == "yes" or str(escape).lower() == "true":
        child = pexpect_obj.spawn(command, timeout=int(timeout), env=env)
    else:
        child = pexpect_obj.spawn(command, timeout=int(timeout))
    return child

def connect_ssh(ip, port="22", username="", password="", logfile=None, timeout=60,
                prompt=".*(%|#|\$)", conn_options="", custom_keystroke="", escape="", **kwargs):
    """
    - Initiates SSH connection via a specific port. Creates log file.
    - return session as object and conn_string(pre and post login message).
    """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'connect_ssh' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/warrior_connect_class.py'")

    sshobj = None
    conn_string = ""
    conn_options = "" if conn_options is False or conn_options is None else conn_options
    custom_keystroke = "wctrl:M" if not custom_keystroke else custom_keystroke
    # delete -o StrictHostKeyChecking=no and put them in conn_options
    if not conn_options or conn_options is None:
        conn_options = ""
    command = 'ssh -p {0} {1}@{2} {3}'.format(port, username, ip, conn_options)
    #command = ('ssh -p '+ port + ' ' + username + '@' + ip)
    print_debug("connectSSH: cmd = %s" % command)
    if WarriorCliClass.cmdprint:
        pNote(("connectSSH: :CMD: %s" %command))
        return None, ""
    child = pexpect_spawn_with_env(pexpect, command, timeout=int(timeout),
                                   escape=escape, env={"TERM": "dumb"})

    child.logfile = sys.stdout

    if logfile is not None:
        try:
            fdobj = open(logfile, "a")
            if fdobj:
                child.logfile = fdobj
        except Exception as exception:
            print_exception(exception)

    try:
        flag = True
        child.setecho(False)
        child.delaybeforesend = .5
        while True:
            result = child.expect(["(yes/no)", prompt, '.*(?i)password:.*',
                                   ".*(?i)(user(name)?:|login:) *$", pexpect.EOF, pexpect.TIMEOUT,
                                   '.*(?i)remote host identification has '
                                   'changed.*'])

            if result == 0:
                child.sendline('yes')
            elif result == 1:
                sshobj = child
                conn_string = conn_string + child.before + child.after
                break
            elif result == 2:
                child.sendline(password)
                conn_string = conn_string + child.before + child.after
            elif result == 3:
                child.sendline(username)
            elif result == 4:
                pNote("Connection failed: {0}, with the system response: {1}"\
                      .format(command, child.before), "error")
                break
            elif result == 5:
                # Some terminal expect specific keystroke before showing login prompt
                if flag is True:
                    pNote("Initial timeout occur, sending custom_keystroke")
                    _send_cmd_by_type(child, custom_keystroke)
                    flag = False
                    continue
                pNote("Connection timed out: {0}, expected prompt: {1} "\
                      "is not found in the system response: {2}"\
                      .format(command, prompt, child.before), "error")
                break
            elif result == 6:
                cmd = "ssh-keygen -R " + ip if port == '22' else \
                      "ssh-keygen -R " + "[" + ip + "]:" + port
                print_debug("SSH Host Key is changed - Remove it from "
                            "known_hosts file : cmd = %s" % cmd)
                subprocess.call(cmd, shell=True)
                child = pexpect_spawn_with_env(pexpect, command, timeout=int(timeout),
                                               escape=escape, env={"TERM": "dumb"})
                print_debug("ReconnectSSH: cmd = %s" % command)
    except Exception as exception:
        print_exception(exception)
    return sshobj, conn_string

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

    :Returns:
        1.telnet session as object
        2.conn_string(pre and post login message)
    """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'connect_telnet' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/warrior_connect_class.py'")

    conn_options = "" if conn_options is False or conn_options is None else conn_options
    custom_keystroke = "wctrl:M" if not custom_keystroke else custom_keystroke
    print_debug("timeout is: %s" % timeout)
    print_debug("port num is: %s" % port)
    command = ('telnet '+ ip + ' '+ port)
    if not conn_options or conn_options is None:
        conn_options = ""
    command = command + str(conn_options)
    print_debug("connectTelnet cmd = %s" % command)
    child = pexpect_spawn_with_env(pexpect, command, timeout=int(timeout),
                                   escape=escape, env={"TERM": "dumb"})
    conn_string = ""
    telnetobj = None
    try:
        child.logfile = open(logfile, "a")
    except Exception:
        child.logfile = None

    try:
        flag = True
        child.setecho(False)
        child.delaybeforesend = .5
        while True:
            result = child.expect([prompt, '.*(?i)password:.*',
                                   ".*(?i)(user(name)?:|login:) *$", pexpect.EOF, pexpect.TIMEOUT])
            if result == 0:
                telnetobj = child
                conn_string = conn_string + child.before + child.after
                break
            elif result == 1:
                child.sendline(password)
                conn_string = conn_string + child.before + child.after
            elif result == 2:
                child.sendline(username)
            elif result == 3:
                pNote("Connection failed: {0}, with the system response: {1}"\
                      .format(command, child.before), "error")
                break
            elif result == 4:
                # timed out tryonce with Enter has some terminal expects it
                if flag is True:
                    pNote("Initial timeout occur, sending custom_keystroke")
                    _send_cmd_by_type(child, custom_keystroke)
                    flag = False
                    continue
                pNote("Connection timed out: {0}, expected prompt: {1} "\
                      "is not found in the system response: {2}"\
                      .format(command, prompt, child.before), "error")
                break
    except Exception as exception:
        print_error(" ! could not connect to %s...check logs" % ip)
        print_exception(exception)
    else:
        return telnetobj, conn_string


def disconnect_telnet(child):
    """Disconnects a telnet session """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'disconnect_telnet' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/warrior_connect_class.py'")

    time.sleep(2)
    child.sendcontrol(']')
    time.sleep(2)
    child.expect('telnet> ')
    time.sleep(2)
    child.sendline('q')
    time.sleep(2)
    child.close()
    return child


def disconnect(child):
    """
    - Disconnects a pexpect session
    - Returns session object(same child)
    """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'disconnect' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/warrior_connect_class.py'")

    if child.isalive():
        if child.ignore_sighup:
            child.ignore_sighup = False
        child.close()
    return child

@cmdprinter
def send_command_and_get_response(sessionobj, prompt1, prompt2, command):
    """"Sends a command to a terminal expects a completion prompt
    If completion prompt was found, returns the response of the command """
    response = ""
    try:
        boolprompt = sessionobj.expect(prompt1)
    except Exception as exception:
        print_info("Could not find the prompt "+prompt1)
        print_exception(exception)

    if boolprompt == 0:
        sessionobj.sendline(command)
        try:
            sessionobj.expect(prompt2)
        except Exception as exception:
            print_info("Could not find the prompt "+prompt2)
            print_exception(exception)
        else:
            response = sessionobj.before
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
    system_name = None

    if testdatafile is not None:
        # when the testdatafile is a dictionary - this happens only when
        # the testdatafile is taken from database server
        if isinstance(testdatafile, dict):
            db_td_obj = database_utils_class.\
             create_database_connection('dataservers', testdatafile.get('td_system'))
            root = db_td_obj.get_tdblock_as_xmlobj(testdatafile)
            db_td_obj.close_connection()
        else:
            root = xml_Utils.getRoot(testdatafile)
        system_name = data_Utils._get_global_var(root, "system_name")

    con_settings_dir = Tools.__path__[0] + os.sep + 'connection' + os.sep
    con_settings = con_settings_dir + "connect_settings.xml"

    if system_name is not None:
        sys_elem = xml_Utils.getElementWithTagAttribValueMatch(con_settings, "system", "name", system_name.text)
        if sys_elem is None or sys_elem.find("testdata") is None:
            return None
    else:
        system_list = xml_Utils.getElementListWithSpecificXpath(con_settings, "system[search_string]")
        for sys_elem in system_list:
            if sys_elem.find("search_string").text in prompt and sys_elem.find("testdata") is not None:
                return con_settings_dir + sys_elem.find("testdata").text
        return None

    return con_settings_dir + sys_elem.find("testdata").text

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
    if xml_Utils.getElementWithTagAttribValueMatch(connect_testdata, "testdata", "title", tag_value) is not None:
        print_info("**********The following command are sent as part of the smart analysis**********")
        main_log = session_object.logfile
        if pre_tag:
            smart_log = main_log.name.replace(".log", "pre_.log")
        else:
            smart_log = main_log.name.replace(".log", "post_.log")
        session_object.logfile = open(smart_log, "a")
        send_commands_from_testdata(connect_testdata, session_object, title=tag_value, system_name=call_system_name)
        session_object.logfile = main_log
        print_info("**********smart analysis finished**********")
    else:
        print_error()

def smart_action(datafile, call_system_name, raw_prompt, session_object, tag_value, connect_testdata=None):
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
    testdata, varconfigfile = data_Utils.get_td_vc(datafile, call_system_name, None, None)
    pre_tag = False
    if connect_testdata is None:
        connect_testdata = smart_analyze(raw_prompt, testdata)
        pre_tag = True

    if connect_testdata is not None:
        send_smart_cmd(connect_testdata, session_object, tag_value, call_system_name, pre_tag)
        return connect_testdata
    return None

def get_connection_port(conn_type, inpdict):
    """Gets the port for ssh or telnet connections
    1. ssh :
        - looks if ssh_port is present in  inpdict.
        - if not checks for conn_port
        - if both not present returns None
    """
    if inpdict:
        conn_string = "{0}_port".format(conn_type)
        if  conn_string in inpdict and inpdict[conn_string] is not False\
        and inpdict[conn_string] is not None:
            inpdict["port"] = inpdict["{0}_port".format(conn_type)]
        elif "conn_port" in inpdict and inpdict["conn_port"] is not False\
        and inpdict["conn_port"] is not None:
            inpdict["port"] = inpdict["conn_port"]

    return inpdict

@cmdprinter
def send_command(session_object, start_prompt, end_prompt, command,
                 timeout=60):
    """
    Send an command to pexpect session object and resturns the status of the command sent
    - Checks for the availability of the start_prompt.
    - if start prompt was available sends the command
    - if failure response is not None and failure response fond in
    response then returns False.
    - else if failure repsonse was not found
    and end prompt also not found returns False.
    - else if failure response was not found and end prompt found,
    then returns true.
    """
    print_warning("This method is obsolete and will be deprecated soon. Please"
                  " use 'send_command' method of 'PexpectConnect' class "
                  "in 'warrior/Framework/ClassUtils/warrior_connect_class.py'")

    tmout = {None: 60, "":60, "none":60}.get(timeout, str(timeout).lower())
    session_object.timeout = int(tmout)
    pNote("Command timeout: {0}".format(session_object.timeout))
    response = ""
    msg = ""
    end_time = False
    status = False
    cmd_timedout = False
    #time_format = "%Y-%b-%d %H:%M:%S"
    try:
        boolprompt = session_object.expect(start_prompt)
    except Exception as exception:
        pNote("Could not find the start_prompt '{0}'!! exiting!!".format(str(start_prompt)), "error")
        boolprompt = -1
    if boolprompt == 0:
        start_time = datetime_utils.get_current_timestamp()
        pNote("[{0}] Sending Command: {1}".format(start_time, command))
        _send_cmd_by_type(session_object, command)
        try:
            while True:
                result = session_object.expect([end_prompt, pexpect.EOF, pexpect.TIMEOUT]) if end_prompt\
                else -1
                end_time = datetime_utils.get_current_timestamp()
                if result == 0:
                    curr_time = datetime_utils.get_current_timestamp()
                    msg1 = "[{0}] Command completed successfully".format(end_time)
                    msg2 = "[{0}] Found end prompt '{1}' after command had timed out".format(curr_time, end_prompt)
                    status = {True:"ERROR", False:True}.get(cmd_timedout)
                    msg = {True:msg2, False:msg1}.get(cmd_timedout)
                    break
                elif result == -1:
                    pNote("[{0}] end prompt not provided".format(end_time), "error")
                    status = "ERROR"
                    break
                elif result == 1:
                    msg = "[{0}] EOF encountered".format(end_time)
                    status = "ERROR"
                    break
                elif result == 2:
                    tmsg1 = "[{0}] Command timed out, command will be marked as error".format(end_time)
                    tmsg2 = "Will wait 60 more seconds to get end prompt '{0}'".format(end_prompt)
                    tmsg3 = "Irrespective of whether end prompt is received or not command will "\
                           "be marked as error because command had timed out once."
                    if not cmd_timedout:
                        session_object.timeout = 1
                        pNote(tmsg1, "debug")
                        pNote(tmsg2, "debug")
                        pNote(tmsg3, "debug")
                        tstamp = datetime_utils.get_current_timestamp()
                    cmd_timedout = True
                    status = "ERROR"
                    tdelta = datetime_utils.get_time_delta(tstamp)
                    if int(tdelta) >= 60:
                        msg = "[{0}] Did not find end prompt '{1}' even after 60 seconds post"\
                              "command time out".format(datetime_utils.get_current_timestamp(),
                                                        end_prompt)
                        break
                    else:
                        continue
        except Exception as exception:
            print_exception(exception)
        else:
            response = session_object.before
            response = str(response) + str(session_object.after)
            if session_object.env is not None and 'TERM' in session_object.env and session_object.env['TERM'] == 'dumb': 
                escape_seq = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
                response = escape_seq.sub('', response)
            pNote("Response:\n{0}\n".format(response))
            pNote(msg, "debug")
            if status is True:
                duration = datetime_utils.get_time_delta(start_time, end_time)
                pNote("Command Duration: {0} sec".format(duration))
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
    status = False
    command = "ping -c " + count + " " + hostname + " >>" + fname
    print_debug("sendPing, cmd = '%s'" % command)

    response = os.system(command)
    if response == 0:
        print_debug("hostname : '%s' is up " % hostname)
        status = True
    print_debug("hostname : '%s' is down " % hostname)
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
    status = False
    command = "ping -c " + count + " -I " + src_iface + " " + destip + " >>" + fname
    print_debug("command, cmd = '%s'" % command)

    response = os.system(command)
    if response == 0:
        print_debug("hostname : '%s' is up " % destip)
        status = True
    print_debug("hostname : '%s' is down " % destip)
    return status


def send_commands_from_testdata(testdatafile, obj_session, **args):
    """
    - Parses the testdata file and gets the command details
    for rows marked execute=yes and row=str_rownum.
    - Sends the obtained commands to the pexpect session (obj_Session).
    - If the commands have verification attribute set,
    then verifies the verification text for presence/absence as defined
    in the respective found attribute in the testdatfile.

    :Arguments:
        1. testdatafile = the xml file where command details are available
        2. obj_session = pexpect session object
        3. logfile = logfile of the pexpect session object.
        4. varconfigfile=  xml file from which the values will be taken for subtitution
        5. var_sub(string) = the pattern [var_sub] in the testdata commands,
                                 start_prompt, end_prompt, verification search
                                 will substituted with this value.
        6. args = Optional filter to specify title/rownum
    :Returns:
        1. finalresult = boolean
    """
    responses_dict = {}
    varconfigfile = args.get('varconfigfile', None)
    datafile = args.get("datafile", None)
    var_sub = args.get('var_sub', None)
    title = args.get('title', None)
    row = args.get('row', None)
    if WarriorCliClass.cmdprint:
        pNote( "**************{}**************".format('Title: ' + title))
        if row:
            pNote("**************{}**************".format('Row: ' + row))
    system_name = args.get("system_name")
    session_name = args.get("session_name")
    if session_name is not None:
        system_name = system_name + "." + session_name
    testdata_dict = data_Utils.get_command_details_from_testdata(testdatafile, varconfigfile,
                                                                 var_sub=var_sub, title=title,
                                                                 row=row, system_name=system_name, datafile=datafile)
    finalresult = True if len(testdata_dict) > 0 else False
    for key, details_dict in testdata_dict.iteritems():
        response_dict = {}
        responses_dict[key]=""
        command_list = details_dict["command_list"]
        stepdesc = "Send the following commands: "
        pNote(stepdesc)
        n=0
        for commands in command_list:
            pNote("Command #{0}\t: {1}".format((n+1), commands))
            n = n + 1
        intsize = len(command_list)
        if intsize == 0:
            finalresult = False

        # Send Commands
        for i in range(0, intsize):
            print_info("")
            print_debug(">>>")
            command = details_dict["command_list"][i]
            pNote("Command #{0}\t: {1}".format(str(i+1), command))
            new_obj_session, system_name, details_dict = \
                _get_obj_session(details_dict, obj_session,
                                 system_name, index=i)
            if new_obj_session:
                result, response = _send_cmd_get_status(new_obj_session, details_dict, index=i, system_name=system_name)
                result, response = _send_command_retrials(new_obj_session, details_dict, index=i,
                                                          result=result, response=response, system_name=system_name)
                response_dict = _get_response_dict(details_dict, i, response,
                                                   response_dict)
                print_debug("<<<")
            else:
                finalresult = "ERROR"
                pNote("COMMAND STATUS:{0}".format(finalresult))
                print_debug("<<<")
                continue

            if result == "ERROR" or finalresult == "ERROR":
                result = "ERROR"
                finalresult = "ERROR"
            finalresult = finalresult and result
        responses_dict[key]=response_dict
    return finalresult, responses_dict

@cmdprinter
def _send_cmd(obj_session, **kwargs):
    """method to send command based on the type of object """
    result = False
    response = ""
    command = kwargs.get('command')
    if isinstance(obj_session,
                  Framework.ClassUtils.warrior_connect_class.WarriorConnect):
        startprompt = kwargs.get('startprompt', ".*")
        endprompt = kwargs.get('endprompt', None)
        cmd_timeout = kwargs.get('cmd_timeout', None)
        result, response = obj_session.send_command(startprompt, endprompt,
                                                    command, cmd_timeout)
    # below block is for backward compatibility - should be removed when we
    # take out send_command method from this file
    elif isinstance(obj_session, pexpect.spawn):
        startprompt = kwargs.get('startprompt', ".*")
        endprompt = kwargs.get('endprompt', None)
        cmd_timeout = kwargs.get('cmd_timeout', None)
        result, response = send_command(obj_session, startprompt, endprompt,
                                        command, cmd_timeout)
    elif isinstance(obj_session, Framework.ClassUtils.ssh_utils_class.SSHComm):
        result, response = obj_session.get_response(command)
        print_info(response)
    return result, response


def _get_response_dict(details_dict, index, response, response_dict):
    """Get the response dict for a command. """
    resp_ref = details_dict["resp_ref_list"][index]
    resp_req = details_dict["resp_req_list"][index]
    resp_pat_req = details_dict["resp_pat_req_list"][index]

    resp_req = {None:'y', '':'y',
                'no':'n', 'n':'n'}.get(str(resp_req).lower(), 'y')
    resp_ref = {None:index+1, '':index+1 }.get(resp_ref, str(resp_ref))
    #response_key=resp_ref_list[i] if resp_ref_list[i] else i+1
    if not resp_req=="n":
        if resp_pat_req is not None:
            # if the requested pattern not found return empty string
            reobj=re.search(resp_pat_req, response)
            response=reobj.group(0) if reobj is not None else ""
            pNote("User has requested saving response. Response pattern required by user is : {0}".format(resp_pat_req))
            pNote("Portion of response saved to the data repository with key: {0}, value: {1}".format(resp_ref, response))
    else:
        response=""
    response_dict[resp_ref]=response
    return response_dict


def start_threads(started_thread_for_system, thread_instance_list, same_system, unique_log_verify_list, system_name):
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
    started_thread_for_system = []
    thread_instance_list = []
    same_system = []
    for i in range(0, len(unique_log_verify_list)):
        if unique_log_verify_list[i] == system_name:
            temp_list = unique_log_verify_list[i].split(".")
            if len(temp_list)>1:
                unique_log_verify_list[i] = data_Utils.get_session_id(temp_list[0], temp_list[1])
            else:
                unique_log_verify_list[i] = data_Utils.get_session_id(temp_list[0])
            same_system.append(unique_log_verify_list[i])
        else:
            if unique_log_verify_list[i]:
                temp_list = unique_log_verify_list[i].split(".")
                if len(temp_list)>1:
                    unique_log_verify_list[i] = data_Utils.get_session_id(temp_list[0], temp_list[1])
                else:
                    unique_log_verify_list[i] = data_Utils.get_session_id(temp_list[0])
                datarep_obj = get_object_from_datarepository(unique_log_verify_list[i])
                if datarep_obj is False:
                    print_info("{0} does not exist in data repository".format(unique_log_verify_list[i]))
                else:
                    try:
                        new_thread = ThreadedLog()
                        new_thread.start_thread(datarep_obj)
                        print_info("Collecting response from: {0}".format(unique_log_verify_list[i]))
                        started_thread_for_system.append(unique_log_verify_list[i])
                        thread_instance_list.append(new_thread)
                    except:
                        print_info("Unable to collect response from: {0}".format(unique_log_verify_list[i]))
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
    remote_resp_dict = {}
    for i in range(0, len(same_system)):
        remote_resp_dict[same_system[i]] = response

    for i in range(0, len(started_thread_for_system)):
        data = thread_instance_list[i].data
        thread_instance_list[i].stop_thread()
        pNote("\n\n++++++++++++++++++++++++ RESPONSE FROM SYSTEM: {0} "
              "++++++++++++++++++++\n\n".format(started_thread_for_system[i]))
        pNote(data)
        pNote("\n\n++++++++++++++++++++++++ END OF DATA FROM SYSTEM: {0} "
              "++++++++++++++++++++\n\n".format(started_thread_for_system[i]))
        remote_resp_dict[started_thread_for_system[i]] = data

    if len(started_thread_for_system) > 0:
        print_info("Waiting for maximum of 30 seconds to stop collecting "
                   "logs from verify_on system(s)")

    for i in range(0, len(started_thread_for_system)):
        thread_instance_list[i].join_thread(timeout=30, retry=3)
        if thread_instance_list[i].thread_status() is True:
            print_error("Unable to stop collecting logs from {0}.Please check "
                        "below message for all exception trace that occurred: "
                        "\n{1}".format(started_thread_for_system[i],
                                       thread_instance_list[i].
                                       stop_thread_err_msg))
    return remote_resp_dict


def get_unique_log_and_verify_list(log_list, verify_on_list, system_name):
    """This function loops through the log_list and the verify_on_list
    and returns a unique list containing unique sustem names fromboth the lists
    """
    final_list = []
    if log_list is not None and log_list is not "" and log_list is not False:
        comma_sep_log_names = log_list.split(",")
        for i in range(0, len(comma_sep_log_names)):
            comma_sep_log_names[i] = comma_sep_log_names[i].strip()
    else:
        comma_sep_log_names = []

    comma_sep_verify_names = []
    if verify_on_list is not None and verify_on_list is not "" and verify_on_list is not False:
        for i in range(0, len(verify_on_list)):
            if verify_on_list[i] is not None and verify_on_list[i] is not "" and verify_on_list[i] is not False:
                temp_list = verify_on_list[i].split(",")
                for j in range(0, len(temp_list)):
                    comma_sep_verify_names.append(temp_list[j].strip())
            else:
                comma_sep_verify_names.append([])
    else:
        comma_sep_verify_names = []

    for i in range(0, len(comma_sep_log_names)):
        if comma_sep_log_names[i] not in final_list:
            final_list.append(comma_sep_log_names[i])

    for i in range(0, len(comma_sep_verify_names)):
        if comma_sep_verify_names[i] == "":
            comma_sep_verify_names[i] = system_name
        if comma_sep_verify_names[i] not in final_list:
            final_list.append(comma_sep_verify_names[i])
    return final_list


@cmdprinter
def _send_cmd_get_status(obj_session, details_dict, index, system_name=None):
    """Sends a command, verifies the response and returns
    status of the command """
    command = details_dict["command_list"][index]
    startprompt = details_dict["startprompt_list"][index]
    endprompt = details_dict["endprompt_list"][index]
    verify_list = details_dict["verify_list"][index]
    cmd_timeout = details_dict["timeout_list"][index]
    verify_text_list = details_dict["verify_text_list"][index]
    verify_context_list = details_dict["verify_context_list"][index]
    sleeptime = details_dict["sleeptime_list"][index]
    resp_ref = details_dict["resp_ref_list"][index]
    resp_req = details_dict["resp_req_list"][index]
    resp_pat_req = details_dict["resp_pat_req_list"][index]
    verify_on_list = details_dict["verify_on_list"][index]
    log_list = details_dict["log_list"][index]
    inorder_search = details_dict["inorder_search_list"][index]
    varconfigfile = details_dict["vc_file_list"][index]
    operator = details_dict["operator_list"][index]
    cond_value = details_dict["cond_value_list"][index]
    cond_type = details_dict["cond_type_list"][index]
    unique_log_verify_list = get_unique_log_and_verify_list(log_list,
                                                            verify_on_list,
                                                            system_name)

    startprompt = {None: ".*", "": ".*"}.get(startprompt, str(startprompt))
    resp_req = {None: 'y', '': 'y',
                'no': 'n', 'n': 'n'}.get(str(resp_req).lower(), 'y')
    resp_ref = {None: index+1, '': index+1}.get(resp_ref, str(resp_ref))
    resp_pat_req = {None: ""}.get(resp_pat_req, str(resp_pat_req))
    sleeptime = {None: 0, "": 0, "none": 0, False: 0, "false": 0}.get(
                                str(sleeptime).lower(), str(sleeptime))
    sleeptime = int(sleeptime)

    if inorder_search is not None and inorder_search.lower().startswith("y"):
        inorder_search = True
    else:
        inorder_search = False

    pNote("Startprompt\t: {0}".format(startprompt))
    pNote("Endprompt\t: {0}".format(endprompt))
    pNote("Sleeptime\t: {0}".format(sleeptime))
    pNote("Response required: {0}".format(resp_req))
    pNote("Response reference: {0}".format(resp_ref))
    pNote("Response pattern required: {0}".format(resp_pat_req))

    if not command:
        pNote("Received a boolean False or None type instead of a string "
              "command, Command not provided or Variable substitution for the "
              "command could have gone wrong", "error")
        pNote("Skipping execution of this command, result will be marked as "
              "error", "debug")
        result = 'ERROR'
        response = ''
    else:
        started_thread_for_system, thread_instance_list, same_system = \
            start_threads([], [], [], unique_log_verify_list, system_name)

        result, response = _send_cmd(obj_session, startprompt=startprompt,
                                     endprompt=endprompt, command=command,
                                     cmd_timeout=cmd_timeout)

    if sleeptime > 0:
        pNote("Sleep time of '{0} seconds' requested post command "
              "execution".format(sleeptime))
        time.sleep(sleeptime)

    try:
        remote_resp_dict = get_response_dict(started_thread_for_system,
                                             thread_instance_list,
                                             same_system, response)
    except NameError:
        remote_resp_dict = get_response_dict([], [], [], response)

    verify_on_list_as_list = get_list_by_separating_strings(verify_on_list,
                                                            ",", system_name)
    if result and result is not 'ERROR':
        if verify_text_list is not None and verify_list is not None:
            verify_group = (operator, cond_value, cond_type)
            if inorder_search is True and len(verify_text_list) > 1:
                result = data_Utils.verify_resp_inorder(
                            verify_text_list, verify_context_list, command,
                            response, varconfigfile, verify_on_list_as_list,
                            verify_list, remote_resp_dict, verify_group)
            else:
                result = data_Utils.verify_resp_across_sys(
                            verify_text_list, verify_context_list, command,
                            response, varconfigfile, verify_on_list_as_list,
                            verify_list, remote_resp_dict, endprompt,
                            verify_group)
    command_status = {True: "PASS", False: "FAIL", "ERROR": "ERROR"}.get(
                                                                    result)
    pNote("COMMAND STATUS:{0}".format(command_status))

    return result, response


def _get_obj_session(details_dict, obj_session, kw_system_name, index):
    """If system name is provided in testdata file
    get the session of that system name and use it or
    use the current obj_session"""

    value = False
    kw_system_nameonly, _ = data_Utils.split_system_subsystem(kw_system_name)
    td_sys = details_dict["sys_list"][index]
    # To get the session name if it is provided as part of sys tag in td
    td_sys_split = td_sys.split('.') if isinstance(td_sys, str) else []
    if len(td_sys_split) == 2:
        td_sys = td_sys_split[0]
        session = td_sys_split[1]
    else:
        session = details_dict["session_list"][index]

    td_sys = td_sys.strip() if isinstance(td_sys, str) else td_sys
    td_sys = {None:False, False:False, "":False}.get(td_sys, td_sys)
    session = session.strip() if isinstance(session, str) else session
    session = {None:None, False:None, "":None}.get(session, session)
    if td_sys:
        system_name = kw_system_nameonly + td_sys if td_sys.startswith("[") \
        and td_sys.endswith("]") else td_sys
        session_id = data_Utils.get_session_id(system_name, session)
        obj_session = data_Utils.get_object_from_datarepository(session_id)
        if not obj_session:
            pNote("Could not find a valid connection for "\
                  "system_name={}, session_name={}".format(system_name, session), "error")
            value = False
        else:
            value = obj_session
            # details_dict =
            # _update_details_dict(system_name, datafile, details_dict, var_sub)

    else:
        # print obj_session
        value = obj_session
        system_name = kw_system_name

    pNote("System name\t: {0}".format(system_name))

    if details_dict["sys_list"][index] is not None:
        kw_system_name = details_dict["sys_list"][index]

    return value, kw_system_name, details_dict

@cmdprinter
def _send_command_retrials(obj_session, details_dict, index, **kwargs):
    """ Sends a command to a session, if a user provided pattern
    is found in the command response then tries to resend the command multiple
    times.
    retry_timer = time interval between subsequent retries
    retry_onmatch = the pattern to be matched in the response
                    in order to retry the command.
    retry_count = no of times to retry.
    """
    retry = details_dict["retry_list"][index]
    retry = {None:'n', '':'n', 'none':'n'}.get(str(retry).lower(), retry)
    result = kwargs.get('result')
    response = kwargs.get('response')
    if retry == 'y' and (result == False or result == 'ERROR'):
        retry_timer = details_dict["retry_timer_list"][index]
        retry_onmatch = details_dict["retry_onmatch_list"][index]
        retry_count = details_dict["retry_count_list"][index]
        retry_timer = {None:60, "":60, "none":60}.get(str(retry_timer).lower(), retry_timer)
        retry_count = {None:5, "":5, "none":5}.get(str(retry_count).lower(), retry_count)
        print_info("")
        pNote("Retry was requested for the command")
        pNote("Command re-trials will begin since the most recent "\
              "command status was FAIL or ERROR")
        pNote("Retry count\t: {0}".format(retry_count))
        pNote("Retry timer\t: {0}".format(retry_timer))
        retry_onmatch = {None:False, "":False}.get(retry_onmatch, str(retry_onmatch))
        print_onmatch = {False:""}.get(retry_onmatch, str(retry_onmatch))
        pNote("Retry onmatch: {0}".format(print_onmatch))
        count = 0
        while count < int(retry_count):
            if result == False or result == 'ERROR':
                match_status = _get_match_status(retry_onmatch, response)
                if match_status:
                    count = count + 1
                    print_info("")
                    pNote("RETRIAL ATTEMPT:{0}".format(count))
                    pNote("Wait for {0}sec (retry_timer) before sending"\
                               " the command again".format(retry_timer))
                    time.sleep(int(retry_timer))
                    result, response = _send_cmd_get_status(obj_session, details_dict, index, system_name=kwargs.get("system_name"))
                    command_status = {True: "PASS", False:"FAIL", "ERROR":"ERROR"}.get(result)
                    pNote("RETRIAL ATTEMPT:{0} STATUS:{1}".format(count, command_status))
                else:
                    break
            elif result == True:
                break
    return result, response


def _get_match_status(retry_onmatch, response):
    """ """
    status = True
    if retry_onmatch:
        pNote("Command will be executed again if "\
              "the pattern {0} is present in the "
              "response of the previous execution of the command"\
              .format(retry_onmatch))
        match_object = re.search(retry_onmatch, response)
        if match_object:
            pNote("Found the pattern '{0}' "\
                  "in the response of the previous execution "\
                  "of the command".format(retry_onmatch))
        else:
            pNote("Did not find the pattern '{0}' "\
                  "in the response of the previous execution "\
                  "of the command".format(retry_onmatch))
            status = False
    return status


def _send_cmd_by_type(session_object, command):
    """Determine the command type and
    send accordingly """

    if command.startswith("wctrl:"):
        command = command.split("wctrl:")[1]
        session_object.sendcontrol(command)
    else:
        session_object.sendline(command)


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
