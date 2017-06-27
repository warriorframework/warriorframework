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

""" Selenium keywords for Generic Browser Actions """
import os
from Framework.ClassUtils.WSelenium.browser_mgmt import BrowserManagement

try:
    import Framework.Utils as Utils
except ImportWarning:
    raise ImportError

from Framework.Utils import selenium_Utils
from Framework.Utils import data_Utils
from Framework.Utils.testcase_Utils import pNote, pSubStep
from Framework.ClassUtils.json_utils_class import JsonUtils


class browser_actions(object):

    def __init__(self, *args, **kwargs):
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.jsonobj = JsonUtils()
        self.browser_object = BrowserManagement()

    def browser_launch(self, system_name, browser_name="all",
                       type="firefox", url=None, ip=None,
                       remote=None, element_config_file=None,
                       element_tag=None):
        """
        This will launch a browser.

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

            2. ip = Specify this tag as a direct child of the <system> tag
                    This tag would contain information about the IP of the
                    remote machine on which you want your testcase to run

                    Eg: <ip>167.125.0.1</ip>

            3. remote = Specify this tag as a direct child of the <system> tag
                        This tag when set to set, would use the IP above and
                        start up a browser on that machine. If this tag is set
                        to 'no', a browser would launch on your machine

                        Eg: <remote>yes</remote>

            4. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            5. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            6. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element
                             in the json fie which contains relevant
                             information to that element. If you want to use
                             this one element through out the testcase for a
                             particular browser, you can include it in the
                             data file. If this not the case, then you should
                             create an argument tag in the relevant testcase
                             step and add the value directly in the testcase
                             step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. ip(str) = IP of the remote machine
            6. remote(str) = 'yes' or 'no' to indicate whether you want to
                              connect to the given aboveIP
            7. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that
                                   element

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        output_dict = {}
        wdesc = "Opens browser instances"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}

        if ip is None:
            ip = data_Utils.getSystemData(self.datafile, system_name, "ip")
        if remote is None:
            remote = data_Utils.getSystemData(self.datafile, system_name,
                                              "remote")

        webdriver_remote_url = ip if str(remote).strip().lower() == "yes"\
            else False
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments,
                                                                self.datafile,
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils.\
                    get_browser_details(browser, self.datafile, **arguments)
            if browser_details is not None:
                browser_inst = self.browser_object.open_browser(
                    browser_details["type"], webdriver_remote_url)
                if browser_inst:
                    browser_fullname = "{0}_{1}".format(system_name,
                                                        browser_details["browser_name"])
                    output_dict[browser_fullname] = browser_inst
                    if "url" in browser_details and browser_details["url"]\
                            is not None:
                        result, url = self.browser_object.\
                            check_url(browser_details["url"])
                        if result == True:
                            result = self.browser_object.\
                                go_to(url, browser_inst)
                    else:
                        result = True
                else:
                    pNote("could not open browser on system={0}, "
                          "name={1}".format(system_name,
                                            browser_details["browser_name"]),
                          "error")
                    result = False
                status = status and result
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        return status, output_dict

    def browser_maximize(self, system_name, type="firefox", browser_name="all"):
        """
        This will maximize the browser window.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will get maximized"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.maximize_browser_window(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in the"
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def navigate_to_url(self, system_name, type="firefox", browser_name="all",
                        url=None, element_config_file=None, element_tag=None):
        """
        This will navigate the browser tab to given URL.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>



            5. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that
                                   element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The webpage would be directed to the given URL"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.go_to(browser_details["url"],
                                              current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                          "the datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def navigate_forward(self, system_name, type="firefox", browser_name="all"):
        """
        This will take you forward in the browser history.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will navigate forward"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.go_forward(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                          "the datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def navigate_backward(self, system_name, type="firefox", browser_name="all"):
        """
        This will take you backward in browser history.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will navigate backward"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.go_back(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                          "the datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def browser_refresh(self, system_name, type="firefox", browser_name="all"):
        """
        This will refresh the browser window.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will be refreshed"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.reload_page(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                          "the datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def browser_reload(self, system_name, type="firefox", browser_name="all"):
        """
        This will reload the browser window.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will be reloaded"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.hard_reload_page(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                         "the datarepository"
                         .format(system_name, browser_details["browser_name"]),
                         "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def browser_close(self, system_name, type="firefox", browser_name="all"):
        """
        This will close the browser window.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will be closed"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.close_browser(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in"
                          "the datarepository"
                          .format(system_name,
                          browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def set_window_size(self, system_name, xsize=None, ysize=None,
                        type="firefox", browser_name="all",
                        element_config_file=None, element_tag=None):
        """
        This will set the browser window to a particular size.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. xsize = This <xsize> tag is a child og the <browser> tag in the
                      data file. This tag would contain the information about
                      the x co-ordinate of the window

                      Eg: <xsize>500</zsixe>

            6. ysize = This <ysize> tag is a child og the <browser> tag in the
                      data file. This tag would contain the information about
                      the y co-ordinate of the window

                     Eg: <ysize>750</ysize>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. xsize (int/str) = The x co-ordinate
            3. ysize (int/str) = The y co-ordinate
            4. type(str) = Type of browser: firefox, chrome, ie.
            5. browser_name(str) = Unique name for this particular browser
            6. url(str) = URL to which the browser should be directed
            7. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to
                                   that element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will be resized"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.\
                        set_window_size(int(browser_details["xsize"]),
                                        int(browser_details["ysize"]),
                                        current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def set_window_position(self, system_name, xpos=None, ypos=None,
                            type="firefox", browser_name="all",
                            element_config_file=None, element_tag=None):
        """
        This will set the browser window to a particular position.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. xpos = This <xpos> tag is a child og the <browser> tag in the
                      data file. This tag would contain the information about
                      the x co-ordinate of the window

                      Eg: <xpos>500</xpos>

            5. ypos = This <ypos> tag is a child og the <browser> tag in the
                      data file. This tag would contain the information about
                      the y co-ordinate of the window

                     Eg: <ypos>750</ypos>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. xpos (int/str) = The x co-ordinate
            3. ypos (int/str) = The y co-ordinate
            4. type(str) = Type of browser: firefox, chrome, ie.
            5. browser_name(str) = Unique name for this particular browser
            6. url(str) = URL to which the browser should be directed
            7. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to
                                   that element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will be set to a new position"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.\
                        set_window_position(int(browser_details["xpos"]),
                                            int(browser_details["ypos"]),
                                            current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def open_a_new_tab(self, system_name, type="firefox", browser_name="all",
                       element_config_file=None, element_tag=None, url=None):
        """This will open a new tab.

        DISCLAIMER - A new window will be opened for firefox as Selenium
        does not support tabs in Firefox.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to
                                   that element


        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will open a new tab"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    self.browser_object.open_tab(current_browser,
                                                 browser_details["url"],
                                                 browser_details["type"])
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def switch_between_tabs(self, system_name, type="firefox",
                            browser_name="all", tab_number=None,
                            element_config_file=None, element_tag=None):
        """
        This keyword will let you switch between all open tabs.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. tab_number = This <tab_number> tag is a child og the <browser>
                            tag in the data file. This tag would contain the
                            information about the tab number that you want to
                            switch to from the current tab

                      Eg: <tab_number>3</tab_number>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. tab_number (int/str) = The tab number that you want to
                                      switch to.
            3. type(str) = Type of browser: firefox, chrome, ie.
            4. browser_name(str) = Unique name for this particular browser
            5. url(str) = URL to which the browser should be directed
            6. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            7. element_tag (str) = particular element in the json fie which
                                   contains relevant information to
                                   that element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will switch between tabs"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    status = self.browser_object.\
                             switch_tab(current_browser,
                                        browser_details["tab_number"],
                                        browser_details["type"])
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def close_a_tab(self, system_name, type="firefox", browser_name="all",
                    tab_number=None, element_config_file=None,
                    element_tag=None):
        """
        This keyword will let you close an open tab.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. tab_number = This <tab_number> tag is a child og the <browser>
                            tag in the data file. This tag would contain the
                            information about the tab number that you want to
                            close

                      Eg: <tab_number>3</tab_number>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. tab_number (int/str) = The tab number that you want to close.
            3. type(str) = Type of browser: firefox, chrome, ie.
            4. browser_name(str) = Unique name for this particular browser
            5. url(str) = URL to which the browser should be directed
            6. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            7. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that
                                   element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will switch between tabs"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    status = self.browser_object.\
                        close_tab(current_browser,
                                  browser_details["tab_number"],
                                  browser_details["type"])
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def get_window_size(self, system_name, type="firefox", browser_name="all",
                        element_config_file=None, element_tag=None):
        """
        This keyword will return window size.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that
                                   element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will return current window size"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    width, height = self.browser_object.\
                        get_window_size(current_browser)
                    pNote("Window width: {0} and window"
                          "height: {1}".format(width, height))
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def get_window_position(self, system_name, type="firefox",
                            browser_name="all", element_config_file=None,
                            element_tag=None):
        """
        This keyword will return the window position.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to
                                   that element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "The browser will return current window position"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    x, y = self.browser_object.\
                        get_window_position(current_browser)
                    pNote("Window X co-ordinate: {0} and window Y "
                          "co-ordinate: {1}".format(x, y))
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def save_screenshot(self, system_name, type="firefox", directory=None,
                        filename=None, browser_name="all",
                        element_config_file=None, element_tag=None):
        """
        This keyword will save a screenshot of the current browser window.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. directory = This <directory> tag is a child og the <browser> tag
                           in the data file. This tag would contain the
                           information about the directory in which you want to
                           store the screenshot. If left empty, the screenshots
                           would be saved in the Logs directory

                           Eg: <directory>/home/user/screenshots</directory>

            5. filename = This <filename> tag is a child of the <browser> tag
                          in the data file. This tag would contain the
                          information about the name of file that you want
                          the screenshot to have. If left empty, the
                          screenshot file would be saved with the
                          name screenshot_*timestamp*

                          Eg: <filename>new_screenshot</filename>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/selenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. directory (str) = The directory that would store the
                                     screenshots.
            3. filename (str) = Name of the screenshot file
            4. type(str) = Type of browser: firefox, chrome, ie.
            5. browser_name(str) = Unique name for this particular browser
            6. url(str) = URL to which the browser should be directed
            7. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that
                                   element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "A screenshot of the current browser window would be saved"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    if directory is not None:
                        status = self.browser_object.\
                            save_screenshot(current_browser,
                                            browser_details["filename"],
                                            browser_details["directory"])
                    else:
                        status = self.browser_object.\
                            save_screenshot(current_browser,
                                            browser_details["filename"],
                                            os.path.dirname(self.logsdir))
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def delete_cookies(self, system_name, type="firefox", browser_name="all",
                       element_config_file=None, element_tag=None):
        """
        This keyword will delete all cookies of a browser instance.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            4. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            5. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element
                                           configuration file that contains
                                           all element locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to
                                   that element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "All cookies of  this browser instance would be deleted"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    status = self.browser_object.\
                        delete_all_cookies_in_browser(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status

    def delete_a_cookie(self, system_name, cookie_name, type="firefox",
                        browser_name="all", element_config_file=None,
                        element_tag=None):
        """
        This keyword will delete a particular cookie of a browser instance.

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

            2. type = This <type> tag is a child og the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            3. cookie_name = This <cookie_name> tag is a child og the <browser>
                             tag in the data file. The name of the ccokie that
                             you want to delete can be added here.

                             Eg: <cookie_name>gmail_cookie</cookie_name>

            4. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            5. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            6. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file.
                                     This stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            7. element_tag = This element_tag refers to a particular element in
                             the json fie which contains relevant information
                             to that element. If you want to use this one
                             element through out the testcase for a particular
                             browser, you can include it in the data file. If
                             this not the case, then you should create an
                             argument tag in the relevant testcase step and add
                             the value directly in the testcase step.

                             FOR DATA FILE
                             Eg: <element_tag>json_name_1</element_tag>

                             FOR TEST CASE
                             Eg: <argument name="element_tag"
                             value="json_name_1">

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. cookie_name (str) = Name of the cookie that you want to delete
            4. browser_name(str) = Unique name for this particular browser
            5. url(str) = URL to which the browser should be directed
            6. element_config_file (str) = location of the element
                                           configuration file that contains all
                                           element locators
            7. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that
                                   element

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "A particular cookie of the browser instance would be deleted"
        pNote(wdesc)
        pSubStep(wdesc)
        browser_details = {}
        browser_list, browser_details = selenium_Utils.\
            get_browser_details_from_data_file(system_name, arguments,
                                               browser_details)
        for browser in browser_list:
            browser_details = selenium_Utils.\
                get_current_browser_details(system_name, browser, arguments,
                                            browser_details)
            if browser_details is not None:
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    status = self.browser_object.\
                        delete_a_specific_cookie(current_browser,
                                                 browser_details["cookie_name"])
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        selenium_Utils.report_status_and_screenshot(status, current_browser)
        return status
