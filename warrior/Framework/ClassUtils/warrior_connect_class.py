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

""" Module to handle SSH/Telnet session operations """

import os
import sys
import time
import subprocess

from Framework import Utils
from Framework.Utils.print_Utils import print_info, print_debug,\
 print_exception, print_error
from Framework.Utils.testcase_Utils import pNote
from WarriorCore.Classes.war_cli_class import WarriorCliClass
from Framework.Utils.cli_Utils import cmdprinter, pexpect_spawn_with_env


class WarriorConnect(object):
    """
    Class to handle SSH/Telnet operations.f
    Supported conn_type values : SSH, TELNET, SSH_NESTED
    """

    def __init__(self):
        """ Constructor """
        self.conn_type = None
        self.session_object = None
        self.conn_string = ""
        self.status = None

    def connect(self, credentials):
        """ To create SSH/Telnet connections using pexpect/paramiko modules.
        :Arguments:
            1. credentials = refer constructor method arguments of
                             ParamikoConnect & PexpectConnect classes
         """

        self.status = False
        if 'conn_type' in credentials:
            self.conn_type = credentials['conn_type'].upper()

        if self.conn_type in ["SSH", "TELNET"]:
            self.session_object = PexpectConnect(credentials)
            # pexpect will be used for establishing session
            if self.conn_type == "SSH":
                self.session_object.connect_ssh()
            else:
                self.session_object.connect_telnet()
            # change the status to True if the session creation is successful
            import pexpect
            if isinstance(self.session_object.target_host, pexpect.spawn):
                self.status = True
        elif self.conn_type == "SSH_NESTED":
            # paramiko will be used for establishing session
            self.session_object = ParamikoConnect(credentials)
            self.session_object.connect_ssh()
            # change the status to True if the session creation is successful
            import paramiko
            if isinstance(self.session_object.target_host,
                          paramiko.client.SSHClient):
                self.status = True
        else:
            print_info("Connection type : {} is not "
                       "supported".format(self.conn_type))
            self.session_object, self.conn_string = None, ""

    def disconnect(self):
        """ To close SSH/Telnet session """

        if self.session_object:
            if self.conn_type == "TELNET":
                self.session_object.disconnect_telnet()
            else:
                self.session_object.disconnect()

    @cmdprinter
    def send_command(self, start_prompt, end_prompt, command,
                     timeout=60):
        """ Sends the command to ssh/telnet session """

        status = False
        response = None

        if self.session_object:
            status, response = self.session_object.\
             send_command(start_prompt=start_prompt, end_prompt=end_prompt,
                          command=command, timeout=timeout)

        return status, response

    def isalive(self):
        """
        Returns whether the paramiko/pexpect session is alive or not
        :Returns:
            True if alive else False
        """

        if self.session_object:
            target_host = self.session_object.target_host
        else:
            target_host = False

        if target_host:
            # for paramiko
            if self.conn_type == "SSH_NESTED":
                if target_host.get_transport():
                    status = target_host.get_transport().is_active()
                else:
                    status = False
            # for pexpect
            else:
                status = target_host.isalive()
        else:
            status = False

        return status

    def read_nonblocking(self, size=1024, timeout=None, *args, **kwargs):
        """
        Reads characters(size) from pexpect/paramiko session
        :Arguments:
            1. size = maximum number of bytes to read
        :Returns:
            1. read_string = Characters read from the pexpect/paramiko session
        """

        try:
            if self.session_object:
                if self.conn_type == "SSH_NESTED":
                    read_string = self.session_object.channel.recv(size)
                else:
                    read_string = self.session_object.target_host.\
                     read_nonblocking(size, timeout)
            else:
                read_string = ""
        except Exception:
            read_string = ""

        return read_string

    @property
    def timeout(self):
        """ Get session timeout(mins) value of pexpect/paramiko session  """

        timeout = None
        if self.conn_type in ["SSH", "TELNET"]:
            timeout = self.session_object.target_host.timeout
        # elif self.conn_type == "SSH_NESTED":
        #    timeout = self.session_object.timeout
        #    # paramiko timeout value will be in seconds, convert it to mins
        #    if timeout:
        #        timeout = timeout/60

        return timeout

    @timeout.setter
    def timeout(self, value):
        """ Set session timeout value(mins) for pexpect/paramiko session """

        if self.conn_type in ["SSH", "TELNET"]:
            self.session_object.target_host.timeout = value
        # elif self.conn_type == "SSH_NESTED":
        #    # paramiko accepts timeout value in seconds
        #    self.session_object.timeout = value * 60


