#!/usr/bin/env python
"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os
import sys

usePythonServer = 0

####
# Check number 1: Don't run the server if django not installed. 
# 
try:
    import django
except: 
    print """
    You are missing the django framework. 
    Please install django on you system. 
    Try  sudo pip install django 

    Refer to this link for more information 
    https://docs.djangoproject.com/en/1.11/topics/install/
    """
    usePythonServer = 1; 

import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


warningMessage="""
<H1>You are not running django! </H1>
Please make sure you are running katana with django installed for the server. <p>
<a href="https://docs.djangoproject.com/en/1.11/topics/install/">Documentation for installing django here.</a>
""";

HandlerClass = SimpleHTTPRequestHandler
ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.0"
REDIRECTIONS = {"/": "http://python.org/",
                "/katana/": "http://google.com/"}
LAST_RESORT = "http://google.com/"  

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body>%s</body></html>" % warningMessage)

    def do_HEAD(self):
        self.send_response(301)
        self.send_header("Location", REDIRECTIONS.get(self.path, LAST_RESORT))
        self.end_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body>%s</body></html>" % warningMessage)
        # self.wfile.write("<html><body><h1>DONT POST!</h1></body></html>")


if __name__ == "__main__":

    """
    This file is a wrapper file to run manage.py via katana.py.

    This wrapper file was introduced to maintain backward compatibility between katana running on
    the bottle server amd katana running on Django

    The commands accepted are:

    - python katana.py : This would start the server at localhost:5000
    - python katana.py -p <port> : This would start the server at localhost:<port>

    katana.py can also be run from a different directory : python /path/to/katana.py [-p <port>]

    """

    args = sys.argv[1:]
    directory = os.path.dirname(sys.argv[0])

    python_executable = sys.executable

    if not python_executable:
        command = "python"
    else:
        command = python_executable

    port = 5000
    runserver = "runserver"
    filepath = "manage.py"

    if directory is not "":
        filepath = directory + os.sep + filepath

    for i in range(0, len(args)):
        if args[i] == "-p":
            if i+1 >= len(args):
                print "No port number given. Exiting."
                sys.exit()
            else:
                port = args[i+1]
            break
    if usePythonServer:
        server_address = ('127.0.0.1', int(port))
        HandlerClass.protocol_version = Protocol 
        httpd = ServerClass(server_address, SimpleHandler)
        sa = httpd.socket.getsockname()
        print "WARNING Serving django-less server on", sa[0], "port", sa[1], "..."
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
    else: 
        os.system("{0} {1} {2} {3}".format(command, filepath, runserver, port))
    
    
    
