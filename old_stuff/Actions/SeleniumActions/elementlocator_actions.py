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

""" Selenium keywords for Element Locator Actions """
from Framework.ClassUtils.WSelenium.element_locator import ElementLocator
try:
    import Framework.Utils as Utils
except ImportWarning:
    raise ImportError

from Framework.Utils import xml_Utils
from Framework.Utils import data_Utils
from Framework.Utils import selenium_Utils
from Framework.Utils.testcase_Utils import pNote,pSubStep


class elementlocator_actions(object):
    """This is a class that deals with all 'element' (HTML element) related
    functionality like locating an element via its tag name, class name, name,
    id, css selector, partial and complete links."""

    def __init__(self):
        """This is a constructor for the elementlocator_actions class"""
        self.datafile = Utils.config_Utils.datafile
        self.elem_loc_object = ElementLocator()

    def get_element(self, system_name, locator_type=None, locator=None,
                    element_config_file=None, element_tag=None,
                    browser_name="all"):
        """
        This will get an element by the given locator

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

            3. locator_type = This contains information about the type of
                              locator that you want to use. Can be 'xpath',
                              'id', 'css', 'link', 'tag','class', 'name'

            4. locator = This contains the value of the locator. Something like
                         "form", "nav-tags", "//[dh./dhh[yby]"

            5. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            6. element_tag = This contains the name of the element in that
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
            2. locator_type(str) = type of the locator - xpath, id, etc.
            3. locator(str) = locator by which the element should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its given locator and locator type."
        output_dict = {}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
                    element = self.elem_loc_object.\
                        get_element(current_browser,
                                    browser_details["locator_type"] + "=" +
                                    browser_details["locator"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["locator_type"] + "=" +
                                browser_details["locator"]] = element
                else:
                    pNote("Browser {0} not found in the data "
                          "repository".format(system_name +
                                              "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict

    def get_element_by_xpath(self, system_name, xpath=None,
                             element_config_file=None, element_tag=None,
                             browser_name="all"):
        """
        This will get an element by the element's xpath

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

            3. xpath = This contains the xpath of the element that you want to
                       find.

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING XPATH, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ==================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the xpath. So if
            xpath = [some_xpath], then Warrior can search for an element with
            that xpath

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            get_element_by_xpath, an child element of the element_tag with id
            as 'xpath' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. xpath must be given
                2. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If xpath is given, then it would have priority. Otherwise,
                the element_config_file would be searched

                The xpath and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. xpath(str) = xpath of the element
            3. browser_name(str) = Unique name for this particular browser
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its xpath."
        output_dict = {}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
                if not browser_details["xpath"].startswith("xpath"):
                    browser_details["xpath"] = \
                        "xpath=" + browser_details["xpath"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    element = self.elem_loc_object.\
                        get_element(current_browser, browser_details["xpath"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["xpath"]] = element
                else:
                    pNote("Browser {0} not found in the data "
                          "repository".format(system_name + "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict

    def get_element_by_id(self, system_name, id=None,
                             element_config_file=None, element_tag=None,
                             browser_name="all"):
        """
        This will get an element by the element's ID

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

            3. id = This contains the id of the element that you want to find.

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING ID, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ===============================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the id. So if  id = x_id,
            then Warrior can search for an element with that id

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            get_element_by_id, an child element of the element_tag with id
            as 'id' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. id must be given
                2. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If id is given, then it would have priority. Otherwise,
                the element_config_file would be searched

                The id and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. id(str) = id of the element
            3. browser_name(str) = Unique name for this particular browser
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its ID."
        output_dict = {}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
            pNote(browser_details)
            if browser_details is not None:
                if not browser_details["id"].startswith("id"):
                    browser_details["id"] = "id=" + browser_details["id"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    element = self.elem_loc_object.\
                        get_element(current_browser, browser_details["id"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["id"]] = element
                else:
                    pNote("Browser {0} not found in the data "
                          "repository".format(system_name + "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict

    def get_element_by_selector(self, system_name, css_selector=None,
                             element_config_file=None, element_tag=None,
                             browser_name="all"):
        """
        This will get an element by the element's CSS selector

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

            3. css_selector = This contains the css selector of the element that
                              you want to find.

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING CSS_SELECTOR, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ===============================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the id. So if
            css_selector = x_css_selector, then Warrior can search for an
            element with that css

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            get_element_by_selector, an child element of the element_tag with id
            as 'css' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. css_selector must be given
                2. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If css_selector is given, then it would have priority.
                Otherwise, the element_config_file would be searched

                The css_selector and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. css_selector(str) = css_selector of the element
            3. browser_name(str) = Unique name for this particular browser
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its CSS selector."
        output_dict ={}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
                if not browser_details["css_selector"].startswith("css"):
                    browser_details["css_selector"] = \
                        "css=" + browser_details["css_selector"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    element = self.elem_loc_object.\
                        get_element(current_browser,
                                    browser_details["css_selector"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["css_selector"]] = element
                else:
                    pNote("Browser {0} not found in the data "
                          "repository".format(system_name + "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict

    def get_element_by_link_text(self, system_name, link_text=None,
                             element_config_file=None, element_tag=None,
                             browser_name="all"):
        """
        This will get an element by the element's Link Text

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

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            3. link_text = This contains the link text of the element that
                           you want to find.

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING LINK_TEXT, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ====================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the link_text. So if
            link_text = x_link_text, then Warrior can search for an
            element with that link text

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            get_element_by_link_text, an child element of the element_tag with
            id as 'link' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. link_text must be given
                2. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If link_text is given, then it would have priority.
                Otherwise, the element_config_file would be searched

                The link_text and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. link_text(str) = link_text of the element
            3. browser_name(str) = Unique name for this particular browser
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its link text."
        output_dict = {}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
                if not browser_details["link_text"].startswith("link"):
                    browser_details["link_text"] = "link=" + \
                                                   browser_details["link_text"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    element = self.elem_loc_object.\
                        get_element(current_browser,
                                    browser_details["link_text"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["link_text"]] = element
                else:
                    pNote("Browser {0} not found in the data "
                          "repository".format(system_name +
                                              "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict

    def get_element_by_partial_link_text(self, system_name,
                                         partial_link_text=None,
                                         element_config_file=None,
                                         element_tag=None, browser_name="all"):
        """
        This will get an element by the element's Partial Link Text

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

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            3. partial_link_text = This contains the partial link text of the
                                   element that you want to find.

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING PARTIAL_LINK_TEXT, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ====================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the link_text. So if
            partial_link_text = x_partial_link_text, then Warrior can search for
            link element containing that text

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            get_element_by_link_text, an child element of the element_tag with
            id as 'partial_link' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. partial_link_text must be given
                2. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If partial_link_text is given, then it would have priority.
                Otherwise, the element_config_file would be searched

                The partial_link_text and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. partial_ink_text(str) = partial link text of the element
            3. browser_name(str) = Unique name for this particular browser
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its partial link text."
        output_dict = {}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
                if not browser_details["partial_link_text"].startswith("partial"):
                    browser_details["partial_link_text"] = "partial_link=" + browser_details["partial_link_text"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    element = self.elem_loc_object.\
                        get_element(current_browser,
                                    browser_details["partial_link_text"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["partial_link_text"]] = element
                else:
                    pNote("Browser {0} not found in the data "
                          "repository".format(system_name +
                                              "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict

    def get_element_by_tagname(self, system_name, tag_name=None,
                             element_config_file=None, element_tag=None,
                             browser_name="all"):
        """
        This will get an element by the element's tag name

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

            3. tag_name = This contains the tag name of the element that
                          you want to find.

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING TAG_NAME, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ====================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the tag_name. So if
            tag_name = x_tag_name, then Warrior can search for an
            element with that tag name

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            get_element_by_tag_name, an child element of the element_tag with
            id as 'tag' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. tag_name must be given
                2. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If tag_name is given, then it would have priority.
                Otherwise, the element_config_file would be searched

                The tag_name and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. tag_name(str) = tag_name of the element
            3. browser_name(str) = Unique name for this particular browser
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its TAG name."
        output_dict = {}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
                if not browser_details["tag_name"].startswith("tag"):
                    browser_details["tag_name"] = "tag=" + \
                                                  browser_details["tag_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    element = self.elem_loc_object.\
                        get_element(current_browser,
                                    browser_details["tag_name"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["tag_name"]] = element
                else:
                    pNote("Browser {0} not found in the data "
                          "repository".format(system_name +
                                              "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict

    def get_element_by_classname(self, system_name, class_name=None,
                             element_config_file=None, element_tag=None,
                             browser_name="all"):
        """
        This will get an element by the element's class name

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

            3. class_name = This contains the class name of the element that
                            you want to find.

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING CLASS_NAME, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ======================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the class_name. So if
            class_name = x_class_name, then Warrior can search for an
            element with that class name

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            get_element_by_class_name, an child element of the element_tag with
            id as 'class' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. class_name must be given
                2. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If class_name is given, then it would have priority.
                Otherwise, the element_config_file would be searched

                The class_name and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. class_name(str) = class_name of the element
            3. browser_name(str) = Unique name for this particular browser
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its CLASS name."
        output_dict = {}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
                if not browser_details["class_name"].startswith("class"):
                    browser_details["class_name"] = \
                        "class=" + browser_details["class_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    element = self.elem_loc_object.\
                        get_element(current_browser,
                                    browser_details["class_name"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["class_name"]] = element
                else:
                    pNote("Browser {0} not found in the data "
                          "repository".format(system_name + "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict

    def get_element_by_name(self, system_name, name_of_element=None,
                             element_config_file=None, element_tag=None,
                             browser_name="all"):
        """
        This will get an element by the element's name

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

            3. browser_name = This <browser_name> tag is a child og the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>

            3. name_of_element = This contains the name of the element that you
                                 want to find.

            4. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            5. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING NAME_OF_ELEMENT, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            ==========================================================

            None of these arguments are mandatory BUT to search an element,
            you need to provide Warrior with some way to do it.

            a. You can either directly give values for the name_of_element. So
            if name_of_element = x_name_of_element, then Warrior can search for
            an element with that name

            b. You can give location of the element_config_file and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there. Now, as this is the keyword -
            get_element_by_name, an child element of the element_tag with
            id as 'name' would be searched for in the element_config_file

            NOTES:
                For these three arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. name_of_element must be given
                2. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If name_of_element is given, then it would have priority.
                Otherwise, the element_config_file would be searched

                The name_of_element and the element_tag can be given the datafile
                as children of the <browser> tag, but these values would remain
                constant for that browser. It is recommended that these values
                be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        :Arguments:

            1. system_name(str) = the system name.
            2. name_of_element(str) = name_of_element of the element
            3. browser_name(str) = Unique name for this particular browser
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
            2. output_dict(dict) = dictionary containing information about the
                                   browser
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Finding an element by its name."
        output_dict = {}
        pNote(wdesc)
        pSubStep(wdesc)
        element = None
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
                if not browser_details["name_of_element"].startswith("name"):
                    browser_details["name_of_element"] = \
                        "name=" + browser_details["name_of_element"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(system_name + "_" + browser_details["browser_name"])
                if current_browser:
                    element = self.elem_loc_object.\
                        get_element(current_browser,
                                    browser_details["name_of_element"])
                    output_dict[system_name + "_" +
                                browser_details["browser_name"] + "_" +
                                browser_details["name_of_element"]] \
                        = element
                else:
                    pNote("Browser {0} not found in the data"
                          "repository".format(system_name + "_" +
                                              browser_details["browser_name"]),
                          "Error")
                    status = False
            browser_details = {}
        if element is None or element is False:
            status = False
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status, output_dict
