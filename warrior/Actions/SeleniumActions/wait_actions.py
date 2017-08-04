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

""" Selenium keywords for Wait Actions """
from Framework.ClassUtils.WSelenium.element_locator import ElementLocator
from Framework.ClassUtils.WSelenium.wait_operations import WaitOperations
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
    """This class has the functionality to wait till an event has happened on
    the webpage - such as the browser will wait till an element is clickable,
    visible, or present on a webpage. Implicit wait can also be set for a
    webpage with this class """

    def __init__(self):
        """This is a constructor for the wait_actions class"""
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.jsonobj = JsonUtils()
        self.wait_oper_object = WaitOperations()
        self.element_locator_obj = ElementLocator()

    def set_implicit_wait(self, system_name, timeout, browser_name="all",
                          element_config_file=None, element_tag=None):
        """
        This keyword would permanently set the implicit wait time for given
        browser instance(s)

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

            3. timeout = This contains the information of how much time the
                         browser needs to wait for any action to be performed
                         on it

                         Eg: <timeout>15</timeout>

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
            3. timeout(str) = amount of time the browser should wait
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
        wdesc = "This would permanently set the implicit wait time for " \
                "given browser instance(s)"
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
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments,
                                                                self.datafile,
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if not current_browser:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
                else:
                    self.wait_oper_object.\
                        implicit_wait(current_browser,
                                      browser_details["timeout"])
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def wait_until_element_is_clickable(self, system_name, timeout=5,
                                        locator=None, locator_type=None,
                                        browser_name="all", element_tag=None,
                                        element_config_file=None):
        """
        This keyword would check whether an element is visible and
        enabled such that we can click on the element

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

            3. timeout = This contains the information of how much time the
                         browser needs to wait for the element to become
                         clickable

                         Eg: <timeout>15</timeout>

            4. locator_type = This contains information about the type of
                              locator that you want to use. Can be 'xpath',
                              'id', 'css', 'link', 'tag','class', 'name'

            5. locator = This contains the value of the locator. Something like
                         "form", "nav-tags", "//[dh./dhh[yby]"

            6. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            7. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING LOCATOR_TYPE, LOCATOR, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the locator_type and
            locator. So if locator_type = name and locator = navigation-bar,
            then Warrior can search for an element with name "navigation-bar"

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there.

            - Now, if the locator type is given, Warrior
            will search for that locator_type in the children of that element in
            the element_config_file

            - You can also set defaults in the element_config_file, and now,
            even if the locator_type is not given, Warrior will know which
            element to find. If locator_type is given, the default will be
            overridden

            - If locator_type is not f=given, and the defaults are not
            specified, then the first element in the child list of the element
            tag would be picked.

            NOTES:
                For these four arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. locator_type and locator must be given
                2. locator_type, element_config_file, and element_tag must be given
                3. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If all arguments are passed from the same place, then, if
                locator and locator_type are given, then they would have
                priority. Otherwise, the element_config_file would be searched

                The locator_type locator, element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. browser_name(str) = Unique name for this particular browser
            3. timeout(str) = amount of time the browser should wait
            4. locator_type(str) = type of the locator - xpath, id, etc.
            5. locator(str) = locator by which the element should be located.
            6. element_config_file(str) = location of the element config file
            7. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Browser would wait until element is clickable"
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
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments,
                                                                self.datafile,
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if not current_browser:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
                else:
                    status = self.wait_oper_object.\
                        wait_until_element_is_clickable(current_browser,
                                                        browser_details["locator_type"],
                                                        browser_details["locator"],
                                                        browser_details["timeout"])
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def wait_until_presence_of_element_located(self, system_name, timeout=5,
                                               locator=None, locator_type=None,
                                               browser_name="all",
                                               element_tag=None,
                                               element_config_file=None):
        """
        This keyword would check whether an element is present on the DOM
        of a page

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

            3. timeout = This contains the information of how much time the
                         browser needs to wait for the element to be located

                         Eg: <timeout>15</timeout>

            4. locator_type = This contains information about the type of
                              locator that you want to use. Can be 'xpath',
                              'id', 'css', 'link', 'tag','class', 'name'

            5. locator = This contains the value of the locator. Something like
                         "form", "nav-tags", "//[dh./dhh[yby]"

            6. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            7. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING LOCATOR_TYPE, LOCATOR, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the locator_type and
            locator. So if locator_type = name and locator = navigation-bar,
            then Warrior can search for an element with name "navigation-bar"

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there.

            - Now, if the locator type is given, Warrior
            will search for that locator_type in the children of that element in
            the element_config_file

            - You can also set defaults in the element_config_file, and now,
            even if the locator_type is not given, Warrior will know which
            element to find. If locator_type is given, the default will be
            overridden

            - If locator_type is not f=given, and the defaults are not
            specified, then the first element in the child list of the element
            tag would be picked.

            NOTES:
                For these four arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. locator_type and locator must be given
                2. locator_type, element_config_file, and element_tag must be given
                3. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If all arguments are passed from the same place, then, if
                locator and locator_type are given, then they would have
                priority. Otherwise, the element_config_file would be searched

                The locator_type locator, element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. browser_name(str) = Unique name for this particular browser
            3. timeout(str) = amount of time the browser should wait
            4. locator_type(str) = type of the locator - xpath, id, etc.
            5. locator(str) = locator by which the element should be located.
            6. element_config_file(str) = location of the element config file
            7. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Browser would wait until presence of element is detected"
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
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments,
                                                                self.datafile,
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if not current_browser:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
                else:
                    status = self.wait_oper_object.\
                        wait_until_presence_of_element_located(current_browser,
                                                               browser_details["locator_type"],
                                                               browser_details["locator"],
                                                               browser_details["timeout"])
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def wait_until_presence_of_all_elements_located(self, system_name,
                                                    timeout=5, locator=None,
                                                    locator_type=None,
                                                    browser_name="all",
                                                    element_tag=None,
                                                    element_config_file=None):
        """
        This keyword would check whether all the elements is present on
        the DOM of a page

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

            3. timeout = This contains the information of how much time the
                         browser needs to wait for all the elemnts to be located

                         Eg: <timeout>15</timeout>

            4. locator_type = This contains information about the type of
                              locator that you want to use. Can be 'xpath',
                              'id', 'css', 'link', 'tag','class', 'name'

            5. locator = This contains the value of the locator. Something like
                         "form", "nav-tags", "//[dh./dhh[yby]"

            6. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            7. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING LOCATOR_TYPE, LOCATOR, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the locator_type and
            locator. So if locator_type = name and locator = navigation-bar,
            then Warrior can search for an element with name "navigation-bar"

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there.

            - Now, if the locator type is given, Warrior
            will search for that locator_type in the children of that element in
            the element_config_file

            - You can also set defaults in the element_config_file, and now,
            even if the locator_type is not given, Warrior will know which
            element to find. If locator_type is given, the default will be
            overridden

            - If locator_type is not f=given, and the defaults are not
            specified, then the first element in the child list of the element
            tag would be picked.

            NOTES:
                For these four arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. locator_type and locator must be given
                2. locator_type, element_config_file, and element_tag must be given
                3. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If all arguments are passed from the same place, then, if
                locator and locator_type are given, then they would have
                priority. Otherwise, the element_config_file would be searched

                The locator_type locator, element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. browser_name(str) = Unique name for this particular browser
            3. timeout(str) = amount of time the browser should wait
            4. locator_type(str) = type of the locator - xpath, id, etc.
            5. locator(str) = locator by which the element should be located.
            6. element_config_file(str) = location of the element config file
            7. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Browser would wait until presence of elements is detected"
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
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments,
                                                                self.datafile,
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if not current_browser:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
                else:
                    status = self.wait_oper_object.\
                        wait_until_presence_of_all_elements_located(current_browser,
                                                                    browser_details["locator_type"],
                                                                    browser_details["locator"],
                                                                    browser_details["timeout"])
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def wait_until_visibility_is_determined(self, system_name, timeout="5",
                                            locator=None, locator_type=None,
                                            browser_name="all",
                                            element_tag=None,
                                            element_config_file=None):
        """
        This keyword would check whether an element, known to be present on
        the DOM of a page, is visible

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

            3. timeout = This contains the information of how much time the
                         browser needs to wait for an element known to exist in
                         the DOM to become visible

                         Eg: <timeout>15</timeout>

            4. locator_type = This contains information about the type of
                              locator that you want to use. Can be 'xpath',
                              'id', 'css', 'link', 'tag','class', 'name'

            5. locator = This contains the value of the locator. Something like
                         "form", "nav-tags", "//[dh./dhh[yby]"

            6. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            7. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING LOCATOR_TYPE, LOCATOR, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the locator_type and
            locator. So if locator_type = name and locator = navigation-bar,
            then Warrior can search for an element with name "navigation-bar"

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there.

            - Now, if the locator type is given, Warrior
            will search for that locator_type in the children of that element in
            the element_config_file

            - You can also set defaults in the element_config_file, and now,
            even if the locator_type is not given, Warrior will know which
            element to find. If locator_type is given, the default will be
            overridden

            - If locator_type is not f=given, and the defaults are not
            specified, then the first element in the child list of the element
            tag would be picked.

            NOTES:
                For these four arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. locator_type and locator must be given
                2. locator_type, element_config_file, and element_tag must be given
                3. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If all arguments are passed from the same place, then, if
                locator and locator_type are given, then they would have
                priority. Otherwise, the element_config_file would be searched

                The locator_type locator, element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. browser_name(str) = Unique name for this particular browser
            3. timeout(str) = amount of time the browser should wait
            4. locator_type(str) = type of the locator - xpath, id, etc.
            5. locator(str) = locator by which the element should be located.
            6. element_config_file(str) = location of the element config file
            7. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Browser would wait until visibility of an element known to " \
                "be present in the DOM is determined"
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
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments,
                                                                self.datafile,
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if not current_browser:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
                else:
                    element = Utils.data_Utils.\
                        get_object_from_datarepository(system_name + "_" +
                                                       browser_details["browser_name"] + "_" +
                                                       browser_details["locator_type"] + "=" +
                                                       browser_details["locator"])
                    if element:
                        status = self.wait_oper_object.\
                            wait_until_visibilty_is_confirmed(current_browser,
                                                              element,
                                                              browser_details["timeout"])
                    else:
                        element = self.element_locator_obj.\
                            get_element(current_browser,
                                        browser_details["locator_type"] + "=" +
                                        browser_details["locator"])
                        status = self.wait_oper_object.\
                            wait_until_visibilty_is_confirmed(current_browser,
                                                              element,
                                                              browser_details["timeout"])
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def wait_until_visibility_of_element_located(self, system_name, timeout="5",
                                                 locator=None,
                                                 locator_type=None,
                                                 browser_name="all",
                                                 element_tag=None,
                                                 element_config_file=None):
        """
        This keyword would check whether an element is present on the DOM of a
        page and visible.

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

            3. timeout = This contains the information of how much time the
                         browser needs to wait for an element whose existence in
                         the DOM is unknown to become visible

                         Eg: <timeout>15</timeout>

            4. locator_type = This contains information about the type of
                              locator that you want to use. Can be 'xpath',
                              'id', 'css', 'link', 'tag','class', 'name'

            5. locator = This contains the value of the locator. Something like
                         "form", "nav-tags", "//[dh./dhh[yby]"

            6. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            7. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING LOCATOR_TYPE, LOCATOR, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the locator_type and
            locator. So if locator_type = name and locator = navigation-bar,
            then Warrior can search for an element with name "navigation-bar"

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there.

            - Now, if the locator type is given, Warrior
            will search for that locator_type in the children of that element in
            the element_config_file

            - You can also set defaults in the element_config_file, and now,
            even if the locator_type is not given, Warrior will know which
            element to find. If locator_type is given, the default will be
            overridden

            - If locator_type is not f=given, and the defaults are not
            specified, then the first element in the child list of the element
            tag would be picked.

            NOTES:
                For these four arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. locator_type and locator must be given
                2. locator_type, element_config_file, and element_tag must be given
                3. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If all arguments are passed from the same place, then, if
                locator and locator_type are given, then they would have
                priority. Otherwise, the element_config_file would be searched

                The locator_type locator, element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. browser_name(str) = Unique name for this particular browser
            3. timeout(str) = amount of time the browser should wait
            4. locator_type(str) = type of the locator - xpath, id, etc.
            5. locator(str) = locator by which the element should be located.
            6. element_config_file(str) = location of the element config file
            7. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Browser would wait until visibility of an element known to " \
                "be is determined"
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
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments,
                                                                self.datafile,
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if not current_browser:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
                else:
                    status = self.wait_oper_object.\
                        wait_until_visibility_of_element_located(current_browser,
                                                                 browser_details["locator_type"],
                                                                 browser_details["locator"],
                                                                 browser_details["timeout"])
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status
