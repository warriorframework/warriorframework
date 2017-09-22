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

"""" robot_wrapper driver """
from WarriorCore import kw_driver
from plugins.robot_wrapper_plugin.bin import actions


def main(keyword, data_repository, args_repository):
    """ Import all actions related to robot_wrapper driver and call the driver Utils
    to execute a keyword """
    # Declare a list of packages to be used by this driver,
    # if you want to add more packages import them outside the main function
    # and then add them to the package_list below
    package_list = [actions]

    return kw_driver.execute_keyword(keyword, data_repository, args_repository, package_list)
