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

""" selenium verify operations library"""

from Framework.Utils.print_Utils import print_error, print_info, print_debug, print_exception
from selenium.webdriver.support import expected_conditions as EC


try:
    from selenium import webdriver
except Exception as exception:
    print_exception(exception)

class VerifyOperations(object):
    """Browser management class"""

    def __init__(self, *args, **kwargs):
        """Verify operations constructor """

    def get_page_property(self, browser_instance, value_type=None):
        a = ["current_url", "name", "page_source", "title"]
        return_value = False
        if value_type is not None:
            if value_type not in a:
                print_error("Only {0}, {1}, {2}, {3} are supported value types.".format(a[0], a[1], a[2], a[3]))
            else:

                for i in range(0, len(a)):
                    if value_type == a[i]:
                        if i == 0:
                            return_value = browser_instance.current_url
                        if i == 1:
                            return_value = browser_instance.name
                        if i == 2:
                            return_value = browser_instance.page_source
                        if i == 3:
                            return_value = browser_instance.title
        return return_value

    def verify_alert_is_present(self, browser_instance, action="accept"):
        status = False
        try:
            if action.lower().strip() == "dismiss":
                browser_instance.switch_to.alert.dismiss()
            else:
                browser_instance.switch_to.alert.accept()
            status = True
        except Exception:
            print_error("No alert present!")
        return status