class ParamikoConnect(object):
    """ Class to handle SSH operations using Paramiko module """
    def __init__(self, credentials):
        """ Constructor

        :Arguments
            1. credentials:
                1. ip = target_system ip
                2. port = target_system ssh port
                3. username(string) = target_system username
                4. password(string) = target_system password
                5. logfile = logfile name
                6. timeout = wait for response in target_system
                7. via_ip = intermediate_system ip
                8. via_port = intermediate_system ssh port
                9. via_username(string) = intermediate_system username
                10. via_password(string) = intermediate_system password
                11. via_timeout = wait for response in intermediate_system
         """

        self.paramiko = None
        self.__import_paramiko()
        self.conn_string = ""
        self.response = ""
        self.target_host = None
        self.channel = None
        self.conn_type = credentials.get('conn_type')
        self.ip = credentials.get('ip')
        self.port = credentials.get('port')
        if self.port is not None:
            self.port = int(self.port)
        self.username = credentials.get('username', '')
        self.password = credentials.get('password', '')
        self.logfile = credentials.get('logfile')
        self.timeout = credentials.get('timeout', 60)

        if self.conn_type and self.conn_type.upper() == "SSH_NESTED":
            self.via_ip = credentials.get('via_ip')
            self.via_port = credentials.get('via_port')
            if self.via_port is not None:
                self.via_port = int(self.via_port)
            self.via_username = credentials.get('via_username', '')
            self.via_password = credentials.get('via_password', '')
            self.via_timeout = credentials.get('via_timeout', 60)

    def __import_paramiko(self):
        """Import the paramiko module """

        try:
            import paramiko
        except ImportError:
            print_info("{0}: paramiko module is not "
                       "installed".format(os.path.abspath(__file__)))
            print_info("Warrior Framework uses paramiko module for "
                       "cli(via nested SSH) related operations")
        else:
            self.paramiko = paramiko

    def connect_ssh(self):
        """
        Initiates SSH connection to target system using paramiko module.
        For nested SSH connections, session will be established
        via intermediate system.
        """

        if self.paramiko is None:
            print_error("Paramiko is not installed, please install it")
            return

        self.port = self.port if self.port else "22"
        try:
            # for nested SSH session
            if self.conn_type and self.conn_type.upper() == "SSH_NESTED":
                pNote("Nested SSH connection is requested, first connecting to"
                      " intermediate system - {}".format(self.via_ip))
                self.via_host = self.paramiko.SSHClient()
                self.via_host.set_missing_host_key_policy(
                 self.paramiko.AutoAddPolicy())
                self.via_host.connect(self.via_ip, port=self.via_port,
                                      username=self.via_username,
                                      password=self.via_password,
                                      timeout=self.via_timeout)

                self.via_transport = self.via_host.get_transport()

                dest_addr = (self.ip, self.port)
                local_addr = ('127.0.0.1', 22)

                self.via_channel = self.via_transport.open_channel(
                 "direct-tcpip", dest_addr, local_addr)
                pNote("Connection to intermediate system - {} "
                      "is successful".format(self.via_ip))
            else:
                self.via_channel = None

            self.target_host = self.paramiko.SSHClient()
            self.target_host.set_missing_host_key_policy(
             self.paramiko.AutoAddPolicy())

            self.target_host.connect(self.ip, port=self.port,
                                     username=self.username,
                                     password=self.password,
                                     timeout=self.timeout,
                                     sock=self.via_channel)

            if self.logfile is not None:
                # paramiko logging level is DEBUG(default)
                self.paramiko.util.log_to_file(self.logfile)
            # self.conn_string = self.target_host.get_transport().get_banner()
            # Use invoke_shell option to get conn_string value
            self.channel = self.target_host.invoke_shell()
            self.conn_string = self.channel.recv(9999).decode("utf-8")
        except Exception as exception:
            self.target_host = None
            print_exception(exception)

    def disconnect(self):
        """ Disconnects nested paramiko session """
        self.channel.close()
        self.target_host.close()
        # for nested ssh session
        if self.conn_type and self.conn_type.upper() == "NESTED_SSH":
            self.via_host.close()

    def send_command(self, command, get_pty=False, *args, **kwargs):
        """ Execute the command on the remote host

        :Arguments:
            1.command = command to be executed
            2.get_pty = request a pseudo-terminal

        """

        response = ""
        status = False

        try:
            start_time = Utils.datetime_utils.get_current_timestamp()
            pNote("[{0}] Sending Command: {1}".format(start_time, command))

            stdin, stdout, stderr = self.target_host.\
                exec_command(command, get_pty=get_pty)

            end_time = Utils.datetime_utils.get_current_timestamp()
            stdin.close()

            # If a linux command fails, corresponding response will be in
            # stderr, stdout.channel.recv_exit_status() will give non-zero
            # value but stderr value is also a valid response in Warrior
            # execution.we can't fail the command execution based on
            # recv_exit_status value.
            if stdout:
                response = response + stdout.read()
            if stderr:
                response = response + stderr.read()

            pNote("[{0}] Command execution completed".format(end_time))
            pNote("Response:\n{0}\n".format(response))
            status = True
        except Exception as exception:
            print_exception(exception)

        return status, response


