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

""" Selenium element operations library """
from time import sleep
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


from Framework.Utils.print_Utils import print_error, print_info, print_exception
from Framework.Utils.data_Utils import get_object_from_datarepository
from Framework.ClassUtils.WSelenium.element_locator import ElementLocator

try:
    from selenium.webdriver.remote.webelement import WebElement
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import StaleElementReferenceException
except ImportError as exception:
    print_exception(exception)

EL = ElementLocator()
ACTIONS = {'click': '_click_element',
           'double_click': '_double_click_element',
           'send_keys': '_send_keys',
           'type': '_type_keys',
           'fill': '_type_keys',
           'clear_text': '_clear_text',
           'get_text': '_get_text',
           'clear': '_clear_text',
           'drag_and_drop': '_drag_and_drop',
           'mouse_over':'_mouse_over',
           'drag_and_drop_by_offset':'_drag_and_drop_by_offset',
           'get_property': '_get_property',
           'check_property': '_check_property',
           'perform_keypress': '_perform_keypress'
           }
KEYS = {'ADD': Keys.ADD, 'ALT': Keys.ALT, 'ARROW_DOWN': Keys.ARROW_DOWN,
        'ARROW_LEFT': Keys.ARROW_LEFT, 'ARROW_RIGHT': Keys.ARROW_RIGHT, 'ARROW_UP': Keys.ARROW_UP,
        'BACKSPACE': Keys.BACK_SPACE, 'CANCEL': Keys.CANCEL, 'CLEAR': Keys.CLEAR,
        'COMMAND': Keys.COMMAND, 'CONTROL': Keys.CONTROL, 'DECIMAL': Keys.DECIMAL,
        'DELETE': Keys.DELETE, 'DIVIDE': Keys.DIVIDE, 'DOWN': Keys.DOWN, 'END': Keys.END,
        'ENTER': Keys.RETURN, 'EQUALS': Keys.EQUALS, 'ESCAPE': Keys.ESCAPE, 'F1': Keys.F1,
        'F10': Keys.F10, 'F11': Keys.F11, 'F12': Keys.F12, 'F2': Keys.F2, 'F3': Keys.F3, 'F4': Keys.F4,
        'F5': Keys.F5, 'F6': Keys.F6, 'F7': Keys.F7, 'F8': Keys.F8, 'F9': Keys.F9,
        'HELP': Keys.HELP, 'HOME': Keys.HOME, 'INSERT': Keys.INSERT, 'LEFT': Keys.LEFT,
        'LEFT_ALT': Keys.LEFT_ALT, 'LEFT_CONTROL': Keys.LEFT_CONTROL, 'LEFT_SHIFT': Keys.LEFT_SHIFT,
        'META': Keys.META, 'MULTIPLY': Keys.MULTIPLY, 'NULL': Keys.NULL, 'NUMPAD0': Keys.NUMPAD0,
        'NUMPAD1': Keys.NUMPAD1, 'NUMPAD2': Keys.NUMPAD2, 'NUMPAD3': Keys.NUMPAD3,
        'NUMPAD4': Keys.NUMPAD4, 'NUMPAD5': Keys.NUMPAD5, 'NUMPAD6': Keys.NUMPAD6,
        'NUMPAD7': Keys.NUMPAD7, 'NUMPAD8': Keys.NUMPAD8,  'NUMPAD9': Keys.NUMPAD9,
        'PAGE_DOWN': Keys.PAGE_DOWN, 'PAGE_UP': Keys.PAGE_UP, 'PAUSE': Keys.PAUSE,
        'RETURN': Keys.RETURN, 'RIGHT': Keys.RIGHT, 'SEMICOLON': Keys.SEMICOLON, 'SEPARATOR': Keys.SEPARATOR,
        'SHIFT': Keys.SHIFT, 'SPACE': Keys.SPACE, 'SUBTRACT': Keys.SUBTRACT, 'TAB': Keys.TAB,
         'UP': Keys.UP
         }


