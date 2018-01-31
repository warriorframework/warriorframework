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

""" Selenium element locator library """


from Framework.Utils.print_Utils import print_error, print_info, print_exception, \
    print_debug

try:
    from selenium.common.exceptions import NoSuchElementException
except ImportError as exception:
    print_exception(exception)

STRATEGIES = {'id': '_get_element_by_id',
              'name': '_get_element_by_name',
              'xpath': '_get_element_by_xpath',
              'link': '_get_element_by_link_text',
              'partial_link': '_get_element_by_partiallink',
              'tag': '_get_element_by_tagname',
              'class': '_get_element_by_classname',
              'css': '_get_element_by_css_selector'}

class ElementLocator(object):
    """Element Locator class """

    def __init__(self, *args, **kwargs):
        """Element locator constructor"""
        pass

    def get_element(self, browser, locator, **kwargs):
        """Get an element based on the locator and value
        - By defaults gets a single element,
        - To get the list of all elements matching the value
        use findall='y' as argument.

        :Arguments:
            - browser = instance of selenium webdriver browser.
            - locator = how to locate the element in the webpage.
                        supported format: "supported locator value = value for the locator"
                        1. to locate element by its id:
                            format = "id=id of the element"
                            eg: "id=j_username" will find the element whose\
                            id is j_username
                        2. "name=name of the element"
                        3. "xpath=xpath of the element"
                        4. "link=link to the element"
                        5. "partial_link=partial link to the element"
                        6. "tag=tag of the element"
                        7. "class=class of the element"
                        8. "css=css of the element"
            - **kwargs:
                1. findall = 'y' - finds all the elements with matching value
                           = None - finds the first elemtn with matching value.

        :Returns:
            - the selenium webdriver element if found.
            - None if element was not found
            (prints a NoSuchElementException message to the user)
        """
        assert browser is not None
        print_info("Finding element by {0}"\
                    .format(locator))
        element = self._get_element(browser, locator, **kwargs)
        if element is None:
            print_error("Could not find element(s) with {0}"\
                        .format(locator))
        return element


    # private methods

    def _get_element(self, browser, locator, **kwargs):
        """gets the element with matching criteria
        uses other private methods """
        findall = kwargs.get('findall', None)
        prefix, value = self._parse_locator(locator)
        if prefix is None:
            raise ValueError(("Strategy to find elements is "\
                              "not provided in the locator={0}".format(locator)))
        locator_function = self._get_strategy_function(prefix)
        if not locator_function:
            raise ValueError(("{0} in locator={1} is not a "\
                              "supported strategy to find elements.".format(prefix, locator)))
        try:
            element = locator_function(value, browser, findall)
        except NoSuchElementException as exception:
            #print_exception(exception)
            element = None
        else:
            print_debug("Element found")
        return element

    def _parse_locator(self, locator):
        prefix = None
        criteria = None
        locator_parts = locator.partition('=')
        if len(locator_parts[1]) > 0:
            prefix = locator_parts[0]
            criteria = locator_parts[2].strip()
        return (prefix, criteria)

    def _get_strategy_function(self, locator):
        """ Get the function for the provided locator """
        locator_function = STRATEGIES.get(locator.lower().replace(' ', ''), None)
        return getattr(self, locator_function) if locator_function else None

    # fucntions for specific strategy

    @staticmethod
    def _get_element_by_id(element_id, browser, findall):
        """Get element(s) by its id """
        elem = browser.find_element_by_id(element_id)
        if not findall:
            elem = elem
        elif findall:
            elem = [elem]
        return elem

    @staticmethod
    def _get_element_by_name(element_name, browser, findall):
        """ Get element(s) by name"""
        if not findall:
            elem = browser.find_element_by_name(element_name)
        elif findall:
            elem = browser.find_elements_by_name(element_name)
        return elem

    @staticmethod
    def _get_element_by_xpath(xpath, browser, findall):
        """Get element(s) by xpath """
        if not findall:
            elem = browser.find_element_by_xpath(xpath)
        elif findall:
            elem = browser.find_elements_by_xpath(xpath)
        return elem

    @staticmethod
    def _get_element_by_link_text(text, browser, findall):
        """Get element(s) with matching link text """
        if not findall:
            elem = browser.find_element_by_link_text(text)
        elif findall:
            elem = browser.find_elements_by_link_text(text)
        return elem

    @staticmethod
    def _get_element_by_partiallink(text, browser, findall):
        """Get element(s) with matching partial link text """
        if not findall:
            elem = browser.find_element_by_partial_link_text(text)
        elif findall:
            elem = browser.find_elements_by_partial_link_text(text)
        return elem

    @staticmethod
    def _get_element_by_tagname(tag_name, browser, findall):
        """Gets element(s) by its tagname """
        if not findall:
            elem = browser.find_element_by_tag_name(tag_name)
        elif findall:
            elem = browser.find_elements_by_tag_name(tag_name)
        return elem

    @staticmethod
    def _get_element_by_classname(class_name, browser, findall):
        """Gets element(s) by its classname """
        if not findall:
            elem = browser.find_element_by_class_name(class_name)
        elif findall:
            elem = browser.find_elements_by_class_name(class_name)
        return elem

    @staticmethod
    def _get_element_by_css_selector(css_selector, browser, findall):
        """Gets element(s) by its css selector """
        if not findall:
            elem = browser.find_element_by_css_selector(css_selector)
        elif findall:
            elem = browser.find_elements_by_css_selector(css_selector)
        return elem



