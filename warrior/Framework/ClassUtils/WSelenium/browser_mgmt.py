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

""" selenium browser management library"""
import os
import re
from time import sleep
import urllib2
from Framework.Utils.datetime_utils import get_current_timestamp
from Framework.Utils.print_Utils import print_error, print_info, print_debug, print_exception


try:
    from selenium import webdriver
    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    from selenium.common.exceptions import WebDriverException

    KEYS = {1: Keys.NUMPAD1, 2: Keys.NUMPAD2, 3: Keys.NUMPAD3,
            4: Keys.NUMPAD4, 5: Keys.NUMPAD5, 6: Keys.NUMPAD6,
            7: Keys.NUMPAD7, 8: Keys.NUMPAD8, 9: Keys.NUMPAD9}

except Exception as exception:
    print_exception(exception)


BROWSER_NAMES = {'ff': "_make_ff",
                 'firefox': "_make_ff",
                 'chrome': "_make_chrome"
                }


class BrowserManagement(object):
    """Browser management class"""

    def __init__(self, *args, **kwargs):
        """Browser management constructor """
        self.current_browser = None
        self.current_window = None

    def open_browser(self, browser_name='firefox', webdriver_remote_url=False,
                     desired_capabilities=None, binary=None, gecko_path=None,
                     **kwargs):
        """Open a browser session"""

        profile_dir = kwargs.get('profile_dir', None)

        if webdriver_remote_url:
            print_debug("Opening browser '{0}' through remote server at '{1}'"\
                        .format(browser_name, webdriver_remote_url))
        else:
            print_debug("Opening browser '%s'" % (browser_name))
        browser_name = browser_name
        browser = self._make_browser(browser_name, desired_capabilities,
                                     profile_dir, webdriver_remote_url,
                                     binary=binary, gecko_path=gecko_path)
        return browser

    def close_browser(self, browser_instance=None):
        """closes a browser session """
        status = True
        try:
            if browser_instance is not None:
                browser_instance.quit()
            else:
                self.current_browser.quit()
        except Exception as exception:
            print_exception(exception)
            status = False
        return status

    # window management

    def close_window(self, browser_instance=None):
        """close the current window """
        status = True
        try:
            if browser_instance is not None:
                browser_instance.close()
            else:
                self.current_browser.close()
        except Exception as exception:
            print_exception(exception)
            status = False
        return status

    def maximize_browser_window(self, browser_instance=None):
        """Maximizes current browser window."""
        status = True
        try:
            if browser_instance is not None:
                browser_instance.maximize_window()
            else:
                self.current_browser.maximize_window()
        except Exception as exception:
            print_exception(exception)
            status = False
        return status

    def save_screenshot(self, browser_instance=None, filename=None,
                        directory=None):
        """"""
        status = True
        if browser_instance is None:
            browser_instance = self.current_browser

        if filename is None:
            current_datetime = str(get_current_timestamp())
            current_datetime = current_datetime.replace(" ", "_")
            current_datetime = current_datetime.replace(":", "-")
            filename = "screenshot_" + current_datetime + ".png"
        else:
            filename += ".png"

        print_info("Screenshot will be saved by the name {0} in directory {1}".format(filename, directory))

        directory = os.path.join(directory, filename)
        try:
            browser_instance.save_screenshot(directory)
            sleep(10)
        except Exception as e:
            print_error("Could not save screenshot {0}". format(e))
            status = False

        return status

    def get_window_size(self, browser_instance=None):
        """Returns current window size as `width` then `height`."""
        if browser_instance is None:
            browser_instance = self.current_browser
        size = browser_instance.get_window_size()
        return size['width'], size['height']

    def set_window_size(self, width, height, browser_instance=None):
        """Sets the `width` and `height` of the current window
        to the specified values."""
        if browser_instance is not None:
            browser_instance.set_window_size(width, height)
        else:
            self.current_window.set_window_size(width, height)

    def get_window_position(self, browser_instance=None):
        """Returns current window position as `x` then `y`."""
        if browser_instance is None:
            browser_instance = self.current_browser
        position = browser_instance.get_window_position()
        return position['x'], position['y']

    def set_window_position(self, x, y, browser_instance=None):
        """Sets the position `x` and `y` of the current
        window to the specified values."""
        if browser_instance is not None:
            browser_instance.set_window_position(x, y)
        else:
            self.current_window.set_window_position(x, y)
        return

    # navigation

    def go_back(self, browser_instance=None):
        """Simulates the user clicking the "back" button on their browser."""
        if browser_instance is not None:
            browser_instance.back()
        else:
            self.current_browser.back()

    def go_forward(self, browser_instance=None):
        """Simulates the user clicking the "back" button on their browser."""
        if browser_instance is not None:
            browser_instance.forward()
        else:
            self.current_browser.forward()

    def check_url(self, url):
        """To check whether the user provided url is valid or not."""
        status = True
        search_http = re.search("http", url)
        if not search_http:
            print_error("Provide the url along with http/https")
            status = False
            return status, url
        try:
            url_open = urllib2.urlopen(url)
            get_status_code = url_open.code
            pattern = re.compile('^2[0-9][0-9]$')
            if not pattern.match(str(get_status_code)):
                status = False
        except urllib2.HTTPError as http_error:
            print_error("URLError: {} reason: ({}) status code: {}".format(url, http_error.reason, http_error.code))
            status = False
        except urllib2.URLError as url_err:
            print_error("URLError: {} reason: ({})".format(url, url_err.reason))
            status = False
        if status == False:
            print_error("Incorrect URL provided")
        return status, url

    def go_to(self, url, browser_instance=None):
        """Navigates the active browser instance to the provided URL."""
        status = True
        try:
            print_info("Opening url '%s'" % url)
            if browser_instance is not None:
                browser_instance.get(url)
            else:
                self.current_browser.get(url)
        except Exception as exception:
            print_exception(exception)
            status = False
        return status

    def reload_page(self, browser_instance=None):
        """Simulates user reloading page."""
        if browser_instance is not None:
            browser_instance.refresh()
        else:
            self.current_browser.refresh()

    def hard_reload_page(self, browser_instance=None):
        if browser_instance is None:
            self.current_browser.refresh()

        element = browser_instance.find_element_by_tag_name("body")
        element.send_keys(Keys.LEFT_CONTROL, Keys.F5)
        sleep(1)

    def open_tab(self, browser_instance=None, url=None, browser_type="firefox"):
        if browser_instance is None:
            browser_instance = self.current_browser

        if browser_type == "firefox":
            element = browser_instance.find_element_by_tag_name("body")
            element.send_keys(Keys.LEFT_CONTROL, 'n')
        else:
            element = browser_instance.find_element_by_tag_name("body")
            element.send_keys(Keys.LEFT_CONTROL, 't')
        sleep(1)
        browser_instance.switch_to.window(browser_instance.window_handles[len(browser_instance.window_handles) - 1])

        if url is not None:
            self.go_to(url, browser_instance)
            sleep(1)

    def switch_tab(self, browser_instance=None, tab_number=None, browser_type="firefox"):
        status = True
        if browser_instance is None:
            browser_instance = self.current_browser
        if tab_number is not None:
            try:
                tab_number = int(tab_number)
            except:
                print_error("{0} is not a valid tab number".format(tab_number))
                status = False
            else:
                if tab_number > len(browser_instance.window_handles) or tab_number < 1:
                    print_error("{0} is not a valid tab number".format(tab_number))
                    status = False
                else:
                    tab_number -= 1
                    current_tab = 0
                    current_window_handle = browser_instance.current_window_handle
                    for i in range(0, len(browser_instance.window_handles)):
                        if browser_instance.window_handles[i] == current_window_handle:
                            current_tab = i
                            break
                    if tab_number != current_tab:
                        if current_tab < tab_number:
                            times = tab_number - current_tab
                        else:
                            times = len(browser_instance.window_handles) - current_tab
                            times += tab_number
                        if browser_type == "firefox":
                            action_chains = ActionChains(browser_instance)
                            action_chains.key_down(Keys.ALT)
                            for i in range(0, times):
                                action_chains.send_keys('`')
                            action_chains.perform()
                        else:
                            element = browser_instance.find_element_by_tag_name('body')
                            for i in range(0, times):
                                element.send_keys(Keys.LEFT_CONTROL, Keys.TAB)
                        browser_instance.switch_to.window(browser_instance.window_handles[tab_number])
        else:
            current_tab = 0
            current_window_handle = browser_instance.current_window_handle
            for i in range(0, len(browser_instance.window_handles)):
                if browser_instance.window_handles[i] == current_window_handle:
                    current_tab = i
            tab_number = current_tab + 1
            if tab_number >= len(browser_instance.window_handles):
                tab_number = 0
            if browser_type == "firefox":
                browser_instance.find_element_by_tag_name('body').send_keys(Keys.LEFT_ALT, '`')
            else:
                browser_instance.find_element_by_tag_name('body').send_keys(Keys.LEFT_CONTROL, Keys.TAB)
            browser_instance.switch_to.window(browser_instance.window_handles[tab_number])

        return status

    def close_tab(self, browser_instance=None, tab_number=None, browser_type="firefox"):
        if browser_instance is None:
            browser_instance = self.current_browser

        if len(browser_instance.window_handles) > 1:
            prior_current_tab = False
            current_window_handler = browser_instance.current_window_handle
            for i in range(0, len(browser_instance.window_handles)):
                if browser_instance.window_handles[i] == current_window_handler:
                    prior_current_tab = i

            status = True
            if tab_number is not None:
                status = self.switch_tab(browser_instance, tab_number, browser_type)
                if status:
                    tab_number = int(tab_number) - 1
                    browser_instance.find_element_by_tag_name('body').send_keys(Keys.LEFT_CONTROL, 'w')
                    sleep(2)
                    if tab_number == len(browser_instance.window_handles):
                        tab_number -= 1
                    browser_instance.switch_to.window(browser_instance.window_handles[tab_number])
                    if prior_current_tab == len(browser_instance.window_handles):
                        prior_current_tab -= 1

                    if prior_current_tab != tab_number:
                        if tab_number < prior_current_tab:
                            times = prior_current_tab - tab_number
                        else:
                            times = len(browser_instance.window_handles) - tab_number
                            times += prior_current_tab
                        if browser_type == "firefox":
                            action_chains = ActionChains(browser_instance)
                            action_chains.key_down(Keys.ALT)
                            for i in range(0, times):
                                action_chains.send_keys('`')
                            action_chains.perform()
                        else:
                            element = browser_instance.find_element_by_tag_name('body')
                            for i in range(0, times):
                                element.send_keys(Keys.LEFT_CONTROL, Keys.TAB)

                    browser_instance.switch_to.window(browser_instance.window_handles[prior_current_tab])
            else:
                if browser_type == "firefox":
                    print_info("The tab_number argument is None. Current window will be closed")
                else:
                    print_info("The tab_number argument is None. Current tab will be closed")
                browser_instance.find_element_by_tag_name('body').send_keys(Keys.LEFT_CONTROL, 'w')
                if prior_current_tab == len(browser_instance.window_handles):
                    prior_current_tab = 0
                browser_instance.switch_to.window(browser_instance.window_handles[prior_current_tab])
        else:
            status = self.close_browser(browser_instance)

        return status

    def delete_all_cookies_in_browser(self, browser_instance=None):
        status = True
        if browser_instance is None:
            browser_instance = self.current_browser
        try:
            browser_instance.delete_all_cookies
        except Exception as e:
            print_error("Could not delete cookies! Message: {0}".format(e))
            status = False

        return status

    def delete_a_specific_cookie(self, browser_instance=None, cookie_name=None):
        status = True
        if browser_instance is None:
            browser_instance = self.current_browser
        if cookie_name is not None:
            try:
                browser_instance.delete_cookie(cookie_name)
            except Exception as e:
                print_error("Could not delete cookie! Message: {0}".format(e))
                status = False
        else:
            print_error("Cookie name not specified! Cannot delete cookie.")
            status = False

        return status

    # private methods
    def _make_browser(self, browser_name, desired_capabilities=None,
                      profile_dir=None, webdriver_remote_url=None,
                      binary=None, gecko_path=None):
        """method to open a browser, calls other sepcific/generic
        make browser methods to open a browser """
        creation_func = self._get_browser_creation_function(browser_name)

        if not creation_func:
            raise ValueError(browser_name + " is not a supported browser.")

        browser = creation_func(webdriver_remote_url, desired_capabilities,
                                profile_dir, binary, gecko_path)
        return browser

    def _get_browser_creation_function(self, browser_name):
        """Gets the browser function for the supported browsers
        from the BROWSER_NAMES dictionary """
        func_name = BROWSER_NAMES.get(browser_name.lower().replace(' ', ''))
        return getattr(self, func_name) if func_name else None

    def _make_ff(self, webdriver_remote_url, desired_capabilites, profile_dir,
                 binary, gecko_path):
        """Create an instance of firefox browser"""
        try:
            if webdriver_remote_url:
                browser = \
                    self._create_remote_web_driver(
                        webdriver.DesiredCapabilities.FIREFOX,
                        webdriver_remote_url, desired_capabilites,
                        profile_dir)
            else:
                ff_capabilities = webdriver.DesiredCapabilities.FIREFOX
                if ff_capabilities['marionette']:
                    ff_capabilities['acceptInsecureCerts'] = True
                    ffbinary = FirefoxBinary(binary)
                    browser = webdriver.Firefox(firefox_binary=ffbinary,
                                                firefox_profile=profile_dir,
                                                executable_path=gecko_path)
                else:
                    browser = webdriver.Firefox(firefox_profile=profile_dir)
            return browser
        except WebDriverException as e:
            if "executable needs to be in PATH" in str(e):
                print_info("Please provide path for geckodriver executable")
            elif "Expected browser binary location" in str(e):
                print_info("Please provide path of firefox executable")

    def _make_chrome(self, webdriver_remote_url, desired_capabilities,
                     profile_dir, binary, gecko_path):
        """Creates an instance of chrome browser and returns it
        Need to have selenium chrome driver exe placed in the python path"""
        return self._generic_make_browser(webdriver.Chrome,
                                          webdriver.DesiredCapabilities.CHROME,
                                          webdriver_remote_url,
                                          desired_capabilities, binary)

    def _generic_make_browser(self, webdriver_type, desired_cap_type,
                              webdriver_remote_url, desired_caps, binary):
        """most of the make browser functions just call this function which creates the
        appropriate web-driver"""
        try:
            if not webdriver_remote_url:
                if binary is not None:
                    browser = webdriver_type(binary)
                else:
                    browser = webdriver_type()
            else:
                browser = self._create_remote_web_driver(desired_cap_type,
                                                         webdriver_remote_url,
                                                         desired_caps)
            return browser
        except WebDriverException as e:
            if "executable needs to be in PATH" in str(e):
                print_info("Please provide path for chrome driver executable")

    def _create_remote_web_driver(self, capabilities_type, webdriver_remote_url,
                                  desired_capabilities=None, profile=None):
        """parses the string based desired_capabilities if neccessary and
        creates the associated remote web driver"""

        desired_capabilities_object = capabilities_type.copy()

        if isinstance(desired_capabilities, (str, unicode)):
            desired_capabilities = self._parse_capabilities_string(desired_capabilities)

        desired_capabilities_object.update(desired_capabilities or {})

        return webdriver.Remote(desired_capabilities=desired_capabilities_object,
                                command_executor=str(webdriver_remote_url),
                                browser_profile=profile)

    @staticmethod
    def _parse_capabilities_string(capabilities_string):
        """parses the string based desired_capabilities which should be in the form
        key1:val1,key2:val2
        """
        desired_capabilities = {}

        if not capabilities_string:
            return desired_capabilities

        for cap in capabilities_string.split(","):
            (key, value) = cap.split(":", 1)
            desired_capabilities[key.strip()] = value.strip()

        return desired_capabilities
