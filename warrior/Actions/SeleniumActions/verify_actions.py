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

""" Selenium keywords for Verify Actions """
from Framework.ClassUtils.WSelenium.verify_operations import VerifyOperations
from Framework.ClassUtils.json_utils_class import JsonUtils

try:
    import json
    import os
    import sys
    import re
    import getopt
    import datetime
    import Framework.Utils as Utils
except ImportWarning:
     raise ImportError

from Framework.Utils import data_Utils
from Framework.Utils.testcase_Utils import pNote, pSubStep
from Framework.Utils import xml_Utils
from Framework.Utils import selenium_Utils


class wait_actions(object):

    def __init__(self):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.jsonobj = JsonUtils()
        self.verify_oper_object = VerifyOperations()

    def verify_page_by_property(self, system_name, expected_value, value_type,
                                browser_name="all", element_config_file=None,
                                element_tag=None):
        """
        This keyword will verify page by property.

        :Datafile Usage:

            Tags or attributes to be used in input datafile for the system or
            subsystem. If both tag and attribute is provided the attribute will
            be used.

            1. system_name = This attribute can be specified in the datafile as
                             a <system> tag directly under the <credentials>
                             tag. An attribute "name" has to be added to this
                             tag and the value of that attribute would be taken
                             in as value to this keyword attribute.

                             <system name="name_of_thy_system"/>

            2. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            3. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            4. expected_value = This <expected_value> tag is a child og the
                                <browser> tag in the data file. This tag would
                                contain the the value you expect the browser to
                                have. This can be either a  url, page title,
                                page source, or page name

                    Eg: <expected_value>http://www.google.com</expected_value>

            5. value_type = This <value_type> tag is a child of the <browser>
                            tag in the data file. This tag would contain the
                            type of browser information that you want to verify.
                            It can either be current_url, title, name, or
                            page_source

                            Eg: <value_type>title</value_type>

            6. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/selenium_config.json
                                      </element_config_file>

            7. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information to
                             that element. If you want to use this one element
                             through out the testcase for a particular browser,
                             you can include it in the data file. If this not
                             the case, then you should create an argument tag
                             in the relevant testcase step and add the value
                             directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag" value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. expected_value (str) = The expected value of the information
                                      retrieved from the web page.
            3. value_type (str) = Type of page information that you wat to
                                  verify: current_url, name, title, or
                                  page_source
            4. browser_name(str) = Unique name for this particular browser
            5. url(str) = URL to which the browser should be directed
            6. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            7. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will verify page by {0}".format(value_type)
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}

        system = xml_Utils.getElementWithTagAttribValueMatch(self.datafile,
                                                             "system",
                                                             "name",
                                                             system_name)
        browser_list = system.findall("browser")
        try:
            browser_list.extend(system.find("browsers").findall("browser"))
        except AttributeError:
            pass

        if not browser_list:
            browser_list.append(1)
            browser_details = arguments

        for browser in browser_list:
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments, self.datafile, browser)
            if browser_details == {}:
                browser_details = selenium_Utils.\
                    get_browser_details(browser, self.datafile, **arguments)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    obtained_value = self.verify_oper_object.get_page_property(current_browser, browser_details["value_type"])
                    if str(obtained_value) == expected_value:
                        pNote("The obtained {0}: {1} matches the expected "
                              "value: {2}. Verification success!".
                              format(value_type, obtained_value,
                                     expected_value))
                    else:
                        pNote("The obtained {0}: {1} does not match the "
                              "expected value: {2}. Verification failed!".
                              format(value_type, obtained_value,
                                     expected_value), "Error")
                        status = False
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def verify_alert_is_present(self, system_name, action="accept",
                                browser_name="all", element_config_file=None,
                                element_tag=None):
        """
        This keyword will verify page by property.

        :Datafile Usage:

            Tags or attributes to be used in input datafile for the system or
            subsystem. If both tag and attribute is provided the attribute will
            be used.

            1. system_name = This attribute can be specified in the datafile as
                             a <system> tag directly under the <credentials>
                             tag. An attribute "name" has to be added to this
                             tag and the value of that attribute would be taken
                             in as value to this keyword attribute.

                             <system name="name_of_thy_system"/>

            2. browser_name = This <browser_name> tag is a child of the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            3. action = This contains the information of what action needs to
                        be performed on the alert. It can be either accept or
                        dismiss. The default is accept.

                        Eg: <action>dismiss</action>

            4. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/selenium_config.json
                                      </element_config_file>

            5. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information to
                             that element. If you want to use this one element
                             through out the testcase for a particular browser,
                             you can include it in the data file. If this not
                             the case, then you should create an argument tag
                             in the relevant testcase step and add the value
                             directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag" value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. browser_name(str) = Unique name for this particular browser
            3. actions(str) = action that needs to be performed on the alert
            4. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            5. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will accept or dismiss the alert"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}

        system = xml_Utils.getElementWithTagAttribValueMatch(self.datafile,
                                                             "system",
                                                             "name",
                                                             system_name)
        browser_list = system.findall("browser")
        try:
            browser_list.extend(system.find("browsers").findall("browser"))
        except AttributeError:
            pass

        if not browser_list:
            browser_list.append(1)
            browser_details = arguments

        for browser in browser_list:
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments, self.datafile, browser)
            if browser_details == {}:
                browser_details = selenium_Utils.\
                    get_browser_details(browser, self.datafile, **arguments)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    status = self.verify_oper_object.verify_alert_is_present(current_browser, browser_details["action"])
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status
