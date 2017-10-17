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

"""Warrior Network File operations module """

import re
from Framework.ClassUtils.WNetwork.base_class import Base
from Framework.Utils import cli_Utils, file_Utils
from Framework.Utils.testcase_Utils import pNote


class FileOps(Base):
    """Warrior File operations class """

    def __init__(self, *args, **kwargs):
        """ Constructor """
        super(FileOps, self).__init__(*args, **kwargs)

    @staticmethod
    def ftp_put_from_remote(session_object, filename):
        """For ftping the file to destination
        Assumes a ftp session is already present

        :Arguments:
            1. session_object-session object to be used
            2. filename(string) - filename string

        :Returns
            1. status(bool) - True/False

        """
        _, output = session_object.send_command(".*", ">", "put {}".format(filename))
        if output.find("226 Transfer complete"):
            status = True
            pNote("successfully put file from dest")
        else:
            status = False

        return status

    @staticmethod
    def sftp_get_from_remote(session_object, filename, filedir):
        """For Fetching the file from destination
        Assumes a sftp session is already present

        :Arguments:
            1. session_object-session object to be used
            2. filename(string) - filename string
            3. filedir(string) - directory path of the file

        :Returns
            1. status(bool) - True/False

        """
        _, output = session_object.send_command(".*", ">", "get {}".format(filename))
        if output.find("Fetching {0} to {1}".format(filedir + "/" + filename, filename)):
            status = True
            pNote("successfully got file from dest")
        else:
            status = False

        return status

    @staticmethod
    def sftp_put_from_remote(session_object, filename, filedir):
        """For sftping the file to destination
        Assumes a sftp session is already present

        :Arguments:
            1. session_object-session object to be used
            2. filename(string) - filename string
            3. filedir(string) - directory path of the file

        :Returns
            1. status(bool) - True/False

         """
        _, output = session_object.send_command(".*", ">", "put {}".format(filename))
        if output.find("Uploading {0} to {1}".format(filename, filedir+"/"+filename)):
            status = True
            pNote("successfully put file from dest")
        else:
            status = False

        return status

    @staticmethod
    def ftp_get_from_remote(session_object, filename):
        """For fetching the file from destination
        Assumes a ftp session is already present

        :Arguments:
            1. session_object-session object to be used
            2. filename(string) - filename string

        :Returns
            1. status(bool) - True/False

         """

        # To check Fetching from remote host
        _, output = session_object.send_command(".*", ">", "get {}".format(filename))
        if output.find("226 Transfer complete"):
            status = True
            pNote("successfully got file from dest")
        else:
            status = False

        return status

    @staticmethod
    def get_file_size(session_object, prompt, filename, session=None):
        """
        To get file size for a given file
        This assumes you are in the correct directory
        This also handles file size in ftp and sftp prompt

        :Arguments:
            1. session_object = session object to be used
            2. prompt(string) = prompt expected
            2. filename(string) = filename string
            3. session(string) = ftp/sftp/others

        :Returns
            1. status(bool) = True/False

         """
        if session == "ftp":

            command = "ls {} ".format(filename)
            _, output = session_object.send_command(".*", ">", command)
            size1 = ([line for line in output.split("\n")
                      if filename in line][1].split(" "))
            size = [line for line in size1 if line != ""][4]

        elif session == "sftp":

            command = "ls -l {} ".format(filename)
            _, output = session_object.send_command(".*", ">", command)
            size1 = output.split("\n")[1].split(" ")
            size = [line for line in size1 if line != ""][4]
        else:

            command = "ls -l {} | awk '{{print $5}}'".format(filename)
            _, output = session_object.send_command(".*", prompt, command)
            # to remove discrepancy between solaris and linux
            output_list = [output.replace('\r', '')
                           for output in output.split("\n")
                           if command not in output]
            size = output_list[0]

        pNote("File:{0} size found to be:{1}".format(filename, str(size)))
        return size

    @staticmethod
    def file_exists_on_remote(session_object, prompt, filename):
        """
        To check file exists
        This assumes you are in the correct directory

        :Arguments:
            1. session_object = session object to be used
            2. prompt(string) = prompt expected
            3. filename(string) = filename string

        :Returns
            1. status(bool) = True/False

        """
        status = False
        command = "ls -l {}".format(filename)
        _, output = session_object.send_command(".*", prompt, command)
        if output.find("No such file or directory") >= 0:
            pNote("File:{} not  found".format(filename), "error")
        else:
            status = True

        return status

    @staticmethod
    def start_ftp_on_remote(session_object, command, username, password):
        """ To start ftp connection on remote machine

        :Arguments:
            1. session_object = session object to be used
            2. command(string) = ftp command
            2. username(string) = username
            3. password(string) = password

        :Returns
            1. status(bool) = True/False

        """
        session_object.send_command(".*", ":", command)
        session_object.send_command(".*", ":", username)
        status, response = session_object.send_command(".*", ">", password)
        if status and "Login successful" in response:
            status = True
            pNote("ftp session established successfully")
        else:
            status = False
            pNote("ftp session cannot be established", "error")
        return status

    @staticmethod
    def start_sftp_on_remote(session_object, command, password, prompt):
        """ To start sftp connection on remote machine

        :Arguments:
            1. session_object = session object to be used
            2. command(string) = sftp command
            3. username(string) = username
            4. password(string) = password
            5. prompt(string) = prompt in source system

        :Returns
            1. status(bool) = True/False

        """
        status, response = session_object.send_command(".*", "password:|>", command)

        if re.search('.*(?i)remote host identification has changed.*', response):
            line_del = re.search('Offending key in .*?:(\d+)', response).group(1)

            ssh_key_remove = "sed '"+line_del+"d' ~/.ssh/known_hosts> /tmp/temp "\
                             "&& mv -f /tmp/temp  ~/.ssh/known_hosts"

            status, _ = session_object.send_command(".*", prompt, ssh_key_remove)

            status, response = session_object.send_command(".*", "password:|>", command)
        if re.search('(yes/no)', response):
            status, _ = session_object.send_command(".*", '.*(?i)password.*', 'yes')
            if status is not True:
                status, response = session_object.send_command(".*", "password:|>", command)

        status, _ = session_object.send_command(".*", ">", password)
        if status is True:
            pNote("sftp session established successfully")
        else:
            status = False
            pNote("sftp session cannot be established", "error")
        return status

    @classmethod
    def ftp_from_remotehost(cls, session_object, ip_type, ftp_operation,
                            filepath, prompt, dest_address, username, password,
                            filepath_dest):
        """ftp(test both put and get).This keyword can be used to transfer
        file from source _system to destination system or vice versa.
        It checks the size after transfer in both get and put.

        :Arguments:
            1. session_object(string)  = name of the Linux machine on which\
                                      to execute
            2. ip_type(string) = iptype of the dest system through \
                                 which it needs to be connected.
                                 needs to be one of \
                                 (ip/ipv4/dns/lmp_ip/lmp_ipv6).It has to be \
                                 present in the input data file.
            3. ftp_operation(string) = get/put/both
            4. filepath(string) = file with filepath in source\
                                  system(used for put)
            5. prompt(string)  = prompt of the source system
            6. dest_address(string) = ipv4 address or defaulted to lcn ip
            7. username(string) = username of the dest system
            8. password(string) = password of the dest system
            9. filepath_dest(string) = file with filepath in destination\
                               system(used for get)
        :Returns:
            1. bool (True/False)

        """
        put = True if ("put" in ftp_operation or "both" in ftp_operation) \
            else False
        get = True if ("get" in ftp_operation or "both" in ftp_operation) \
            else False

        status_get = False if get else True
        status_put = False if put else True

        ftp_cmd = "ftp"
        if ip_type == "ipv6":
            ftp_cmd = "ftp6"

        filedir, filename = (file_Utils.getDirName(filepath),
                             file_Utils.getFileName(filepath))
        filedir_dest, filename_dest = (file_Utils.getDirName(filepath_dest),
                                       file_Utils.getFileName(filepath_dest))

        command = ftp_cmd + " [{}]".format(dest_address)
        # move into the path
        session_object.send_command(".*", prompt, "cd {}".format(filedir))

        # check whether file is available
        putfilepresent = cls.file_exists_on_remote(session_object, prompt,
                                                   filename)
        if putfilepresent:
            # check the put file size
            put_file_size = cls.get_file_size(session_object, prompt, filename)

        else:
            pNote("Specified put file:{} not found".format(filename), "error")

        # Starting the ftp connection
        status = cls.start_ftp_on_remote(session_object, command,
                                         username, password)
        if status:
            session_object.send_command(".*", ">", "cd {}".format(filedir_dest))

            if putfilepresent and put:
                status_put = cls.ftp_put_from_remote(session_object, filename)
                put_file_size_transf = cls.get_file_size(session_object, ">",
                                                         filename,
                                                         session="ftp")
                if status_put:
                    pNote("Actual put file size:{0} Transferred put file size"
                          ":{1}".format(str(put_file_size), str(put_file_size_transf)))
                    if str(put_file_size) == str(put_file_size_transf):
                        status_put = True
                        pNote("Transferred put file size matches the origin")
                    else:
                        status_put = False
                        pNote("Transferred put file size does not"
                              "match the origin")

            if get:
                # check whether file is available
                getfilepresent = cls.file_exists_on_remote(session_object, ">",
                                                           filename_dest)

                if getfilepresent:
                    gfile_size = cls.get_file_size(session_object, ">",
                                                   filename_dest,
                                                   session="ftp")
                    status_get = cls.ftp_get_from_remote(session_object,
                                                         filename_dest)

                    # exiting the ftp terminal
                    session_object.send_command(".*", prompt, "exit")

                    if status_get:
                        # check the get file size after transfer
                        gfile_size_transf = cls.get_file_size(session_object,
                                                              prompt,
                                                              filename_dest)

                        pNote("Actual get file size:{0} Transferred get file"
                              "size:{1}".format(str(gfile_size), str(gfile_size_transf)))
                        if str(gfile_size) == str(gfile_size_transf):
                            status_get = True
                            pNote("Transferred get file size matches the origin")
                        else:
                            status_get = False
                            pNote("Transferred get file size matches the origin")
                else:
                    pNote("Specified get file:{} not found".format(filename_dest),
                          "error")

            else:
                session_object.send_command(".*", prompt, "exit")

            status = status_get and status_put
        else:
            status = False
        return status

    @classmethod
    def sftp_from_remotehost(cls, session_object, ip_type, sftp_operation, port,
                             filepath, prompt, dest_address, username,
                             password, filepath_dest):
        """sftp(test both put and get).This keyword can be used to transfer
        file from source _system to destination system or vice versa.
        It checks the size after transfer in both get and put.

        :Arguments:
            1. session_object(string)  = name of the Linux machine on which\
                                      to execute
            2. ip_type(string) = iptype of the dest system through \
                                 which it needs to be connected.
                                 needs to be one of \
                                 (ip/ipv4/dns/lmp_ip/lmp_ipv6).It has to be \
                                 present in the input data file.
            3. sftp_operation(string) = get/put/both
            4. port(string) = source port
            5. filepath(string) = file with filepath in source\
                                  system(used for put)
            6. prompt(string)  = prompt of the source system
            7. dest_address(string) = ipv4 address or defaulted to lcn ip
            8. username(string) = username of the dest system
            9. password(string) = password of the dest system
            9. filepath_dest(string) = file with filepath in destination\
                               system(used for get)
        :Returns:
            1. bool (True/False)

        """
        put = True if ("put" in sftp_operation or "both" in sftp_operation) \
            else False
        get = True if ("get" in sftp_operation or "both" in sftp_operation) \
            else False

        status_get = False if get else True
        status_put = False if put else True

        filedir, filename = (file_Utils.getDirName(filepath),
                             file_Utils.getFileName(filepath))
        filedir_dest, filename_dest = (file_Utils.getDirName(filepath_dest),
                                       file_Utils.getFileName(filepath_dest))

        sftp_cmd = "sftp"
        if ip_type == "ipv6":
            sftp_cmd = "sftp6"

        # move into the path
        session_object.send_command(".*", prompt, "cd {}".format(filedir))
        command = sftp_cmd + "  -oPort={0} {1}@{2}".format(port, username,
                                                           dest_address)

        # check whether file is available
        putfilepresent = cls.file_exists_on_remote(session_object, prompt,
                                                   filename)
        if putfilepresent:
            # check the put file size
            put_file_size = cls.get_file_size(session_object, prompt, filename)

        else:
            pNote("Specified put file:{} not found".format(filename), "error")

        # Starting the sftp connection
        status = cls.start_sftp_on_remote(session_object, command,
                                          password, prompt)
        if status:
            session_object.send_command(".*", ">", "cd {}".format(filedir_dest))

            if putfilepresent and put:
                status_put = cls.sftp_put_from_remote(session_object,
                                                      filename, filedir)
                put_file_size_transf = cls.get_file_size(session_object, ">",
                                                         filename,
                                                         session="sftp")
                if status_put:
                    pNote("Actual put file size:{0} Transferred put file size"
                          ":{1}".format(str(put_file_size), str(put_file_size_transf)))
                    if str(put_file_size) == str(put_file_size_transf):
                        status_put = True
                        pNote("Transferred put file size matches the origin")
                    else:
                        status_put = False
                        pNote("Transferred put file size does not"
                              "match the origin")

            if get:
                # check whether file is available
                getfilepresent = cls.file_exists_on_remote(session_object, ">",
                                                           filename_dest)

                if getfilepresent:
                    gfile_size = cls.get_file_size(session_object, ">",
                                                   filename_dest,
                                                   session="sftp")
                    status_get = cls.sftp_get_from_remote(session_object,
                                                          filename_dest,
                                                          filedir_dest)

                    # exiting the sftp terminal
                    session_object.send_command(".*", prompt, "exit")

                    if status_get:
                        # check the get file size after transfer
                        gfile_size_transf = cls.get_file_size(session_object,
                                                              prompt,
                                                              filename_dest)

                        pNote("Actual get file size:{0} Transferred get file"
                              "size:{1}".format(str(gfile_size), str(gfile_size_transf)))
                        if str(gfile_size) == str(gfile_size_transf):
                            status_get = True
                            pNote("Transferred get file size matches the origin")
                        else:
                            status_get = False
                            pNote("Transferred get file size matches the origin")
                else:
                    pNote("Specified get file:{} not found".format(filename_dest),
                          "error")

            else:
                session_object.send_command(".*", prompt, "exit")

            status = status_get and status_put
        else:
            status = False
        return status

