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

from setuptools import setup

PACKAGE_NAME = "warriorframework"
PACKAGE_VERSION = "3.11.0"

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author="warriorframework org",
    url="https://github.com/warriorframework/warriorframework",
    install_requires=["pexpect==4.2", "requests==2.21.0", "selenium==2.53.0",
                      "lxml==3.3.3", "paramiko==2.4.2", "pysnmp==4.3.2",
                      "pyvirtualdisplay==0.2.1"]

)
