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
import subprocess
from xml.etree import ElementTree
import Framework.Utils.config_Utils as cfgUtils
from Framework.Utils.print_Utils import print_info, print_error
from Framework.Utils.warhorn_test_utils import get_installed_pkges


class WarhornTestActions(object):
    """class WarhornTestActions having methods (keywords) to test warhorn
    """

    def __init__(self):
        """ Constructor
        """
        self.resultfile = cfgUtils.resultfile
        self.datafile = cfgUtils.datafile
        self.logsdir = cfgUtils.logsdir
        self.filename = cfgUtils.filename
        self.logfile = cfgUtils.logfile

    def test_dependency_config(self, config_file):
        status = True
        root = ElementTree.parse(config_file).getroot()
        node = root.find("warhorn")
        dependencies = node.findall("dependency")
        pkges_to_install = set([d.attrib['name'] for d in dependencies
                                if d.attrib['install'] == 'yes'])
        print_info("pkges to install:\n%s" % pkges_to_install)

        before_installed_pkges = get_installed_pkges()
        pkges_to_check = pkges_to_install - before_installed_pkges
        print_info("pkges to check: %s" % pkges_to_check)

        subprocess.check_call(['../warhorn/warhorn.py', config_file])
        after_installed_pkges = get_installed_pkges()
        pkges_not_installed = pkges_to_check - after_installed_pkges
        if pkges_not_installed:
            print_error("Could not install the following packages due to some "
                        "issue: {}".format(pkges_not_installed))
            status = False
        else:
            print_info("warhorn installed the required packages successfully")
        result = "Success" if status else "Failure"
        print_info("Checking config file {} for dependency resulted "
                   "in {}".format(config_file, result))
        return status
