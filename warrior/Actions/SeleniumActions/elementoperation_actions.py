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

""" Selenium keywords for Element Operation Actions """
from Framework.ClassUtils.WSelenium.element_operations import ElementOperations
from Framework.ClassUtils.json_utils_class import JsonUtils
from Framework.Utils.list_Utils import get_list_comma_sep_string

try:
    import Framework.Utils as Utils
except ImportWarning:
    raise ImportError

from Framework.Utils import data_Utils
from Framework.Utils import selenium_Utils
from Framework.Utils.testcase_Utils import pNote,pSubStep
from Framework.Utils import xml_Utils

class elementoperation_actions(object):
    """This is a class that deals with all 'element' (HTML element) related
    operations like clicking on an element, drag and drop of an element,
    hovering on an element"""

    def __init__(self):
        """This is a constructor for the elementoperation_actions class"""
        self.datafile = Utils.config_Utils.datafile
        self.jsonobj = JsonUtils()
        self.elem_oper_obj = ElementOperations()

    def clear_text(self, system_name, locator_type=None, locator=None,
                   element_config_file=None, element_tag=None,
                   browser_name="all"):
        """
        This will clear text in the given element

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

            4. browser_name = This <browser_name> tag is a child og the
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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Clear the text"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                                   browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name),
                              "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator, "clear_text",
                                                   browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "clear_text",
                                               browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def verify_text(self, system_name, locator_type=None, locator=None,
                   element_config_file=None, element_tag=None, var=None,
                   expected=None, browser_name="all"):
        """
        This will get text in the given element and store in the data repository
        as var variable if specified else stores in "default" var and verify
        if it is same as expected if expected provided

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

            4. browser_name = This <browser_name> tag is a child og the
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
            7. var = variable name in data repository where this text will
                     be stored. If not provided, would be stored in element_name
                     got by system_name + "_" + browser_details["browser_name"] + 
                     "_" + comp_locator
            8. expected = The expected value for this text. If not provided
                          only the var would be stored in data repository but
                          verification wont be done

            USING LOCATOR_TYPE, LOCATOR, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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

            - If locator_type is not given, and the defaults are not
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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file
            7. var(str) = name in which text would be stored in data repository
                          if not provided, would be stored in element_name
                          got by system_name + "_" + browser_details["browser_name"] +
                          "_" + comp_locator (optional)
            8. expected(str) = string to be verified with text (optional)

        :Returns:

            1. status(bool)= True if expected is provided and it matches with
                             text otherwise False.

        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "verify the text from the element/input box"
        " is matching expected"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                                                                'self.datafile',
                                                                browser)
            if browser_details == {}:
                browser_details = selenium_Utils. \
                    get_browser_details(browser, datafile=self.datafile, **arguments)
            if browser_details is not None:
                comp_locator = browser_details["locator_type"] + "=" + \
                                   browser_details["locator"]
                element_name = system_name + "_" + \
                    browser_details["browser_name"] + "_" + comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_element = Utils.data_Utils.\
                    get_object_from_datarepository(element_name)
                if not var:
                    var = element_name + "_text"
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    current_browser = Utils.data_Utils.\
                        get_object_from_datarepository(br_name)
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name),
                              "error")
                    else:
                        '''work on the browser instance on which to perform the
                        action since enclosed element not provided
                        '''
                        status, value = self.elem_oper_obj.perform_element_action(
                            current_browser, comp_locator, "get_text",
                            browser=current_browser)
                        data_Utils.update_datarepository({var: value})
                        if expected is not None:
                            status = self.elem_oper_obj.verify_text(
                                    var=var, expected=expected)
                else:
                    '''enclosing element of the locator is itself provided
                    use that to perform the action
                    '''
                    status, value = self.elem_oper_obj.perform_element_action(
                        current_element, comp_locator, "get_text",
                        browser=current_browser)
                    data_Utils.update_datarepository({var: value})
                    if expected is not None:
                        status = self.elem_oper_obj.verify_text(
                                var=var, expected=expected)
            browser_details = {}
        step_res = 'TRUE' if status else 'ERROR'
        Utils.testcase_Utils.report_substep_status(step_res)
        return status

    def click_an_element(self, system_name, locator_type=None, locator=None,
                         element_config_file=None, element_tag=None,
                         browser_name="all"):
        """
        This will simulate a click on the given element

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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Simulate a click"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator, "click",
                                                   browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "click", browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def clear(self, system_name, locator_type=None, locator=None,
              element_config_file=None, element_tag=None, browser_name="all"):
        """
        This will clear any text, checks on the given element

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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Clear all actions performed on an element"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator, "clear",
                                                   browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "clear", browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def type_text(self, system_name, locator_type=None, locator=None,
                  element_config_file=None, element_tag=None, text="",
                  browser_name="all"):
        """
        This will type text into a given element

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

            3. text = This would contain text that you want to type into any
                      element. This can be given as a child of the <browser> tag
                      but that restricts you to only that text per browser
                      instance. It is therefore recommended that you include
                      this as an argument to the testcase step or include it as
                      a child of a particular element_tag in the
                      element_config_file

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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "This would type text into an input element"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator, "type",
                                                   value=browser_details["text"],
                                                   browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "type", value=browser_details["text"],
                                               browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def fill_an_element(self, system_name, locator_type=None, locator=None,
                        element_config_file=None, element_tag=None, text="",
                        browser_name="all"):
        """
        This will fill an element

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

            3. text = This would contain text that you want to type into any
                      element. This can be given as a child of the <browser> tag
                      but that restricts you to only that text per browser
                      instance. It is therefore recommended that you include
                      this as an argument to the testcase step or include it as
                      a child of a particular element_tag in the
                      element_config_file

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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Fills an element"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator,
                                                   "fill", value=browser_details["text"],
                                                   browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "fill", value=browser_details["text"],
                                               browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def send_keys_to_an_element(self, system_name, locator_type=None, locator=None,
                                element_config_file=None, element_tag=None,
                                text="", browser_name="all"):
        """
        This will send keys like ENTER, COMMAND, F1 to the element

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

            3. text = This would contain key like ENTER, CONTROL, ESCAPE - that
                      you want to type. This can be given as a child of the
                      <browser> tag but that restricts you to only that text per
                      browser instance. It is therefore recommended that you
                      include this as an argument to the testcase step or
                      include it as a child of a particular element_tag in the
                      element_config_file

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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "This will send Keyboard Keys to an element"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator,
                                                   "send_keys",
                                                   value=browser_details["text"],
                                                   browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "send_keys",
                                               value=browser_details["text"],
                                               browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def double_click_an_element(self, system_name, locator_type=None,
                                locator=None, element_config_file=None,
                                element_tag=None, browser_name="all"):
        """
        This will simulate a double-click on the given element

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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Simulate a double-click"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator, "double_click",
                                                   browser=current_browser)
                else:
                    current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "double_click",
                                               browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def drag_and_drop_an_element(self, system_name, source_locator_type=None,
                                 source_locator=None, target_locator_type=None,
                                 target_locator=None, element_config_file=None,
                                 second_element_config_file=None,
                                 element_tag=None, second_element_tag=None,
                                 browser_name="all"):
        """
        This will simulate a drag and drop on the given element

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

            3. source_locator_type = This contains information about the type
                                     of locator that you want to use to locate
                                     the source element that needs to dragged.
                                     Can be 'xpath', 'id', 'css', 'link', 'tag',
                                     'class', 'name'

            4. source_locator = This contains the value of the locator of the
                                source element that needs to be dragged.
                                Something like "form", "nav-tags",
                                "//[dh./dhh[yby]"

            5. target_locator_type = This contains information about the type
                                     of locator that you want to use to locate
                                     the target element where the source element
                                     needs to be dropped. Can be 'xpath', 'id',
                                     'css', 'link', 'tag', 'class', 'name'

            6. target_locator = This contains the value of the locator that you
                                want to use to locate the target element where
                                the source element needs to be dropped.
                                Something like "form", "nav-tags",
                                "//[dh./dhh[yby]"

            7. element_config_file = This contains the location of the default
                                     json file that contains information about
                                     all the elements that you require for the
                                     testcase execution

            8. element_tag = This contains the name of the default element in
                             either of the element_config_files which you want
                             to use

            9. second_element_config_file = This contains the location of the
                                    second json file that you may want to use

            10. second_element_tag = This contains the name of the element in
                             either of the element_config_files which you want
                             to use

            USING SOURCE_LOCATOR_TYPE, LOCATOR, TARGET_LOCATOR_TYPE,
            TARGET_LOCATOR, ELEMENT_CONFIG_FILE, ELEMENT_TAG,
            SECOND_ELEMENT_CONFIG_FILE, AND SECOND_ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

            a. You can either directly give values for the
            source/target_locator_type and source/target_locator. So if
            source/target_locator_type = name and
            source/target_locator = navigation-bar, then Warrior can search for
            an element with name "navigation-bar"

            b. You can give location of the element_config_files and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there.

            - Now, if the source/target_locator type is given, Warrior
            will search for that source/target_locator_type in the children of
            that element in the element_config_file

            - You can also set defaults in the element_config_files, and now,
            even if the source/target_locator_type is not given, Warrior will
            know which element to find. If source/target_locator_type is given,
            the default will be overridden

            - If source/target_locator_type is not given, and the defaults are
            not specified, then the first element in the child list of the
            element tag would be picked.

            NOTES:
                For these four arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. source/target_locator_type and source/target_locator must be
                   given
                2. source/target_locator_type, element_config_file, and
                   element_tag must be given
                3. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If all arguments are passed from the same place, then, if
                source/target_locator and source/target_locator_type are given,
                then they would have priority. Otherwise, the
                element_config_file would be searched

                The source/target_locator_type locator, element_tag can be given
                the datafile as children of the <browser> tag, but these values
                would remain constant for that browser. It is recommended that
                these values be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        The element_config_files and element_tags can be linked to one another
        as the example given below:

        Eg:

        <step TS= '25' Driver='selenium_driver' Keyword='drag_and_drop_an_element' >
            <Arguments>
                <argument name="system_name" value="system_1"/>
                <argument name="source_locator_type" value="element_tag=xpath"/>
                <argument name="target_locator_type" value="second_element_tag=xpath"/>
                <argument name="element_config_file" value="../Config_files/demo_selenium_tc_Config_1.json"/>
                <argument name="second_element_config_file" value="../Config_files/demo_selenium_tc_Config_2.json"/>
                <argument name="element_tag" value="element_config_file=source"/>
                <argument name="second_element_tag" value="second_element_config_file=target"/>
            </Arguments>
        </step>

        Here, the source_locator_type will be searched for in the element_tag
        in the element_config_file, while the the target_locator_type will be
        searched for in the second_element_tag in the second_element_config_file

        :Arguments:

            1. system_name(str) = the system name.
            2. source_locator_type(str) = type of the locator - xpath, id, etc
                                          for the source element
            3. source_locator(str) = locator by which the elemnt should be
                                     located for the source element
            2. target_locator_type(str) = type of the locator - xpath, id, etc
                                          for the target element
            3. target_locator(str) = locator by which the elemnt should be
                                     located for the target element
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Simulate a drag and drop"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                source_comp_locator = browser_details["source_locator_type"] + "=" + browser_details["source_locator"]
                target_comp_locator = browser_details["target_locator_type"] + "=" + browser_details["target_locator"]
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                else:
                    status = self.elem_oper_obj.perform_element_action(current_browser, source_comp_locator, "drag_and_drop", browser=current_browser, target_locator=target_comp_locator)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def mouse_over(self, system_name, locator_type=None, locator=None,
                   element_config_file=None, element_tag=None,
                   browser_name="all"):
        """
        This will perform the mouse over operation in the given element

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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. locator(str) = locator by which the elemnt should be located.
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.

        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "simulate a mouse over operation"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name),
                              "error")
                    else:
                        status = self.elem_oper_obj.\
                                 perform_element_action(current_browser,
                                                        comp_locator, "mouse_over",
                                                        browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                             perform_element_action(current_element, comp_locator,
                                                    "mouse_over",
                                                    browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def execute_script(self, system_name, user_script=None, browser_name="all"):
        """
        This will execute the user provided script
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
            2. user_script = string containing javascript as argument

            3. browser_name = This <browser_name> tag is a child of the
                              <browser> tag in the data file. Each browser
                              instance should have a unique name. This name can
                              be added here

                              Eg: <browser_name>Unique_name_1</browser_name>
        :Arguments:

            1. system_name(str) = the system name.
            2. user_script(str) = string containing javascript
            3. browser_name(str) = Unique name for this particular browser

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False

        wdesc = "To execute a user provided script"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                if not current_browser:
                    pNote("No browser instance {0} found in the data repository!".format(br_name), "error")
                else:
                    status = selenium_Utils.execute_script(current_browser, browser_details["user_script"])
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def drag_and_drop_by_offset(self, system_name, source_locator_type=None,
                                source_locator=None, element_config_file=None,
                                element_tag=None, xoffset=None, yoffset=None,
                                browser_name="all"):
        """
        This will drag and drop the given element to the user provided x and y offset position
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

            3. source_locator_type = This contains information about the type
                                     of locator that you want to use to locate
                                     the source element that needs to dragged.
                                     Can be 'xpath', 'id', 'css', 'link', 'tag',
                                     'class', 'name'

            4. source_locator = This contains the value of the locator of the
                                source element that needs to be dragged.
                                Something like "form", "nav-tags",
                                "//[dh./dhh[yby]"

            5. element_config_file = This contains the location of the default
                                     json file that contains information about
                                     all the elements that you require for the
                                     testcase execution

            6. element_tag = This contains the name of the default element in
                             either of the element_config_files which you want
                             to use


            USING SOURCE_LOCATOR_TYPE, LOCATOR, ELEMENT_CONFIG_FILE, ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

            a. You can either directly give values for the
            source_locator_type and source_locator. So if
            source_locator_type = name and
            source_locator = navigation-bar, then Warrior can search for
            an element with name "navigation-bar"

            b. You can give location of the element_config_files and a tag inside
            it so that Warrior can search for that tag and get the required
            information from there.

            - Now, if the source_locator type is given, Warrior
            will search for that source_locator_type in the children of
            that element in the element_config_file

            - You can also set defaults in the element_config_files, and now,
            even if the source_locator_type is not given, Warrior will
            know which element to find. If source_locator_type is given,
            the default will be overridden

            - If source_locator_type is not given, and the defaults are
            not specified, then the first element in the child list of the
            element tag would be picked.
            NOTES:
                For these four arguments to be given correctly, ONE of the
                following conditions must be satisfied.

                1. source_locator_type and source_locator must be
                   given
                2. source_locator_type, element_config_file, and
                   element_tag must be given
                3. element_config_file, and element_tag must be given

                The datafile has the first priority, then the json file, and
                then finally the testcase.

                If all arguments are passed from the same place, then, if
                source_locator and source_locator_type are given,
                then they would have priority. Otherwise, the
                element_config_file would be searched

                The source_locator_type locator, element_tag can be given
                the datafile as children of the <browser> tag, but these values
                would remain constant for that browser. It is recommended that
                these values be passed from the testcase step.

                The element_config_file typically would not change from step to
                step, so it can be passed from the data file

        The element_config_files and element_tags can be linked to one another
        as the example given below:

        Eg:

        <step TS= '25' Driver='selenium_driver' Keyword='drag_and_drop_an_element' >
            <Arguments>
                <argument name="system_name" value="system_1"/>
                <argument name="source_locator_type" value="element_tag=xpath"/>
                <argument name="element_config_file" value="../Config_files/demo_selenium_tc_Config_1.json"/>
                <argument name="element_tag" value="element_config_file=source"/>
                <argument name="xoffset" value="100"/>
                <argument name="yoffset" value="0"/>
            </Arguments>
        </step>
        Here, the source_locator_type will be searched for in the element_tag
        in the element_config_file

        :Arguments:

            1. system_name(str) = the system name.
            2. source_locator_type(str) = type of the locator - xpath, id, etc
                                          for the source element
            3. source_locator(str) = locator by which the elemnt should be
                                     located for the source element
            4. element_config_file(str) = location of the element config file
            5. element_tag(str) = json id of the locator that you want to use
                                  from the element config file
            6. xoffset = X offset to move to
            7. yoffset = Y offset to move to
            8. browser_name(str) = Unique name for this particular browser

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Simulate a drag and drop with offset"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                source_comp_locator = browser_details["source_locator_type"] + "=" + browser_details["source_locator"]
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                else:
                    status = self.elem_oper_obj.perform_element_action(current_browser,
                                                                       source_comp_locator,
                                                                       "drag_and_drop_by_offset",
                                                                       browser=current_browser,
                                                                       xoffset=browser_details["xoffset"],
                                                                       yoffset=browser_details["yoffset"])
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def get_property_of_element(self, system_name, attribute_name,
                                locator_type=None, locator=None,
                                element_config_file=None, element_tag=None,
                                browser_name="all"):
        """
        This will get property or attribute of the given element

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

            3. attribute_name = This contains information about the attribute
                                name of the element who's property you want to
                                get.

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

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. attribute_name (str) = Name of the attribute
            4. locator(str) = locator by which the elemnt should be located.
            5. browser_name(str) = Unique name for this particular browser
            6. element_config_file(str) = location of the element config file
            7. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Gets the requested attribute or property of the element."
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator, "get_property",
                                                   attribute_name=browser_details["attribute_name"],
                                                   browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "get_property",
                                               attribute_name=browser_details["attribute_name"],
                                               browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def check_property_of_element(self, system_name, attribute_name,
                                  property_name, locator_type=None,
                                  locator=None, element_config_file=None,
                                  element_tag=None, browser_name="all"):
        """This will get property or attribute of the given element

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

            3. attribute_name = This contains information about the attribute
                                name of the element who's property you want to
                                verify.

            4. property_name = This contains information about the property you
                               want to verify.

            5. locator_type = This contains information about the type of
                              locator that you want to use. Can be 'xpath',
                              'id', 'css', 'link', 'tag','class', 'name'

            6. locator = This contains the value of the locator. Something like
                         "form", "nav-tags", "//[dh./dhh[yby]"

            7. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution
            8. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

            USING LOCATOR_TYPE, LOCATOR, ELEMENT_CONFIG_FILE, AND ELEMENT_TAG
            =================================================================

            None of these arguments are mandatory BUT to search an element or to
            retrieve it from the data repository, you need to provide Warrior
            with some way to do it.

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
            3. attribute_name (str) = Name of the attribute
            4. property_name (str) = Name of the property
            5. locator(str) = locator by which the elemnt should be located.
            6. browser_name(str) = Unique name for this particular browser
            7. element_config_file(str) = location of the element config file
            8. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = False
        wdesc = "Checks the given attribute or property of the element."
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                comp_locator = browser_details["locator_type"] + "=" + \
                               browser_details["locator"]
                element_name = system_name + "_" + \
                               browser_details["browser_name"] + "_" + \
                               comp_locator
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.get_object_from_datarepository(br_name)
                current_element = Utils.data_Utils.get_object_from_datarepository(element_name)
                if not current_element:
                    pNote("No element instance {0} found in the data "
                          "repository!".format(element_name), "info")
                    if not current_browser:
                        pNote("No browser instance {0} found in the data "
                              "repository!".format(br_name), "error")
                    else:
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   comp_locator,
                                                   "check_property",
                                                   attribute_name=browser_details["attribute_name"],
                                                   property_name=browser_details["property_name"],
                                                   browser=current_browser)
                else:
                    status = self.elem_oper_obj.\
                        perform_element_action(current_element, comp_locator,
                                               "check_property",
                                               attribute_name=browser_details["attribute_name"],
                                               property_name=browser_details["property_name"],
                                               browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status

    def perform_keypress(self, system_name, keys, simultaneous="yes",
                         element_config_file=None,
                         element_tag=None, browser_name="all"):
        """
        This will simulate key presses for the given keys

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

            3. keys = This argument takes in the keys whose keypresses need to
                      be simulated. It an be just one key - or if multiple
                      keys are needed, then a comma separated list of keys

                      Eg: f5
                          control, alt, delete

            4. simultaneous = When set to 'yes', all the key-presses for the
                              given keys would be performed simultaneously. When
                              set to 'no', the key-presses for the keys would be
                              simulated one after the other.


            7. element_config_file = This contains the location of the json
                                     file that contains information about all
                                     the elements that you require for the
                                     testcase execution

            8. element_tag = This contains the name of the element in that
                             element_config_file which you want to use

        :Arguments:

            1. system_name(str) = the system name.
            2. keys (str) = The keys whose key-presses have to be simulated
            3. simultaneous (str) = Whether the keys given above should be
                                    pressed simultaneously or not
            4. browser_name(str) = Unique name for this particular browser
            5. element_config_file(str) = location of the element config file
            6. element_tag(str) = json id of the locator that you want to use
                                  from the element config file

        :Returns:

            1. status(bool)= True / False.
        """
        arguments = locals()
        arguments.pop('self')
        status = True
        wdesc = "Simulates key presses for the given keys"
        pNote(wdesc)
        pSubStep(wdesc)
        Utils.testcase_Utils.pSubStep(wdesc)
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
                br_name = system_name + "_" + browser_details["browser_name"]
                current_browser = Utils.data_Utils.\
                    get_object_from_datarepository(br_name)
                if not current_browser:
                    pNote("No browser instance {0} found in the data "
                          "repository!".format(br_name), "error")
                else:
                    list_keys = get_list_comma_sep_string(browser_details["keys"])
                    if simultaneous.lower() == "yes":
                        pNote("Simulating simultaneous key presses for keys: {0}".format(browser_details["keys"]))
                        status = self.elem_oper_obj.\
                            perform_element_action(current_browser,
                                                   None,
                                                   "perform_keypress",
                                                   keys=list_keys,
                                                   browser=current_browser)
                    else:
                        for key in list_keys:
                            pNote("Simulating key press for {0}".format(key))
                            status = status and self.elem_oper_obj.\
                                perform_element_action(current_browser,
                                                       None,
                                                       "perform_keypress",
                                                       keys=[key],
                                                       browser=current_browser)
            browser_details = {}
        Utils.testcase_Utils.report_substep_status(status)
        if current_browser:
            selenium_Utils.save_screenshot_onerror(status, current_browser)
        return status
