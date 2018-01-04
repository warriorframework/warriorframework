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
import os
import subprocess
import shutil
from Framework.Utils.print_Utils import print_info, print_error


def get_pip_cmd_output(addl_attrs):
    pip_cmd_list = ['pip']
    pip_cmd_list.extend(addl_attrs)
    return subprocess.check_output(pip_cmd_list)


def get_installed_pkges():
    pip_freeze = get_pip_cmd_output(['freeze'])
    installed_pkges = set([pkg.split('==')[0] for pkg in pip_freeze.split()])
    print_info("installed packages: %s" % installed_pkges)
    return installed_pkges


def activate_virtualenv():
    '''Activate virtual environment to add dependencies
    '''
    ve_name = os.path.join(os.curdir, 'warhorn_check')
    ve_loc = '~/.local/bin/virtualenv'
    try:
        if os.path.exists(ve_name):
            shutil.rmtree(ve_name)
        venv_cmd = os.path.expanduser(ve_loc)
        subprocess.check_call([venv_cmd, "--system-site-packages", ve_name])
        venv_file = "{}/bin/activate_this.py".format(ve_name)
        execfile(venv_file, dict(__file__=venv_file))
        return True
    except Exception as e:
        print "Activating virtual env at {} resulted in exception {}".format(ve_name, e)
        print "Check {} is a proper virtualenv binary".format(ve_loc)
        return False
