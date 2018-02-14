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
import subprocess
import signal
from utils.directory_traversal_utils import get_parent_dir_path, join_path
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
    def __init__(self, path):
        self.og_process = None
        self.manage_path = path

    def signal_handler(self):
        print('Ended Server')
        self.og_process.kill()

    @staticmethod
    def run_process(os_string):
        return subprocess.Popen(os_string.split(), shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)

    def to_string(self, args):
        args[0] = self.manage_path
        if len(args) > 1 and args[1] == 'database':
            args.remove('database')
        return 'python ' + ' '.join(args)

    def katana_init(self, args):
        args[0] = self.manage_path
        self.og_process = self.run_process(self.to_string(args))
        signal.signal(signal.SIGINT, self.signal_handler)
        if len(args) > 1 and args[1] == 'database':
            self.database_init()
        signal.pause()

    def database_init(self):
        proc = self.run_process('python {0} makemigrations'.format(self.manage_path))
        proc.wait()
        proc = self.run_process('python {0} migrate --run-syncdb'.format(self.manage_path))
        proc.wait()


if __name__ == "__main__":
    if not use_py_server:
        katana = Katana(join_path(get_parent_dir_path(sys.argv[0]), "manage.py"))
        katana.katana_init(sys.argv)
    else:
        main('8000')
