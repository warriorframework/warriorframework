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
'''
netconf.py  NETCONF client library.
2017/7/11
ymizugaki
'''
import socket
import traceback
import random
import os
import re
from threading import Thread, Event
from select import select
from binascii import hexlify
from xml.dom.minidom import parseString
from lxml import etree
from datetime import datetime
import paramiko

from Framework.Utils.testcase_Utils import pNote

BUF_SIZE = 65536
POLL_INTERVAL = 0.1
NETCONF_DELIM = "]]>]]>"
XML_HEADER = "<?xml version='1.0' encoding='utf-8'?>"
NETCONF_BASE_NS = "urn:ietf:params:xml:ns:netconf:base:1.0"
NETCONF_NTFCN_NS = "urn:ietf:params:xml:ns:netconf:notification:1.0"
NETCONF_GETSCHEMA_NS = "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"
TIMEOUT_VALUE = 600
NETCONF_DELIM_11 = "\n##\n"

def connect(host, port, username, password, hostkey_verify=False, protocol_version=""):
    '''
    #creates client instance and returns it if connection success
    '''
    netconf_obj = client()
    if netconf_obj.connect(host, port, username, password, hostkey_verify, protocol_version):
        return netconf_obj
    return None


class client(Thread):
    '''
    #netconf client class
    '''

    def __init__(self):
        '''
        initialize
        '''
        self.__t = None
        self.__chan = None
        self.__sock = None
        self.__temp_buf = ""
        Thread.__init__(self)
        self.setDaemon(True)
        self.__host_keys = paramiko.HostKeys()
        self.__wait_resp = Event()
        self.__wait_resp.clear()
        self.__wait_rept = Event()
        self.__wait_rept.clear()
        self.__response_buffer = ""
        self.__hello_buffer = ""
        self.__session_id = None
        self.__isCOMPLD = False
        self.__error_message = ""
        self.__isOpen = False
        self.__send_data = ""
        self.__protocol_ver = "1.0"
        self.__notification_list = []
        self.__wait_string = ("", {})
        self.__host_name = ""
        self.__exp_protocol_version = ""
        self.__notification_list_print = []

    def connect(self, host, port, username, password, hostkey_verify=False, protocol_version=""):
        '''
        #ssh connect
        #  host = hostname or ip (string)
        #  port = port number (integer)
        #  username = login user name (string)
        #  password = password (string)
        #  hostkey_verify = True/False(default)
        #  protocol_version = 1.0/1.1/null (string)
        '''
        pNote("netconf: Connecting to " + host + ":" + str(port))
        # connect
        try:
            # self.__sock = socket.socket(socket.AF_INET,
            #                            socket.SOCK_STREAM,
            #                            socket.getprotobyname('tcp'))
            # self.__sock.settimeout(30)
            # self.__sock.connect((host, port))
            self.__sock = socket.create_connection((host, port), 60)
        except (socket.error, socket.herror, socket.gaierror, socket.timeout):
            pNote("netconf: Connection failed", "error")
            traceback.print_exc()
            return False

        # self.__sock.settimeout(None)

        try:
            self.__t = paramiko.Transport(self.__sock)
            try:
                self.__t.start_client()
            except paramiko.SSHException:
                pNote("netconf: SSH negotiation failed", "error")
                traceback.print_exc()
                return False
        except paramiko.SSHException:
            pNote("netconf: Connection failed", "error")
            traceback.print_exc()
            return False

        # hostkey verify
        server_key = self.__t.get_remote_server_key()
        # fingerprint = self.__colonify(hexlify(server_key.get_fingerprint()))
        if hostkey_verify:
            self.__load_known_hosts()
            known_host = self.__host_keys.check(host, server_key)
            if not known_host:
                known_host = self.__host_keys.check('[%s]:%s' %(host, port), server_key)
                if not known_host:
                    pNote("netconf: unknown host", "warning")
        try:
            self.__t.auth_password(username, password)
        except paramiko.AuthenticationException:
            pNote("netconf: Authentication failed", "error")
            self.__t.close()
            return False

        if not self.__t.is_authenticated():
            pNote("netconf: Authentication failed", "error")
            self.__t.close()
            return False

        self.__chan = self.__t.open_session()
        self.__chan.set_name("netconf")
        self.__chan.invoke_subsystem("netconf")
        self.__host_name = host
        self.__isOpen = True
        self.__exp_protocol_version = protocol_version
        # recv thread start
        self.start()

        # send hello pdu
        self.send_hello()

        return True

    def __colonify(self, fp):
        '''
        #format fingerprint with ":"
        '''
        finga = fp[:2]
        for idx in range(2, len(fp), 2):
            finga += ":" + fp[idx:idx + 2]
        return finga

    def __load_known_hosts(self, filename=None):
        '''
        #load ssh known_hosts setting form a file
        '''
        if filename is None:
            filename = os.path.expanduser('~/.ssh/known_hosts')
            try:
                self.__host_keys.load(filename)
            except IOError:
                # for windows
                filename = os.path.expanduser('~/ssh/known_hosts')
                try:
                    self.__host_keys.load(filename)
                except IOError:
                    pass
        else:
            self.__host_keys.load(filename)

    def run(self):
        '''
        #start receiving thread
        '''
        pNote("netconf: start receiving thread")
        self.__receive()
        pNote("netconf: receiving thread terminated")

    def __send(self, data):
        '''
        #send data to host
        #  data = data to send (xml string)
        '''
        ret = True
        if self.__isOpen:
            self.__send_data = data
            self.__response_buffer = ""
            # self.__notification_buffer = ""
            #
            dispdata = data.replace("\n", "")
            dispdata = re.sub("> +<", "><", dispdata)
            pNote("netconf send: \n" + \
                  parseString(dispdata).toprettyxml(
                  indent="  ", encoding="utf-8"))
            #
            try:
                if data.endswith("\n"):
                    data = data[:-1]
                if self.__protocol_ver == "1.0":
                    data += NETCONF_DELIM
                elif self.__protocol_ver == "1.1":
                    chunksize = len(data)
                    data = "\n#" + str(chunksize) + "\n" + data
                    data += NETCONF_DELIM_11

                while data:
                    n = self.__chan.send(data)
                    if n <= 0:
                        pNote("netconf: send data failed.", "error")
                        self.__error_message = "send data failed"
                        ret = False
                        break
                    data = data[n:]
            except socket.error as e:
                pNote(str(e.__class__) + ': ' + str(e), "error")
                self.__error_message = str(e)
                traceback.print_exc()
                ret = False
        else:
            pNote("netconf: port not opened", "warning")
            self.__error_message = "port not opened"
            ret = False
        return ret

    def __receive(self):
        '''
        #receiving thread
        #if data=rpc-reply, stores in response_buffer, wait_resp flag set,
        #if rpc-error, isCOMPLD=False, otherwise isCOMPLD=True,
        #if data=notification, stores in notification_list,
        #if data=hello, stores in hello_buffer
        '''
        try:
            while True:
                if self.__protocol_ver == "1.0":
                    temp_delim = NETCONF_DELIM
                else:
                    temp_delim = NETCONF_DELIM_11
                xml_len = self.__temp_buf.find(temp_delim)

                if xml_len >= 0:
                    recv_data = self.__temp_buf[:xml_len]

                    if self.__protocol_ver == "1.1":
                        recv_data = re.sub("\n#[0-9].+\n", "", recv_data)
                    self.__temp_buf = self.__temp_buf[xml_len +
                                                      len(temp_delim):]

                    try:
                        recv_dom = parseString(recv_data)
                    except Exception as e:
                        pNote(str(e), "error")
                        pNote(recv_data)
                        pNote("\nreceived xml is invalid, closing port.\n", "error")
                        self.close()
                        return False
                    resType = recv_dom.documentElement.tagName
                    if resType == "rpc-reply":
                        if len(recv_dom.getElementsByTagName("rpc-error")) == 0:
                            self.__isCOMPLD = True
                            self.__error_message = ""
                        else:
                            self.__isCOMPLD = False
                            sev = recv_dom.getElementsByTagName(
                                "error-severity")[0].childNodes[0].data
                            etyp = recv_dom.getElementsByTagName(
                                "error-type")[0].childNodes[0].data
                            etag = recv_dom.getElementsByTagName(
                                "error-tag")[0].childNodes[0].data
                            if len(recv_dom.getElementsByTagName("error-message")) != 0:
                                # msg = recv_dom.getElementsByTagName("error-message")[0].childNodes[0].data
                                msg = ""
                                if len(recv_dom.getElementsByTagName(
                                    "error-message")[0].childNodes) != 0:
                                    msg = recv_dom.getElementsByTagName(
                                        "error-message")[0].childNodes[0].data
                            else:
                                msg = ""
                            if len(recv_dom.getElementsByTagName("bad-element")) != 0:
                                bele = ""
                                if len(recv_dom.getElementsByTagName(
                                    "bad-element")[0].childNodes) != 0:
                                    bele = recv_dom.getElementsByTagName(
                                        "bad-element")[0].childNodes[0].data
                            else:
                                bele = ""
                            self.__error_message = "%s:%s:%s:%s:%s" % (
                                sev, etyp, etag, msg, bele)
                        self.__response_buffer += recv_data
                        self.__wait_resp.set()
                    elif resType == "notification":
                        pNote("\n[NETCONF Notification %s from %s]\n%s" % (datetime.now(), self.__host_name, recv_data))
                        self.__notification_list.append(recv_data)
                        self.__notification_list_print.append(recv_data)
                    elif resType == "hello":
                        self.__hello_buffer = recv_data
                        pNote(recv_data)
                        cap = recv_dom.getElementsByTagName("capability")
                        for c in cap:
                            if c.childNodes[0].data == "urn:ietf:params:netconf:base:1.1":
                                self.__protocol_ver = "1.1"
                                break
                        if self.__exp_protocol_version:
                            if self.__protocol_ver != self.__exp_protocol_version:
                                self.__protocol_ver = "1.0"
                            else:
                                self.__protocol_ver = self.__exp_protocol_version
                        sid = recv_dom.getElementsByTagName(
                            "session-id")[0].childNodes[0].data
                        if sid:
                            self.__session_id = sid
                        else:
                            pNote("session-id could not be found", "error")
                            self.close()
                            return False
                    else:
                        # unknown data type
                        pNote("netconf: unknown type:%s" %resType, "warning")

                rlist, wlist, xlist = select(
                    [self.__chan], [], [], POLL_INTERVAL)
                if rlist:
                    data = self.__chan.recv(BUF_SIZE)
                    if data:
                        self.__temp_buf += str(data)
                    else:
                        # in case of something unexpected happens
                        if len(self.__temp_buf) > 0:
                            pNote(self.__temp_buf)
                        self.__error_message = "port closed"
                        self.__wait_resp.set()
                        self.close()
                        return False

                if len(self.__wait_string) != 0 and self.__wait_string[0]:
                    waitstr = self.__wait_string
                    for notification in self.__notification_list:
                        pNote("Checking notification: "
                              "##{}##".format(notification))
                        xml = etree.fromstring(notification)
                        # Contains list of xpath
                        match, xpath_list = True, waitstr[0].split(",")
                        for xpath in xpath_list:
                            # Validation for the xpath given
                            if not xml.xpath(xpath, namespaces=waitstr[1]):
                                match = False
                                break

                        if match:
                            self.__wait_rept.set()
                            self.__notification_list.remove(notification)
                            break

        except Exception as e:
            pNote(str(e), "error")
            self.__error_message = str(e)
            traceback.print_exc()
            self.close()
            return False
        return True

    def close(self):
        '''
        #session close
        '''
        try:
            self.__chan.close()
            self.__t.close()
        except Exception as e:
            pNote(str(e), "error")
            traceback.print_exc()
        self.__isOpen = False
        pNote("netconf: port closed")

        return True

    def __wait_recv_data(self):
        '''
        #wait receive for rpc-reply until timeout expires
        '''
        self.__wait_resp.clear()
        self.__wait_resp.wait(TIMEOUT_VALUE)
        if self.__wait_resp.isSet():
            if not self.__isOpen:
                return False
            else:
                return True
        else:
            pNote("netconf: RESPONSE TIMEOUT", "warning")
            self.__error_message = "response timeout"
            return False

    def send_hello(self):
        '''
        #send hello
        # just send, no wait
        '''
        xml = XML_HEADER
        xml += "<hello xmlns='%s'>" % NETCONF_BASE_NS
        xml += "<capabilities>"
        xml += "<capability>urn:ietf:params:netconf:base:1.0</capability>"
        if self.__exp_protocol_version != "1.0":
            xml += "<capability>urn:ietf:params:netconf:base:1.1</capability>"
        xml += "</capabilities>"
        xml += "</hello>"
        return self.__send(xml)

    def rpc(self, xml):
        '''
        #send a rpc
          xml = xml string to send
          returns: response data
        '''
        data = XML_HEADER
        data += "<rpc message-id = '%s' xmlns='%s'>" % (random.randint(1, 1000), NETCONF_BASE_NS)
        data += xml
        data += "</rpc>"
        if self.__send(data):
            self.__wait_recv_data()
        return self.__response_buffer

    def get_config(self, source, filter_string=None, filter_type="subtree"):
        '''
        #send get-config rpc
           source = datastore name (candidate/running/startup)
           filter_string = filter string, xml string or xpath string
           filter_type = filter type (subtree or xpath)
        '''
        xml = ""
        xml += "<get-config>"
        xml += "<source><%s/></source>" % source
        if filter_string:
            if filter_type == "subtree":
                xml += "<filter type='subtree'>%s</filter>" % filter_string
            elif filter_type == "xpath":
                if "'" in filter_string:
                    xml += "<filter type='xpath' select=\"%s\"/>" % filter_string
                else:
                    xml += "<filter type='xpath' select='%s'/>" % filter_string
        xml += "</get-config>"

        return self.rpc(xml)

    def edit_config(self, target, config_string,
                    default_operation=None,
                    test_option=None,
                    error_option=None):
        '''
        #send edit-config rpc
          target = datastore name (candidate/running)
          configString = xml string
          default_operation = merge(default)/replace/none
          test_option = test-then-set(default)/set/test-only
          error_option = stop-on-error(default)/continue-on-error/rollback-on-error
        '''
        xml = ""
        xml += "<edit-config>"
        xml += "<target><%s/></target>" % target
        if default_operation:
            xml += "<default-operation>%s</default-operation>" % default_operation
        if test_option:
            xml += "<test-option>%s</test-option>" % test_option
        if error_option:
            xml += "<error-option>%s</error-option>" % error_option
        if config_string.startswith("<config>"):
            xml += config_string
        else:
            xml += "<config>%s</config>" % config_string
        xml += "</edit-config>"
        return self.rpc(xml)

    def copy_config(self, target, source):
        '''
        #send copy-config rpc
          target = destination datastore
          source = source datastore
        '''
        xml = ""
        xml += "<copy-config>"
        xml += "<target><%s/></target>" % target
        if source.find("config") != -1:
            xml += "<source>%s</source>" % source
        else:
            xml += "<source><%s/></source>" % source
        xml += "</copy-config>"
        return self.rpc(xml)

    def delete_config(self, target):
        '''
        #send delete-config rpc
          target = target datastore
        '''
        xml = ""
        xml += "<delete-config>"
        xml += "<target><%s/></target>" % target
        xml += "</delete-config>"
        return self.rpc(xml)

    def lock(self, target):
        '''
        #send lock rpc
          target = target datastore
        '''
        xml = ""
        xml += "<lock>"
        xml += "<target><%s/></target>" % target
        xml += "</lock>"
        return self.rpc(xml)

    def unlock(self, target):
        '''
        #send unlock rpc
          target = target datastore
        '''
        xml = ""
        xml += "<unlock>"
        xml += "<target><%s/></target>" % target
        xml += "</unlock>"
        return self.rpc(xml)

    def get(self, filter_string=None, filter_type=None):
        '''
        #send get rpc
          filterString = filter string, xml string or xpath string
        '''
        xml = ""
        xml += "<get>"
        if filter_string:
            if filter_type == "subtree":
                xml += "<filter type='subtree'>%s</filter>" % filter_string
            elif filter_type == "xpath":
                if "'" in filter_string:
                    xml += "<filter type='xpath' select=\"%s\"/>" % filter_string
                else:
                    xml += "<filter type='xpath' select='%s'/>" % filter_string
            else:
                xml += "%s" %filter_string
        xml += "</get>"
        return self.rpc(xml)

    def close_session(self):
        '''
        #send close-session rpc
        '''
        xml = ""
        xml += "<close-session/>"
        return self.rpc(xml)

    def kill_session(self, session_id):
        '''
        #send kill-session rpc
          session_id = session-id to be killed
           ! not current session !
        '''
        xml = ""
        xml += "<kill-session>"
        xml += "<session-id>%s</session-id>" % session_id
        xml += "</kill-session>"
        return self.rpc(xml)

    def commit(self, confirmed=None,
               confirm_timeout=None,
               persist=None,
               persist_id=None):
        '''
        #send commit rpc
          confirmed = any string if using confirmed commit
          confirm_timeout = timeout value in sec. when confirmed commit
          persist = string of persist-id
          persist_id = persist-id if specified in previous commit
        '''
        xml = ""
        xml += "<commit>"
        if confirmed:
            xml += "<confirmed/>"
            if confirm_timeout:
                xml += "<confirm-timeout>%s</confirm-timeout>" % confirm_timeout
            if persist:
                xml += "<persist>%s</persist>" % persist
        if persist_id:
            xml += "<persist-id>%s</persist-id>" % persist_id
        xml += "</commit>"
        return self.rpc(xml)

    def cancel_commit(self, persist_id=None):
        '''
        #send cancel-commit rpc
          persist_id = persist-id string
        '''
        xml = ""
        xml += "<cancel-commit>"
        if persist_id:
            xml += "<persist-id>%s</persist-id>" % persist_id
        xml += "</cancel-commit>"
        return self.rpc(xml)

    def discard_changes(self):
        '''
        #send discard-changes rpc
        '''
        xml = ""
        xml += "<discard-changes/>"
        return self.rpc(xml)

    def validate(self, source="candidate", config=None):
        '''
        #send validate rpc
          source = datastore
        '''
        xml = ""
        xml += "<validate>"
        if source.find("config") != -1:
            xml += "<source><config>%s</config></source>" % config
        else:
            xml += "<source><%s/></source>" % source
        xml += "</validate>"
        return self.rpc(xml)

    def create_subscription(self, stream_from=None,
                            filter_string=None,
                            filter_type=None,
                            start_time=None,
                            stop_time=None):
        '''
        #send create-subscription rpc (RFC-5277)
          stream = stream name (NETCONF/SNMP/syslog...)
          filterString = xml string or xpath string
          filterType = subtree or xpath
          startTime = Start time to replay
          stopTime = Stop time to replay
        '''
        xml = ""
        xml += "<create-subscription xmlns='%s'>" % NETCONF_NTFCN_NS
        if stream_from:
            xml += "<stream>%s</stream>" % stream_from
        if filter_string:
            if filter_type == "xpath":
                if "'" in filter_string:
                    xml += "<filter type='xpath' select=\"%s\"/>" % filter_string
                else:
                    xml += "<filter type='xpath' select='%s'/>" % filter_string
            elif filter_type == "subtree":
                xml += "<filter type='subtree'>%s</filter>" % filter_string
            xml += filter_string
        if start_time:
            xml += "<startTime>%s</startTime>" % start_time
        if stop_time:
            xml += "<stopTime>%s</stopTime>" % stop_time
        xml += "</create-subscription>"
        return self.rpc(xml)

    def waitfor_subscription(self, wait_string, timeout=600):
        '''waitfor a notification event report
        :ARGUMENTS:
            wait_string(tuple) = tuple of xpath string and namespace dict(
                                key - prefix
                                value - namespace string)
            timeout(integer) = timeout in sec.
        :Returns:
            True: if successful
            False: if unsuccessful
        '''
        status = False
        self.__wait_rept.clear()
        self.__wait_string = wait_string
        if len(self.__wait_string) != 0:
            self.__wait_rept.wait(timeout)
        if self.__wait_rept.isSet():
            status = True
            # pNote("netconf: waitfor %s received" % wait_string[0])
        else:
            pNote("netconf: waitfor timeouted:%s" % wait_string[0], "warning")
        self.__wait_string = ("", {})
        return status
    def clear_notification_buffer(self):
        '''
        clear the notification buffer
        '''
        self.__notification_list = []
        return True

    def clear_notification_print_buffer(self):
        '''
        clear the notification buffer for print
        '''
        self.__notification_list_print = []
        return True

    def get_schema(self, identifier, version_number=None, format_type=None):
        '''
        get-schama rpc
        '''
        xml = ""
        xml += "<get-schema xmlns='%s'>" % NETCONF_GETSCHEMA_NS
        xml += "<identifier>%s</identifier>" % identifier
        if version_number:
            xml += "<version>%s</version>" % version_number
        if format_type:
            xml += "<format>%s</format>" % format_type
        xml += "</get-schema>"
        return self.rpc(xml)

    @property
    def session_id(self):
        '''
        session-id
        '''
        return self.__session_id

    @property
    def send_data(self):
        '''
        previous send data
        '''
        return self.__send_data

    @property
    def response_data(self):
        '''
        netconf reply data
        '''
        return self.__response_buffer

    @property
    def notification_data(self):
        '''
        netconf notification data
        '''
        # return self.__notification_buffer
        return self.__notification_list_print

    @property
    def capability_data(self):
        '''
        netconf capabilities
        '''
        return self.__hello_buffer

    @property
    def isCOMPLD(self):
        '''
        whether rpc comannd gets ok
        '''
        return self.__isCOMPLD

    @property
    def isOpen(self):
        '''
        whether port is opened
        '''
        return self.__isOpen

    @property
    def error_message(self):
        '''
        error message
        '''
        return self.__error_message
    @property
    def current_protocol_version(self):
        '''
        protocol version
        '''
        return self.__protocol_ver