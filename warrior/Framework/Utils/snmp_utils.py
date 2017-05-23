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


def split_mib_path(custom_mib_paths):
    """
    Split comma separated mib paths and add @mib@ at the end of the path if required.
    Argument:
    custom_mib_paths: comma separated mib paths as a string
    Return: Updated custom_mib_paths as a list
    """
    __custom_mib_paths = []
    custom_mib_paths = custom_mib_paths.split(',')
    for paths in custom_mib_paths:
        if 'http' in paths and '@mib@' not in paths:
            if paths[-1] == '/':
                paths = paths+'/@mib@'
            else:
                paths = paths+'@mib@'
        if 'http' in paths and 'browse' in paths:
            paths = paths.replace('browse', 'raw')
        __custom_mib_paths.append(paths)
    __custom_mib_paths.append('/usr/share/snmp/mibs')
    return __custom_mib_paths
