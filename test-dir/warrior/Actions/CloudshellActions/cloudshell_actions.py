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

"""This is the CloudShell Actions module that has all Cloudshell related keywords """
from Framework.Utils import config_Utils, data_Utils, file_Utils
from Framework.Utils import testcase_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_exception, print_info
import os
import time

try:
    from cloudshell.api.cloudshell_api import CloudShellAPISession as cs
except ImportError:
    print_info("{0}: Cloudshell Python Package is not installed".format(os.path.abspath(__file__)))
    print_info("Please install latest Cloudshell Python Package.")


cloud_shell = None


class CloudShellActions(object):
    '''
    Cloudshell wrapper APIs to create reservations, adding topologies and
    deletion
    '''
    def __init__(self):
        '''
        Constructor for Cloudshell Actions
        '''
        self.resultfile = config_Utils.resultfile
        self.datafile = config_Utils.datafile
        self.logsdir = config_Utils.logsdir
        self.filename = config_Utils.filename
        self.logfile = config_Utils.logfile


    def connect_to_cs(self, system_name):
        """Logs in to API host using passed user credentials and domain

        :Datafile usage:
             NA
        :Arguments:
            1. system_name(string) = Name of the system from the datafile

        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "Logon to CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        global cloud_shell
        cloud_shell = self._create_cs_obj(system_name)
        testcase_Utils.pNote("Login, cs obj-{}".format(cloud_shell), "info")

        status = False
        if cloud_shell is not None:
            testcase_Utils.pNote("\n\n *** Login to Cloudshell System-{}"
                                 " successfull, domain-{}\n".\
                                 format(cloud_shell.host,\
                                 cloud_shell.domain), "info")
            status = True
        else:
            testcase_Utils.pNote("\n\n *** Login to Cloudshell System"
                                 " failed\n", "warning")

        testcase_Utils.report_substep_status(status)
        return status


    def cs_logoff(self):
        """To logoff from CS

        :Datafile usage:
             NA
        :Arguments:
             NA
        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "To logoff from CS"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        status = False
        testcase_Utils.pNote("cs_logoff, cs obj-{}".format(cloud_shell), "info")
        xml_resp = cloud_shell.Logoff()

        if xml_resp is not None:
            testcase_Utils.pNote("\n\n *** Cloudshell LogOff successfull-%s"
                                 % (cloud_shell.host), "info")
            status = True
        else:
            testcase_Utils.pNote("\n\n *** Cloudshell LogOff failed-%s"
                                 % (cloud_shell.host), "warning")

        testcase_Utils.report_substep_status(status)
        return status

    def cs_create_reservation(self, system_name, reservation_name,
                              duration_in_mins, notify_on_start, notify_on_end,
                              notify_mins_before_end):
        """
        Defines a reservation to be created.

        This keyword only defines the reservation with all its details by saving
        the details in the data repository. Actual creation is done by using the
        cs_add_topology_to_reservation keyword by providing the reservation name
        to it.

        :Datafile usage:
            Tags or attributes to be used in input datafile for the system
            or subsystem.If both tag and attribute is provided the attribute
            will be used.
            1. username   = name of the cloudshell user

        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. duration_in_mins(int) = Specify the length of the reservation.
            4. notify_on_start(bool) = Indicate whether to notify the
               reservation owner when the reservation starts.
            5. notify_on_end(bool) = Indicate whether to notify the reservation
               owner when the reservation ends.
            6. notify_mins_before_end(int) = Notification Minutes Before End -
               Indicate the number of minutes before the end of the reservation
               to send out a Notify On End alert to the reservation owner.
               (0 = disabled)

        :Returns:
            1. status(bool)= True/False
            2. output_dict = consists of following key value pairs:
               1. domain_id: Domain Id returned after login to cloudshell.
               2. reservation_id: Reservation Id returned after successful
                  creation of resources.
        """

        wdesc = "Save reservation details for the reservation name provided"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("save reservation, cs obj-{}".\
                             format(cloud_shell), "info")

        keys_for_credentials = ['username']
        credentials = data_Utils.get_credentials(self.datafile, system_name,
                                                 keys_for_credentials)

        status = True
        output_dict = {}
        try:
            pNote("This keyword will only collect the reservation information "\
                  "and save the details in data repository.\n")
            pNote("In order to create reservation in cloudshell, execute this keyword and then "\
                  "use the keyword 'cs_add_topology_to_reservation' and provide the "\
                  "reservation_name to it, 'cs_add_topology_to_reservation' keyword will use "\
                  "the reservation  details for he reservation_name provided, create a "\
                  "reservation and add topology to the reservation.")

            res_key = "{0}_{1}_cs_rsrv_details".format(system_name, reservation_name)
            output_dict = {
                           res_key: {"reservation_name": reservation_name,
                                     "username": credentials['username'],
                                     "duration": duration_in_mins,
                                     "notify_on_start": notify_on_start,
                                     "notify_on_end": notify_on_end,
                                     "notify_mins_before_end": notify_mins_before_end
                                     }
                           }

        except Exception as exception:
            pNote("Saving reservation details for reservation_name={0} failed!!"\
                  .format(reservation_name))
            print_exception(exception)
            status = False
        else:
            pNote("Sucessfully saved reservation details for reservation_name={0}"\
                  .format(reservation_name))

        testcase_Utils.report_substep_status(status)
        return status, output_dict


    def cs_create_topology_reservation(self, system_name, reservation_name,
                              duration_in_mins, notify_on_start, notify_on_end,
                              notify_mins_before_end, topology_full_path):
        """Defines a reservation to be started immediately

        :Datafile usage:
            Tags or attributes to be used in input datafile for the system
            or subsystem.If both tag and attribute is provided the attribute
            will be used.
            1. username   = name of the cloudshell user

        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. duration_in_mins(int) = Specify the length of the reservation.
            4. notify_on_start(bool) = Indicate whether to notify the
               reservation owner when the reservation starts.
            5. notify_on_end(bool) = Indicate whether to notify the reservation
               owner when the reservation ends.
            6. notify_mins_before_end(int) = Notification Minutes Before End -
               Indicate the number of minutes before the end of the reservation
               to send out a Notify On End alert to the reservation owner.
               (0 = disabled)
            7. topology_full_path(string) = Specify the full topology name. Include
               the full path from the root to the topology, separated by slashes.
               For example: FolderName/Topologies/TopologyName

        :Returns:
            1. status(bool)= True/False
            2. output_dict = consists of following key value pairs:
               1. domain_id: Domain Id returned after login to cloudshell.
               2. reservation_id: Reservation Id returned after successful
                  creation of resources.
        """

        wdesc = "Create Topology Reservation in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_create_topology_reservation, cs obj-{}".\
                             format(cloud_shell), "info")

        keys_for_credentials = ['username']
        credentials = data_Utils.get_credentials(self.datafile, system_name,
                                                 keys_for_credentials)

        status = False
        output_dict = {}
        try:
            xml_resp = cloud_shell.CreateImmediateTopologyReservation(reservation_name,
                                                              credentials['username'],
                                                              int(duration_in_mins),
                                                              notify_on_start,
                                                              notify_on_end,
                                                              int(notify_mins_before_end),
                                                              topology_full_path)
            if xml_resp is not None:
                reservation_id = xml_resp.Reservation.Id
                output_dict = {'domain_id': cloud_shell.domain,
                               '{0}_{1}_reservationId'.
                               format(system_name, reservation_name): reservation_id}
                testcase_Utils.pNote("\n\n *** Cloudshell CreateTopologyReservation"
                                     " successfull for ResName-\"{}\" ResId-{}\n".\
                                     format(reservation_name,
                                            output_dict['{0}_{1}_reservationId'.\
                                                        format(system_name, reservation_name)]),
                                     "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell CreateTopologyReservation"
                                     " failed for \"{}\"".format(reservation_name),
                                     "warning")
        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status, output_dict

    def cs_add_topology_to_reservation(self, system_name, reservation_name, topology_full_path):
        """
        Create the reservation and add topology to the reservation in Cloudshell

        :Datafile usage:
             NA
        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. topology_full_path(string) = Specify the full topology name. Include
               the full path from the root to the topology, separated by slashes.
               For example: FolderName/Topologies/TopologyName

        :Returns:
            1. status(bool)= True/False
        """
        wdesc = "Create the reservation and add Topology to Reservation in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        status = True
        res_key = "{0}_{1}_cs_rsrv_details".format(system_name, reservation_name)
        res_details = data_Utils.get_object_from_datarepository(res_key)
        output_dict = {}

        if res_details:
            username = res_details["username"]
            reservation_name = res_details["reservation_name"]
            duration = int(res_details["duration"])
            notify_on_start = res_details["notify_on_start"]
            notify_on_end = res_details["notify_on_end"]
            notify_mins_before_end = int(res_details["notify_mins_before_end"])
            try:
                xml_resp = cloud_shell.CreateImmediateTopologyReservation(reservation_name,
                                                                          username,
                                                                          duration,
                                                                          notify_on_start,
                                                                          notify_on_end,
                                                                          notify_mins_before_end,
                                                                          topology_full_path)
                if xml_resp is not None:
                    reservation_id = xml_resp.Reservation.Id
                    output_dict = {'domain_id': cloud_shell.domain,
                                   '{0}_{1}_reservationId'.
                                   format(system_name, reservation_name): reservation_id}

                    testcase_Utils.pNote("\n\n *** Cloudshell CreateReservation"
                                         " successful for ResName-\"{}\" ResId-{}\n".\
                                         format(reservation_name,
                                                output_dict['{0}_{1}_reservationId'.\
                                                            format(system_name,
                                                                   reservation_name)]),
                                         "info")

                    testcase_Utils.pNote("\n\n *** Cloudshell Add Topology \"{}\""
                                         " successful for \"{}\"\n".\
                                         format(topology_full_path, reservation_name),
                                         "info")

                else:
                    testcase_Utils.pNote("\n\n *** Cloudshell CreateReservation"
                                         " failed for \"{}\"".format(reservation_name),
                                         "warning")

                    testcase_Utils.pNote("\n\n *** Cloudshell Add Topology \"{}\""
                                         " failed for \"{}\"".\
                                         format(topology_full_path, reservation_name),
                                         "warning")
                    status = False
            except Exception as exception:
                print_exception(exception)
                status = False
        else:
            pNote("Details for reservation_name={0}, for sysem={1} "\
                  "not found in data repository. Please make sure "\
                  "to execute the keyword '{2}' before this"\
                  "step".format(reservation_name, system_name, 'cs_create_reservation'),
                  "warning")
            status = False

        testcase_Utils.report_substep_status(status)
        return status, output_dict




    def cs_activate_topology(self, system_name, reservation_name,
                             topology_full_path, time_out=60):
        """Activate Topology to reservation in Cloudshell

        :Datafile usage:
             NA
        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. topology_path(string) = Specify the full topology name. Include
               the full path from the root to the topology, separated by slashes.
               For example: FolderName/Topologies/TopologyName
            4. time_out(int): Before activating topology, we need to check status
                of the reservation. If it is started, then we need to activate the
                topology.
                Need to wait for some time before activating topology for
                reservation status to get started, making the default value of
                time_out as 60 sec and can change the value depending on number
                of resources.
        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "Activate Topology to Reservation in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_activate_topology, cs obj-{}".\
                             format(cloud_shell), "info")

        status = True
        cs_res_id = data_Utils.get_object_from_datarepository\
                    (system_name+"_"+reservation_name+"_reservationId")

        #Before entering try block to activate the topology,
        #check whether Reservation status is Started. If status is not Started,
        #then wait for time_out seconds before activating.

        reservation_status = cloud_shell.GetReservationDetails(cs_res_id).ReservationDescription.Status
        sec = 0
        while reservation_status != "Started":
            sec = sec + 1
            reservation_status = cloud_shell.GetReservationDetails(cs_res_id).ReservationDescription.Status
            time.sleep(1)
            if sec == int(time_out):
                testcase_Utils.pNote("Waited for {0} seconds, the current reservation"
                                     " status is {1}, but the"
                                     " expected status is Started".\
                                     format(int(time_out), reservation_status),
                                     "warning")
                status = False
                break
        if status:
            try:
                xml_resp = cloud_shell.ActivateTopology(cs_res_id, topology_full_path)
                if xml_resp is not None:
                    testcase_Utils.pNote("\n\n *** Cloudshell Activate Topology-\"{}\""
                                         " successfull for \"{}\"\n".\
                                         format(topology_full_path, reservation_name),\
                                         "info")
                else:
                    testcase_Utils.pNote("\n\n *** Cloudshell Activate Topology-\"{}\""
                                         " failed for \"{}\"".\
                                         format(topology_full_path, reservation_name),
                                         "warning")
                    status = False
            except Exception as exception:
                print_exception(exception)
                status = False
        testcase_Utils.report_substep_status(status)
        return status

    def cs_disconnect_routes(self, system_name, reservation_name, first_endpoint, second_endpoint):

        """Disconnects the routes in the cloud shell

        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. first_endpoint(str) = The first endpoint of the two end points
            4. second_endpoint(str) = The second endpoint of the two end points
        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "Disconnect Routes in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_disconnect_routes, cs obj-{}".\
                             format(cloud_shell), "info")

        endpoints = [first_endpoint, second_endpoint]

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository\
                (system_name+"_"+reservation_name+"_reservationId")
        try:
            xml_resp = cloud_shell.DisconnectRoutesInReservation(cs_res_id, endpoints)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Cloudshell Disconnect Routes"
                                     " successfull for \"{}\"\n".\
                                     format(reservation_name), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell Disconnect Routes"
                                     " failed for \"{}\"".\
                                     format(reservation_name), "warning")

        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status

    def cs_connect_routes(self, system_name, reservation_name, first_endpoint, second_endpoint, mapping_type):

        """Connects the routes in the cloud shell

        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. first_endpoint(str) = The first endpoint of the two end points
            4. second_endpoint(str) = The second endpoint of the two end points
            5. mapping_type(str) = Specify bi-directional or uni-directional as the mapping type
        :Returns:
            1. status(bool) = True/False
        """

        wdesc = "Connect Routes in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_connect_routes, cs obj-{}".\
                             format(cloud_shell), "info")

        endpoints = [first_endpoint, second_endpoint]

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository\
                (system_name+"_"+reservation_name+"_reservationId")
        try:
            xml_resp = cloud_shell.ConnectRoutesInReservation(cs_res_id, endpoints, mapping_type)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Cloudshell Connect Routes"
                                     " successfull for \"{}\"\n".\
                                     format(reservation_name), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell Connect Routes"
                                     " failed for \"{}\"".\
                                     format(reservation_name), "warning")

        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status


    def cs_remove_route_from_reservation(self, system_name, reservation_name,
                                          first_endpoint, second_endpoint,
                                          mapping_type):

        """Disconnects two endpoints and removes the mapped route between
           them

        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. first_endpoint(str) = The first endpoint of the two end points
            4. second_endpoint(str) = The second endpoint of the two end points
            5. mapping_type(string) = Specify bi-directional or uni-directional
               as the mapping type
        :Returns:
            1. status(bool) = True/False
        """

        wdesc = "Remove Route From Reservation in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_remove_route_from_reservation, cs obj-{}".
                             format(cloud_shell), "info")

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository(
                system_name+"_"+reservation_name+"_reservationId")
        list_of_endpoints = [first_endpoint, second_endpoint]
        try:
            xml_resp = cloud_shell.RemoveRoutesFromReservation(
                cs_res_id, list_of_endpoints, mapping_type)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Cloudshell Remove Route From"
                                     " Reservation successfull for \"{}\"\n".
                                     format(reservation_name), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell Remove Route From"
                                     " Reservation failed for \"{}\"".
                                     format(reservation_name), "warning")

        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status


    def cs_create_route_in_reservation(self, system_name, reservation_name,
                                       source_resource_full_path,
                                       target_resource_full_path,
                                       override_active_routes,
                                       mapping_type, max_hops, route_alias,
                                       is_shared):

        """Creates routes between the specified source and target resources.

        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. source_resource_full_path(string) = Specify the source resource
                full path
            4. target_resource_full_path(string) = Specify the target resource
                full path
            5. mapping_type(string) = Specify bi-directional or uni-directional
               as the mapping type
            6. max_hops(integer) = The maximum number of allowed hops.
            7. route_alias(string) = Specify the route alias
            8. override_active_routes(bool) = Specify whether the new route
                can override existing routes.
            9. is_shared(bool) = Specify whether these routes are shared.
        :Returns:
            1. status(bool) = True/False
        """

        wdesc = "Create Route In Reservation in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_create_route_in_reservation, cs obj-{}".
                             format(cloud_shell), "info")

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository(
                    system_name+"_"+reservation_name+"_reservationId")
        try:
            xml_resp = cloud_shell.CreateRouteInReservation(
                       cs_res_id, source_resource_full_path,
                       target_resource_full_path,  override_active_routes, 
                       mapping_type, int(max_hops), route_alias, is_shared)

            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Cloudshell Create Route In"
                                     " Reservation successfull for \"{}\"\n".
                                     format(reservation_name), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell Create Route In"
                                     " Reservation failed for \"{}\"".
                                     format(reservation_name), "warning")

        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status

    def cs_remove_routes_from_reservation(self, system_name, reservation_name,
                                          list_of_endpoints, mapping_type):

        """Disconnects a list of endpoints and removes the mapped route between
           them

        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. list_of_endpoints(list) = The list of endpoints which needs to
               be removed
            4. mapping_type(string) = Specify bi-directional or uni-directional
               as the mapping type
        :Returns:
            1. status(bool) = True/False
        """

        wdesc = "Remove Routes From Reservation in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_remove_routes_from_reservation, cs obj-{}".\
                             format(cloud_shell), "info")

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository\
                (system_name+"_"+reservation_name+"_reservationId")
        try:
            xml_resp = cloud_shell.RemoveRoutesFromReservation(cs_res_id,
                                                list_of_endpoints, mapping_type)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Cloudshell Remove Routes From"
                                     " Reservation successfull for \"{}\"\n".\
                                     format(reservation_name), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell Remove Routes From"
                                     " Reservation failed for \"{}\"".\
                                     format(reservation_name), "warning")

        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status

    def cs_create_routes_in_reservation(self, system_name, reservation_name,
                                        list_of_source_resources,
                                        list_of_target_resources,
                                        override_active_routes,
                                        mapping_type, max_hops, route_alias,
                                        is_shared):

        """Creates routes between the listed source and target resources.
            Routes will be created for each pair of source and target resources

        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. list_of_source_resources(list) = The list of source resource
                names.
            4. list_of_target_resources(list) = The list of target resource
                names.
            5. override_active_routes(bool) = Specify whether the new route
                can override existing routes.
            6. mapping_type(string) = Specify bi-directional or uni-directional
               as the mapping type
            7. max_hops(integer) = The maximum number of allowed hops.
            8. route_alias(string) = Specify the route alias
            9. is_shared(bool) = Specify whether these routes are shared.
        :Returns:
            1. status(bool) = True/False
        """

        wdesc = "Create Routes In Reservation in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_create_routes_in_reservation, cs obj-{}".\
                             format(cloud_shell), "info")

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository\
                (system_name+"_"+reservation_name+"_reservationId")
        try:
            xml_resp = cloud_shell.CreateRoutesInReservation(cs_res_id,
                                                list_of_source_resources,
                                                list_of_target_resources,
                                                override_active_routes,
                                                mapping_type, int(max_hops),
                                                route_alias,
                                                is_shared)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Cloudshell Create Routes In"
                                     " Reservation successfull for \"{}\"\n".\
                                     format(reservation_name), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell Create Routes In"
                                     " Reservation failed for \"{}\"".\
                                     format(reservation_name), "warning")

        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status

    def cs_end_reservation(self, system_name, reservation_name, unmap):
        """End the reservation in Cloudshell

        :Datafile usage:
             NA
        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. unmap(bool) = Unmap resources - Specify whether to keep mappings
               or release mapped resources when deleting the reservation.
        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "End Reservation in CloudShell API Host"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_end_reservation, cs obj-{}".\
                             format(cloud_shell), "info")

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository\
                   (system_name+"_"+reservation_name+"_reservationId")
        try:
            xml_resp = cloud_shell.EndReservation(cs_res_id, unmap)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Cloudshell End reservation"
                                     " successfull for \"{}\"\n".\
                                     format(reservation_name), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell End Reservation"
                                     " failed for \"{}\"".\
                                     format(reservation_name), "warning")

        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status


    def cs_add_users_to_reservation(self, system_name, reservation_name, list_of_usernames):
        """Add one or more permitted users to the specified reservation.

        :Datafile usage:
             NA
        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.
            3. list_of_usernames(list) = list of usernames to permit access to
               reservation.
               For example: To add many users to access the reservation
                            list_of_usernames = ['user1','user2','userx']

        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "Add one or more permitted users to the reservation"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        testcase_Utils.pNote("cs_add_users_to_reservation, cs obj-{}".\
                             format(cloud_shell), "info")

        usernames = list_of_usernames[0:]
        testcase_Utils.pNote("cs_add_users_to_reservation, res_name-{},"\
                             "users-{}".format(reservation_name, usernames))

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository\
                    (system_name+"_"+reservation_name+"_reservationId")
        try:
            xml_resp = cloud_shell.AddPermittedUsersToReservation(cs_res_id,\
                                                                  usernames)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Cloudshell Add users \"{}\" to"
                                     "reservation successfull".\
                                     format(usernames), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Cloudshell Add users \"{}\" to"
                                     "Reservation failed".format(usernames),
                                     "warning")
        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status


    #Get Utility Methods
    def cs_get_topo_details(self, topology_path):
        """To get the Cloudshell topology details for a given path

        :Datafile usage:
             NA
        :Arguments:
            1. topology_path(string) = Specify the full topology name. Include
               the full path from the root to the topology, separated by slashes.
               For example: FolderName/Topologies/TopologyName

        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "To get the Cloudshell topology details for a given path"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        status = False
        testcase_Utils.pNote("cs_get_topo_details, cs obj-{}".\
                             format(cloud_shell), "info")
        try:
            xml_resp = cloud_shell.GetTopologyDetails(topology_path)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Get Topolopy \"%s\" successfull\n"\
                                     % (topology_path), "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Get Topolopy \"%s\" failed\n"\
                                     % (topology_path), "warning")
        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status


    def cs_get_current_reservation(self, reservation_owner):
        """Retrieves current reservations for the specified owner

        :Datafile usage:
             NA
        :Arguments:
            1. reservation_owner(string) = Specify the user name of the
               reservation owner.

        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "To retrieve current reservations for the specified owner"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        status = False
        testcase_Utils.pNote("cs_get_current_reservation, cs obj-{}".\
                             format(cloud_shell), "info")
        try:
            xml_resp = cloud_shell.GetCurrentReservations(reservation_owner)

            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Get current reservation for "
                                     "\"(%s)\" successfull\n" % (reservation_owner),\
                                     "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Get current reservation for "
                                     "\"(%s)\" failed\n" % (reservation_owner),\
                                     "warning")
        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status


    def cs_get_reservation_details(self, system_name, reservation_name):
        """Retrieves all details and parameters for a specified reservation

        :Datafile usage:
             NA
        :Arguments:
            1. system_name(string) = Name of the UAP system from the datafile
            2. reservation_name(string) = Specify the name of the reservation.

        :Returns:
            1. status(bool)= True/False
        """

        wdesc = "To retrieve all details and parameters for a specified"\
                "reservation"
        testcase_Utils.pSubStep(wdesc)
        testcase_Utils.pNote(file_Utils.getDateTime())

        status = False
        cs_res_id = data_Utils.get_object_from_datarepository\
                    (system_name+"_"+reservation_name+"_reservationId")
        testcase_Utils.pNote("cs_get_reservation_details, cs obj-{}".\
                             format(cloud_shell), "info")
        try:
            xml_resp = cloud_shell.GetReservationDetails(cs_res_id)
            if xml_resp is not None:
                testcase_Utils.pNote("\n\n *** Get reservation details for "
                                     "\"(%s)\" successfull\n" % (reservation_name),\
                                     "info")
                status = True
            else:
                testcase_Utils.pNote("\n\n *** Get reservation details for "
                                     "\"(%s)\" failed\n" % (reservation_name),\
                                     "warning")
        except Exception as exception:
            print_exception(exception)

        testcase_Utils.report_substep_status(status)
        return status



    #Helper Methods
    def _create_cs_obj(self, system_name):
        '''Initializes the CloudShell object and logons to cloudshell
        returns the cloudshell object
        '''
        keys_for_credentials = ['ip', 'cloudshell_port', 'username',
                                'password', 'domain']
        credentials = data_Utils.get_credentials(self.datafile, system_name,
                                                 keys_for_credentials)

        return cs(credentials['ip'], credentials['username'],
                  credentials['password'], credentials['domain'])


    def _get_reservation_id(self, responseObject, topology):
        '''Fetch the reservation id from the xml response of get current
           reservation
        returns the cloudshell reservation id
        '''
        for attr, value in responseObject.__dict__.iteritems():
            for val in value:
                topo1 = val.Topologies[0]
                topo2 = topo1.split("/", 2)
                topo = topo2[2]
                if topo == topology.split("/", 2)[2]:
                    return val.Id