class ElementOperations():
    """ Element operations """

    def __init__(self, *args, **kwargs):
        """ constructor """
        pass

    def perform_element_action(self, element_or_browser, locator=None,
                               action=None, **kwargs):
        """Generic method to perform specific actions on an element
        :Currently supported actions and the values that they take
        if the user provided action is "get_text", it would return the
        value of the particular element and the status of it. If not it would
        return only the status"""
        browser = kwargs.get('browser')
        status = True
        if action != "perform_keypress":
            element = self._get_element(element_or_browser, locator)
        else:
            element = element_or_browser
        if element:
            action_function = self._get_action_function(action.lower())
            if not action_function:
                print_error((action + " is not a supported "
                             "a supported value."))
            else:
                count = 0
                while (count <= 3):
                    try:
                        if action == "get_text":
                            status, value = action_function(element, **kwargs)
                            if status is True:
                                return status, value
                            else:
                                status, count = self.wait_time(count, browser,
                                                               locator,
                                                               action)
                                if status is True:
                                    return status
                        else:
                            status = action_function(element, **kwargs)
                            if status is True:
                                return status
                            else:
                                status, count = self.wait_time(count, browser,
                                                               locator,
                                                               action)
                                if status is True:
                                    return status
                    except StaleElementReferenceException:
                        status = False
                        try:
                            if action == "get_text":
                                count = count + 1
                                print_info("waiting for 3 seconds "
                                           "before retrying")
                                sleep(3)
                                status, value = action_function(element,
                                                                **kwargs)
                                if status is True:
                                    return status, value
                            else:
                                status, count = self.wait_time(count, browser,
                                                               locator,
                                                               action)
                                if status is True:
                                    return status
                        except StaleElementReferenceException:
                            status = False
                    except Exception as exception:
                        status = False
                        print_exception(exception)
                        return status
                else:
                    print_error("StaleElementReferenceException occured."
                                "Tried three times to locate the element")
                    status = False
        else:
            status = False
            print_error("Provide a valid WebElement to perform "
                        "a {0} operation got {1}".format(action, element))
        return status

    def wait_time(self, count, browser, locator, action):
        """ wait time to find the element again """
        count = count + 1
        print_info("waiting for 3 seconds before retrying")
        sleep(3)
        status = self._stale_element_exception(browser, locator, action)
        return status, count

    def get_page_source(self, browser):
        '''
        Get page source of the browser
        '''
        return browser.getPageSource()

    def verify_text(self, **kwargs):
        """stores the text from element in data repository with var variable
        and verifies if it is same as expected if expected is provided
        :Arguments:
            1. var = variable in which to store the text
            2. expected = value to compare with as a list separated by comma
        """
        status = True
        value = get_object_from_datarepository(kwargs.get('var'))
        expected = kwargs.get('expected').split(',')
        if value not in expected:
            print_error("element text expected to be <<{}>> "
                        "but found to be <<{}>>".format(', '.join(expected),
                                                        value))
            status = False

        return status

