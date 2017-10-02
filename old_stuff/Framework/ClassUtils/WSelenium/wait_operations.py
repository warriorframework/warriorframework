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

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


from Framework.Utils.print_Utils import print_error

BYCLASS = {'ID': By.ID,
           'NAME': By.NAME,
           'XPATH': By.XPATH,
           'LINK': By.LINK_TEXT,
           'PARTIAL_LINK': By.PARTIAL_LINK_TEXT,
           'TAG': By.TAG_NAME,
           'CLASS': By.CLASS_NAME,
           'CSS_SELECTOR': By.CSS_SELECTOR}

class WaitOperations():
    """Wait operations class"""
    
    def __init__(self, *args, **kwargs):
        """consructor """

    def wait_until_element_is_clickable(self, browser_instance, locator_type, locator,
                                        timeout=5):
        try:
            WebDriverWait(browser_instance, int(timeout)).until(EC.element_to_be_clickable((BYCLASS[locator_type.strip().upper()], locator)))
            status = True
        except KeyError:
            print_error("The given locator_type - '{0}' does not match any of "
                        "the accepted locator_types.".format(locator_type))
            print_error("{0}, {1}, {2}, {3}, {4}, {5}, {6}, and {7} are the "
                        "accepted locator types.".format("id", "xpath", "link"
                                                         "class", "tag", "name",
                                                         "css_selector",
                                                         "partial_link"))
            status = "ERROR"
        except TimeoutException:
            print_error("Element unclickable after {0} seconds".format(timeout))
            status = False
        except Exception as e:
            print_error("An Exception Ocurred: {0}".format(e))
            status = "ERROR"
        return status

    def wait_until_presence_of_element_located(self, browser_instance,
                                               locator_type, locator, timeout=5):
        try:
            WebDriverWait(browser_instance, int(timeout)).until(EC.presence_of_element_located((BYCLASS[locator_type.strip().upper()], locator)))
            status = True
        except KeyError:
            print_error("The given locator_type - '{0}' does not match any of "
                        "the accepted locator_types.".format(locator_type))
            print_error("{0}, {1}, {2}, {3}, {4}, {5}, {6}, and {7} are the "
                        "accepted locator types.".format("id", "xpath", "link"
                                                         "class", "tag", "name",
                                                         "css_selector",
                                                         "partial_link"))
            status = "ERROR"
        except TimeoutException:
            print_error("Element not present after {0} seconds".format(timeout))
            status = False
        except Exception as e:
            print_error("An Exception Ocurred: {0}".format(e))
            status = "ERROR"
        return status

    def wait_until_presence_of_all_elements_located(self, browser_instance,
                                                    locator_type, locator, timeout=5):
        try:
            WebDriverWait(browser_instance, int(timeout)).until(EC.presence_of_all_elements_located((BYCLASS[locator_type.strip().upper()], locator)))
            status = True
        except KeyError:
            print_error("The given locator_type - '{0}' does not match any of "
                        "the accepted locator_types.".format(locator_type))
            print_error("{0}, {1}, {2}, {3}, {4}, {5}, {6}, and {7} are the "
                        "accepted locator types.".format("id", "xpath", "link"
                                                         "class", "tag", "name",
                                                         "css_selector",
                                                         "partial_link"))
            status = "ERROR"
        except TimeoutException:
            print_error("Elements not present after {0} seconds".format(timeout))
            status = False
        except Exception as e:
            print_error("An Exception Ocurred: {0}".format(e))
            status = "ERROR"
        return status

    def wait_until_visibilty_is_confirmed(self, browser_instance,
                                               element, timeout=5):
        try:
            WebDriverWait(browser_instance, int(timeout)).until(EC.visibility_of(element))
            status = True
        except TimeoutException:
            print_error("Element not visible after {0} seconds".format(timeout))
            status = False
        except Exception as e:
            print_error("An Exception Ocurred: {0}".format(e))
            status = "ERROR"
        return status

    def wait_until_visibility_of_element_located(self, browser_instance,
                                                      locator_type, locator,
                                                      timeout=5):
        try:
            WebDriverWait(browser_instance, int(timeout)).until(EC.visibility_of_element_located((BYCLASS[locator_type.strip().upper()], locator)))
            status = True
        except KeyError:
            print_error("The given locator_type - '{0}' does not match any of "
                        "the accepted locator_types.".format(locator_type))
            print_error("{0}, {1}, {2}, {3}, {4}, {5}, {6}, and {7} are the "
                        "accepted locator types.".format("id", "xpath", "link"
                                                         "class", "tag", "name",
                                                         "css_selector",
                                                         "partial_link"))
            status = "ERROR"
        except TimeoutException:
            print_error("Element not visible after {0} seconds".format(timeout))
            status = False
        except Exception as e:
            print_error("An Exception Ocurred: {0}".format(e))
            status = "ERROR"
        return status

    def implicit_wait(self, browser_instance, timeout):
        browser_instance.implicitly_wait(int(timeout))
        return True
