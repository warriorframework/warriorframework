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


"""SNMP utility module using the python PYSNMP module"""

import os
import re, sys, time
from time import sleep
from Framework.Utils import testcase_Utils, data_Utils, config_Utils
import threading
try:
    from pysnmp.entity.rfc3413.oneliner import cmdgen, ntforg
    from pysnmp import error as snmp_exception
    from pysnmp.proto.api import v2c
    from pysnmp.entity import engine, config
    from pysnmp.carrier.asyncore.dgram import udp, udp6, unix
    from pyasn1.codec.ber import decoder
    from pysnmp.proto import api
    from pysnmp.smi import builder, view, compiler, rfc1902, error
    from pysnmp import debug
    from pysnmp.proto.rfc1902 import OctetString
    from pysnmp.carrier.base import AbstractTransportDispatcher
except ImportError:
    testcase_Utils.pNote("Please Install PYSNMP 4.3.8 or Above", "error")


def threadsafe_function(fn):
    """
    Decorator for making sure that the decorated function is thread safe
    Puts a lock before the function uses any resuorces which are not exclusive for a single thread.
    """
    lock = threading.Lock()

    def new(*args, **kwargs):
        """
        This is new
        :param args:
        :param kwargs:
        :return:
        """
        lock.acquire()
        try:
            r = fn(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            lock.release()
        return r

    return new


class WSnmp(object):
    """SNMP Util class using PYSNMP"""
    data_repo = {}
    snmpEngine = {}
    mibViewController = None
    udptransport = {}
    authProtocol = {'usmHMACMD5AuthProtocol': config.usmHMACMD5AuthProtocol,
                    'usmHMACSHAAuthProtocol': config.usmHMACSHAAuthProtocol,
                    'usmAesCfb128Protocol': config.usmAesCfb128Protocol,
                    'usmAesCfb256Protocol': config.usmAesCfb256Protocol,
                    'usmAesCfb192Protocol': config.usmAesCfb192Protocol,
                    'usmDESPrivProtocol': config.usmDESPrivProtocol,
                    }

    def __init__(self, communityname, mpModel, ipaddr, port='161',
                 snmp_timeout=60, userName=None, authKey=None, privKey=None,
                 authProtocol=None, privProtocol=None):
        """
        This is intialization part
        :param communityname:
        :param mpModel:
        :param ipaddr:
        :param port:
        :param snmp_timeout:
        :param userName:
        :param authKey:
        :param privKey:
        :param authProtocol:
        :param privProtocol:
        """

        self.communityname = communityname
        self.mpModel = int(mpModel)  ## Accepts only Int type value
        self.ipaddr = ipaddr
        self.port = port
        self.exception = snmp_exception.PySnmpError
        self.timeout = int(snmp_timeout)  ## Accepts only Int type value

        # bellow arguments are only for SNMPv3 or mpModel = 2 and in that
        # case communityname will be None
        self.userName = userName
        self.authKey = authKey
        self.privKey = privKey
        self.authProtocol = authProtocol
        self.privProtocol = privProtocol

    def commandgenerator(self):
        """
        SNMP Command generator
        Return: command generator object
        """
        return cmdgen.CommandGenerator()

    def communitydata(self):
        """
        Creates communityData object
        for SNMP v1 and V2c
        :Return: Community data object
        """
        comdata = cmdgen.CommunityData(communityIndex=self.communityname,
                                       communityName=self.communityname,
                                       mpModel=self.mpModel)
        return comdata

    def usmuserdata(self):
        """
        Creates SNMP v3 User Security Model (USM) configuration entry.
        Returns: USM object
        """
        if self.authProtocol and ',' in self.authProtocol:
            self.authProtocol = tuple([int(e) if e.isdigit() else e for e in
                                       self.authProtocol.split(',')])
        if self.privProtocol and ',' in self.privProtocol:
            self.privProtocol = tuple([int(e) if e.isdigit() else e for e in
                                       self.privProtocol.split(',')])
        if self.authProtocol == "usmHMACMD5AuthProtocol":
            self.authProtocol = cmdgen.usmHMACMD5AuthProtocol
        if self.authProtocol == "usmHMACSHAAuthProtocol":
            self.authProtocol = cmdgen.usmHMACSHAAuthProtocol
        if self.privProtocol == "usmAesCfb128Protocol":
            self.privProtocol = cmdgen.usmAesCfb128Protocol
        if self.privProtocol == "usmAesCfb192Protocol":
            self.privProtocol = cmdgen.usmAesCfb192Protocol
        if self.privProtocol == "usmAesCfb256Protocol":
            self.privProtocol = cmdgen.usmAesCfb256Protocol
        if self.privProtocol == "usm3DESEDEPrivProtocol":
            self.privProtocol = cmdgen.usm3DESEDEPrivProtocol
        if self.privProtocol == "usmDESPrivProtocol":
            self.privProtocol = cmdgen.usmDESPrivProtocol
        if not self.privProtocol:
            self.privProtocol = cmdgen.usmNoPrivProtocol
        if not self.authProtocol:
            self.authProtocol = cmdgen.usmNoAuthProtocol
        return cmdgen.UsmUserData(userName=self.userName,
                                  authKey=self.authKey, privKey=self.privKey,
                                  authProtocol=self.authProtocol,
                                  privProtocol=self.privProtocol
                                  )

    def udptransporttarget(self):
        """
        Creates UDP transport object
        Return: UDPTransport object
        """
        return cmdgen.UdpTransportTarget((self.ipaddr, self.port),
                                         timeout=self.timeout, retries=3)

    def udp6transporttarget(self):
        """
        Creates IPV6 UDP transport object
        Returns: IPv6 UDPTransport object
        """
        return cmdgen.Udp6TransportTarget((self.ipaddr, self.port),
                                          timeout=self.timeout, retries=3)

    def mibvariable(self, mib_name, mib_index, mib_value=''):
        """
        Creates MIB Object
        Arguments:
            1.(string) mib_name="IP-MIB"
            2.(string) mib_index="ipAdEntAddr"
            3.(string) mib_value="127.0.0.1"
        Return: MIB Object
        """
        if mib_value:
            return cmdgen.MibVariable(mib_name, mib_index, mib_value)
        else:
            return cmdgen.MibVariable(mib_name, mib_index)

    @staticmethod
    def checkoctetstring(val):
        """
        Check for OctetString
        Arguments:
            1.val: pysnmp object
        :return: True or False
        """
        if isinstance(val, OctetString):
            return True
        else:
            return False

    ##TRAP Listner related method
    ## This will support SNMP v1 v2 V3 Trap and Inform as well

    @classmethod
    def get_asyncoredispatcher(cls, port):
        """
        This is
        :param port:
        :return:
        """
        eng = "snmpEngine{}".format(port)
        if cls.snmpEngine.get(eng) == None:
            cls.snmpEngine.update({eng: engine.SnmpEngine()})
        return cls.snmpEngine.get(eng)

    @staticmethod
    def get_proto_api():
        """
        This is
        :return:
        """
        return api()

    @staticmethod
    def get_asn_decoder():
        """
        This is
        :return:
        """
        return decoder()

    @classmethod
    def start_trap_listner_job(cls, port):
        """
        Start the listner Job
        Dispatcher will never finish as job#1 never reaches zero
        :return:None
        """
        snmpEngine = cls.get_asyncoredispatcher(port)
        try:
            # Dispatcher will never finish as job#1 never reaches zero
            snmpEngine.transportDispatcher.runDispatcher()
        except:
            snmpEngine.transportDispatcher.closeDispatcher()
            raise

    @classmethod
    def create_trap_listner_job(cls,
                                port="162"
                                ):
        """
        Create Trap listner job
        :param port:
        :return:None
        """
        mibBuilder = builder.MibBuilder()
        custom_mib_path = cls.data_repo.get("custom_mib_path")
        load_mib_module = cls.data_repo.get("load_mib_module")
        temp_custom_mib_paths = []
        if custom_mib_path and load_mib_module:
            custom_mib_paths = custom_mib_path.split(',')
            for paths in custom_mib_paths:
                paths = paths.strip()
                if 'http' in paths and '@mib@' not in paths:
                    if paths[-1] == '/':
                        paths = paths + '/@mib@'
                    else:
                        paths = paths + '@mib@'
                if 'http' in paths and 'browse' in paths:
                    paths = paths.replace('browse', 'raw')
                if 'http' in paths and 'browse' in paths:
                    paths = paths.replace('browse', 'raw')
                temp_custom_mib_paths.append(paths)
            if os.name == 'posix' and '/usr/share/snmp/' not in custom_mib_path:
                temp_custom_mib_paths.append('/usr/share/snmp/')
            try:
                compiler.addMibCompiler(mibBuilder, sources=temp_custom_mib_paths)
                cls.mibViewController = view.MibViewController(mibBuilder)
                mibs = load_mib_module.split(",")
                mibBuilder.loadModules(*mibs)
            except error.MibNotFoundError as excep:
                testcase_Utils.pNote("{} Mib Not Found!".format(excep), "Error")
        snmpEngine = cls.get_asyncoredispatcher(port)
        udptransport = udp.UdpTransport()
        cls.udptransport.update({"udptransport{}".format(port): udptransport})
        config.addTransport(snmpEngine, udp.domainName, udptransport.openServerMode(('0.0.0.0', int(port))))
        snmpEngine.transportDispatcher.jobStarted(1)

    @classmethod
    def close_trap_listner_job(cls, port):
        """
        Close the trap listner job
        :param transportDispatcher:
        :return:None
        """
        snmpEngine = cls.get_asyncoredispatcher(port)
        snmpEngine.transportDispatcher.jobFinished(1)
        # t = AbstractTransportDispatcher.getTransport(udp.domainName)
        try:
            snmpEngine.transportDispatcher.unregisterTransport(udp.domainName)
            udptransport = cls.udptransport.get("udptransport{}".format(port))
            udptransport.closeTransport()
            del cls.snmpEngine["snmpEngine{}".format(port)]
            del cls.udptransport["udptransport{}".format(port)]
            # snmpEngine.transportDispatcher.jobFinished(1)
        #   AbstractTransportDispatcher.unregisterTransport(udp.domainName)
        #  t.closeTransport()
        except:
            testcase_Utils.pNote("Can not unregister udp Transport domain",
                                 'warning')

    @classmethod
    @threadsafe_function
    def trap_decoder(cls, snmpEngine, stateReference, contextEngineId, contextName,
                     varBinds, cbCtx):
        """
        Decode the trap messages and saves it in to data repository
        This is call back method which will be coalled internaly for each trap message
        :param transportDispatcher:
        :param transportDomain:
        :param transportAddress:
        :param wholeMsg:
        :return: the actual ASN1 data dumps
        """
        ticks = time.ctime()
        transportAddress = snmpEngine.msgAndPduDsp.getTransportInfo(stateReference)[-1][0]
        if not cls.data_repo.get("snmp_trap_messages_{}".format(transportAddress)):
            cls.data_repo.update({"snmp_trap_messages_{}".format(transportAddress): []})
        execContext = snmpEngine.observer.getExecutionContext(
            'rfc3412.receiveMessage:request'
        )
        decoded_msg = []
        decoded_msg.append({"time_stamp": ticks})
        decoded_msg.append({"contextEngineId": contextEngineId.prettyPrint()})
        decoded_msg.append({"SNMPVER": execContext["securityModel"]})
        decoded_msg.append({"securityName": execContext['securityName']})
        for oid, val in varBinds:
            try:
                output = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid),
                                            val).resolveWithMib(cls.mibViewController).prettyPrint()
            except error.SmiError as excep:
                testcase_Utils.pNote("{} Decode Error!".format(excep), "Error")
            op_list = output.split(" = ")
            oid = op_list[0].strip()
            value = op_list[1].strip()
            decoded_msg.append((oid, value))
        temp_decoded_msg = cls.data_repo.get("snmp_trap_messages_{}".format(transportAddress))
        temp_decoded_msg.append(decoded_msg)
        cls.data_repo.update({"snmp_trap_messages_{}".format(transportAddress): temp_decoded_msg})

    @staticmethod
    def get_first_node_name(mib_filepath, mib_filename):
        """
        Get the node name from the given mib file path and file name
        :param mib_filepath: Mib file path of the git url or abs file path
        :param mib_filename: MIB file name
        :return: oid, lable, suffix, mibView, mibBuilder
        """
        mibBuilder = builder.MibBuilder()
        compiler.addMibCompiler(mibBuilder, sources=mib_filepath.split(","))
        for mib in mib_filename.split(","):
            mibBuilder.loadModules(mib)
        mibView = view.MibViewController(mibBuilder)
        oid, label, suffix = mibView.getFirstNodeName()
        return oid, label, suffix, mibView, mibBuilder

    @classmethod
    def add_user(cls, port, username, securityengineid,
                 authkey=None, privkey=None,
                 authProtocol=None, privProtocol=None):
        """
        Add SNMP V3 User
        :param port: SNMP Trap Port
        :param username: SNMP User name
        :param securityengineid: SNMP Engine id in Hex form
        :param authkey: SNMP Authkey default is None
        :param privkey: SNMP Privkey string default is None
        :param authProtocol: Auth Protocol, default is None
        :param privProtocol: Privacy Protocol, default is None
        :return: Treu or False
        """
        result = True
        snmpEngine = cls.get_asyncoredispatcher(port)
        # debug.setLogger(debug.Debug('all'))
        try:
            authprotocol = cls.authProtocol.get(authProtocol, None)
            privprotocol = cls.authProtocol.get(privProtocol, None)
            config.addV3User(
                snmpEngine=snmpEngine, userName=username,
                authProtocol=authprotocol, authKey=authkey,
                privProtocol=privprotocol, privKey=privkey,
                securityEngineId=v2c.OctetString(hexValue=securityengineid)
            )
        except:
            testcase_Utils.pNote("ADD SNMPv3 User Failed", "error")
            result = False
        return result

    @classmethod
    def add_community(cls, port, community="public"):
        """
        Add SNMP Community
        for this NEW Trap/Inform Reciver its mandatory to add community string also
        :param port: SNMP TRAP/Inform Port
        :param community: SNMP community string, default is 'public'
        :return:
        """
        snmpEngine = cls.get_asyncoredispatcher(port)
        result = True
        try:
            config.addV1System(snmpEngine, community, community)
            testcase_Utils.pNote("Added SNMP Community {}".format(community))
        except:
            testcase_Utils.pNote("ADD SNMP Community Failed", "error")
            result = False
        return result
