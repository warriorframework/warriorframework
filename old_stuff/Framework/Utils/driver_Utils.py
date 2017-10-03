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

"""Driver utils module which handles gathers the argument
information about the keywords, executes the keywords and reports the
keyword status back to the product driver

************* !!!! This is a temporary module that calls kw_driver to execute a keyword !!!!!  ****************
It is left here for backward compatibility purposes
This module will be DEPCRECATE IN THE NEXT RELEASE OF WARRIOR FRAMEWORK"""


from WarriorCore import kw_driver


def execute_keyword(keyword, data_repository, args_repository, package_list):
    """ Executes the keyword provided by product driver
    1. searches for class methods in the package list
    2. searches for independent functions in the package list
    3. If class method matching the keyword is found in the actions package executes it
        else searches for independent fucntions matching the keyword name and executes it
    """
    return kw_driver.execute_keyword(keyword, data_repository, args_repository, package_list)

    