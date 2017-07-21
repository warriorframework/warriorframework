Requirement:
============
- python2.7
- Django


How to start Warrior UI (Katana):
=================================
1. Clone the warriorframework repository using this command:
    - git clone https://github.com/warriorframework/warriorframework.git

2. Traverse to /warriorframework/katana

3. Execute "python katana.py"
	- by default Warrior UI (katana) will start on port 5000.

4. If you wish to start Warrior UI on a different port, execute
   - "python katana.py -p <port>" (where <port>=port number to be used)


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