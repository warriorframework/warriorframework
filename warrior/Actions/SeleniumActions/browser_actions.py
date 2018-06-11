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
from urlparse import urlparse
from Framework.ClassUtils.WSelenium.browser_mgmt import BrowserManagement
from Actions.SeleniumActions.verify_actions import verify_actions
from Actions.SeleniumActions.elementlocator_actions import elementlocator_actions

import Framework.Utils as Utils
from Framework.Utils import selenium_Utils
from Framework.Utils import data_Utils
from Framework.Utils import xml_Utils
from Framework.Utils.testcase_Utils import pNote, pSubStep
from Framework.ClassUtils.json_utils_class import JsonUtils
from Framework.Utils.rest_Utils import remove_invalid_req_args


class browser_actions(object):
    """This is a class that deals with all 'browser' related functionality like
    opening and closing a browser, maximizing a browser window, navigating to
    a URL, resizing a browser window."""

    def __init__(self, *args, **kwargs):
        """This is a constructor for the browser_actions class"""
        self.resultfile = Utils.config_Utils.resultfile
        self.datafile = Utils.config_Utils.datafile
        self.logsdir = Utils.config_Utils.logsdir
        self.filename = Utils.config_Utils.filename
        self.logfile = Utils.config_Utils.logfile
        self.jsonobj = JsonUtils()
        # Browser object is the Selenium Utils for all the browser related operations
        self.browser_object = BrowserManagement()
        self.verify_obj = verify_actions()
        self.elementlocator_obj = elementlocator_actions()

    def browser_launch(self, system_name, browser_name="all", type="firefox",
                       url=None, ip=None, remote=None, element_config_file=None,
                       element_tag=None, headless_mode=None):
        """
        The Keyword would launch a browser and Navigate to the url, if provided by the user.

        --------------------------------------------------------------------------------------
        This keyword does not validate the url provided by the user. Please use
        navigate_to_url_with_verification instead of providing a url with this keyword if you
        need to verify the navigation result.
        --------------------------------------------------------------------------------------

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

            4. type = This <type> tag is a child of the <browser> tag in the
                      data file. The type of browser that should be opened can
                      be added in here.

                      Eg: <type>firefox</type>

            5. browser_name = This <browser_name> tag is a child of the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            6. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
                             the json file which contains relevant information to
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

            9. headless_mode = Run selenium test in headless mode
                                Used in system with no GUI component

            The next 5 arguments are added for Selenium 3 with Firefox
            Please use them inside the browser tag in system data file
            binary = The absolute path of the browser executable
                        Eg: <binary>../../firefox/firefox</binary>

            gecko_path = The absolute path of the geckodriver
                             geckodriver is mandatory if using Firefox version 47 or above
                             This also required Selenium 3.5 or above
                             For more information please visit:
                             https://github.com/mozilla/geckodriver#selenium
                             Eg: <gecko_path>../../../geckodriver</gecko_path>

            gecko_log = The absolute path for the geckodriver log to be saved
                            This file only get generated if firefox is launched with geckodriver
                            and failuer/error occur
                            Default is the testcase log directory

            proxy_ip = This <proxy_ip> tag refers to the ip of the proxy
                           server. When a proxy is required this tag has to set
                           Eg: <proxy_ip>xx.xxx.xx.xx</proxy_ip>

            proxy_port = This <proxy_port> tag refers to the port of the
                            proxy server. When a proxy is required for
                            remote connection this tag has to set.
                           Eg: <proxy_port>yyyy</proxy_port>


        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. ip(str) = IP of the remote machine
            6. remote(str) = 'yes' or 'no' to indicate whether you want to
                              connect to the given aboveIP
            7. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element
            9. headless_mode(str) = Enable headless_mode


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

        # Get optional argument from system data file if it is not specified in keyword arg
        optional_arg_keys = ["ip", "remote", "headless_mode"]
        optional_args = {}
        for arg in optional_arg_keys:
            if arguments.get(arg, None) is None:
                optional_args[arg] = data_Utils.getSystemData(self.datafile, system_name, arg)

        optional_args["webdriver_remote_url"] = optional_args["ip"]\
            if str(optional_args["remote"]).strip().lower() == "yes" else False

        system = xml_Utils.getElementWithTagAttribValueMatch(self.datafile,
                                                             "system", "name", system_name)

        browser_list = []

        # Create a list of browser
        if system.findall("browser") is not None:
            browser_list.extend(system.findall("browser"))
        if system.find("browsers") is not None:
            browser_list.extend(system.find("browsers").findall("browser"))

        if not browser_list:
            "No browser found in system: {}, please check datafile".format(system_name)
            status = False

        # Headless mode operation
        enable_headless = Utils.data_Utils.get_object_from_datarepository("wt_enable_headless")
        if str(optional_args["headless_mode"]).strip().lower() in ["yes", "y"] or enable_headless:
            status = selenium_Utils.create_display()
            if not status:
                browser_list = []
            else:
                output_dict[system_name+"_headless"] = True
                output_dict["headless_display"] = True

        for browser in browser_list:
            arguments = Utils.data_Utils.get_default_ecf_and_et(arguments, self.datafile, browser)
            browser_optional_arg_keys = {"binary": None, "gecko_path": None, "proxy_ip": None, 
                                         "proxy_port": None, "gecko_log": None}
            # Adding browser_optional_arg_keys to arguments to get corresponding values from datafile.
            arguments.update(browser_optional_arg_keys)
            browser_details = selenium_Utils.\
                              get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None:
                # Call utils to launch correct type of browser
                # Need to pass the binary, gecko_path, proxy_ip, proxy_port, gecko_log 
                # if specified in the datafile
                browser_optional_args = {}
                for arg in browser_optional_arg_keys:
                    if browser_details.get(arg) is not None:
                        browser_optional_args[arg] = browser_details.get(arg)
                browser_inst = self.browser_object.open_browser(
                    browser_details["type"], **browser_optional_args)
                if browser_inst:
                    browser_fullname = "{0}_{1}".format(system_name,
                                                        browser_details["browser_name"])
                    output_dict[browser_fullname] = browser_inst
                    url = browser_details["url"]
                    if url is not None:
                        urlschema = urlparse(url)
                        if urlschema.scheme:
                            result = self.browser_object.go_to(url, browser_inst)
                        else:
                            result = False
                            pNote("Protocol scheme in your URL: \'{0}\' is missing, protocol could"
                                  "be http/ftp/file".format(url), "error")
                    else:
                        result = True
                else:
                    pNote("could not open browser on system={0}, name={1}".format
                          (system_name, browser_details["browser_name"]), "error")
                    result = False
                status = status and result
            else:
                pNote("Cannot load correct browser detail in system {}, please check datafile".\
                      format(system_name))
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
                current_browser = Utils.data_Utils.get_object_from_datarepository(
                    system_name + "_" + browser_details["browser_name"])
                headless = Utils.data_Utils.get_object_from_datarepository(
                    system_name + "_headless")
                if current_browser:
                    status &= self.browser_object.maximize_browser_window(current_browser, headless)
                else:
                    pNote("Browser of system {0} and name {1} not found in the"
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status &= False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        return status

    def browser_launch_and_maximize(self, system_name, browser_name="all", type="firefox",
                                    url=None, ip=None, remote=None, element_config_file=None,
                                    element_tag=None):
        """
        This will launch a browser and maximize the browser window if it is set.

        :Datafile Usage:

            Tags or attributes to be used in input datafile for the system or
            subsystem. If both tag and attribute is provided the attribute will
            be used.

            1. system_name = This attribute can be specified in the datafile as
                             a <system> tag directly under the <credentials>
                             tag. An attribute "name" has to be added to this
                             tag and the value of that attribute would be taken
                             in as value to this keyword attribute.

                             <system name="name_of_the_system"/>

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

            5. browser_name = This <browser_name> tag is a child tag the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            6. url = The URL that you want to open your browser to can be added
                     in the <url> tag under the <browser> tag.

                     Eg: <url>https://www.google.com</url>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
                             the json file which contains relevant information to
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
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. ip(str) = IP of the remote machine
            6. remote(str) = 'yes' or 'no' to indicate whether you want to
                              connect to the given aboveIP
            7. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser

        """
        wdesc = "Opens browser instances and maximizes them"
        pNote(wdesc)
        pSubStep(wdesc)

        status, output_dict = self.browser_launch(system_name=system_name, type=type,
                                                  browser_name=browser_name, url=url, ip=ip,
                                                  remote=remote,
                                                  element_config_file=element_config_file,
                                                  element_tag=element_tag)
        if status:
            for current_browser in output_dict:
                self.browser_object.maximize_browser_window(output_dict[current_browser])

        return status, output_dict

    def navigate_to_url(self, system_name, type="firefox", browser_name="all",
                        url=None, element_config_file=None, element_tag=None):
        """
        This will navigate the browser tab to given URL.

        -----------------------------------------------------------------------------
        This keyword does not validate the url provided by the user. Please use
        navigate_to_url_with_verification if you need to verify the navigation result.
        ------------------------------------------------------------------------------

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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
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
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element


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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
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
        Utils.testcase_Utils.report_substep_status(status)
        return status

    def navigate_to_url_with_verification(self, system_name, type="firefox", browser_name="all",
                                          url=None, element_config_file=None, element_tag=None,
                                          value_type=None, expected_value=None, locator_type=None,
                                          locator=None):
        """
        The webpage would be directed to the given URL and then whether the navigation was
        successful or not would be verified

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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
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

            7.locator_type = This contains information about the type of
                              locator that you want to use. Can be 'xpath',
                              'id', 'css', 'link', 'tag','class', 'name'

            8. locator = This contains the value of the locator. Something like
                         "form", "nav-tags", "//[dh./dhh[yby]"

            9. expected_value = This <expected_value> tag is a child og the
                                <browser> tag in the data file. This tag would
                                contain the the value you expect the browser to
                                have. This can be either a  url, page title,
                                page source, or page name

                    Eg: <expected_value>http://www.google.com</expected_value>

            10. value_type =This <value_type> tag is a child of the <browser>
                            tag in the data file. This tag would contain the
                            type of browser information that you want to verify.
                            It can either be current_url, title, name, or
                            page_source

                            Eg: <value_type>title</value_type>

            USING LOCATOR_TYPE & LOCATOR, VALUE_TYPE & EXPECTED_VALUE
            =========================================================

            Please provide either the locator type and locator or provide value_type and
            expected_value for the verificationr to be performed successfully

            Note: Even though, current_url is an acceptable value_type, it is not recommended that
                  you use it since it can result in a false positive. Please use it only if you are
                  sure that the verification would go through correctly.

        :Arguments:

            1. system_name(str) = the system name.
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element
            7. locator_type (str) = type of the locator - xpath, id, etc.
            8. locator (str) = locator by which the element should be located.
            9. expected_value (str) = The expected value of the information
                                      retrieved from the web page.
            10. value_type(str) = Type of page information that you wat to
                                  verify: current_url, name, title, or
                                  page_source


        :Returns:

            1. status(bool)= True / False.

        """
        wdesc = "The webpage would be directed to the given URL and then whether the navigation " \
                "was successful or not would be verified."
        pNote(wdesc)
        pSubStep(wdesc)

        status = self.navigate_to_url(system_name=system_name, type=type, browser_name=browser_name,
                                      url=url, element_config_file=element_config_file,
                                      element_tag=element_tag)

        if all((value_type is not None, expected_value is not None)):
            status = status and self.verify_obj.verify_page_by_property(system_name=system_name,
                                                                        expected_value=expected_value,
                                                                        value_type=value_type,
                                                                        browser_name=browser_name,
                                                                        element_config_file=element_config_file,
                                                                        element_tag=element_tag)
        elif all((locator is not None, locator_type is not None)):
            status = status and self.elementlocator_obj.get_element(system_name=system_name,
                                                                    locator_type=locator_type,
                                                                    locator=locator,
                                                                    element_tag=element_tag,
                                                                    element_config_file=element_config_file,
                                                                    browser_name=browser_name)[0]
        else:
            pNote("The navigation result could not be verified as enough information was not "
                  "provided. Either the locator and locator_type or the value_type and "
                  "expected_value should be given.", "error")
            status = False

        Utils.testcase_Utils.report_substep_status(status)
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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    self.browser_object.go_forward(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                          "the datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    self.browser_object.go_back(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                          "the datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    self.browser_object.reload_page(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                          "the datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    self.browser_object.hard_reload_page(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in "
                          "the datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    self.browser_object.close_browser(current_browser)
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status = False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
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
            2. xsize (int/str) = The x co-ordinate
            3. ysize (int/str) = The y co-ordinate
            4. type(str) = Type of browser: firefox, chrome, ie.
            5. browser_name(str) = Unique name for this particular browser
            6. url(str) = URL to which the browser should be directed
            7. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    self.browser_object.set_window_size(int(browser_details["xsize"]), int(browser_details["ysize"]),
                                                        current_browser)
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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
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
            2. xpos (int/str) = The x co-ordinate
            3. ypos (int/str) = The y co-ordinate
            4. type(str) = Type of browser: firefox, chrome, ie.
            5. browser_name(str) = Unique name for this particular browser
            6. url(str) = URL to which the browser should be directed
            7. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    self.browser_object.set_window_position(int(browser_details["xpos"]),
                                                            int(browser_details["ypos"]),
                                                            current_browser)
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

    def open_a_new_tab(self, system_name, type="firefox", browser_name="all",
                       element_config_file=None, element_tag=None, url=None):
        """This will open a new tab.

        DISCLAIMER - A new window will be opened for firefox as Selenium does not
        support tabs in Firefox.

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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
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
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                        status &= self.browser_object.open_tab(current_browser,
                                                               browser_details["url"],
                                                               browser_details["type"])
                else:
                    pNote("Browser of system {0} and name {1} not found in the "
                          "datarepository"
                          .format(system_name, browser_details["browser_name"]),
                          "Exception")
                    status &= False
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
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
            2. tab_number (int/str) = The tab number that you want to switch to.
            3. type(str) = Type of browser: firefox, chrome, ie.
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
        wdesc = "The browser will switch between tabs"
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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
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
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
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
            2. tab_number (int/str) = The tab number that you want to close.
            3. type(str) = Type of browser: firefox, chrome, ie.
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
        wdesc = "The browser will switch between tabs"
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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
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
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
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
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    width, height = self.browser_object.\
                        get_window_size(current_browser)
                    pNote("Window width: {0} and window height: {1}".format(width, height))
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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
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
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
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
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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

            5. filename = This <filename> tag is a child of the <browser> tag in
                          the data file. This tag would contain the information
                          about the name of file that you want the screenshot to
                          have. If left empty, the screenshot file would be
                          saved with the name screenshot_*timestamp*

                          Eg: <filename>new_screenshot</filename>

            7. element_config_file = This <element_config_file> tag is a child
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/selenium_config.json
                                      </element_config_file>

            8. element_tag = This element_tag refers to a particular element in
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
            2. directory (str) = The directory that would store the
                                     screenshots.
            3. filename (str) = Name of the screenshot file
            4. type(str) = Type of browser: firefox, chrome, ie.
            5. browser_name(str) = Unique name for this particular browser
            6. url(str) = URL to which the browser should be directed
            7. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            8. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
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
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
                                      </element_config_file>

            6. element_tag = This element_tag refers to a particular element in
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
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. browser_name(str) = Unique name for this particular browser
            4. url(str) = URL to which the browser should be directed
            5. element_config_file (str) = location of the element configuration
                                           file that contains all element
                                           locators
            6. element_tag (str) = particular element in the json fie which
                                   contains relevant information to that element

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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    status = self.browser_object.delete_all_cookies_in_browser(current_browser)
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
                                     of the <browser> tag in the data file. This
                                     stores the location of the element
                                     configuration file that contains all
                                     element locators.

                                  Eg: <element_config_file>
                                      ../Config_files/slenium_config.json
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
            2. type(str) = Type of browser: firefox, chrome, ie.
            3. cookie_name (str) = Name of the cookie that you want to delete
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
        wdesc = "A particular cookie of the browser instance would be deleted"
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
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(system_name + "_" +
                                                   browser_details["browser_name"])
                if current_browser:
                    status = self.browser_object.delete_a_specific_cookie(
                        current_browser, browser_details["cookie_name"])
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
