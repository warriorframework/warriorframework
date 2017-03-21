Katana:

OS support: 
===========
- Creation of Testcases, Testsuites, Projects in both Windows and Linux operating systems.
- Execution is currently supported only in Linux.
  (xterm has to be installed and available to support execution in Linux)

Python requirement:
===================
- pyhton2.7 has to be installed inorder to use Katana


How to start Katana:
====================
1. Download the git repository

2. traverse to the directory called katana

3. execute "python katana.py"
	- by default katana start on port# 5000.

4. If port # 5000 is not available or user wishes to start katana on a different port
   - execute "python katana.py -p x" (where x=port number to be used)
   - If the port is not available to be used a error message is printed and it is user responsibility to provide a available port


Limitations:
============
1) Editing a existing xml file:
	 - Current version of Katana is designed to edit (or open) a xml file that was created by Katana. If a xml file was created by some other xml editor and has missing/incorrect tags/fields then such errors cannot be handled by Katana and editing the xml file will fail.


2) In the current version Katana works as a stand alone client mode. i.e. each user is expected to have katana installed in his/her desktop/server and start the service locally in the desktop/server and access it via a browser. 
Katana currently does not support a server-client model where the service can be started in a remote server and accessed by different user sessions from different clients. This feature will be added in the upcoming releases of Katana.

If there is only one server available and multiple users want to run katana on the same server, then each user should download a copy of Katana git repository and save it in a unique location in the server.

While starting Katana, each user should start his/her copy of Katana by specifying port number as described in the "How to start Katana" section above, and they can use all the functionalities of Katana.