class PexpectConnect(object):
    """ Class to handle SSH operations using Pexpect module """

    def __init__(self, credentials):
        """ Constructor

        :Arguments
            1. credentials:
                1. ip = destination ip
                2. port = ssh/telnet port
                3. username(string) = username
                4. password(string) = password
                5. logfile(string) = logfile name
                6. timeout = timeout duration
                7. prompt(string) = destination prompt
                8. conn_options = connection options
                9. custom_keystroke = keystroke(to be given
                                      after initial timeout)
         """

        self.pexpect = None
        self.__import_pexpect()
        self.conn_string = ""
        self.response = ""
        self.target_host = None
        self.channel = None
        self.ip = credentials.get('ip')
        self.port = credentials.get('port')
        self.username = credentials.get('username', '')
        self.password = credentials.get('password', '')
        self.logfile = credentials.get('logfile')
        self.timeout = credentials.get('timeout', 60)
        self.prompt = credentials.get('prompt', '.*(%|#|\$)')
        self.conn_options = credentials.get('conn_options', '')
        self.custom_keystroke = credentials.get('custom_keystroke', '')
        self.escape = credentials.get('escape', False)

    def __import_pexpect(self):
        """Import the pexpect module """

        try:
            import pexpect
        except ImportError:
            print_info("{0}: pexpect module is not "
                       "installed".format(os.path.abspath(__file__)))
            print_info("Warrior Framework uses pexpect module for "
                       "cli(SSH & telent) related operations")
        else:
            self.pexpect = pexpect

    def connect_ssh(self):
        """
        Initiates SSH connection via a specific port. Creates log file.
        """

        if self.pexpect is None:
            print_error("Pexpect is not installed, please install it")
            return

        self.target_host = None
        self.conn_string = ""
        self.port = self.port if self.port else "22"
        conn_options = "" if self.conn_options is False or \
            self.conn_options is None else self.conn_options
        custom_keystroke = "wctrl:M" if not self.custom_keystroke else \
            self.custom_keystroke
        # delete -o StrictHostKeyChecking=no and put them in conn_options
        if not conn_options or conn_options is None:
            conn_options = ""
        command = 'ssh -p {0} {1}@{2} {3}'.format(self.port, self.username,
                                                  self.ip, conn_options)
        # command = ('ssh -p '+ port + ' ' + username + '@' + ip)
        print_debug("connectSSH: cmd = %s" % command)
        if WarriorCliClass.cmdprint:
            pNote("connectSSH: :CMD: %s" % command)
            return None, ""
        child = pexpect_spawn_with_env(self.pexpect, command, timeout=int(self.timeout),
                                       escape=self.escape, env={"TERM": "dumb"})

        child.logfile = sys.stdout

        if self.logfile is not None:
            try:
                fdobj = open(self.logfile, "a")
                if fdobj:
                    child.logfile = fdobj
            except Exception as exception:
                print_exception(exception)

        try:
            flag = True
            child.setecho(False)
            child.delaybeforesend = .5
            while True:
                result = child.expect(["(yes/no)", self.prompt,
                                       '.*(?i)password:.*',
                                       ".*(?i)(user(name)?:|login:) *$",
                                       self.pexpect.EOF, self.pexpect.TIMEOUT,
                                       '.*(?i)remote host identification has '
                                       'changed.*'])
                if result == 0:
                    child.sendline('yes')
                elif result == 1:
                    self.target_host = child
                    self.conn_string = self.conn_string + child.before + \
                        child.after
                    break
                elif result == 2:
                    child.sendline(self.password)
                    self.conn_string = self.conn_string + child.before + \
                        child.after
                elif result == 3:
                    child.sendline(self.username)
                elif result == 4:
                    pNote("Connection failed: {0}, with the system response: "
                          "{1}".format(command, child.before), "error")
                    break
                elif result == 5:
                    # Some terminal expect specific keystroke before showing
                    # login prompt
                    if flag is True:
                        pNote("Initial timeout occur, "
                              "sending custom_keystroke")
                        Utils.cli_Utils._send_cmd_by_type(child,
                                                          custom_keystroke)
                        flag = False
                        continue
                    pNote("Connection timed out: {0}, expected prompt: {1} "
                          "is not found in the system response: {2}"
                          .format(command, self.prompt, child.before), "error")
                    break
                elif result == 6:
                    cmd = "ssh-keygen -R " + self.ip if self.port == '22' else\
                          "ssh-keygen -R " + "[" + self.ip + "]:" + self.port
                    print_debug("SSH Host Key is changed - Remove it from "
                                "known_hosts file : cmd = %s" % cmd)
                    subprocess.call(cmd, shell=True)
                    child = self.pexpect.spawn(command,
                                               timeout=int(self.timeout))
                    print_debug("ReconnectSSH: cmd = %s" % command)
        except Exception as exception:
            print_exception(exception)

    def connect_telnet(self):
        """
        Initiates Telnet connection via a specific port. Creates log file.
        """

        self.target_host = None
        self.conn_string = ""
        self.port = self.port if self.port else "23"
        conn_options = "" if self.conn_options is False or \
            self.conn_options is None else self.conn_options
        custom_keystroke = "wctrl:M" if not self.custom_keystroke else \
            self.custom_keystroke
        print_debug("timeout is: %s" % self.timeout)
        print_debug("port num is: %s" % self.port)
        command = ('telnet ' + self.ip + ' ' + self.port)
        if not conn_options or conn_options is None:
            conn_options = ""
        command = command + str(conn_options)
        print_debug("connectTelnet cmd = %s" % command)

        child = pexpect_spawn_with_env(self.pexpect, command, timeout=int(self.timeout),
                                       escape=self.escape, env={"TERM": "dumb"})

        try:
            child.logfile = open(self.logfile, "a")
        except Exception:
            child.logfile = None

        try:
            flag = True
            child.setecho(False)
            child.delaybeforesend = .5
            while True:
                result = child.expect([self.prompt, '.*(?i)password:.*',
                                       ".*(?i)(user(name)?:|login:) *$",
                                       self.pexpect.EOF,
                                       self.pexpect.TIMEOUT])
                if result == 0:
                    self.target_host = child
                    self.conn_string = self.conn_string + child.before + \
                        child.after
                    break
                elif result == 1:
                    child.sendline(self.password)
                    self.conn_string = self.conn_string + child.before + \
                        child.after
                elif result == 2:
                    child.sendline(self.username)
                elif result == 3:
                    pNote("Connection failed: {0}, with the system response: "
                          "{1}".format(command, child.before), "error")
                    break
                elif result == 4:
                    # timed out tryonce with Enter has some terminal expects it
                    if flag is True:
                        pNote("Initial timeout occur, "
                              "sending custom_keystroke")
                        Utils.cli_Utils._send_cmd_by_type(child,
                                                          custom_keystroke)
                        flag = False
                        continue
                    pNote("Connection timed out: {0}, expected prompt: {1} "
                          "is not found in the system response: {2}"
                          .format(command, self.prompt, child.before), "error")
                    break
        except Exception as exception:
            print_error(" ! could not connect to %s...check logs" % self.ip)
            print_exception(exception)

    def disconnect(self):
        """
        Disconnects a pexpect session
        """
        if self.target_host.isalive():
            if self.target_host.ignore_sighup:
                self.target_host.ignore_sighup = False
            self.target_host.close()

    def disconnect_telnet(self):
        """
        Disconnects a telnet session
        """
        if self.target_host.isalive():
            time.sleep(2)
            self.target_host.sendcontrol(']')
            time.sleep(2)
            self.target_host.expect('telnet> ')
            time.sleep(2)
            self.target_host.sendline('q')
            time.sleep(2)
            self.target_host.close()

    @cmdprinter
    def send_command(self, start_prompt, end_prompt, command,
                     timeout=60, *args, **kwargs):
        """
        Send an command to pexpect session object and returns
        the status of the command sent
        - Checks for the availability of the start_prompt.
        - if start prompt was available sends the command
        - if failure response is not None and failure response found in
        response then returns False.
        - else if failure response was not found
        and end prompt also not found returns False.
        - else if failure response was not found and end prompt found,
        then returns true.
        """
        tmout = {None: 60, "": 60, "none": 60}.get(timeout,
                                                   str(timeout).lower())
        self.target_host.timeout = int(tmout)
        pNote("Command timeout: {0}".format(self.target_host.timeout))
        response = ""
        msg = ""
        end_time = False
        status = False
        cmd_timedout = False
        # time_format = "%Y-%b-%d %H:%M:%S"
        try:
            boolprompt = self.target_host.expect(start_prompt)
        except Exception as exception:
            pNote("Could not find the start_prompt '{0}'!! exiting!!".
                  format(str(start_prompt)), "error")
            boolprompt = -1
        if boolprompt == 0:
            start_time = Utils.datetime_utils.get_current_timestamp()
            pNote("[{0}] Sending Command: {1}".format(start_time, command))
            Utils.cli_Utils._send_cmd_by_type(self.target_host, command)
            try:
                while True:
                    result = self.target_host.expect([end_prompt,
                                                      self.pexpect.EOF,
                                                      self.pexpect.TIMEOUT]) \
                                                      if end_prompt else -1
                    end_time = Utils.datetime_utils.get_current_timestamp()
                    if result == 0:
                        curr_time = Utils.datetime_utils.\
                            get_current_timestamp()
                        msg1 = "[{0}] Command completed successfully". \
                            format(end_time)
                        msg2 = "[{0}] Found end prompt '{1}' after command" \
                            "had timed out".format(curr_time, end_prompt)
                        status = {True: "ERROR", False: True}.get(cmd_timedout)
                        msg = {True: msg2, False: msg1}.get(cmd_timedout)
                        break
                    elif result == -1:
                        pNote("[{0}] end prompt not provided".format(end_time),
                              "error")
                        status = "ERROR"
                        break
                    elif result == 1:
                        msg = "[{0}] EOF encountered".format(end_time)
                        status = "ERROR"
                        break
                    elif result == 2:
                        tmsg1 = "[{0}] Command timed out, command will be " \
                            "marked as error".format(end_time)
                        tmsg2 = "Will wait 60 more seconds to get end " \
                            "prompt '{0}'".format(end_prompt)
                        tmsg3 = "Irrespective of whether end prompt is " \
                            "received or not command will be marked as error" \
                            " because command had timed out once."
                        if not cmd_timedout:
                            self.target_host.timeout = 1
                            pNote(tmsg1, "debug")
                            pNote(tmsg2, "debug")
                            pNote(tmsg3, "debug")
                            tstamp = Utils.datetime_utils.\
                                get_current_timestamp()
                        cmd_timedout = True
                        status = "ERROR"
                        tdelta = Utils.datetime_utils.get_time_delta(tstamp)
                        if int(tdelta) >= 60:
                            msg = "[{0}] Did not find end prompt '{1}' even " \
                                "after 60 seconds post command time out". \
                                format(Utils.datetime_utils.
                                       get_current_timestamp(),
                                       end_prompt)
                            break
                        else:
                            continue
            except Exception as exception:
                print_exception(exception)
            else:
                response = self.target_host.before
                response = str(response) + str(self.target_host.after)
                pNote("Response:\n{0}\n".format(response))
                pNote(msg, "debug")
                if status is True:
                    duration = Utils.datetime_utils.get_time_delta(start_time,
                                                                   end_time)
                    pNote("Command Duration: {0} sec".format(duration))
        return status, response
