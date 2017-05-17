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
Implementation of the standard SNMP protocol commands for SNMP v1 and v2c and V3(Not for TRAPs)
and IPv6 support added.
"""
import os
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_exception
from Framework.ClassUtils.snmp_utlity_class import WSnmp as ws
from Framework.Utils import testcase_Utils, config_Utils, data_Utils
from threading import Thread
from time import sleep
import Queue




class CommonSnmpActions(object):
    """
    Class for standard SNMP protocol commands
    """

    def __init__(self):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.snmpver = {'1':'0', '2':'1', '2c':'1', '3':'2'}

    def snmp_get(self, snmp_ver, mib_name,
                 mib_index, mib_value,
                 system_name, oid_string=None, communityname=None,
                 snmp_timeout=60,
                 userName=None, authKey=None, privKey=None,authProtocol=None,
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
            12.authProtocol(string) = An indication of whether messages sent on behalf of this USM user
                              can be authenticated, and if so, the type of
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
                      e.g. 'https://github.com/warriorframework/warriorframework, /data/users/username/MIBS/FNC'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            15.load_mib_modules: User can provide the MIBS(name) need to be loaded from the path "custom_mib_path".
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

        snmp_parameters = ['ip', 'snmp_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ipaddr = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_port')

        output_dict = {}

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

        if oid_string:
            oid = tuple([int(e) if e.isdigit() else e for e in oid_string.split('.')])
        else:
            if custom_mib_paths and load_mib_modules:
                custom_mib_paths = custom_mib_paths.split(',')
                load_mib_modules = load_mib_modules.split(',')
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).addMibSource(*custom_mib_paths).loadMibs(*load_mib_modules)
            if load_mib_modules and not custom_mib_paths:
                load_mib_module = load_mib_modules.split(',')
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).loadMibs(*load_mib_modules)
            if not load_mib_modules and not custom_mib_paths:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value)
        try:
            errindication, errstatus,\
            errindex, result = cmdgen.getCmd(auth_data, transport, oid)
            output_dict = {
                           '{0}_errindication'.format(system_name):errindication,
                           '{0}_errstatus'.format(system_name):errstatus,
                           '{0}_errindex'.format(system_name):errindex,
                           '{0}_result'.format(system_name):result}

            status = True
            testcase_Utils.pNote("Successfully executed SNMP GET command {}".format(result), "info")

        except wsnmp.exception:
            status = False
            testcase_Utils.pNote("SNMP GET command Failed.", "error")

        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def snmp_getnext(self, snmp_ver, mib_name,
                 mib_index, mib_value,
                 system_name, oid_string=None, communityname=None,
                 snmp_timeout=60,
                 userName=None, authKey=None, privKey=None,authProtocol=None,
                 privProtocol=None,
                 custom_mib_paths=None,
                 load_mib_modules=None):
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
            #arguments 9-13 are only for SNMPv3 or mpModel = 2 and in that
            # case communityname will be None
            9.userName(string) = A human readable string representing the
                                  name of the SNMP USM user.
                                  e.g. 'usr1'
            10.authKey(string) = Initial value of the secret authentication key.
                                 e.g. 'authkey1'
            11.privKey(string) = Initial value of the secret encryption key.
                                 e.g. 'privkey1'
            12.authProtocol(string) = An indication of whether messages sent on behalf of this USM user
                              can be authenticated, and if so, the type of
                              authentication protocol which is used.
                              supported protocols: usmNoAuthProtocol,
                              usmHMACMD5AuthProtocol, usmHMACSHAAuthProtocol
                              authProtocol='1,3,6,1,6,3,10,1,1,2'
            13.privProtocols(string) = An indication of whether messages sent on behalf
                              of this USM user be encrypted, and if so,
                              the type of encryption protocol which is used.
                              supported usmNoPrivProtocol(default),
                              usmDESPrivProtocol, usm3DESEDEPrivProtocol, usmAesCfb128Protocol
                              e.g. privProtocol='1,3,6,1,6,3,10,1,2,2)'
            14.custom_mib_paths: User can provide multiple MIB source path seperated by comma (',')
                      Source path can be url or just absolute directory path. Refer bellow example.
                      e.g. 'https://github.com/warriorframework/warriorframework, /data/users/username/MIBS/FNC'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            15.load_mib_module: User can provide the MIBS(name) need to be loaded from the path "custom_mib_path".
                      It is a string of MIB names separated by comma(',')
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

        snmp_parameters = ['ip', 'snmp_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ipaddr = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_port')

        output_dict = {}

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

        if oid_string:
            oid = tuple([int(e) if e.isdigit() else e for e in oid_string.split('.')])
        else:
            if custom_mib_paths and load_mib_modules:
                print "Sourav1"
                custom_mib_paths = custom_mib_paths.split(',')
                load_mib_modules = load_mib_modules.split(',')
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).addMibSource(*custom_mib_paths).loadMibs(*load_mib_modules)
            if load_mib_modules and not custom_mib_paths:
                load_mib_module = load_mib_modules.split(',')
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).loadMibs(*load_mib_modules)
            if not load_mib_modules and not custom_mib_paths:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value)
        try:
            errindication, errstatus, errindex, \
            result = cmdgen.nextCmd(auth_data,
                                    transport, oid, lexicographicMode=True,
                                    ignoreNonIncreasingOid=True, maxRows=1,
                                    lookupNames=True, lookupValues=True)
            #  maxRows=1 will control the mib walk
            output_dict = {
                           '{0}_errindication'.format(system_name):errindication,
                           '{0}_errstatus'.format(system_name):errstatus,
                           '{0}_errindex'.format(system_name):errindex,
                           '{0}_result'.format(system_name):result}

            status = True
            testcase_Utils.pNote("Successfully executed SNMP GET-NEXT "
                                 "command {}".format(result), "info")
        except wsnmp.exception:
            status = False
            testcase_Utils.pNote("SNMP GET-Next command Failed.", "error")

        Utils.testcase_Utils.report_substep_status(status)

        return status, output_dict

    def snmp_walk(self, snmp_ver, mib_name,
                 mib_index, mib_value,
                 system_name, oid_string=None, communityname=None,
                 snmp_timeout=60,
                 userName=None, authKey=None, privKey=None,authProtocol=None,
                 privProtocol=None,
                 custom_mib_paths=None,
                 load_mib_modules=None):
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
            12.authProtocol(string) = An indication of whether messages sent on behalf of this USM user
                              can be authenticated, and if so, the type of
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
                      e.g. 'https://github.com/warriorframework/warriorframework, /data/users/username/MIBS/FNC'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            15.load_mib_modules: User can provide the MIBS(name) need to be loaded from the path "custom_mib_path".
                      It is a string of MIB names separated by comma(',')
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

        snmp_parameters = ['ip', 'snmp_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ipaddr = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_port')

        output_dict = {}

        wsnmp = ws(communityname, self.snmpver.get(snmp_ver), ipaddr, port, snmp_timeout,
                   userName, authKey, privKey,authProtocol,
                   privProtocol)
        cmdgen = wsnmp.commandgenerator()
        if self.snmpver.get(snmp_ver) is 2:# for snmp v3
            auth_data = wsnmp.usmuserdata()
        else:                              #for snmp v1 or v2c
            auth_data = wsnmp.communitydata()

        if ':' in ipaddr:#for ipv6
            transport = wsnmp.udp6transporttarget()
        else:    #for ipv4
            transport = wsnmp.udptransporttarget()

        if oid_string: #OID String is optional
            oid = tuple([int(e) if e.isdigit() else e for e in oid_string.split('.')])
        else:
            if custom_mib_paths and load_mib_modules:
                custom_mib_paths = custom_mib_paths.split(',')
                load_mib_modules = load_mib_modules.split(',')
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).addMibSource(*custom_mib_paths).loadMibs(*load_mib_modules)
            if load_mib_modules and not custom_mib_paths:
                load_mib_module = load_mib_modules.split(',')
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).loadMibs(*load_mib_modules)
            if not load_mib_modules and not custom_mib_paths:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value)
        try:
            errindication, errstatus, errindex,\
            result = cmdgen.nextCmd(auth_data,
                                    transport,
                                    oid, lexicographicMode=True,
                                    ignoreNonIncreasingOid=True, maxRows=5000,
                                    lookupNames=True, lookupValues=True)
            output_dict = {
                           '{0}_errindication'.format(system_name):errindication,
                           '{0}_errstatus'.format(system_name):errstatus,
                           '{0}_errindex'.format(system_name):errindex,
                           '{0}_result'.format(system_name):result}

            status = True
            testcase_Utils.pNote("Successfully executed SNMP WALK command {}".format(result), "info")
        except wsnmp.exception:
            status = False
            testcase_Utils.pNote("SNMP Walk command Failed.", "error")
        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def snmp_bulkget(self, snmp_ver, mib_name,
                 mib_index, mib_value,
                 system_name, oid_string=None, communityname=None,
                     snmp_timeout=60,
                 userName=None, authKey=None, privKey=None,authProtocol=None,
                 privProtocol=None,
                 custom_mib_paths=None,
                 load_mib_modules=None):
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
            13.authProtocol(string) = An indication of whether messages sent on behalf of this USM user
                              can be authenticated, and if so, the type of
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
                      e.g. 'https://github.com/warriorframework/warriorframework, /data/users/username/MIBS/FNC'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            16.load_mib_modules: User can provide the MIBS(name) need to be loaded from the path "custom_mib_path".
                      It is a string of MIB names separated by comma(',')
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

        snmp_parameters = ['ip', 'snmp_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ipaddr = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_port')

        output_dict = {}

        wsnmp = ws(communityname, self.snmpver.get(snmp_ver), ipaddr, port, snmp_timeout,
                   userName, authKey, privKey,authProtocol,
                   privProtocol)
        cmdgen = wsnmp.commandgenerator()
        if self.snmpver.get(snmp_ver) is 2:# for ssnmp v3
            auth_data = wsnmp.usmuserdata()
        else:                              #for snmp v1 or v2c
            auth_data = wsnmp.communitydata()

        if ':' in ipaddr:#for ipv6
            transport = wsnmp.udp6transporttarget()
        else:    #for ipv4
            transport = wsnmp.udptransporttarget()

        if oid_string:
            oid = tuple([int(e) if e.isdigit()
                         else e for e in oid_string.split('.')])
        else:
            if custom_mib_paths and load_mib_modules:
                print "Sourav1"
                custom_mib_paths = custom_mib_paths.split(',')
                load_mib_modules = load_mib_modules.split(',')
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).addMibSource(*custom_mib_paths).loadMibs(*load_mib_modules)
            if load_mib_modules and not custom_mib_paths:
                load_mib_module = load_mib_modules.split(',')
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value).loadMibs(*load_mib_modules)
            if not load_mib_modules and not custom_mib_paths:
                oid = wsnmp.mibvariable(mib_name, mib_index, mib_value)
        try:
            errindication, errstatus, errindex, \
            result = cmdgen.bulkCmd(auth_data,
                                    transport,
                                    1, 25, oid, lexicographicMode=True,
                                    lookupNames=True,
                                    lookupValues=True,
                                    maxRows=20)
            # nonRepeaters(1)(int): One MIB variable is requested in response
            # for the first nonRepeaters MIB variables in request.
            # maxRepetitions(25)(int): maxRepetitions MIB variables are
            # requested in response for each of the remaining MIB variables in
            # the request (e.g. excluding nonRepeaters). Remote SNMP engine may
            # choose lesser value than requested.
            output_dict = {
                           '{0}_errindication'.format(system_name):errindication,
                           '{0}_errstatus'.format(system_name):errstatus,
                           '{0}_errindex'.format(system_name):errindex,
                           '{0}_result'.format(system_name):result}

            status = True
            testcase_Utils.pNote("Successfully executed SNMP BULK GET "
                                 "command".format(result), "info")
        except wsnmp.exception:
            status = False
            testcase_Utils.pNote("SNMP BULK GET command Failed.", "error")

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

        #Non-empty errorIndication string indicates SNMP engine-level error.
        #The pair of errorStatus and errorIndex variables determines SNMP
        #PDU-level error. If errorStatus evaluates to true, this indicates SNMP
        #PDU error caused by Managed Object at position errorIndex-1 in \
        #varBinds. Doing errorStatus.prettyPrint() would return an
        # explanatory text error message.

        result_list = []
        status = False
        if errindication:
            testcase_Utils.pNote("%s" % errindication)
        else:
            if errorstatus:
                testcase_Utils.pNote('%s at %s' % (errorstatus.prettyPrint(),
                                                   errindex and
                                                   varBindTable[-1][int(errindex)-1][0]or '?'))
            else:
                if type(varBindTable[0]) is not list:
                    # for SNMP Get/Get-Next output only
                    for name, val in varBindTable:
                        if ws.checkoctetstring(val):
                            if '0x' == val.prettyPrint()[:2]: # to
                                # confirm if it is a hex string or not
                                if len(val.prettyPrint()) == 14:# for MAC
                                    s = val.prettyPrint()
                                    val = ':'.join( s[x:x+2] for x in
                                                    range(2,len(s), 2))
                                if len(val.prettyPrint()) == 12:# for IP
                                    s = val.prettyPrint()
                                    val = '.'.join( s[x:x+2] for x in
                                                    range(2,len(s), 2))

                            result_list.append((name.prettyPrint(),
                                                val))
                            testcase_Utils.pNote('%s = %s' %(
                                name.prettyPrint(),val))
                        else:
                            result_list.append((name.prettyPrint(),
                                                val.prettyPrint()))
                            testcase_Utils.pNote('%s = %s' % (
                                name.prettyPrint(),val.prettyPrint()))
                else:
                    # for SNMP Getbulk/walk output only
                    for varBindTableRow in varBindTable:
                        for name, val in varBindTableRow:
                            if ws.checkoctetstring(val):
                                if '0x' == val.prettyPrint()[:2]: # to
                                    # confirm if it is a hex string or not
                                    if len(val.prettyPrint()) == 14:# for MAC
                                        s = val.prettyPrint()
                                        val = ':'.join( s[x:x+2] for x in
                                                        range(2,len(s), 2))
                                    if len(val.prettyPrint()) == 12:# for IP
                                        s = val.prettyPrint()
                                        val = '.'.join( s[x:x+2] for x in
                                                        range(2,len(s), 2))

                                result_list.append((name.prettyPrint(),
                                                    val))
                                testcase_Utils.pNote('%s = %s' %(
                                    name.prettyPrint(),val))
                            else:
                                result_list.append((name.prettyPrint(),
                                                    val.prettyPrint()))
                                testcase_Utils.pNote('%s = %s' %
                                                     (name.prettyPrint(),
                                                      val.prettyPrint()))

        for element in result_list:
            if mib_string:
                if mib_string in element and snmp_result in element:
                    status = True
                    testcase_Utils.pNote('%s and %s found in SNMP Output' %(
                        mib_string, snmp_result))
                    break
            else:
                if snmp_result in element:
                    status = True
                    testcase_Utils.pNote('%s found in SNMP Output' %(
                        snmp_result))
                    break

        Utils.testcase_Utils.report_substep_status(status)

        return status

    def start_tarp_listener(self, system_name, 
                           ipv4_addr='0.0.0.0',
                           ipv6_addr='::1',
                           provision_ipv4='yes',
                           provision_ipv6='no',
                           custom_mib_path=None,
                           load_mib_module='SNMPv2-MIB,SNMP-COMMUNITY-MIB'
                           ):
        """
        Start trap listener on Given port and IP address. It creates a socket
        with given port and ip.The Trap listner is only for SNMP v1 and v2c.
        Arguments:
            system_name: SNMP Agents system name from the data file.
            ipv4_addr: ipv4 string e.g. "192.45.16.203" if not provided set it as "0.0.0.0".
                       CAUTION if user system dont has a inetrace with specific ip address the bind will fail.
                       Therefore its advisable to leave this argument as default.
            ipv6_addr: ipv6 string e.g. "2110:db8:0:1::136" if not provided set it as "::1"
                       CAUTION if user system dont has a inetrace with specific ip address the bind will fail.
                       Therefore its advisable to leave this argument as default.
            port: UDP port for SNMP-TRAP by default "162". But if SNMP -162  port is reserved  by
                      superuser user can't reuse the same unless user is the superuser.
                      In that case user has to make the port forwarding of SNMP agent to
                      some other port other than "161" or "162" and same should
                      be provided as argument e.g. '1036'.
            provision_ipv4: if yes provision ipv4 address. Default is 'yes'
            provision_ipv6: if yes provision ipv6 address. Default is 'no'
            custom_mib_path: User can provide multiple MIB source path seperated by comma (',')
                      Source path can be url or just absolute directory path. Refer bellow example.
                      e.g. 'https://github.com/warriorframework/warriorframework, /data/users/username/MIBS/FNC'.
                      For URL it supports http, file, https, ftp and sftp.
                      Use @mib@ placeholder token in URL location to refer.
            load_mib_module: User can provide the MIBS(name) need to be loaded from the path "custom_mib_path".
                      It is a string of MIB names separated by comma(',')
                      e.g. "FSS-COMMON-TC,FSS-COMMON-LOG,FSS-COMMON-SMI"
        Return: True or False and dictionary with {'transportdispatcher_obj': transportDispatcher,'provision_ipv4':provision_ipv4,'provision_ipv6':provision_ipv6}
        """
        status = True
        wdesc = "Starting Trap listener"

        snmp_parameters = ['ip', 'snmp_trap_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        ip = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_trap_port')
        Utils.testcase_Utils.pSubStep(wdesc)
        transportDispatcher = ws.get_asyncoredispatcher()
        transportDispatcher.registerRecvCbFun(ws.trap_decoder)
        ws.data_repo.update({"custom_mib_path":custom_mib_path,
                        "load_mib_module":load_mib_module})
        q = Queue.Queue(maxsize=10)
        _trap_listner_job = Thread(target=ws.create_trap_listner_job, args=(
            transportDispatcher, q, ipv4_addr, ipv6_addr,
            port, provision_ipv4, provision_ipv6))
        _trap_listner_job_start = Thread(target=ws.start_trap_listner_job, args=(
            transportDispatcher,))
        _trap_listner_job.daemon = True
        _trap_listner_job_start.daemon = True
        _trap_listner_job.start()
        sleep(1)
        status = q.get()
        if status:
            _trap_listner_job_start.start()
        sleep(2)
        Utils.testcase_Utils.report_substep_status(status)
        return status, {
                        "transportdispatcher_obj_{}".format(port): transportDispatcher,
                        "provision_ipv4":provision_ipv4,
                        "provision_ipv6":provision_ipv6
                        }

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
        transportDispatcher = Utils.data_Utils.get_object_from_datarepository("transportdispatcher_obj_{}".format(port))
        provision_ipv6 = Utils.data_Utils.get_object_from_datarepository("provision_ipv6")
        provision_ipv4 = Utils.data_Utils.get_object_from_datarepository("provision_ipv4")
        q = Queue.Queue(maxsize=10)
        t3 = Thread(target=ws.close_trap_listner_job, args=(transportDispatcher,
                                                         provision_ipv4,
                                                         provision_ipv6, q))
        t3.start()
        t3.join()
        status = q.get()
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
        __status = []
        status = False
        wdesc = "Validate the Received Trap Messages from {}".format(system_name)
        Utils.testcase_Utils.pSubStep(wdesc)
        snmp_parameters = ['ip', 'snmp_trap_port']
        snmp_param_dic = Utils.data_Utils.get_credentials(self.datafile,
                                                          system_name,
                                                          snmp_parameters)
        agent_ip = snmp_param_dic.get('ip')
        port = snmp_param_dic.get('snmp_trap_port')
        __op_trap = ws.data_repo.get("snmp_trap_messages_{}".format(agent_ip))
        if __op_trap:
            testcase_Utils.pNote("Total No# {} of Trap message(s) Received from {}".format(len(__op_trap), agent_ip))
            for __list in __op_trap:
                for __items in __list[1:]:
                    if match_oid_op_value_pair.lower() == "no":
                        if value and value in __items[1]:
                            testcase_Utils.pNote("Value# {} is present in: \n# {} = {}".format(value, __items[0], __items[1]))
                            __status.append(True)
                            break
                    elif oid_string and value:
                        if oid_string in __items[0] and value in __items[1]:
                            testcase_Utils.pNote("OID #{} and Value #{} is present in: \n# {} = {}".format(oid_string, value, __items[0], __items[1]))
                            __status.append(True)
                            break
                    if True in __status:
                        break
                if True in __status:
                    break
        else:
            testcase_Utils.pNote("No Trap Received!", "error")
        if True in __status:
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
        __op_trap = ws.data_repo.get("snmp_trap_messages_{}".format(agent_ip))
        if __op_trap:
            testcase_Utils.pNote("Total No# {} of Trap message(s) Received from {}".format(len(__op_trap), agent_ip))
            for __list in __op_trap:
                __ticks = __list[0].get("time_stamp")
                testcase_Utils.pNote(" ---------------------->>Notification message(Time Stamp:{})<<---------------------- From: {}:".format(__ticks, agent_ip))
                for __items in __list[1:]:
                    testcase_Utils.pNote("{} = {}".format(__items[0], __items[1]))
        else:
            testcase_Utils.pNote("No Trap Received from {}!".format(agent_ip), "error")
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        return status
