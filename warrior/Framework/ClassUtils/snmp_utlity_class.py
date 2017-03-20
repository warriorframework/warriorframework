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
#!/usr/bin/env python

import os
import re, sys, time
from time import sleep
from Framework.Utils import testcase_Utils, data_Utils, config_Utils
from Framework.Utils.print_Utils import print_info, print_error, print_debug, print_exception
from pysnmp.entity.rfc3413.oneliner import cmdgen, ntforg
from pysnmp import error as snmp_exception
from pysnmp.proto.rfc1902 import OctetString
import threading
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.carrier.asyncore.dgram import udp, udp6, unix
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from pysnmp.smi import builder, view, compiler, rfc1902
import Framework.Utils as Utils


def threadsafe_function(fn):
    """
    Decorator for making sure that the decorated function is thread safe
    Puts a lock before the function uses any resuorces which are not exclusive for a single thread.
    """
    lock = threading.Lock()
    def new(*args, **kwargs):
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
    
    data_repo={}
    
    def __init__(self,communityname, mpModel, ipaddr, port='161',
                 snmp_timeout=60, userName=None, authKey=None, privKey=None,
                 authProtocol=None, privProtocol=None ):

        self.communityname = communityname
        self.mpModel = int(mpModel) ## Accepts only Int type value
        self.ipaddr = ipaddr
        self.port = port
        self.exception = snmp_exception.PySnmpError
        self.timeout = int(snmp_timeout)## Accepts only Int type value

        #bellow arguments are only for SNMPv3 or mpModel = 2 and in that
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
        comdata = cmdgen.CommunityData(communityIndex = self.communityname,
                                       communityName = self.communityname,
                                       mpModel=self.mpModel )
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
    @staticmethod
    def get_asyncoredispatcher():
        return AsyncoreDispatcher()

    @staticmethod
    def get_proto_api():
        return api()

    @staticmethod
    def get_asn_decoder():
        return decoder()

    @staticmethod
    def start_trap_listner_job(transportDispatcher):
        """
        Start the listner Job
        Dispatcher will never finish as job#1 never reaches zero
        :param transportDispatcher:
        :return:None
        """
        try:
            # Dispatcher will never finish as job#1 never reaches zero
            transportDispatcher.runDispatcher()
        except:
            transportDispatcher.closeDispatcher()
            raise

    @staticmethod
    def create_trap_listner_job(transportDispatcher, q,
                            ipv4_addr=None,
                            ipv6_addr=None,
              port="162", provision_ipv4='yes', provision_ipv6='no'
              ):
        """
        Create Trap listner job
        :param transportDispatcher:
        :param ipv4_addr:
        :param ipv6_addr:
        :param port:
        :return:None
        """
        #transportDispatcher.registerRecvCbFun(__trap_decoder)
        if provision_ipv4.lower() == 'yes' and ipv4_addr:
            try:
                transportDispatcher.registerTransport(udp.domainName,
                                              udp.UdpSocketTransport().openServerMode(
                                                  (ipv4_addr, int(port))))
                q.put(True)
            except:
                testcase_Utils.pNote("Can not bind {} and {}".format(ipv4_addr, port),
                                     'warning')
                q.put(False)
        if provision_ipv6.lower() == 'yes' and ipv6_addr:
            try:
                transportDispatcher.registerTransport(udp6.domainName,
                                              udp6.Udp6SocketTransport().openServerMode(
                                                  (ipv6_addr, int(port))))
                q.put(True)
            except:
                testcase_Utils.pNote("Can not bind {} and {}".format(ipv6_addr, port),
                                     'warning')
                q.put(False)
        transportDispatcher.jobStarted(1)

    @staticmethod 
    def close_trap_listner_job(transportDispatcher, provision_ipv4,
                           provision_ipv6, queue):
        """
        Close the trap listner job
        :param transportDispatcher:
        :return:None
        """
        transportDispatcher.jobFinished(1)
        transportDispatcher.unregisterRecvCbFun(recvId=None)
        if provision_ipv4.lower() == 'yes':
            try :
                transportDispatcher.unregisterTransport(udp.domainName)
                queue.put(True)
            except:
                queue.put(False)
                testcase_Utils.pNote("Can not unregister udp Transport domain",
                                     'warning')
        if provision_ipv6.lower() == 'yes':
            try:
                queue.put(True)
                transportDispatcher.unregisterTransport(udp6.domainName)
            except:
                queue.put(False)
                testcase_Utils.pNote("Can not unregister udp6 transport domanin",
                                     'warning')

    @classmethod
    @threadsafe_function
    def trap_decoder(cls, transportDispatcher, transportDomain,
                 transportAddress,
                 wholeMsg):
        """
        Decode the trap messages and saves it in to data repository
        :param transportDispatcher:
        :param transportDomain:
        :param transportAddress:
        :param wholeMsg:
        :return: the actual ASN1 data dumps
        """
        ticks = time.ctime()
        decoded_msg = []
        decoded_msg.append({"time_stamp":ticks})
        if not cls.data_repo.get("snmp_trap_messages_{}".format(transportAddress[0])):
            cls.data_repo.update({"snmp_trap_messages_{}".format(transportAddress[0]):[]})
        mibBuilder = builder.MibBuilder()
        custom_mib_path = cls.data_repo.get("custom_mib_path")
        load_mib_module = cls.data_repo.get("load_mib_module")
        if custom_mib_path:
            #for mib_path in custom_mib_path.split(","):
            compiler.addMibCompiler(mibBuilder, sources=custom_mib_path.split(","))
            mibViewController = view.MibViewController(mibBuilder)
            for mibs in load_mib_module.split(","):
                mibBuilder.loadModules(mibs)
            mibBuilder.loadModules('SNMPv2-MIB', 'SNMP-COMMUNITY-MIB')#common MIBS needed for timetick, systime etc.
        else:
            for mibs in load_mib_module.split(","):
                mibBuilder.loadModules(mibs)
            mibBuilder.loadModules('SNMPv2-MIB', 'SNMP-COMMUNITY-MIB')
            mibViewController = view.MibViewController(mibBuilder)
        #mibBuilder.loadModules('RFC-1212', 'RFC-1215', 'RFC1065-SMI', 'RFC1155-SMI', 'RFC1158-MIB', 'RFC1213-MIB', 'SNMP-FRAMEWORK-MIB', 'SNMP-TARGET-MIB', 'SNMPv2-CONF', 'SNMPv2-SMI', 'SNMPv2-TC', 'SNMPv2-TM', 'TRANSPORT-ADDRESS-MIB')
        while wholeMsg:
            msgVer = int(api.decodeMessageVersion(wholeMsg))
            if msgVer in api.protoModules:
                pMod = api.protoModules[msgVer]
            else:
                testcase_Utils.pNote('SNMP version %s' % msgVer)
                return
            reqMsg, wholeMsg = decoder.decode(
                wholeMsg, asn1Spec=pMod.Message(),
            )
            reqPDU = pMod.apiMessage.getPDU(reqMsg)
            if reqPDU.isSameTypeWith(pMod.TrapPDU()):
                varBinds = pMod.apiPDU.getVarBindList(reqPDU)
                for oid, val in varBinds:
                    objectType = rfc1902.ObjectType(rfc1902.ObjectIdentity(oid.prettyPrint()))
                    objectType.resolveWithMib(mibViewController)
                    oid = str(objectType).strip().strip("=").strip()
                    value=val.prettyPrint().strip()
                    match=re.search(r"(_BindValue:.*=.*=.*\n\s+)(.*-value=.*$)", value , re.DOTALL)
                    value = match.group(2)
                    decoded_msg.append((oid, value))
                    #print '{} = {}'.format(oid, value)
        __decoded_msg = cls.data_repo.get("snmp_trap_messages_{}".format(transportAddress[0]))
        __decoded_msg.append(decoded_msg)
        cls.data_repo.update({"snmp_trap_messages_{}".format(transportAddress[0]):__decoded_msg})
        return wholeMsg
