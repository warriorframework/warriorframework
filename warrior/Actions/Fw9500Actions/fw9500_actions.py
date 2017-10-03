"""fw9500_actions module where keywords"""
import time
import Framework.Utils as Utils
import os
from Framework.Utils.print_Utils import print_info
from Framework.Utils.testcase_Utils import pNote
from Actions.CliActions.cli_actions import CliActions


class CdsActions(object):
    """class CdsActions having methods (keywords) that are common for all the products"""

    def __init__(self):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile

    def login(self, system_name, session_name=None):
        """
        Login to the Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Login to the Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "login"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Logged in successfully")

        else:
            pNote("Login failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict


    def logout(self, system_name, session_name=None):
        """
        Logout of the Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Logout of the Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "logout"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Logged out successfully")

        else:
            pNote("Logout failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict


    def set_tid(self, system_name, session_name=None):
        """
        Set target identifier in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Set target identifier in the  Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "set_tid"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Logged out successfully")

        else:
            pNote("Logout failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def create_users(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Create users in the  Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "create_users"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Users created successfully")

        else:
            pNote("Creating users failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def delete_users(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Create users in the  Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "delete_users"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Users created successfully")

        else:
            pNote("Creating users failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def provision_cards(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision cards in fw9500"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_cards"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Card provisioned successfully")

        else:
            pNote("Card provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def provision_sfp(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision sfp in fw9500"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_sfp"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("sfp provisioned successfully")

        else:
            pNote("sfp provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def provision_eth(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision  eth in fw9500"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_eth"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Eth provisioned successfully")

        else:
            pNote("Eth provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def deprovision_eqpt(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "deprovision cards, sfp, eth in fw9500"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "deprovision_eqpt"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Eqpt deprovisioned successfully")

        else:
            pNote("Eqpt deprovisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def provision_link_protection(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision LAG in FW9500"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_link_protection"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("LAG provisioned successfully")

        else:
            pNote("LAG provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def deprovision_link_protection(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Deprovision LAG in FW9500"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "deprovision_link_protection"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("LAG de-provisioned successfully")

        else:
            pNote("LAG de-provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def provision_vlan(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision Vlan in FW9500"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_vlan"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Vlan provisioned successfully")

        else:
            pNote("Vlan provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def deprovision_vlan(self, system_name, session_name=None):
        """
        Create users in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Deprovision Vlan in FW9500"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "deprovision_vlan"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("Vlan de-provisioned successfully")

        else:
            pNote("Vlan de-provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

##

##



    def provision_ports(self, system_name):
        """Provision ports in fwcds switch

        :Arguments:
            1. system_name(string) = name of the system from the system datafile

        :Returns:
            1. status (bool)
        """

        WDesc = "Provisioning ports in FWCDS switch"
        Utils.testcase_Utils.pSubStep(WDesc)
        status = True
        client_port_list = ["1-1-1"]
        network_port_list = ["1-1-25", "1-2-25"]

        pNote("\n")
        pNote("++++++    Start provisioning ports on {0}    ++++++".format(system_name))
        for port in client_port_list:
            pNote("Provisioning client port {0}".format(port))
            pNote("port {0} created".format(port))
            time.sleep(.5)

        for port in network_port_list:
            pNote("Provisioning network port {0}".format(port))
            pNote("port {0} created".format(port))
            time.sleep(.5)

        pNote("\n")
        pNote("Creating 1 to 1 protected links")
        pNote("Creating protected group {0}".format("1-LAG-1"))
        pNote("Protection group {0} created".format("1-LAG-1"))
        pNote("port {0} is the primary link".format("1-1-25"))
        pNote("port {0} is the secondary link".format("1-2-25"))

        pNote(" ++++++    Provisioning ports on {0} completed successfully    ++++++".format(system_name))


        Utils.testcase_Utils.report_substep_status(status)
        return status

    def deprovision_ports(self, system_name):
        """Deprovision ports in fwcds switch

        :Arguments:
            1. system_name(string) = name of the system from the system datafile

        :Returns:
            1. status (bool)
        """

        WDesc = "Deprovision ports in FWCDS switch"
        Utils.testcase_Utils.pSubStep(WDesc)
        status = True
        client_port_list = ["1-1-1"]
        network_port_list = ["1-1-25", "1-2-25"]

        pNote("\n")
        pNote("++++++    Start Deprovisioning ports on {0}    ++++++".format(system_name))

        pNote("Deleting 1 to 1 protected links")
        pNote("Deleting protected group {0}".format("1-LAG-1"))
        pNote("Protection group {0} deleted".format("1-LAG-1"))

        pNote("\n")

        for port in client_port_list:
            pNote("Deprovision client port {0}".format(port))
            pNote("port {0} deleted".format(port))
            time.sleep(.5)

        for port in network_port_list:
            pNote("Deprovision network port {0}".format(port))
            pNote("port {0} deleted".format(port))
            time.sleep(.5)




        pNote("++++++    Deleted ports on {0} completed successfully    ++++++".format(system_name))


        Utils.testcase_Utils.report_substep_status(status)
        return status

    def provision_vlans(self, system_name):
        """Configure vlans in fwcds switch

        :Arguments:
            1. system_name =

        :Returns:
            1. status (bool)
        """

        WDesc = "Provision vlans in FWCDS switch"
        Utils.testcase_Utils.pSubStep(WDesc)
        status = True
        client_port_list = ["1-1-1"]
        network_port_list = ["1-LAG-1"]
        vlanid = "100"
        client_tpid = "8100"
        network_tpid = "88a8"


        pNote("\n")
        pNote("++++++    Start provisioning vlans on {0}    ++++++".format(system_name))

        for port in client_port_list:
            pNote("Assigning vlan {0} to port {1}..".format(vlanid, port))
            pNote("vlan {0} assigned".format(vlanid))

            time.sleep(.5)

        for port in network_port_list:
            pNote("Assigning vlan {0} to port {1}..".format(vlanid, port))
            pNote("vlan {0} assigned".format(vlanid))
            time.sleep(.5)

        pNote("++++++    Provisioning vlans on {0} completed successfully    ++++++".format(system_name))


        Utils.testcase_Utils.report_substep_status(status)
        return status

    def deprovision_vlans(self, system_name):
        """Deprovision vlans in fwcds switch

        :Arguments:
            1. system_name =

        :Returns:
            1. status (bool)
        """

        WDesc = "Deprovision vlans in FWCDS switch"
        Utils.testcase_Utils.pSubStep(WDesc)
        status = True
        client_port_list = ["1-1-1"]
        network_port_list = ["1-LAG-1"]
        vlanid = "100"
        client_tpid = "8100"
        network_tpid = "88a8"


        pNote("\n")
        pNote("++++++    Start Deprovisioning vlans on {0}    ++++++".format(system_name))

        for port in client_port_list:
            pNote("Deleting vlan {0} from port {1}..".format(vlanid, port))
            pNote("vlan {0} deleted".format(vlanid))

            time.sleep(.5)

        for port in network_port_list:
            pNote("Deleting vlan {0} from port {1}..".format(vlanid, port))
            pNote("vlan {0} deleted".format(vlanid))
            time.sleep(.5)

        pNote("++++++    Deprovisioning vlans on {0} completed successfully    ++++++".format(system_name))


        Utils.testcase_Utils.report_substep_status(status)
        return status

    def verify_switch_to_protect(self):
        """
        Retrieve events from the NE and verify
        that the event denoting switch over to protect
        link is raised

        :Arguments:
            1. system_name =

        :Returns:
            1. status (bool)
        """

        WDesc = "Verify event for switch over to protect link"
        Utils.testcase_Utils.pSubStep(WDesc)
        status = True
        pNote("\n")
        pNote("Verifying events/conditions raised in the network element")
        pNote("Sending command RTRV-AO to get the events raised")
        pNote("Response:")
        pNote(">")
        pNote("SV-FWCDS-SHLF-01")
        pNote("A  000824 REPT EVT LAGPORT")
        pNote("1-1-25:WKSWPR,TC,,,NEND,NA,,,:\"Switched from Working to Protection\",,,")
        pNote(";")
        pNote(">")
        pNote("\n")
        pNote("Switch over from work link to protect link was successful")


        Utils.testcase_Utils.report_substep_status(status)
        return status










    def provision_shelf(self, system_name, session_name=None):
        """
        Provision shelf in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision shelf in the  Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_shelf"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("shelf provisioned successfully")

        else:
            pNote("shelf provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def provision_eqpt(self, system_name, session_name=None):
        """
        Provision eqpt(shelf, card, sfp) in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision eqpt(shelf, card, sfp) in the  Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_eqpt"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("eqpt provisioned successfully")

        else:
            pNote("eqpt provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def provision_mvlan(self, system_name, session_name=None):
        """
        Provision mvlans in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision mvlans in the  Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_mvlan"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("mvlan provisioned successfully")

        else:
            pNote("mvlan provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def enable_ssh(self, system_name, session_name=None):
        """
        Enable ssh in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Enable ssh in the  Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "enable_ssh"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("ssh enabled successfully")

        else:
            pNote("enabing ssh failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def provision_lcn_ip(self, system_name, session_name=None):
        """
        Provision lcn ip in the  Fujitsu network element

        :Arguments:
            1. system_name(string) = name of the system/subsystem from the input datafile
            2. cmd_set_title(string) = title of the testdata block from which commands will be sent
            3. session_name = name of the session to the system/subsystem
        """
        WDesc = "Provision lcn ip in the  Fujitsu network element"
        Utils.testcase_Utils.pSubStep(WDesc)
        output_dict = {}
        title = "provision_lcn_ip"

        status, td_dict = CliActions().send_commands_by_testdata_title(title, system_name,
                                                                       session_name=session_name)

        if status:
            pNote("LCN provisioned successfully")

        else:
            pNote("LCN provisioning failed")


        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict
