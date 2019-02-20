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

"""
Implementation of the standard SNMP protocol commands for SNMP v1 and v2c and V3
and IPv6 support added.
SNMP v3 Trap and Inform support added. 
"""
import os, re, ast
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_exception
from Framework.ClassUtils.snmp_utlity_class import WSnmp as ws
from Framework.Utils import testcase_Utils, config_Utils, data_Utils, snmp_utils
from threading import Thread
from time import sleep
import Queue
try:
    from pysnmp.entity.rfc3413 import ntfrcv
    from pysnmp.smi import builder, view, compiler, rfc1902, error
except ImportError:
    testcase_Utils.pNote("Please Install PYSNMP 4.3.8 or Above", "error")


class CommonSnmpActions(object):
    """
    Class for standard SNMP protocol commands

    """

    def __init__(self):
        """
        This is intialization
        """
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.snmpver = {'1':'0', '2':'1', '2c':'1', '3':'2'}

    def snmp_get(self, snmp_ver, system_name, mib_name=None,
                 mib_index=None, mib_value=None,
                 oid_string=None, communityname=None,
                 snmp_timeout=60,
                 userName=None, authKey=None, privKey=None, authProtocol=None,
                 privProtocol=None,
                 custom_mib_paths=None,
                 load_mib_modules=None):
        """
        snmp_get uses the SNMP GET request to query for information on a
        network entity
        :Datafile usage:
            1.(string) Agents IP address. address="192.168.1.68"
            2.(string) SNMP UDP port. port="161"
        :Arguments:
            1.communityname : SNMP v1/v2c community string. e.g. 'public'
            2. snmp_ver: Support for v1 and V2 and V3 1 for v1, 2 for V2, 3 for V3
            3.mib_name : Name of the Management Information Base e.g. 'IF-MIB'
            4.mib_index: MIB index name e.g. 'ipAdEntAddr'
            5.mib_value: e.g. '127.0.0.1'
            6.oid_string: object identifiers (OIDs) that are available on the
                      managed device.
                      e.g. '1.3.6.1.2.1.2.2.1.6' which is, ifPhysAddress
                      The physical address of the interface.
           User can provide either MIB or oid_string.
            7.system_name(string) = Name of the system from the input datafile
            8.snmp_timeout: Number of seconds the SNMP manager will wait for a
            responce from SNMP Agent. In case of SNMP walk the may need to
            set to higher.
            #arguments 9-13 are only for SNMPv3 or mpModel = 2 and in that
            # case communityname will be None
            9.userName(string) = A human readable string representing the
                                  name of the SNMP USM user.
                                  e.g. 'usr1'
            10.authKey(string) = Initial value of the secret authentication key.
                                 e.g. 'authkey1'
            11.privKey(string) = Initial value of the secret encryption key.
                                 e.g. 'privkey1'
            12.authProtocol(string) = An indication of whether messages sent on behalf of
                              this USM user can be authenticated, and if so, the type of
                              authentication protocol which is used.
                              supported protocols: usmNoAuthProtocol,
                              usmHMACMD5AuthProtocol, usmHMACSHAAuthProtocol
                              authProtocol="1,3,6,1,6,3,10,1,1,2"
            13.privProtocol(string) = An indication of whether messages sent on behalf
                              of this USM user be encrypted, and if so,
                              the type of encryption protocol which is used.
                              supported usmNoPrivProtocol(default),
                              usmDESPrivProtocol, usm3DESEDEPrivProtocol, usmAesCfb128Protocol
                              e.g. privProtocol="1,3,6,1,6,3,10,1,2,2"
            14.custom_mib_paths: User can provide multiple MIB source path seperated by comma (',')
                      Source path can be url or just absolute directory path. Refer bellow example.
                      e.g. 'http://<URL>/@mib@, /data/users/MIBS/'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            15.load_mib_modules: User can provide the MIBS(name) need to be loaded
                      from the path "custom_mib_path".
                      It is a string of MIB names separated by comma(',')
        :Return:
            status(bool)= True / False.
            output_dict = consists of following key value:
            1.errindication: If this string is not empty, it indicates the SNMP
                            engine error.
            2.errstatus: If this element evaluates to True, it indicates an
                        error in the SNMP communication.Object that generated
                        the error is indicated by the errindex element.
            3.errindex: If the errstatus indicates that an error has occurred,
                        this field can be used to find the SNMP object that
                        caused the error. The object position in the result
                        array is errindex-1.
            4.result: This element contains a list of all returned SNMP object
                      elements. Each element is a tuple that contains the name
                      of the object and the object value.
        """

        wdesc = "Executing SNMP GET command"
        Utils.testcase_Utils.pSubStep(wdesc)
        status = False
        snmp_parameters = ['ip', 'snmp_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ipaddr = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_port')

        output_dict = {}
        temp_custom_mib_paths = None

        wsnmp = ws(communityname, self.snmpver.get(snmp_ver), ipaddr, port, snmp_timeout,
                   userName, authKey, privKey, authProtocol,
                   privProtocol)
        cmdgen = wsnmp.commandgenerator()
        if self.snmpver.get(snmp_ver) is '2':# for ssnmp v3
            auth_data = wsnmp.usmuserdata()
        else:                              #for snmp v1 or v2c
            auth_data = wsnmp.communitydata()
        if ':' in ipaddr:#for ipv6
            transport = wsnmp.udp6transporttarget()
        else:    #for ipv4
            transport = wsnmp.udptransporttarget()
        if custom_mib_paths:
            temp_custom_mib_paths = snmp_utils.split_mib_path(custom_mib_paths)

        if oid_string == None and mib_name == None:
            testcase_Utils.pNote("Please provide OID or MIB Information!", "error")
        if oid_string:
            oid = tuple([int(e) if e.isdigit() else e for e in oid_string.split('.')])
        else:
            if custom_mib_paths:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).\
                    addAsn1MibSource(*temp_custom_mib_paths)
            else:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value)
        try:
            errindication, errstatus,\
            errindex, result = cmdgen.getCmd(auth_data, transport, oid)
            output_dict = {
                '{0}_errindication'.format(system_name):errindication,
                '{0}_errstatus'.format(system_name):errstatus,
                '{0}_errindex'.format(system_name):errindex,
                '{0}_result'.format(system_name):result,
                '{0}_custom_mib_paths'.format(system_name):temp_custom_mib_paths,
                '{0}_load_mib_modules'.format(system_name):load_mib_modules
            }
            if result != []:
                status = True
                testcase_Utils.pNote("Successfully executed SNMP GET command {}"
                                     .format(result), "info")
            else:
                testcase_Utils.pNote("Failure SNMP Command Return Null Value! {}"
                                     .format(result), "error")

        except wsnmp.exception as excep:
            status = False
            testcase_Utils.pNote("SNMP GET command Failed!\n{}".format(excep), "error")

        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def snmp_getnext(self, snmp_ver, system_name, mib_name=None,
                     mib_index=None, mib_value=None,
                     oid_string=None, communityname=None,
                     snmp_timeout=60, max_rows=1,
                     userName=None, authKey=None, privKey=None, authProtocol=None,
                     privProtocol=None, custom_mib_paths=None, load_mib_modules=None):
        """
        snmp_get_next uses the SNMP GETNEXT request to query for information
        on a network entity
        :Datafile usage:
            1.(string) Agents IP address. address="192.168.1.68"
            2.(string) SNMP UDP port. port="161"
        :Arguments:
            1.communityname : SNMP v1/v2c community string. e.g. 'public'
            2. snmp_ver: Support for v1 and V2 and V3 1 for v1, 2 for V2, 3 for V3
            3.mib_name : Name of the Management Information Base e.g. 'IF-MIB'
            4.mib_index: MIB index name e.g. 'ipAdEntAddr'
            5.mib_value: e.g. '127.0.0.1'
            6.oid_string: object identifiers (OIDs) that are available on the
                      managed device.
                      e.g. '1.3.6.1.2.1.2.2.1.6' which is, ifPhysAddress
                      The physical address of the interface.
           User can provide either MIB or oid_string.
            7. system_name(string) = Name of the system from the input datafile
            8. snmp_timeout: Number of seconds the SNMP manager will wait for a
            responce from SNMP Agent. In case of SNMP walk the may need to
            set to higher.
            9.max_rows = By default its value is one if user wants to change the
            no of get next message from the given OID or MIB value they can change it with
            different no.
            #arguments 9-13 are only for SNMPv3 or mpModel = 2 and in that
            # case communityname will be None
            10.userName(string) = A human readable string representing the
                                  name of the SNMP USM user.
                                  e.g. 'usr1'
            11.authKey(string) = Initial value of the secret authentication key.
                                 e.g. 'authkey1'
            12.privKey(string) = Initial value of the secret encryption key.
                                 e.g. 'privkey1'
            13.authProtocol(string) = An indication of whether messages sent on behalf of this
                              USM user can be authenticated, and if so, the type of
                              authentication protocol which is used.
                              supported protocols: usmNoAuthProtocol,
                              usmHMACMD5AuthProtocol, usmHMACSHAAuthProtocol
                              authProtocol='1,3,6,1,6,3,10,1,1,2'
            14.privProtocols(string) = An indication of whether messages sent on behalf
                              of this USM user be encrypted, and if so,
                              the type of encryption protocol which is used.
                              supported usmNoPrivProtocol(default),
                              usmDESPrivProtocol, usm3DESEDEPrivProtocol, usmAesCfb128Protocol
                              e.g. privProtocol='1,3,6,1,6,3,10,1,2,2)'
            15.custom_mib_paths: User can provide multiple MIB source path seperated by comma (',')
                      Source path can be url or just absolute directory path. Refer bellow example.
                      e.g. 'http://<URL>/@mib@, /data/users/MIBS/'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            16.load_mib_module: User can provide the MIBS(name) need to be loaded from the path
                 "custom_mib_path".It is a string of MIB names separated by comma(',')
        :Return:
            status(bool)= True / False.
            output_dict = consists of following key value:
            1.errindication: If this string is not empty, it indicates
                             the SNMP engine error.
            2.errstatus: If this element evaluates to True,it indicates an error
                         in the SNMP communication.Object that generated
                         the error is indicated by the errindex element.
            3.errindex: If the errstatus indicates that an error has occurred,
                        this field can be used to find the SNMP object that
                        caused the error.
                        The object position in the result array is errindex-1.
            4.result: This element contains a list of all returned SNMP object
                      elements. Each element is a tuple that contains the name
                      of the object and the object value.
        """

        wdesc = "Executing SNMP GETNEXT command"
        Utils.testcase_Utils.pSubStep(wdesc)
        status = False
        snmp_parameters = ['ip', 'snmp_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ipaddr = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_port')

        output_dict = {}
        temp_custom_mib_paths = None
        wsnmp = ws(communityname, self.snmpver.get(snmp_ver), ipaddr, port, snmp_timeout,
                   userName, authKey, privKey, authProtocol,
                   privProtocol)
        cmdgen = wsnmp.commandgenerator()
        if self.snmpver.get(snmp_ver) is '2':# for ssnmp v3
            auth_data = wsnmp.usmuserdata()
        else:                              #for snmp v1 or v2c
            auth_data = wsnmp.communitydata()

        if ':' in ipaddr:#for ipv6
            transport = wsnmp.udp6transporttarget()
        else:    #for ipv4
            transport = wsnmp.udptransporttarget()
        if custom_mib_paths:
            temp_custom_mib_paths = snmp_utils.split_mib_path(custom_mib_paths)
        if oid_string == None and mib_name == None:
            testcase_Utils.pNote("Please provide OID or MIB Information!", "error")

        if oid_string:
            oid = tuple([int(e) if e.isdigit() else e for e in oid_string.split('.')])
        else:
            if custom_mib_paths:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).\
                    addAsn1MibSource(*temp_custom_mib_paths)
            else:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value)
        try:
            errindication, errstatus, errindex, \
            result = cmdgen.nextCmd(auth_data,
                                    transport, oid,
                                    ignoreNonIncreasingOid=True, maxRows=int(max_rows),
                                    lookupNames=True, lookupValues=True, lexicographicMode=True)
            #  maxRows=1 will control the mib walk
            output_dict = {
                '{0}_errindication'.format(system_name):errindication,
                '{0}_errstatus'.format(system_name):errstatus,
                '{0}_errindex'.format(system_name):errindex,
                '{0}_result'.format(system_name):result,
                '{0}_custom_mib_paths'.format(system_name):temp_custom_mib_paths,
                '{0}_load_mib_modules'.format(system_name):load_mib_modules}
            if result != []:
                status = True
                testcase_Utils.pNote("Successfully executed SNMP GET-NEXT "
                                     "command {}".format(result), "info")
            else:
                testcase_Utils.pNote("Failure SNMP Command Return Null Value! {} {} {} {} xyz".
                                     format(result, errindication, errstatus, errindex), "error")
        except wsnmp.exception as excep:
            status = False
            testcase_Utils.pNote("SNMP GET-Next command Failed! \n{}".format(excep), "error")

        Utils.testcase_Utils.report_substep_status(status)

        return status, output_dict

    def snmp_walk(self, snmp_ver, system_name, mib_name=None, mib_index=None,
                  mib_value=None, oid_string=None, communityname=None,
                  snmp_timeout=60, userName=None, authKey=None, privKey=None,
                  authProtocol=None, privProtocol=None, custom_mib_paths=None,
                  load_mib_modules=None, lexicographicMode="False"):
        """
        snmp_walk uses the SNMP WALK request to query for information on
        a network entity
        :Datafile usage:
            1.(string) Agents IP address. address="192.168.1.68"
            2.(string) SNMP UDP port. port="161"
        :Arguments:
            1.communityname : SNMP v1/v2c community string. e.g. 'public'
            2. snmp_ver: Support for v1 and V2 and V3 1 for v1, 2 for V2, 3 for V3
            3.mib_name : Name of the Management Information Base e.g. 'IF-MIB'
            4.mib_index: MIB index name e.g. 'ipAdEntAddr'
            5.mib_value: e.g. '127.0.0.1'
            6.oid_string: object identifiers (OIDs) that are available on the
                      managed device.
                      e.g. '1.3.6.1.2.1.2.2.1.6' which is, ifPhysAddress
                      The physical address of the interface.
           User can provide either MIB or oid_string.
            7. system_name(string) = Name of the system from the input datafile
            8. snmp_timeout: Number of seconds the SNMP manager will wait for a
            responce from SNMP Agent. In case of SNMP walk the may need to
            set to higher.
            #arguments 9-13 are only for SNMPv3 or mpModel = 2 and in that
            # case communityname will be None
            9.userName(string) = A human readable string representing the
                                  name of the SNMP USM user.
                                  e.g. 'usr1'
            10.authKey(string) = Initial value of the secret authentication key.
                                 e.g. 'authkey1'
            11.privKey(string) = Initial value of the secret encryption key.
                                 e.g. 'privkey1'
            12.authProtocol(string) = An indication of whether messages sent on behalf of this
                              USM user can be authenticated, and if so, the type of
                              authentication protocol which is used.
                              supported protocols: usmNoAuthProtocol,
                              usmHMACMD5AuthProtocol, usmHMACSHAAuthProtocol
                              authProtocol='1,3,6,1,6,3,10,1,1,2'
            13.privProtocol(string) = An indication of whether messages sent on behalf
                              of this USM user be encrypted, and if so,
                              the type of encryption protocol which is used.
                              supported usmNoPrivProtocol(default),
                              usmDESPrivProtocol, usm3DESEDEPrivProtocol, usmAesCfb128Protocol
                              e.g. privProtocol='1,3,6,1,6,3,10,1,2,2'
            14.custom_mib_paths: User can provide multiple MIB source path seperated by comma (',')
                      Source path can be url or just absolute directory path. Refer bellow example.
                      e.g. 'http://<URL>/@mib@, /data/users/MIBS/'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            15.load_mib_modules: User can provide the MIBS(name) need to be loaded from the path
            "custom_mib_path". It is a string of MIB names separated by comma(',')
            16.lexicographicMode : "True" will return everything under given prefix plus the next table also e.g. if request 1.3.6.1 will also provide 1.3.6.2$
                                   "False" will return only under given prefix. Default its False.
        :Return:
            status(bool)= True / False.
            output_dict = consists of following key value:
            1.errindication: If this string is not empty, it indicates
                             the SNMP engine error.
            2.errstatus: If this element evaluates to True,it indicates an error
                         in the SNMP communication.Object that generated
                         the error is indicated by the errindex element.
            3.errindex: If the errstatus indicates that an error has occurred,
                        this field can be used to find the SNMP object that
                        caused the error.
                        The object position in the result array is errindex-1.
            4.result: This element contains a list of all returned SNMP object
                      elements. Each element is a tuple that contains the name
                      of the object and the object value.
        """

        wdesc = "Executing SNMP WALK command"
        Utils.testcase_Utils.pSubStep(wdesc)
        status = False
        snmp_parameters = ['ip', 'snmp_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ipaddr = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_port')

        output_dict = {}
        temp_custom_mib_paths = None
        wsnmp = ws(communityname, self.snmpver.get(snmp_ver), ipaddr, port, snmp_timeout,
                   userName, authKey, privKey, authProtocol,
                   privProtocol)
        cmdgen = wsnmp.commandgenerator()
        if self.snmpver.get(snmp_ver) is '2':# for snmp v3
            auth_data = wsnmp.usmuserdata()
        else:                              #for snmp v1 or v2c
            auth_data = wsnmp.communitydata()

        if ':' in ipaddr:#for ipv6
            transport = wsnmp.udp6transporttarget()
        else:    #for ipv4
            transport = wsnmp.udptransporttarget()

        if oid_string == None and mib_name == None:
            testcase_Utils.pNote("Please provide OID or MIB Information!", "error")
        if custom_mib_paths:
            temp_custom_mib_paths = snmp_utils.split_mib_path(custom_mib_paths)
        if oid_string: #OID String is optional
            oid = tuple([int(e) if e.isdigit() else e for e in oid_string.split('.')])
        else:
            if custom_mib_paths:
                oid = wsnmp.mibvariable(mib_name, mib_index).\
                    addAsn1MibSource(*temp_custom_mib_paths)
            else:
                oid = wsnmp.mibvariable(mib_name, mib_index)
        try:
            errindication, errstatus, errindex,\
            result = cmdgen.nextCmd(auth_data,
                                    transport,
                                    oid, lexicographicMode=ast.literal_eval(lexicographicMode.
                                                                            capitalize()),
                                    ignoreNonIncreasingOid=True, maxRows=50000,
                                    lookupNames=True, lookupValues=True)
            output_dict = {
                '{0}_errindication'.format(system_name):errindication,
                '{0}_errstatus'.format(system_name):errstatus,
                '{0}_errindex'.format(system_name):errindex,
                '{0}_result'.format(system_name):result,
                '{0}_custom_mib_paths'.format(system_name):temp_custom_mib_paths,
                '{0}_load_mib_modules'.format(system_name):load_mib_modules
            }

            if result != []:
                status = True
                testcase_Utils.pNote("Successfully executed SNMP WALK command {}".
                                     format(result), "info")
            else:
                testcase_Utils.pNote("Failure SNMP Command Return Null Value! {} {} {}".
                                     format(result, errindication.prettyPrint(),
                                            errstatus.prettyPrint()), "error")
        except wsnmp.exception as excep:
            status = False
            testcase_Utils.pNote("SNMP Walk command Failed!\n{}".format(excep), "error")
        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def snmp_bulkget(self, snmp_ver, system_name, mib_name=None,
                     mib_index=None, mib_value=None,
                     oid_string=None, communityname=None,
                     snmp_timeout=60, nonrepeaters='0', maxrepetitions='10',
                     userName=None, authKey=None, privKey=None, authProtocol=None,
                     privProtocol=None, custom_mib_paths=None, load_mib_modules=None,
                     lexicographicMode="False"):
        """
        snmp_bulkget uses the SNMP BULKGET request to query for information on
        a network entity
        :Datafile usage:
            1.(string) Agents IP address. address="192.168.1.68"
            2.(string) SNMP UDP port. port="161"
        :Arguments:
            1.communityname : SNMP v1/v2c community string. e.g. 'public'
            2. snmp_ver: Support for v1 and V2 and V3 1 for v1, 2 for V2, 3 for V3
            3.mib_name : Name of the Management Information Base e.g. 'IF-MIB'
            4.mib_index: MIB index name e.g. 'ipAdEntAddr'
            5.mib_value: e.g. '127.0.0.1'
            6.oid_string: object identifiers (OIDs) that are available on the
                      managed device.
                      e.g. '1.3.6.1.2.1.2.2.1.6' which is, ifPhysAddress
                      The physical address of the interface.
           User can provide either MIB or oid_string.
            7. system_name(string) = Name of the system from the input datafile
            9. snmp_timeout: Number of seconds the SNMP manager will wait for a
            responce from SNMP Agent. In case of SNMP walk the may need to
            set to higher.
            #arguments 9-13 are only for SNMPv3 or mpModel = 2 and in that
            # case communityname will be None
            10.userName(string) = A human readable string representing the
                                  name of the SNMP USM user.
                                  e.g. 'usr1'
            11.authKey(string) = Initial value of the secret authentication key.
                                 e.g. 'authkey1'
            12.privKey(string) = Initial value of the secret encryption key.
                                 e.g. 'privkey1'
            13.authProtocol(string) = An indication of whether messages sent on behalf of this
                              USM user can be authenticated, and if so, the type of
                              authentication protocol which is used.
                              supported protocols: usmNoAuthProtocol,
                              usmHMACMD5AuthProtocol, usmHMACSHAAuthProtocol
                              authProtocol='1,3,6,1,6,3,10,1,1,2'
            14.privProtocol(string) = An indication of whether messages sent on behalf
                              of this USM user be encrypted, and if so,
                              the type of encryption protocol which is used.
                              supported usmNoPrivProtocol(default),
                              usmDESPrivProtocol, usm3DESEDEPrivProtocol, usmAesCfb128Protocol
                              e.g. privProtocol='1,3,6,1,6,3,10,1,2,2'
            15.custom_mib_paths: User can provide multiple MIB source path seperated by comma (',')
                      Source path can be url or just absolute directory path. Refer bellow example.
                      e.g. 'http://<URL>/@mib@, /data/users/MIBS/'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            16.load_mib_modules: User can provide the MIBS(name) need to be loaded from the path "custom_mib_path".
                      It is a string of MIB names separated by comma(',')
            17.lexicographicMode : "True" will return everything under given prefix plus the next table also e.g. if request 1.3.6.1 will also provide 1.3.6.2
                                   "False" will return only under given prefix. Default its False.
            18. maxrepetitions: This specifies the maximum number of iterations over the repeating variables. The default is 10.
            19. nonrepeaters : This specifies the number of supplied variables that should not be iterated over. default is 0
        :Return:
            status(bool)= True / False.
            output_dict = consists of following key value:
            1.errindication: If this string is not empty, it indicates
                             the SNMP engine error.
            2.errstatus: If this element evaluates to True,it indicates an error
                         in the SNMP communication.Object that generated
                         the error is indicated by the errindex element.
            3.errindex: If the errstatus indicates that an error has occurred,
                        this field can be used to find the SNMP object that
                        caused the error.
                        The object position in the result array is errindex-1.
            4.result: This element contains a list of all returned SNMP object
                      elements. Each element is a tuple that contains the name
                      of the object and the object value.
        """

        wdesc = "Executing SNMP BULKGET command"
        Utils.testcase_Utils.pSubStep(wdesc)
        status = False
        snmp_parameters = ['ip', 'snmp_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ipaddr = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_port')

        output_dict = {}
        temp_custom_mib_paths = None

        wsnmp = ws(communityname, self.snmpver.get(snmp_ver), ipaddr, port, snmp_timeout,
                   userName, authKey, privKey,authProtocol,
                   privProtocol)
        cmdgen = wsnmp.commandgenerator()
        if self.snmpver.get(snmp_ver) is '2':# for ssnmp v3
            auth_data = wsnmp.usmuserdata()
        else:                              #for snmp v1 or v2c
            auth_data = wsnmp.communitydata()

        if ':' in ipaddr:#for ipv6
            transport = wsnmp.udp6transporttarget()
        else:    #for ipv4
            transport = wsnmp.udptransporttarget()
        if custom_mib_paths:
            temp_custom_mib_paths = snmp_utils.split_mib_path(custom_mib_paths)
        if oid_string == None and mib_name == None:
            testcase_Utils.pNote("Please provide OID or MIB Information!", "error")

        if oid_string:
            oid = tuple([int(e) if e.isdigit()
                         else e for e in oid_string.split('.')])
        else:
            if custom_mib_paths:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).addAsn1MibSource(*temp_custom_mib_paths)
            else:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value)
        try:
            errindication, errstatus, errindex, \
            result = cmdgen.bulkCmd(auth_data,
                                    transport,
                                    int(nonrepeaters), int(maxrepetitions), oid,
                                    lookupNames=True,
                                    lookupValues=True,
                                    lexicographicMode=ast.literal_eval(lexicographicMode.capitalize()),
                                    maxRows=int(maxrepetitions)
                                    )
            # nonrepeaters(1)(int): One MIB variable is requested in response
            # for the first nonRepeaters MIB variables in request.
            # maxRepetitions(25)(int): maxRepetitions MIB variables are
            # requested in response for each of the remaining MIB variables in
            # the request (e.g. excluding nonRepeaters). Remote SNMP engine may
            # choose lesser value than requested.
            output_dict = {
                           '{0}_errindication'.format(system_name):errindication,
                           '{0}_errstatus'.format(system_name):errstatus,
                           '{0}_errindex'.format(system_name):errindex,
                           '{0}_result'.format(system_name):result,
                           '{0}_custom_mib_paths'.format(system_name):temp_custom_mib_paths,
                           '{0}_load_mib_modules'.format(system_name):load_mib_modules}

            if result != []:
                status = True
                testcase_Utils.pNote("Successfully executed SNMP BULK GET "
                                 "command {}".format(result), "info")
            else:
                testcase_Utils.pNote("Failure SNMP Command Return Null Value! {}".format(result), "error")
        except wsnmp.exception as excep:
            status = False
            testcase_Utils.pNote("SNMP BULK GET command Failed!\n{}".format(excep), "error")

        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def verify_snmp_action(self, system_name, snmp_result, mib_string=None
                           ):
        """
        Will Verify SNMP get/getnext/walk/getbulk actions.
        :Datafile usage:
            NA
        :Arguments:
            1. system_name(string) = Name of the system from the input datafile
            2. mib_string(string) = MIB string
            e.g.'SNMPv2-SMI::enterprises.3861.3.2.100.1.2.0'
            3. result(string) = SNMP Output string
            e.g. '1Finity-T100'
        :Returns:
            1. status(bool)
        """
        wdesc = "Verify the SNMP Action Results"
        Utils.testcase_Utils.pSubStep(wdesc)

        errindication = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_errindication")
        varBindTable = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_result")
        errorstatus = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_errstatus")
        errindex = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_errindex")
        custom_mib_paths = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_custom_mib_paths")
        load_mib_modules = Utils.data_Utils.get_object_from_datarepository(str(system_name)+"_load_mib_modules")

        #Non-empty errorIndication string indicates SNMP engine-level error.
        #The pair of errorStatus and errorIndex variables determines SNMP
        #PDU-level error. If errorStatus evaluates to true, this indicates SNMP
        #PDU error caused by Managed Object at position errorIndex-1 in \
        #varBinds. Doing errorStatus.prettyPrint() would return an
        # explanatory text error message.

        result_list = []
        status = False

        if errindication:
            testcase_Utils.pNote("%s" % errindication.prettyPrint())
        else:
            if errorstatus:
                testcase_Utils.pNote('%s at %s' % (errorstatus.prettyPrint(),
                                                   errindex and
                                                   varBindTable[-1][int(errindex)-1][0]or '?'))
            else:
                if varBindTable:
                    if type(varBindTable[0]) is not list:
                        # for SNMP Get/Get-Next output only
                        for name, val in varBindTable:
                            result_list.append(snmp_utils.translate_mib(custom_mib_paths, load_mib_modules, name, val))
                    else:
                        # for SNMP Getbulk/walk output only
                        for varBindTableRow in varBindTable:
                            for name, val in varBindTableRow:
                                result_list.append(snmp_utils.translate_mib(custom_mib_paths, load_mib_modules, name, val))
                else:
                    testcase_Utils.pNote("No SNMP Result Present!", 'error')
        for element in result_list:
            if mib_string:
                if mib_string in element[0] and snmp_result in element[-1]:
                    status = True
                    testcase_Utils.pNote('%s and %s found in SNMP Output' %(
                        mib_string, snmp_result))
                    break
            else:
                if snmp_result in element[-1]:
                    status = True
                    testcase_Utils.pNote('%s Found! in SNMP Output' %(
                        snmp_result))
                    break
        if status == False:
            if mib_string:
                testcase_Utils.pNote('{} and {} NOT Found in SNMP Output'.format(mib_string, snmp_result))
            else:
                testcase_Utils.pNote('{} NOT Found in SNMP Output'.format(snmp_result))
        Utils.testcase_Utils.report_substep_status(status)
        return status


    def add_snmp_v3_user(self, port, username, securityEngineId,
                         authkey=None, privkey=None,
                         authProtocol=None, privProtocol=None):
        """
        Add SNMP V3 User for TRAP and Inform
            Argument:
                1. port: SNMP trap or inform port.
                2. username(string) = snmp v3 username.
                3. securityEngineId(string) = SNMP v3 secure engine id which is a mandatory
                                              argument for any V3 user. both sender and reciver should know
                                              this id. refer: http://www.net-snmp.org/tutorial/tutorial-5/commands/snmptrap-v3.html
                4.authKey(string) = Initial value of the secret authentication key.
                                     e.g. 'authkey1'
                5.privKey(string) = Initial value of the secret encryption key.
                                     e.g. 'privkey1'
                6.authProtocol(string) = An indication of whether messages sent on behalf of this USM user
                                  can be authenticated, and if so, the type of
                                  authentication protocol which is used.
                                  supported protocols: usmNoAuthProtocol,
                                  usmHMACMD5AuthProtocol, usmHMACSHAAuthProtocol
                                  authProtocol="1,3,6,1,6,3,10,1,1,2"
                7.privProtocol(string) = An indication of whether messages sent on behalf
                                  of this USM user be encrypted, and if so,
                                  the type of encryption protocol which is used.
                                  supported usmNoPrivProtocol(default),
                                  usmDESPrivProtocol, usm3DESEDEPrivProtocol, usmAesCfb128Protocol
                                  e.g. privProtocol="1,3,6,1,6,3,10,1,2,2"
        Return: True or False
        """
        status = True
        wdesc = "Add SNMP V3 User for TRAP and Inform"
        Utils.testcase_Utils.pSubStep(wdesc)
        status = ws.add_user(port, username, securityEngineId,
                             authkey, privkey, authProtocol, privProtocol)
        Utils.testcase_Utils.report_substep_status(status)
        return status


    def add_snmp_community(self, port, community_string):
        """
        Add the SNMP community string
        :param port: SNMP TRAP or Inform PORT
        :param community_string: SNMP community String
        :return:
        """
        status = True
        status = ws.add_community(port, community_string)
        Utils.testcase_Utils.report_substep_status(status)
        return status

    def start_trap_listener(self, system_name,
                           custom_mib_path=None,
                           load_mib_module='SNMPv2-MIB,SNMP-COMMUNITY-MIB'
                           ):
        """
        Start trap listener on Given port and IP address. It creates a socket
        with given port and ip.The Trap listner is only for SNMP v1 and v2c and v3.
        Arguments:
            system_name: SNMP Agents system name from the data file.
            custom_mib_path: User can provide multiple MIB source path seperated by comma (',')
                      Source path can be url or just absolute directory path. Refer bellow example.
                      e.g. 'http://<URL>/@mib@, /data/users/MIBS/'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            load_mib_module: User can provide the MIBS(name) need to be loaded from the path "custom_mib_path".
                      It is a string of MIB names separated by comma(',')
                      e.g. "FSS-COMMON-TC,FSS-COMMON-LOG,FSS-COMMON-SMI"
        Data File Usage:
             <ip> : Ip of the agent. It has to be IP not a hostname.
             <snmp_port>: SNMP Port. UDP port e.g. 161 or 1036.
             <snmp_trap_port> : SNMP trap port. UDP port e.g. 162 or any othe custom port.1036
                                if NESNMP or any other SNMP protocol is using the 162 port please use any other port other than 162.
             <community>: form this release community string is mandatory for v2 and v1 SNMP trap.
                          you can add multiple community like 'public,testing' or single like 'public'
             <snmp_username>: For SNMP v3 this and engine id are mandatory argument. e.g. 'user_snmp1234'
             <securityEngineId>: One mandatory argument for V3 trap and inform.e.g. '80000F150000000000000000'.
             For noAuthNoPriv none of the bellow attributes are required.
             <authkey>: Auth password. e.g. 'authkey123'
             <authProtocol>: authProtocol e.g. 'usmHMACMD5AuthProtocol'
                                  authProtocol(string) = An indication of whether messages sent on behalf of this USM user
                                  can be authenticated, and if so, the type of
                                  authentication protocol which is used.
                                  supported protocols: usmNoAuthProtocol,
                                  usmHMACMD5AuthProtocol, usmHMACSHAAuthProtocol
              <privkey>: private key e.g. 'privkey1'
              <privProtocol>: privProtocol e.g. 'usmDESPrivProtocol'
                             privProtocol(string) = An indication of whether messages sent on behalf
                             of this USM user be encrypted, and if so,
                             the type of encryption protocol which is used.
                             supported usmNoPrivProtocol(default),
                             usmDESPrivProtocol, usm3DESEDEPrivProtocol, usmAesCfb128Protocol
        Return: True or False
        """
        status = True
        wdesc = "Starting Trap listener"
        Utils.testcase_Utils.pSubStep(wdesc)
        snmp_parameters = ['ip', 'snmp_trap_port', 'community', 'snmp_username',
                            'securityEngineId', 'authkey', 'privkey',
                            'authProtocol', 'privProtocol']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)

        ip = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_trap_port')
        community = snmp_param_dic.get('community', None)
        username = snmp_param_dic.get('snmp_username', None)
        securityEngineId = snmp_param_dic.get('securityEngineId', None)
        privkey = snmp_param_dic.get('privkey', None)
        authkey = snmp_param_dic.get('authkey', None)
        authProtocol = snmp_param_dic.get('authProtocol', None)
        privProtocol = snmp_param_dic.get('privProtocol', None)

        engine = ws.get_asyncoredispatcher(port)

        ntfrcv.NotificationReceiver(engine, ws.trap_decoder)
        ws.data_repo.update({"custom_mib_path":custom_mib_path,
                        "load_mib_module":load_mib_module})
        trap_listner_job = Thread(target=ws.create_trap_listner_job, args=(port, ))
        trap_listner_job_start = Thread(target=ws.start_trap_listner_job, args=(port,))
        trap_listner_job.daemon = True
        trap_listner_job_start.daemon = True
        trap_listner_job.start()
        if community:
            stats = ws.add_community(port, community)
            status = status and stats
        if username and securityEngineId:
            stats = self.add_snmp_v3_user(port, username, securityEngineId,
                                                authkey, privkey,
                                                authProtocol, privProtocol)
            status = status and stats
        sleep(1)
        trap_listner_job_start.start()
        sleep(2)
        Utils.testcase_Utils.report_substep_status(status)
        return status

    def stop_trap_listener(self, system_name):
        """
        Stop Trap listener job
        Argument:
        system_name: Agent system name given in the data file.
        :return: Binary True or False
        """
        status = True
        wdesc = "Stop Trap listener"
        Utils.testcase_Utils.pSubStep(wdesc)
        snmp_parameters = ['ip', 'snmp_trap_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ip = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_trap_port')
        stop_list = Thread(target=ws.close_trap_listner_job, args=(port,))
        stop_list.daemon = True
        stop_list.start()
        stop_list.join()
        Utils.testcase_Utils.report_substep_status(status)
        return status

    def validate_trap(self, system_name, value, oid_string=None, match_oid_op_value_pair="no"):
        """
        This method will validate the Received traps from a agent.
        Argument:
            1. system_name: Agent System name from the data file
            2. value: The tarp infromation e.g. 'Administrative State Down'
            3. oid_string: MIB string e.g. 'FSS-COMMON-LOG::fssTrapDescription.0'
            3. match_oid_op_value_pair: if set as 'yes' it will match both
            oid_string and value as a pair. Default value 'no'
        :return: Binary True or False
        """
        stats = []
        status = False
        wdesc = "Validate the Received Trap Messages from {}".format(system_name)
        Utils.testcase_Utils.pSubStep(wdesc)
        snmp_parameters = ['ip', 'snmp_trap_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        agent_ip = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_trap_port')
        op_trap = ws.data_repo.get("snmp_trap_messages_{}".format(agent_ip))
        if op_trap:
            testcase_Utils.pNote("Total No# {} of Trap message(s) Received from {}".format(len(op_trap), agent_ip))
            for temp_list in op_trap:
                for items in temp_list[4:]:
                    if match_oid_op_value_pair.lower() == "no":
                        if value and value in items[1]:
                            testcase_Utils.pNote("Value# {} is present in: \n# {} = {}".format(value, items[0], items[1]))
                            stats.append(True)
                            break
                    elif oid_string and value:
                        if oid_string in items[0] and value in items[1]:
                            testcase_Utils.pNote("OID #{} and Value #{} is present in: \n# {} = {}".format(oid_string, value, items[0], items[1]))
                            stats.append(True)
                            break
                    if True in stats:
                        break
                if True in stats:
                    break
        else:
            testcase_Utils.pNote("No Trap Received!", "error")
        if True in stats:
            status = True
        else:
            if value and oid_string:
                testcase_Utils.pNote("OID #{} and Value #{} is NOT Present!".format(oid_string, value), "error")
            else:
                testcase_Utils.pNote("Value #{} is NOT present!".format(oid_string, value), "error")
        Utils.testcase_Utils.report_substep_status(status)
        return status


    def show_received_traps(self, system_name):
        """
        Retrieve the captured SNMP Trap messages and show them in the console.
        Argument:
            system_name: Agent system name from data file.
        Return: Binary- True or False
        """
        status = True
        wdesc = "List out the trap messages from {}".format(system_name)
        Utils.testcase_Utils.pSubStep(wdesc)
        snmp_parameters = ['ip', 'snmp_trap_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        agent_ip = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_trap_port')
        sleep(5)
        op_trap = ws.data_repo.get("snmp_trap_messages_{}".format(agent_ip))
        if op_trap:
            testcase_Utils.pNote("Total No# {} of Trap message(s) Received from {}".format(len(op_trap), agent_ip))
            for temp_list in op_trap:
                ticks = temp_list[0].get("time_stamp")
                contextengineid = temp_list[1].get("contextEngineId")
                snmpver = temp_list[2].get("SNMPVER")
                securityname = temp_list[3].get("securityName")
                testcase_Utils.pNote(" --------->>Notification message(Time Stamp:{})<<------- \n From: {}:\n "
                                     "contextEngineId :{}\n SNMPVER :{}\n securityName: {}"
                                     .format(ticks, agent_ip, contextengineid, snmpver, securityname))
                testcase_Utils.pNote("--------------")
                for items in temp_list[4:]:
                    testcase_Utils.pNote("{} = {}".format(items[0], items[1]))
        else:
            testcase_Utils.pNote("No Trap Received from {}!".format(agent_ip), "error")
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        return status


    def browse_mib(self, mib_filepath, mib_filename, browse='yes'):
        """
        Browse the MIB File/single or multiple
        :param mib_filepath: Mib file path of the git url or abs file path
        :param mib_filename: MIB file name
        :param browse: Default value is 'yes' were only browse the mentioned MIBS mib_filename argument,
        if set 'no' will browse all the Mibs in the given Path
        :return: True or False
        """
        status = True
        wdesc = "Browse the MIB File"
        Utils.testcase_Utils.pSubStep(wdesc)
        oid, label, suffix, mibView, mibBuilder = ws.get_first_node_name(mib_filepath, mib_filename)
        temp_modName, nodeDesc, suffix = mibView.getNodeLocation(oid)
        while 1:
            try:
                modName, nodeDesc, suffix = mibView.getNodeLocation(oid)
                mibNode, = mibBuilder.importSymbols(modName, nodeDesc)
                nodetype = re.search(r"([\w]+)\(", str(mibNode)).group(1)
                if browse.lower() == 'yes':
                    if modName in mib_filename:
                        if nodetype == 'MibScalar':
                             testcase_Utils.pNote('%s     %s -> %s == %s' % ('$$', nodetype, modName+'::'+nodeDesc+'.0', '.'.join(map(str,(oid)))+'.0'))
                        else:
                             testcase_Utils.pNote('** %s -> %s == %s' % (nodetype, modName+'::'+nodeDesc, '.'.join(map(str,(oid)))))
                elif browse.lower() == 'no' :
                    if nodetype == 'MibScalar':
                         testcase_Utils.pNote('%s     %s -> %s == %s' % ('$$', nodetype, modName+'::'+nodeDesc+'.0', '.'.join(map(str,(oid)))+'.0'))
                    else:
                         testcase_Utils.pNote('** %s -> %s == %s' % (nodetype, modName+'::'+nodeDesc, '.'.join(map(str,(oid)))))
                oid, label, suffix = mibView.getNextNodeName(oid)
            except error.SmiError:
                break
        Utils.testcase_Utils.report_substep_status(status)
        return status
