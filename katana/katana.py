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
import sys
import os
from simple_server import main
use_py_server = False

try:
    import django
except ImportError:
    use_py_server = True
except Exception as e:
    print "-- An Error Occurred -- {0}".format(e)


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

    if not use_py_server:
        os.system("{0} {1} {2} {3}".format(command, filepath, runserver, port))
    else:
        main(port)
