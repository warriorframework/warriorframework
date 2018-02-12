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
import subprocess
from simple_server import main
use_py_server = False

try:
    import django
except ImportError:
    use_py_server = True
except Exception as e:
    print "-- An Error Occurred -- {0}".format(e)
    use_py_server = True

class Katana:
    def __init__(self):
        pass

    def runProcess(self, osString):
        print osString
        proc = subprocess.Popen([osString], shell=True,
             stdin=None, stdout=None, stderr=None, close_fds=True)
        return proc

    def to_string(self, args):
        args[0] = 'manage.py'
        if len(args) > 1 and args[1] == 'database':
            args.remove('database')
        return 'python ' + ' '.join(args)

    def katana_init(self, args):
        args[0] = 'manage.py'
        self.runProcess( self.to_string(args) )
        if len(args) > 1 and args[1] == 'database':
            args = self.database_init(args)

    def database_init(self, args):
        proc = self.runProcess('python manage.py makemigrations')
        proc.wait()
        proc = self.runProcess('python manage.py migrate --run-syncdb')
        proc.wait()

if __name__ == "__main__":
    if not use_py_server:
        katana = Katana()
        katana.katana_init(sys.argv)
    else:
        main(port)
