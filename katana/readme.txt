Requirement:
============
- python2.7
- Django


How to start Warrior UI (Katana):
=================================
1. Clone the warriorframework repository using this command:
    - git clone https://github.com/warriorframework/warriorframework.git

2. Traverse to /warriorframework/katana

3. execute "python katana.py"
	- by default katana start on port# 5000.

4. If port # 5000 is not available or user wishes to start katana on a different port
   - execute "python katana.py -p <port>" (where <port>=port number to be used)
   - If the port is not available to be used a error message is printed and it is the user's
     responsibility to provide an available port


Limitations:
============

In the current version, the UI for Warrior works as a stand alone client mode. i.e. each user is
expected to have warriorframework installed on his/her system and start the service locally in
that system and access it via a browser.

Warrior UI currently does not support a server-client model where the service can be started in a
remote server and accessed by different user sessions from different clients. This feature will be
added in its upcoming releases.

If there is only one server available and multiple users want to run Warrior UI on the same server,
then each user should download a copy of warriorframework git repository and save it in a unique
location on their system.