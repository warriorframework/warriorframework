
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
END OF DISCLAIMER

============================
Read the below instructions
============================

Index of contents:
==================
1. Installation of Python
2. Prerequisites.
3. Running Warhorn
4. User Guide

=======
Python:
=======
For Warhorn to run smoothly, it is recommended that Python 2.7.0 and above
till the latest release in the 2.7 family be installed.
Refer https://wiki.python.org/moin/BeginnersGuide/Download on how to install
python on different platforms.

==============
Prerequisites:
==============
Warhorn tool enables the user to install dependencies, clone Warrior, clone
Product Drivers selectively, and clone Warriorspace

The prerequisites for this tools are:

1. Linux.
Warhorn currently supports only Linux.

2. setuptools
setuptools can be installed on Debian like systems by running this command:
    sudo apt-get install python-setuptools

setuptools can be installed on RedHat like systems by running this command:
    sudo yum install python-setuptools

3. git
git can be installed on Debian like systems by running this command:
    sudo apt-get install git

git can be installed on RedHat like systems by running this command:
    sudo yum install git

4. admin privileges
Warhorn is an installation tool. It is necessary for you to be the admin of
the machine on which Warhorn would run.
If you do not have admin privileges, Warhorn would not be able to install
anything on the system. Warhorn would also not be able to run certain git
commands.

5. access to the git repositories
The access to the Fujitsu git repositories is REQUIRED for Warhorn to clone
any repository


===============
Running Warhorn
===============
The git repository is located at:
https://github.com/warriorframework/warriorframework.git

From your command line, go to directory where you would like to clone Warhorn.
Type in the following commands:

	git clone https://github.com/warriorframework/warriorframework.git

Once warhorn has been cloned, open the now cloned repository and open the
"config" folder. Open the file named "default_config.xml". The file has been
prepopulated with xml tags.

Instructions to populate the xml file are given inside that file. Fill out
the xml file as per those instructions and save it. At the least, the value
of the 'destination' attribute inside the warrior tag has been left empty so
as to be filled in by the user. If it is left blank, Warhorn would clone
everything in the current working directory.

Once that is done, go back to your terminal and type in:

	cd warriorframework
	cd warhorn

This command gets you inside the warhorn folder. After that type in:

	python warhorn.py

This command runs Warhorn which will then install Warrior and other repositories
as per the xml file.

Warhorn also has the ability to work with user specified xml files. The command:

    python warhorn.py path/to/xml/file/some_file.xml

will make Warhorn use the xml file with the name "some_file.xml" in the folder
"path/to/xml/file".

===========
User Guide:
===========

The User Guide is located in the docs folder inside the Warhorn directory