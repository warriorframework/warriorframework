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
from Framework.ClassUtils.WSelenium.element_locator import ElementLocator
from Framework.Utils.print_Utils import print_error, print_info
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


class verify_actions(object):
    """This class deals with functionality related to verifications that can be
    performed in a browser window - like verifying a page by its property (like
    url, title, page source, and name), verifying if an alert is present on the
    webpage"""

    def __init__(self):
        """This is a constructor for the verify_actions class"""
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.jsonobj = JsonUtils()
        self.verify_oper_object = VerifyOperations()
        self.element_locator_obj = ElementLocator()

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
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
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

    def verify_text_in_window_pane(self, system_name,
                                   verification_text=None,
                                   browser_name='all',
                                   element_config_file=None,
                                   element_tag=None):
        """
        This keyword is to verify whether the user provided texts exist on the web page

        :Datafile Usage:

            Tags or attributes to be used in input data file for the system or
            subsystem. If both tag and attribute is provided the attribute will
            be used.

            1. system_name = This attribute can be specified in the data file as
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

            3. verification_text = text to be verified in the web page should be given as a comma separated value
                                   without any space in between, if it is multiple values
                                   Eg. <verification_text>Gmail,Google</verification_text>

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     test case execution

            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING NAME_OF_ELEMENT, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ==========================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the verification_text. So
            if verification_text = verification_text(comma seperated values), then Warrior can search 
            the given verification_text in the window pane

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            verify_text_in_window_pane, an child element of the element_tag with
            id as 'verification_text' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. verification_text must be given
                2. element_config_file, and element_tag must be given

                The data file has the first priority, then the json file, and
                then finally the test case.

                If name_of_element is given, then it would have priority.
                Otherwise, the element_config_file would be searched

                The name_of_element and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the test case step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. browser_name(str) = Unique name for this particular browser
            3. verification_text = text to be verified in the webpage
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = True
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
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments,
                                                                self.datafile,
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None and browser_details["verification_text"] is not None:
                if not browser_details["verification_text"].startswith("verification_text"):
                    browser_details["verification_text"] = \
                        "verification_text=" + browser_details["verification_text"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" +
                                                                                  browser_details["browser_name"])
                if not current_browser:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "data repository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
                else:
                    element_located_status = current_browser.page_source
                    if element_located_status:
                        for values in browser_details["verification_text"].split(","):
                            if re.search("verification_text=", values):
                                values = re.sub("verification_text=", "", values)
                            verification_status = self.element_locator_obj.get_element(current_browser, 'xpath=//*[contains(text(),"{}")]'.format(values), findall='y')
                            if verification_status and len(verification_status) > 0:
                                print_info("Verification text found {} times in the window pane".format(len(verification_status)))
                            if not verification_status:
                                print_error("The given string {} is not present in DOM".format(values))
                                status = False
            else:
                print_error("Value for browser_details/verification_text is None. Provide the value")
                status = False
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
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
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