# Private methods

    def _stale_element_exception(self, browser, locator, action, **kwargs):
        element = EL.get_element(browser, locator)
        if element is not None:
            action_function = self._get_action_function(action.lower())
            status = action_function(element, **kwargs)
            return status

    def _get_element(self, element_or_browser, locator):
        """Get the element based on the provided input"""
        value = None
        if isinstance(element_or_browser, WebElement):
            value = element_or_browser
        else:
            value = EL.get_element(element_or_browser, locator)
        return value

    def _mouse_over(self, element, **kwargs ):
        """Moving the mouse to the middle of an element """
        status = False
        print_info("mouse over operation")
        browser_instance = kwargs.get('browser')
        if element is not None:
            ActionChains(browser_instance).move_to_element(element).perform()
            status = True
        return status

    def _get_action_function(self, action):
        """Gets the function call corresponding to the
        action to be performed"""
        action_function = ACTIONS.get(action.lower().replace(' ', ''), None)
        return getattr(self, action_function) if action_function else None

    def _click_element(self, element, **kwargs):
        """ Clicks on the provided element
        :Arguments:
            1. element = a valid WebElement
        """
        status = True
        print_info("Click on element")
        try:
            if element is not None:
                element.click()
        except Exception as e:
            print_error("An Exception Occurred {}".format(e))
            status = False
        return status

    def _double_click_element(self, element, **kwargs):
        """ Double clicks on the provided element
        :Arguments:
            1. element = a valid WebElement
        """
        status = True
        print_info("Double click on element")
        try:
            browser_instance = kwargs.get('browser')
            ActionChains(browser_instance).double_click(element)
        except Exception as e:
            print_error("An Exception Occurred {}".format(e))
            status = False
        return status

    def _type_keys(self, element, **kwargs):
        """Send values to a particular element,
        simulates typing into a element
        :Arguments:
            1. element = a valid WebElement
            2. value = a string that has to be typed into the element.
        """
        status = True
        value = kwargs.get('value', '')
        print_info("Sending '{0}' to element".format(value))
        try:
            element.send_keys(value)
        except Exception as e:
            print_error("An Exception Occurred {}".format(e))
            status = False
        return status

    def _send_keys(self, element, **kwargs):
        """Send values to a particular element,
        simulates typing into a element
        :Arguments:
            1. element = a valid WebElement
            2. value = a Keys object that has to be sent to the element.
        """
        status = True
        value = kwargs.get('value', '')
        try:
            KEYS[value.upper()]
        except KeyError:
            print_error("{0} is not supported by Selenium.".format(value))
            status = False
        else:
            print_info("Type text='{0}' into element".format(value))
            element.send_keys(KEYS[value.upper()])
        return status

    def _drag_and_drop(self, source, **kwargs):
        """Send values to a particular element,
        simulates typing into a element
        :Arguments:
            1. source = a valid WebElement
            2. target = a valid WebElement
        """
        status = True
        print_info("Simulate a drag and drop")
        try:
            browser_instance = kwargs.get('browser')
            target = self._get_element(browser_instance,
                                       kwargs.get('target_locator'))
            if source is not None and target is not None:
                ActionChains(browser_instance).drag_and_drop(source,
                                                             target).perform()
        except Exception as e:
            print_error("An Exception Occurred {}".format(e))
            status = False
        return status

    def _drag_and_drop_by_offset(self, source, **kwargs):
        """Holds down the left mouse button on the source element,
           then moves to the target offset and releases the mouse button
        :Arguments:
            1. source  = a valid WebElement
            2. xoffset = X offset to move to
            3. yoffset = Y offset to move to
        """
        status = True
        print_info("drag and drop an element with offset")
        try:
            xoffset = kwargs.get('xoffset')
            yoffset = kwargs.get('yoffset')
            browser_instance = kwargs.get('browser')
            actions = ActionChains(browser_instance)
            actions.drag_and_drop_by_offset(source, xoffset, yoffset).perform()
        except NoSuchElementException as e:
            print_error("NoSuchElementException occurred")
            status = False
        except Exception as e:
            print_error("An Exception Occurred {}".format(e))
            status = False
        return status

    def _clear_text(self, element, **kwargs):
        """Clears the text if it is a text element
        :Arguments:
            1. element = a valid WebElement
        """
        status = True
        print_info("Clear element")
        try:
            element.clear()
        except Exception as e:
            print_error("An Exception Occurred {}".format(e))
            status = False
        return status

    def _get_text(self, element, **kwargs):
        """gets the text from element
        :Arguments:
            1. element = a valid WebElement
        """
        print_info("get element text")
        print_info("tag: "+element.tag_name)
        if element.tag_name == "input":
            value = element.get_attribute("value")
        else:
            value = element.text
        if value is not None:
            status = True
        print_info("The text for this element is {}".format(value))
        return status, value

    def _get_property(self, element, **kwargs):
        status = True
        if element is not None:
            attribute_name = kwargs.get('attribute_name')
            attr_properties = element.get_attribute(attribute_name)
            if attr_properties is not None:
                print_info("The properties of the attribute '{0}' "
                           "are {1}".format(attribute_name, attr_properties))
            else:
                print_error("Could not find attribute '{0}', hence could not "
                            "retrieve its properties.".format(attribute_name))
                status = False
        else:
            status = False
        return status

    def _check_property(self, element, **kwargs):
        status = True
        if element is not None:
            attribute_name = kwargs.get('attribute_name')
            property_name = kwargs.get('property_name')
            attr_properties = element.get_attribute(attribute_name)
            if attr_properties is not None:
                if property_name in attr_properties:
                    print_info("{0} has a property called {1}. Verification "
                               "success!".format(attribute_name, property_name))
                else:
                    print_error("{0} does not have a property called {1}. "
                                "Verification failed!".format(attribute_name,
                                                              property_name))
                    status = False
            else:
                print_error("Could not find attribute '{0}', hence could not "
                            "retrieve its properties.".format(attribute_name))
                status = False
        else:
            status = False
        return status

    def _perform_keypress(self, element, **kwargs):
        """
        This function expects to receive a browser instance through the
        "browser" argument and a key "keys" through the kwargs.

        The value for "keys" would be a list of keys tha need to pressed.

        """
        status = True
        flag = False
        keys = kwargs.get('keys')
        actions = ActionChains(element)
        for key in keys:
            try:
                selenium_key = KEYS[key.upper()]
            except KeyError:
                print_error("{0} is not supported by Selenium.".format(key))
                status = False
            else:
                flag = True
                actions.send_keys(selenium_key)
        if flag:
            actions.perform()
            sleep(2)

        return status
