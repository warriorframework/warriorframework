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

""""This file provides the template to write a new Product Driver """

from WarriorCore import kw_driver

#======================================================================
# Importing the package specific to your driver
# If your package is a package under the Actions directory of Warrior,
# Import your package like how it is shown in the below example 
# where Actions.SampleActions is imported
#================================================================

import Actions.ExampleActions

def main(keyword, data_repository, args_repository):
    """ Declare a list of packages to be used by this driver in the variable 'package_list' below
    if you want to add more packages import them outside the main function as
    described above and then add them to the package_list below """
    package_list = [Actions.ExampleActions]

    return kw_driver.execute_keyword(keyword, data_repository, args_repository, package_list)
