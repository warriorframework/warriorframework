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

""" Keywords related to File operations """

import Framework.Utils as Utils
from Framework.ClassUtils.WNetwork.file_ops import FileOps
class FileOpsActions(object):
    """File operations keyword class """

    def __init__(self):
        """ Constructor """
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.fileops = FileOps()

    def ftp_from_remotehost(self, system_name, session_name=None,
                            dest_system=None, ftp_operation="both",
                            ip_type="ip"):
        """ftp(test both put and get).This keyword can be used to transfer
        file from source _system to destination system or vice versa.
        It checks the size after transfer in both get and put.

        :Datafile usage:
            Tags or attributes to be used in input datafile for the system
            or subsystem.If both tag and attribute is provided the attribute
            will be used.

            1. prompt = prompt of the source system
            2. filepath = file with filepath in source system(used for put)
            3. ip = ipv4 address or defaulted to lcn ip
            4. ipv6 = ipv6 address or defaulted to lcn ipv6
            5. dns = dns name
            6. lmp_ip = ipv4 address of lmp port of dut
            7. lmp_ipv6 = ipv6 address of lmp port of dut
            8. username = username of the dest system
            9. password = password of the dest system
            10. filepath = file with filepath in destination system \
                           (used for get)
            note: one of <ip>,<ipv6>,<dns>,<lmp_ip>,<lmp_ipv6> tags specified in
                  ip_type argument is sufficient to be present in inputdatafile

        :Arguments:
            1. system_name(string)  = name of the Linux machine on which\
                                      to execute
            2. session_name(string) = name of the session
            3. dest_system(string) = names of the destination system
            4. ftp_operation(string) = get/put/both
            6. ip_type(string) = iptype of the dest system through \
                                 which it needs to be connected.
                                 needs to be one of \
                                 (ip/ipv4/dns/lmp_ip/lmp_ipv6).It has to be \
                                 present in the input data file.

        :Returns:
            1. bool (True/False)

        """
        wdesc = "ftp file from and to dest_system"
        Utils.testcase_Utils.pSubStep(wdesc)
        Utils.testcase_Utils.pNote(system_name)
        Utils.testcase_Utils.pNote(self.datafile)

        keys_for_credentials = [ip_type, "username",
                                "password", "filepath"]

        credentials_dest = Utils.data_Utils.get_credentials(self.datafile,
                                                            dest_system,
                                                            keys_for_credentials
                                                           )
        credentials = Utils.data_Utils.get_credentials(self.datafile,
                                                       system_name,
                                                       ["filepath",
                                                        "prompt"])

        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        session_object = Utils.data_Utils.get_object_from_datarepository(session_id)
        if session_object:
            command_status = self.fileops.ftp_from_remotehost(session_object, ip_type,
                                                              ftp_operation,
                                                              credentials["filepath"],
                                                              credentials["prompt"],
                                                              credentials_dest[ip_type],
                                                              credentials_dest["username"],
                                                              credentials_dest["password"],
                                                              credentials_dest["filepath"])
            status = command_status
        else:
            Utils.testcase_Utils.pNote(("%s-%s is not available for use" %
                                        system_name, session_name), "warning")
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        return status

    def sftp_from_remotehost(self, system_name, session_name=None,
                             dest_system=None, sftp_operation="both",
                             port="1022", ip_type="ip"):
        """sftp(test both put and get).This keyword can be used to transfer
        file from source _system to destination system or vice versa.
        It checks the size after transfer in both get and put.

        :Datafile usage:
            Tags or attributes to be used in input datafile for the system
            or subsystem.If both tag and attribute is provided the attribute
            will be used.

            1. prompt = prompt of the source system
            2. filepath = file with filepath in source system(used for put)
            3. ip = ipv4 address or defaulted to lcn ip
            4. ipv6 = ipv6 address or defaulted to lcn ipv6
            5. dns = dns name
            6. lmp_ip = ipv4 address of lmp port of dut
            7. lmp_ipv6 = ipv6 address of lmp port of dut
            8. username = username of the dest system
            9. password = password of the dest system
            10. filepath = file with filepath in destination system(used for get)
            note: one of <ip>,<ipv6>,<dns>,<lmp_ip>,<lmp_ipv6> tags specified in
                  ip_type argument is sufficient to be present in inputdatafile

        :Arguments:
            1. system_name(string)  = name of the Linux machine on which\
                                      to execute
            2. session_name(string) = name of the session
            3. dest_system(string) = names of the destination system
            4. ftp_operation(string) = get/put/both
            5. ip_type(string) = iptype of the dest system through \
                                 which it needs to be connected.
                                 needs to be one of \
                                 (ip/ipv4/dns/lmp_ip/lmp_ipv6).It has to be \
                                 present in the input data file.

        :Returns:
            1. bool (True/False)

        """
        wdesc = "sftp file from and to dest_system"
        Utils.testcase_Utils.pSubStep(wdesc)
        Utils.testcase_Utils.pNote(system_name)
        Utils.testcase_Utils.pNote(self.datafile)

        keys_for_credentials = [ip_type, "username",
                                "password", "filepath"]

        credentials_dest = Utils.data_Utils.get_credentials(self.datafile,
                                                            dest_system,
                                                            keys_for_credentials
                                                           )

        credentials = Utils.data_Utils.get_credentials(self.datafile,
                                                       system_name,
                                                       ["filepath",
                                                        "prompt"])

        session_id = Utils.data_Utils.get_session_id(system_name, session_name)
        session_object = Utils.data_Utils.get_object_from_datarepository(session_id)
        if session_object:
            command_status = self.fileops.sftp_from_remotehost(session_object,
                                                               ip_type, sftp_operation,
                                                               port, credentials["filepath"],
                                                               credentials["prompt"],
                                                               credentials_dest[ip_type],
                                                               credentials_dest["username"],
                                                               credentials_dest["password"],
                                                               credentials_dest["filepath"])
            status = command_status
        else:
            Utils.testcase_Utils.pNote(("%s-%s is not available for use" %
                                        system_name, session_name), "warning")
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        return status
