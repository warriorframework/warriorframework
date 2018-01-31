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

"""SSH utility module using the python Paramiko module"""
#!/usr/bin/env python

import os
import time
from time import sleep
from Framework.Utils import testcase_Utils, data_Utils
from Framework.Utils.print_Utils import print_info, print_error, print_debug, print_exception

class SSHComm(object):
    """SSHComm class which has methods
       related to SSH communication using paramiko"""

    def __init__(self, target, port=22, uid='', pid='', logfile=None):
        self.param = None
        self.import_param()
        self.sshobj = self.param.SSHClient()
        self.target = target
        self.uid = uid
        self.pid = pid
        self.logfile = logfile
        self.port = port

    def import_param(self):
        """Import the paramiko module """
        try:
            import paramiko
        except ImportError:
            print_error("Paramiko module is not installed"\
                       "Please install requests module to"\
                       "perform any activities related to SSH Communication")
        else:
            self.param = paramiko

    def ssh_con(self, retries=1, interval=1, timeout=60, verify_keys=False,
                invoke_shell=False):
        """Connects to the host using ssh object

        :Arguments:
            1. retries =  No of attempts before returning fail
            2. interval = Time to wait before the next retry
            3. timeout = wait for response
            4. verify_keys = Verify the host entry is available in host key

        :Returns:
            1. status(bool)= True / False

        """
        for attempt in xrange(retries):
            print_debug("Attempt{} connecting to {}".format(attempt+1,
                                                            self.target))
            try:
                if not verify_keys:
                    self.sshobj.set_missing_host_key_policy(\
                                                self.param.AutoAddPolicy())
                self.sshobj.connect(self.target, self.port, self.uid,
                                    self.pid, timeout=timeout,
                                    look_for_keys=verify_keys)
                if invoke_shell:
                    print_info("Opening shell for {}".format(self.sshobj))
                    self.sshobj.invoke_shell()

                if self.logfile is not None:
                    self.log = open(self.logfile, 'w')
            except self.param.SSHException:
                print_error(" ! could not connect to %s...check logs" % self.target)
                return False
            except Exception, err:
                print_error("Login failed {0}".format(str(err)))
                sleep(interval)
                continue
            else:
                print_info("Connected to the host")
                return True
        return False

    def ssh_close(self):
        """Close the SSH connection object

        :Returns:
            1. status(bool)= True / False

        """
        try:
            print_info("Closing SSH connection")
            self.sshobj.close()
            print_info("SSH Connection closed")

        except Exception:
            print_error("Error occured while closing ssh session")
            return False

        else:
            return True

    def ssh_exec(self, command, timeout=None, get_pty=True):
        """Execution of the  command on the remote host

        :Arguments:
           1.command = command to be executed
           2.timeout = wait for response
           3.get_pty = request a pseudo-terminal

        :Returns:
           1. out = command output
           2. stderr = command's error stream object
        """
        print_info("Executing command : %s" % command)
        out = ""
        stdin, stdout, stderr = self.sshobj.exec_command(command,
                                                         timeout=timeout,
                                                         get_pty=get_pty)
        stdin.close()
        if self.logfile is not None:
            self.log.write("*"*20)
            self.log.write("\n")
            self.log.write("Executing command :%s\n" % command)
            self.log.write("Output:\n")

        for line in iter(lambda: stdout.readline(2048), ""):
            print_info(line)
            out = out + line
            if self.logfile:
                self.log.write(line)
                self.log.flush()

        return out, stderr

    def get_response(self, command, timeout=None):
        """Execute a command using the paramiko SSH object and returns
           the response string

          :Arguments:
               1. command - commnad to be executed
               2. timeout - wait for response

          :Returns:
              1. status(bool)= True / False
              2. out/err = response string
        """
        out, stderr = self.ssh_exec(command, timeout)
        err = stderr.read()
        if out:
            return True, out
        else:
            print_error("Error:", err)
            return False, err

    def verify_response(self, command, exp_string, fail_resp, timeout=None):
        """Execute a command using the paramiko SSH object and returns
           the response string

           :Arguments:
               1. command - command to be executed
               2. exp_string - String to be expected
               3. fail_resp - Failure response to be expected
               4. timeout - wait for response

          :Returns:
               1. status(bool)= True / False
               2. out/err = response string
        """
        out, stderr = self.ssh_exec(command, timeout)
        err = stderr.read()
        if out and ((exp_string in out) and (fail_resp not in out)):
            print_info("Output:", out)
            return True, out
        elif out and ((exp_string not in out) or (fail_resp in out)):
            print_info("Error:", out)
            return False, out
        else:
            print_error("Error:", err)
            return False, err

    def copy_file(self, remotepath, localpath, filename):
        """Get the file from remotepath

        :Argument:
             1. remotepath - File path in the remote server
             2. localpath - Local path to save the file
             3. filename - Filename of the file to be tranferred

        :Returns:
             1. status(bool)= True / False
        """
        sftpobj = self.sshobj.open_sftp()
        print_info("Copying {} from {} to {}".format(filename, remotepath,
                                                     localpath))
        if filename:
            remotepath = os.path.join(remotepath, filename)
            localpath = os.path.join(localpath, filename)
        sftpobj.get(remotepath, localpath)
        if os.path.isfile(localpath):
            return True
        else:
            return False

    def send_testdata_cmds(self, testdatafile, **args):
        """
        - Parses the testdata file and
          - gets the command details for rows marked execute=yes (or)
          - gets the command details for rows marked execute=yes and row=str_rownum (or)
          - gets the command details for rows marked execute=yes and title=strtitle
        - Sends the obtained commands to the paramiko session.
        - If the commands have verification attribute set,
        then verifies the verification text for presence/absence as defined
        in the respective found attribute in the testdatfile.

        :Arguments:
            1. testdatafile = the xml file where command details are available
            2. str_rownum = row number of testdata command block to be searched for
               in the testdata file
            3. strtitle = title of testdata command block title to be searched
               for in the testdata file
        :Returns:
            1. finalresult = boolean
        """
        finalresult = True
        varconfigfile = args.get('varconfigfile', None)
        title = args.get('title', None)
        row = args.get('row', None)
        details_dict = data_Utils.get_command_details_from_testdata(testdatafile, varconfigfile, title=title, row=row)
        command_list = details_dict["command_list"]
        stepdesc = "Send the following commands: %s" %command_list
        testcase_Utils.pNote(stepdesc)
        if command_list == False:
            finalresult = False
            command_list = []
        intsize = len(command_list)
        # Send Commands
        for i in range(0, intsize):
            command = details_dict["command_list"][i]
            startprompt = details_dict["startprompt_list"][i]
            endprompt = details_dict["endprompt_list"][i]
            cmd_timeout = details_dict["timeout_list"][i]
            retry = details_dict["retry_list"][i]
            retry_timer = details_dict["retry_timer_list"][i]
            retry_onmatch = details_dict["retry_onmatch_list"][i]
            retry_count = details_dict["retry_count_list"][i]
            sleeptime = details_dict["sleeptime_list"][i]
            verify_text_list = details_dict["verify_text_list"][i]
            verify_context_list = details_dict["verify_context_list"][i]
            sleep = {None: 0, "":0, "none":0}.get(str(sleeptime).lower(), str(sleeptime))
            sleep = int(sleep)
            print("\n")
            print_debug(">>>")
            testcase_Utils.pNote("Command #{0}\t: {1}".format(str(i+1), command))
            testcase_Utils.pNote("startprompt\t: {0}".format(startprompt))
            testcase_Utils.pNote("endprompt\t: {0}".format(endprompt))
            testcase_Utils.pNote("sleeptime\t: {0}".format(sleep))        
            result, response = self.get_response(command_list[i])
            if result and result is not 'ERROR':
                if verify_text_list is not None:
                    result = data_Utils.verify_cmd_response(verify_text_list, verify_context_list,
                                                            command, response, varconfigfile)
            command_status = {True: "Pass", False:"Fail", "ERROR":"ERROR"}.get(result)
            print_info("Command status: {0}".format(command_status))
            print_debug("<<<")
            if sleep > 0:
                testcase_Utils.pNote("Sleep time of '{0} seconds' requested post command execution".format(sleep))
                time.sleep(sleep)        
            if result == "ERROR" or finalresult == "ERROR":
                result = "ERROR"
                finalresult = "ERROR"        
            finalresult = finalresult and result
        return finalresult

    def download_remote_file_sftp(self, remotepath, localpath, filename, \
                                remotehost, username, password, port=22):
        """Downloads a remote file from the remote server to
        the localpath using SFTP

        :Arguments:
            1. remotepath (string) = the remote path to download the file from remotehost
            2. localpath (string) = the local path on the local host
            3. filename (string) = name of the remote file to download
            4. remotehost (string) = remote host
            5. username (string) = remote login username
            6. password (string) = remote login password

        :Returns:
            1. status(bool)
        """
        status = False
        transport = self.param.Transport((remotehost, port))
        transport.connect(username=username, password=password)
        sftp = self.param.SFTPClient.from_transport(transport)

        if filename:
            try:
                sftp.get(remotepath + filename, localpath + filename)
                if os.path.isfile(localpath + filename):
                    print_info("Downloading file from remote server successful")
                    status = True
                else:
                    print_info("Downloading file from remote server failed")
            except Exception as exception:
                print_exception(exception)

            finally:
                sftp.close()
                transport.close()

        return status

    def invoke_shell(self, term='vt100'):
        """Opens a terminal for the SSH session
           :Argument:
             1. term = Type of terminal, default:vt100

           :Returns:
             True: if successful
             False: if unsuccessful
        """
        try:
            print_info("Opening shell...")
            self.sshobj.invoke_shell(term=term)
            return True

        except self.param.SSHException:
            print_error("Invoke shell Unsuccessful")
            return False

    def connect_target_via_host(self, target, user, auth, invoke_shell=False,
                                log=None):
        """Forward the SSH connection to another target client
           :Argument:
             1. target(string) - Name/ip target machine to be connected
             2. user - username to connect
             3. auth - password for the user
             4. invoke_shell - open shell for passing commands

           :Returns:
             1. target_session - Session object for target connection
             2. status(bool)= True / False

        """
        target_session = SSHComm(target, uid=user, pid=auth, logfile=log)
        status = False
        try:
            ssh_transport = self.sshobj.get_transport()


            channel = ssh_transport.open_channel("direct-tcpip", (target, 22),
                                                 ('localhost', 0))
            print_info("Connecting to target: {}".format(target))
            target_session.sshobj.set_missing_host_key_policy(\
                                       self.param.AutoAddPolicy())
            target_session.sshobj.connect(target, port=22, username=user,
                                          password=auth, sock=channel)
            if target_session.logfile:
                target_session.log = open(self.logfile, 'w')
            print_info("Connection to target: {}successful".format(target))
            if invoke_shell:
                print_info("Opening shell for {}".format(target))
                target_session.invoke_shell()

            status = True

        except self.param.SSHException as exception:
            print_exception(exception)

        except Exception as exception:
            print_exception(exception)

        return target_session, status
