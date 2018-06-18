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

import os
import re
import traceback
from time import sleep
import urllib2
import platform
from subprocess import check_output, CalledProcessError
from distutils.version import LooseVersion
from Framework.Utils.datetime_utils import get_current_timestamp
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_error, print_info, print_debug, print_exception,\
    print_warning
from Framework.Utils.data_Utils import get_object_from_datarepository
from Framework.Utils.file_Utils import fileExists

try:
    from selenium import webdriver
    print_info("The Selenium Webdriver version is '{0}'".format(webdriver.__version__))
    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    from selenium.common.exceptions import WebDriverException

    KEYS = {1: Keys.NUMPAD1, 2: Keys.NUMPAD2, 3: Keys.NUMPAD3,
            4: Keys.NUMPAD4, 5: Keys.NUMPAD5, 6: Keys.NUMPAD6,
            7: Keys.NUMPAD7, 8: Keys.NUMPAD8, 9: Keys.NUMPAD9}
except ImportError as exception:
    print_exception(exception)

""" selenium browser management library"""

class BrowserManagement(object):
    """Browser management class"""

    def __init__(self, *args, **kwargs):
        """Browser management constructor """
        self.current_browser = None
        self.current_window = None
        self.ff_binary_object = FirefoxBinary()

    def open_browser(self, browser_name='firefox', webdriver_remote_url=False,
                     desired_capabilities=None, **kwargs):
        """Open a browser session"""

        profile_dir = kwargs.get('profile_dir', None)
        if 'profile_dir' in kwargs:
            kwargs.pop('profile_dir')
        if webdriver_remote_url:
            print_debug("Opening browser '{0}' through remote server at '{1}'"\
                        .format(browser_name, webdriver_remote_url))
        else:
            print_debug("Opening browser '%s'" % (browser_name))
        browser_name = browser_name
        browser = self._make_browser(browser_name, desired_capabilities,
                                     profile_dir, webdriver_remote_url, **kwargs)
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

    def maximize_browser_window(self, browser_instance=None, headless_mode=False):
        """Maximizes current browser window."""
        status = True
        try:
            if browser_instance is None:
                browser_instance = self.current_browser

            # Need to distinguish whether browser is in headless mode or not
            # as maximize_window doesn't work in headless mode
            if headless_mode:
                browser_instance.set_window_size(1920, 1080)
            else:
                browser_instance.maximize_window()

        except Exception as exception:
            print_exception(exception)
            status = False
        return status

    def save_screenshot(self, browser_instance=None, filename=None,
                        directory=None):
        """
            Save screenshot of the specified/current browser
        """
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
        """
        To check whether the user provided url is valid or not.

        DISCLAIMER: This function internally opens the url to assert the validity of the url.

        Returns:
            1. status(bool)= True / False.(Whether the url can be reached)
            2. url : The actual url itself
        """
        status = True
        try:
            url_open = urllib2.urlopen(url)
            get_status_code = url_open.code
            pattern = re.compile('^2[0-9][0-9]$')
            if not pattern.match(str(get_status_code)) and get_status_code is not None:
                print_info("The Status code for url : {} is {}".format(url, get_status_code))
                status = False
        except urllib2.HTTPError as http_error:
            print_warning("URLError: {} reason: ({}) status code: {}".format
                          (url, http_error.reason, http_error.code))
            status = False
        except urllib2.URLError as url_err:
            status = False
            print_warning("URLError: {} reason: ({})".format(url, url_err.reason))
        except Exception, err:
            print_warning("Exception: {0}".format(err))
            status = False
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
        except WebDriverException as err:
            print_error(err)
            if "Reached error page" in str(err):
                print_error("Unable to Navigate to URL:{}"\
                            "possibly because of the url is not valid".format(url))
            else:
                status = False
        except Exception, err:
            print_error(err)
            status = False
            print_error("Unable to Navigate to URL:'%s'" % url)
            traceback.print_exc()
        return status

    def reload_page(self, browser_instance=None):
        """Simulates user reloading page."""
        if browser_instance is not None:
            browser_instance.refresh()
        else:
            self.current_browser.refresh()

    def hard_reload_page(self, browser_instance=None):
        """Simulates Refreshing/Reloading the page just as users using F5 """
        if browser_instance is None:
            self.current_browser.refresh()

        element = browser_instance.find_element_by_tag_name("body")
        element.send_keys(Keys.LEFT_CONTROL, Keys.F5)
        sleep(1)

    def open_tab(self, browser_instance=None, url=None, browser_type="firefox"):
        """Opens a new tab in the browser"""
        status = True
        if browser_instance is None:
            browser_instance = self.current_browser

        # only when firefox version < 47, open new window
        if browser_type == "firefox" and\
           LooseVersion(self.get_browser_version(browser_instance)) < LooseVersion("47.0.0"):
            element = browser_instance.find_element_by_tag_name("body")
            element.send_keys(Keys.LEFT_CONTROL, 'n')
        elif browser_type == "firefox" or (browser_type == "chrome" and\
             LooseVersion(self.get_browser_version(browser_instance)) > LooseVersion("60.0.0")):
            # If FF version > 47, this action is not supported
            print_error("Firefox (47 or above) and Chrome with chromedriver (2.32 or above)"\
                        "doesn't support opening new tab. Open tab may not function correctly")
            status = False
        else:
            # If it is chrome ver < 60, actually open a new tab
            element = browser_instance.find_element_by_tag_name("body")
            element.send_keys(Keys.LEFT_CONTROL, 't')
        sleep(1)
        browser_instance.switch_to.window(browser_instance.window_handles\
                                          [len(browser_instance.window_handles) - 1])

        if url is not None:
            self.go_to(url, browser_instance)
            sleep(1)

        return status

    def switch_tab(self, browser_instance=None, tab_number=None, browser_type="firefox"):
        """Switching to different tabs in a browser with unique tab_number"""
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
        """Closing tabs in a browser with unique tab_number"""
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
        """Delete the cookies for a particular browser instance"""
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
        """Delete a specific cookie on a specific browser instance"""
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

    def get_firefox_version(self, binary):
        """
            Use firefox binary to find out firefox version
            before launching firefox in selenium
        """
        command = ""
        # If the platform is Linux,
        # If Binary - None: default binary is set as "firefox".
        # else the binary path passed through datafile is considered.
        # If the platform is Windows,
        # If Binary - None: default binary is set to Program Files path.
        # else the binary path passed through datafile is considered.
        if platform.system() in "Linux":
            if binary in [False, None]:
                binary = "firefox"
            command = [binary, "-v"]
        elif platform.system() in "Windows":
            if binary in [False, None]:
                binary = self.ff_binary_object._default_windows_location()
            command = "%s -v | more" % (binary) 
        print_info("Platform: {0} Firefox binary path: {1}".format(platform.system(), binary))
        version = False
        try:
            raw_version = check_output(command) 
            match = re.search(r"\d+\.\d+", raw_version)
            if match is not None:
                version = LooseVersion(match.group(0))
            else:
                print_info("Cannot parse Firefox version: {}".format(raw_version))
        except CalledProcessError:
            print_error("Cannot find firefox version, will not launch browser")
        return version

    def get_browser_version(self, browser):
        """
            Get browser version from selenium
        """
        # Return the browser version as string
        browser_version = browser.capabilities.get("version", None)
        if browser_version is None:
            browser_version = browser.capabilities.get("browserVersion", None)
        if browser_version is None:
            print_error("Unable to retrieve browser version, return False")
            browser_version = False
        return browser_version

    def set_firefox_proxy(self, profile_dir, proxy_ip, proxy_port):
        """method to update the given preferences in Firefox profile"""
        # Create a default Firefox profile first and update proxy_ip and port
        ff_profile = webdriver.FirefoxProfile(profile_dir)
        proxy_port = int(proxy_port)
        ff_profile.set_preference("network.proxy.type", 1)
        ff_profile.set_preference("network.proxy.http", proxy_ip)
        ff_profile.set_preference("network.proxy.http_port", proxy_port)
        ff_profile.set_preference("network.proxy.ssl", proxy_ip)
        ff_profile.set_preference("network.proxy.ssl_port", proxy_port)
        ff_profile.set_preference("network.proxy.ftp", proxy_ip)
        ff_profile.set_preference("network.proxy.ftp_port", proxy_port)
        ff_profile.update_preferences()

        return ff_profile

    # private methods
    def _make_browser(self, browser_name, desired_capabilities=None,
                      profile_dir=None, webdriver_remote_url=None, **kwargs):
        """method to open a browser, calls other sepcific/generic
        make browser methods to open a browser """
        browser_methods = {'ff': self._make_ff, 'firefox': self._make_ff,
                           'chrome': self._make_chrome}
        creation_method = browser_methods.get(browser_name, None)

        if creation_method is None:
            print_error("{} is not a supported browser. Please use firefox or chrome".\
                             format(browser_name))
            browser = None
        else:
            kwargs["browser_name"] = browser_name
            browser = creation_method(webdriver_remote_url, desired_capabilities,
                                      profile_dir, **kwargs)
            if browser is not None:
                print_info("The {} browser version is {}".format(
                    browser_name, self.get_browser_version(browser)))
            else:
                print_error("Unable to create browser for: {}".format(browser_name))

        return browser

    def _get_browser_creation_function(self, browser_name):
        """Gets the browser function for the supported browsers
        from the browser_methods dictionary """


    def _make_ff(self, webdriver_remote_url, desired_capabilites, profile_dir, **kwargs):
        """Create an instance of firefox browser"""
        binary = kwargs.get("binary", None)
        gecko_path = kwargs.get("gecko_path", None)
        # gecko_log is the absolute path to save geckodriver log
        gecko_log = kwargs.get("gecko_log", None)
        proxy_ip = kwargs.get("proxy_ip", None)
        proxy_port = kwargs.get("proxy_port", None)
        ff_profile = None
        # if firefox is being used with proxy, set the profile here
        # if firefox_proxy details are not given, set profile_dir
        # as the ff_profile.
        if proxy_ip is not None and proxy_port is not None:
            ff_profile = self.set_firefox_proxy(profile_dir, proxy_ip, proxy_port)
        else:
            ff_profile = profile_dir
        log_dir = get_object_from_datarepository("wt_logsdir") if \
                  gecko_log in [None, False] else gecko_log
        log_dir = os.path.join(log_dir, "gecko_"+kwargs.get("browser_name", "default")+".log")

        browser = None
        try:
            if webdriver_remote_url:
                browser = self._create_remote_web_driver(
                    webdriver.DesiredCapabilities.FIREFOX,
                    webdriver_remote_url, desired_capabilites, ff_profile)
            else:
                optional_args = {}
                ff_capabilities = webdriver.DesiredCapabilities.FIREFOX
                # This is for internal testing needs...some https cert is not secure
                # And firefox will need to know how to handle it
                ff_capabilities['acceptInsecureCerts'] = True

                if binary not in [False, None]:
                    if not fileExists(binary):
                        print_warning("Given firefox binary '{}' does not exist, default "
                                      "firefox will be used for execution.".format(binary))
                        binary = None
                else:
                    print_info("No value given for firefox binary, default "
                               "firefox will be used for execution.")

                # Force disable marionette, only needs in Selenium 3 with FF ver < 47
                # Without these lines, selenium may encounter capability not found issue
                # https://github.com/seleniumhq/selenium/issues/2739
                # https://github.com/SeleniumHQ/selenium/issues/5106#issuecomment-347298110
                if self.get_firefox_version(binary) < LooseVersion("47.0.0"):
                    ff_capabilities["marionette"] = False
                else:
                    # gecko_log will only get generate if there is failure/error
                    # Need to specify log_path for geckodriver log
                    # Gecko driver will only launch if FF version is 47 or above
                    optional_args["log_path"] = log_dir

                ffbinary = FirefoxBinary(binary) if binary is not None else None
                if gecko_path is not None:
                    optional_args["executable_path"] = gecko_path
                browser = webdriver.Firefox(firefox_binary=ffbinary,
                                            capabilities=ff_capabilities,
                                            firefox_profile=ff_profile, **optional_args)
        except WebDriverException as err:
            if "executable needs to be in PATH" in str(err):
                print_error("Please provide path for geckodriver executable")
            elif "Expected browser binary location" in str(err):
                print_error("Please provide path of firefox executable")
            print_error(err)
            traceback.print_exc()
        except Exception as err:
            print_error(err)
            traceback.print_exc()

        if browser is None and\
           any((LooseVersion(webdriver.__version__) < LooseVersion("3.5.0"), gecko_path is None)):
            print_info("Unable to create Firefox browser, one possible reason is because"\
                       "Firefox version >= 47.0.1 and Selenium version < 3.5"\
                       "In order to launch Firefox ver 47 and up, Selenium needs to be updated to >= 3.5"\
                       "and needs geckodriver > 0.16")

        return browser

    def _make_chrome(self, webdriver_remote_url, desired_capabilities, profile_dir, **kwargs):
        """Creates an instance of chrome browser and returns it
        Need to have selenium chrome driver exe placed in the python path"""
        return self._generic_make_browser(webdriver.Chrome,
                                          webdriver.DesiredCapabilities.CHROME,
                                          webdriver_remote_url, desired_capabilities, **kwargs)

    def _generic_make_browser(self, webdriver_type, desired_cap_type,
                              webdriver_remote_url, desired_caps, **kwargs):
        """most of the make browser functions just call this function which creates the
        appropriate web-driver"""
        if not webdriver_remote_url:
            browser = webdriver_type()
        else:
            browser = self._create_remote_web_driver(desired_cap_type, webdriver_remote_url,
                                                     desired_caps)
        return browser


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
