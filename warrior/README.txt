========================================================================================================
Read the below instructions for initial setup and installation to be done before using Warrior framework.
========================================================================================================
 
Index of contents:
==================
1. Installation of python 
2. Installation of required tools.
2. Installation of required packages
3. Creating softlink for Warrior executable in linux (to execute Warrior from any location in the host machine)

=======
Python:
=======
Warrior is supported on python2.7
The primary requirement of Warrior to work is python installation itself, please make sure you have python2.7.0 or a higher version in the 2.7+ family installed in the machine where you want to run Warrior.

refer https://wiki.python.org/moin/BeginnersGuide/Download on how to install python on different platforms.

==============================
External python packages used:
==============================
Warrior Framework by itself does not require any external packages for its operation, but some of the features uses certain external packages 
for their operations, in-order to use these features the external python packages have to be installed in the machine where Warrior Framework is 
used.

1. pexpect-4.0 - used by cli utilities
2. lxml- 3.4.4 and above - used by IronClaw tool
3. requests-2.7.0 and above - used for rest operations
4. selenium-2.45.0 and above - used for web based testing
5. ncclient-0.4.5 - used for netconf operations
6. paramiko-2.4.1 - used by ncclient
7. pysnmp-4.3.1	- used for snmp operations
8. pycryptodome-3.6.1 - used for encryption

Please note: some of the packages may require admin privileges to install them.
These packages are python packages and hence they can be installed using pip/easy_install
So it is recommended to have pip/easy_install installed in the machine where you want to run Warrior.

Installation tools:
===================
pip:
----
	1. Download get-pip.py form the link given below and run python get-pip.py (on any os)
	(or)
	2. sudo apt-get install python-pip (for debian or ubuntu)
	3. sudo yum install pip (for fedora)

	For more details refer: https://pip.pypa.io/en/latest/installing.html

easy_install:
-------------
	Download ez_setup.py from the below link and run python ez_setup.py
	For more details and different installation techniques refer: https://pypi.python.org/pypi/setuptools


++++++++++++++++++++++++++++++++++++++++
Installation of external python packages
+++++++++++++++++++++++++++++++++++++++++

Auto installation:
==================

For auto installation of Warrior, please cd into the warhorn directory inside warriorframework and follow the
instructions given in its readme.


Manual Installation:
====================

Packages:
=========

1. pexpect package of python: version4.0

	------
 	Linux:
	-------
	Warrior uses pexpect for libraries and keywords related to ssh connections while running on Linux like systems. 
	Pexpect can be installed using pip install or easy_install or can be compiled from the source
	
	---------------------
	Installation commands:
	----------------------
	pip install pexpect  
	(or)
	easy_install pexpect 
	
	Install from source package:
		Download the .tar from the site https://pypi.python.org/pypi/pexpect/ 
		Extract the contents in your local machine. It will have a file setup.py
		Run the setup.py with the python version you want to install to
		for eg: /usr/bin/python27 setup.py
	
	Reference links for pexpect installation procedures:
	--------------------------------------------
	ip/easy_install: http://pexpect.readthedocs.org/en/latest/install.html
	source code: https://pypi.python.org/pypi/pexpect/ 

	--------
	Windows:
	--------
	- Warrior as such does not have any restrictions to run on Windows, but the cli libraries use pexpect which is not supported in a
	Windows like terminal, in order to run pexpect in Windows users have to install CYGWIN which provides a unix/linux like
	terminal to windows.
	
	- Please follow the instructions and snapshots provided in "Run_Warrior_with_CYGWIN.pdf" located under the Docs directory.


2. lxml package version 3.4.4 and above
	Warrior uses lxml for its ironclaw utility
	
	Installation commands:
	----------------------
	sudo apt-get install python<x>-lxml    where x = 2.7.x
	sudo pip install lxml
	
	Reference link:
	--------------
	http://lxml.de/installation.html

3. python selenium version 2.45.0 and above:

	In order to user python selenium 2 libraries, you have install the selenium library.
	
	Installation command:
	---------------------
	sudo pip install selenium 

	Reference links:
	----------------
	http://selenium-python.readthedocs.org/en/latest/installation.html

4. requests version 2.7.0 and above:
	In order to perform rest operations, you have to install requests package as the rest_utils uses requests package.
	Installation command:
	---------------------
	sudo pip install requests
	
	Reference links:
	---------------
	http://www.python-requests.org/en/latest/user/install/


5. ncclient version 0.4.5:
	Used for netconf operations

	Installation command:
	---------------------
	sudo pip install ncclient

	Reference links:
	----------------
	https://pypi.python.org/pypi/ncclient


6. paramiko-2.4.1
	Used by nccclient 

	Installation command:
	---------------------
	sudo pip install paramiko

	Reference links:
	----------------
	https://pypi.python.org/pypi/paramiko/1.15.2

7. pysnmp-4.3.1
	Used for netconf operations

	Installation command:
	---------------------
	sudo  pip install pysnmp

	Reference links:
	----------------
	http://pysnmp.sourceforge.net/

8. pycryptodome-3.6.1
	Used for password encryption.
	Method encrypt(message) to return encrypted data. decrypt(message) returns decrypted data. 
	It uses the AES encryption algorithm from pycryptodome library.
	The security key stored is in base64 encoded form and shall be decoded by the utility.
	It needs a security key which is stored in a file. It's Base64 encoded in Tools/admin/secret.key
	This utility reads the secret key from the file and use it for encryption/decryption. 

	Installation command:
	---------------------
	sudo  pip install pycryptodome

	Reference links:
	----------------
	https://pypi.python.org/pypi/pycryptodome


=========================================
Creating softlink for Warrior executable:
=========================================
User may wish to execute Warrior executable form any location in his machine instead of having to traverse 
to the location of Warrior executable and execute it form there.

In Linux like systems this can be achieved by creating a softlink for Warrior executable in the /usr/bin directory.

Eg: Warrior executable is located in /home/user/dir1/dir2/Warrior/Warrior

1. cd /usr/bin
2. sudo ln -s /home/user/dir1/dir2/Warrior/Warrior Warrior (command syntax sudo ln -s <path/to/file> <softlink name>)

Now a softlink will be created for Warrior executable with the name Warrior and you will be able to execute Warrior from any
location in the local machine.
