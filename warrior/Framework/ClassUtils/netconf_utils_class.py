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

"""API for operations related to NetConf Interfaces
Packages used = Requests (documentation available at http://docs.python-requests.org/)
modified by ymizugaki 2017/07/11

"""
from ast import literal_eval

import traceback
from . import netconf

class WNetConf(object):
    """WNetConf class has methods required to interact with NetConf interfaces"""

    def __init__(self):
        '''Constructor for WNetConf'''
        self.nc_manager = None

    def open(self, session_kwds):
        """
        Opens a SSH connection to a Netconf system

        :Arguments:
        The following keywords are allowed in session_kwds:
        <ip> = IP address of the system (Required)
        <nc_port> = use this tag to provide ssh port to connect to (default = 830)
        <username> = username for the ssh session (default = None)
        <password> = password for the ssh session (default = None)
        <hostkey_verify> = enables hostkey verification from ~/.ssh/known_hosts (default = True)
        belows are not used.
        <timeout> = use if you want to set timeout while connecting (default = None)
        <allow_agent> = enables querying SSH agent (default = True)
        <look_for_keys> = enables looking in the usual locations for ssh keys (default = True)
        <unknown_host_cb> = called when the server host key is not recognized (default = None)
        <key_filename> = where the private key can be found (default = None)
        <ssh_config> = enables parsing of OpenSSH configuration file (default = None)
        <device_params> = ncclient device name (default = 'default')

        :Returns:
            1. connected(bool)= True / False
        """
        nc_session = {'host': session_kwds.get('ip'),
                      'port': int(session_kwds.get('nc_port', 830)),
                      'username': session_kwds.get('username', None),
                      'password': session_kwds.get('password', None),
                      'hostkey_verify': literal_eval(session_kwds.get('hostkey_verify')),
                      'protocol_version': session_kwds.get('protocol_version', 'None')
                     }

        try:
            self.nc_manager = netconf.connect(nc_session['host'],
                                              nc_session['port'],
                                              nc_session['username'],
                                              nc_session['password'],
                                              nc_session['hostkey_verify'],
                                              nc_session['protocol_version'])
            # If connection fails return False
            if self.nc_manager is None:
                return False
        except:
            traceback.print_exc()
            return False
        return self.nc_manager.isOpen

    def close(self):
        '''Closes Netconf SSH session
        :Arguments:
            None
        :Returns:
            rpc_reply
        '''
        return self.nc_manager.close_session()

    def request_rpc(self, request):
        '''Send RPC command
        :Arguments:
            1. request = command to be sent as xml string
        :Returns:
            rpc_reply
        '''

        return self.nc_manager.rpc(request)

    def get_config(self, datastore, filter_string=None, filter_type='subtree'):
        '''Get configuration data from datastore
        :Arguments:
            1. datastore = name of datastore being queried
            2. filter_string = portion of the configuration to retrieve. None = Everything
        :Returns:
            rpc_reply
        '''
        return self.nc_manager.get_config(datastore, filter_string, filter_type)

    def edit_config(self, datastore, config,
                    default_operation=None, test_option=None, error_option=None):
        '''Load config to the datastore
        :Arguments:
            1. datastore = Name of datastore being edited
            2. config = The configuration data.
            3. default_operation = [merger | replace | none (default)]
            4. test_option = [test_then_set | set | none (default)]
            5. error_option = [stop-on-error | continue-on-error
                              | rollback-on-error | none (default)]
                    rollback-on-error depends on :rollback-on-error capability
        :Returns:
            rpc_reply
        '''
        return self.nc_manager.edit_config(target=datastore,
                                           config_string=config,
                                           default_operation=default_operation,
                                           test_option=test_option,
                                           error_option=error_option)

    def copy_config(self, source, target):
        """Create or replace an entire configuration datastore
           with the contents of another complete configuration datastore
        :Arguments:
            1. source = name of the configuration datastore to use as the source of the copy
                operation or config element containing the configuration subtree to copy.
            2. target = name of the configuration datastore to use
                         as the destination of the copy operation
        :Returns:
            rpc_reply
        """
        return self.nc_manager.copy_config(target, source)

    def delete_config(self, datastore):
        """Delete a configuration datastore

        :Arguments:
            1. datastore = name of the configuration datastore to be deleted
        :Returns:
            rpc_reply
        """
        return self.nc_manager.delete_config(datastore)

    def commit(self, confirmed=False, timeout=None, persist=None, persist_id=None):
        """Commit the candidate datastore as the device's new current configuration
        :Arguments:
            1. confirmed(bool) = Commit is reverted if there is no followup commit
                                  within the timeout interval.
            2. timeout(int seconds) = The confirm timeout (Default=600 seconds)
            3. persist = string to persistance
            4. persist-id = persist string when if specified in previous commit
        :Returns:
            rpc_reply
        """
        return self.nc_manager.commit(confirmed, timeout, persist, persist_id)

    def lock(self, datastore):
        """Lock the configuration system

        :Arguments:
            1. datastore = name of the configuration datastore to be locked
        :Returns:
            rpc_reply
        """
        return self.nc_manager.lock(datastore)

    def unlock(self, datastore):
        """Release the configuration lock

        :Arguments:
            1. datastore = name of the configuration datastore to be unlocked
        :Returns:
            rpc_reply
        """
        return self.nc_manager.unlock(datastore)

    def get(self, filter_string=None, filter_type=None):
        """Retrieve running configuration and device state information.

        :Arguments:
            1. filter = specifies the portion of the configuration to retrieve
               (by default entire configuration is retrieved)
               xpath string or xml string
        :Returns:
            rpc_reply
        """
        return self.nc_manager.get(filter_string, filter_type)

    def kill_session(self, session_id):
        """Force the termination of a NETCONF session (not the current one!)
        :Arguments:
            1. session_id = is the session identifier of the NETCONF session
                to be terminated as a string
        :Returns:
            rpc_reply
        """
        return self.nc_manager.kill_session(session_id)

    def validate(self, datastore):
        """Validate the contents of the specified configuration.
        :Arguments:
            1. datastore = the name of the configuration datastore being validated
        :Returns:
            rpc_reply
        """
        return self.nc_manager.validate(datastore)

    def cancel_commit(self, persist_id=None):
        '''
        cancel commit
        :Arguments:
            1. persist_id = persist-id which specifed in confirmed commit operation
        :Returns:
            rpc_reply
        '''
        return self.nc_manager.cancel_commit(persist_id)

    def discard_changes(self):
        '''
        discard current modify to candidate datasotre
        :Arguments:
            None
        :Returns:
            rpc_reply
        '''
        return self.nc_manager.discard_changes()

    def create_subscription(self,
                            stream_from="NETCONF",
                            filter_type=None,
                            filter_string=None,
                            start_time=None,
                            stop_time=None):
        '''
        create subscription to receive event notification
        :Arguments:
            1. stream_from = NETCONF/SNMP/syslog etc.
            2. filter_type = filter type xpath or subtree
            3. filter_string = filter string, xml string or xpath string
            4. start_time = start time
            5. stop_time = stop time
        :Returns:
            rpc_reply
        '''
        return self.nc_manager.create_subscription(stream_from,
                                                   filter_type,
                                                   filter_string,
                                                   start_time,
                                                   stop_time)

    def waitfor_subscription(self, wait_string, timeout=600):
        '''
        wait for specified notification event
        :Arguments:
            1. waitString(tuple) = tuple of xpath string and namespace dict
                                   prefix and namespace string).
             e.g.
             wait_string = ("//ns:event[./ns:eventClass/text()='fault']",
                            {'ns':'urn:ietf:params:xml:ns:netconf:notification:1.0'})
               *xpath string must include namespace prefix
            2. timeout(integer) = timeout value in second
        :Returns:
            result(bool)
        '''
        return self.nc_manager.waitfor_subscription(wait_string, timeout)

    def clear_notification_buffer(self):
        '''
        clear notification buffer
        :Arguments:
            None
        :Returns:
            always true
        '''
        return self.nc_manager.clear_notification_buffer()

    def get_schema(self, identifier, version_number=None, format_type=None):
        '''
        get-schema rpc
        :Arguments:
            1. identifier(string) = schema id (name of yang module)
            2. version_number(string) = schema version (e.g. 1.0)
            3. format_type(string) = format name (e.g. yang)
        :Returns:
            rpc reply
        '''
        return self.nc_manager.get_schema(identifier, version_number, format_type)

    def get_notification_buffer(self, notification_type=None):
        """get specified notification type from buffer
            notification_type = Event | Alarm | DB-Change | 
               any product specific notification type
                 och-notif,
                 dhcpv6-client-event etc..
        """
        templist = []
        if notification_type is not None and \
            not notification_type.lower() == "all":
            if notification_type.lower() == "event":
                notification_type = "event-notification"
            elif notification_type.lower() == "alarm":
                notification_type = "alarm-notification"
            elif notification_type.lower() == "db-change":
                notification_type = "netconf-config-change"
            for notif in self.notification_data:
                if notification_type in notif:
                    templist.append(notif)
        else:
            templist = self.notification_data
        return templist

    def clear_notification_buffer_for_print(self):
        """clear the notification print buffer
        """
        return self.nc_manager.clear_notification_print_buffer()

    @property
    def session_id(self):
        '''
        netconf session-id which is in hello message
        '''
        return self.nc_manager.session_id

    @property
    def isCOMPLD(self):
        '''
        indicates whether rpc-reply = ok (True/False)
        '''
        return self.nc_manager.isCOMPLD

    @property
    def ErrorMessage(self):
        '''
        error message when rpc command gets rpc-error
        '''
        return self.nc_manager.error_message

    @property
    def send_data(self):
        '''
        previous send data
        '''
        return self.nc_manager.send_data

    @property
    def response_data(self):
        '''
        rpc-reply data
        '''

        return self.nc_manager.response_data

    @property
    def notification_data(self):
        '''
        received event notification data
        '''
        return self.nc_manager.notification_data
