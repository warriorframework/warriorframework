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

"""Warrior Interface utils """

import os
from xml.etree import ElementTree
katana_dir = os.path.dirname(os.path.dirname(__file__))
wf_dir = os.path.dirname(katana_dir)
wsettings_fpath = os.path.join(wf_dir, 'warrior', 'Tools', 'w_settings.xml' )


class WarriorInterface():

    htmlResults = ''

    def __init__(self):
        pass

    def update_html_result(self, path):
        self.htmlResults = open( path, 'r').read()
        return self.htmlResults

    def set_eoc(self):
        """
        set end of communication string to the html results
        """
        self.htmlResults += "<div class='eoc'></div>"

def write_tree_to_file(root, file_path):
    """
    writes a tree to file
    """
    tree = ElementTree.ElementTree(root)
    tree.write(file_path)



def set_katana_location(k_url):
    """
    Set Katana location in wsettings file
    of warrior
    """

    root = ElementTree.parse(wsettings_fpath).getroot()
    ksetting = root.find("./Setting[@name='katana']")
    ksetting.set('location', k_url)
    write_tree_to_file(root, wsettings_fpath)
    


    