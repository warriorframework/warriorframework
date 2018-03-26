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

# -*- coding: utf-8 -*-
import os, json, shutil
from utils.navigator_util import Navigator
from wui.core.core_utils.app_install.installer import Installer
from utils.directory_traversal_utils import get_dir_from_path, get_sub_files

class Main:
    clone_name = 'temp'
    file_path = os.path.dirname(os.path.abspath(__file__))
    wapp_path = '/warriorframework/katana/wapps'
    rel_path = wapp_path + '/toReplace'
    paths = ['/views.py', '/urls.py', '/apps.py', '/templates/toReplace/index.html', '/static/toReplace/js/main.js', '/static/toReplace/css/main.css', '/wf_config.json']
    directorys = ['/templates/toReplace', '/static/toReplace']
    clone_path = file_path + os.sep + clone_name + rel_path

    def __init__(self):
        pass

    def build_new_app(self, request):
        self.set_variables( json.loads(request.POST.get('data'))[0] )
        self.clone_template()
        self.replace_vars()
        self.rename_path()
        self.install_app()
        self.remove_template()
        return 'success'

    def edit_dev_app(self):
        pass

    def set_variables(self, data):
        self.name = data['name']
        self.noSpaceName = data['name'].replace(' ', '_')
        self.details = data['details']
        self.icon = data['icon']
        self.color = data['color']
        self.developer = data['developer']

    def clone_template(self):
        shutil.copytree(self.file_path + os.sep + 'template_app', self.file_path + os.sep + self.clone_name, symlinks=False, ignore=None)

    def rename_path(self):
        for elem in self.directorys:
            elem = elem.replace('/', os.sep)
            path = self.clone_path + elem
            shutil.move( path, self.clone_path + elem.replace('toReplace', self.noSpaceName))
        shutil.move(self.clone_path, self.file_path + os.sep + self.clone_name + self.wapp_path + os.sep + self.noSpaceName)

    def replace_vars(self):
        for elem in self.paths:
            elem = elem.replace('/', os.sep)
            with open( self.clone_path + elem, 'r+') as f:
                page = f.read()
                f.seek(0)
                f.truncate()
                page = page.replace('toReplace', self.noSpaceName).replace('toFormatedReplace', self.name).replace('toIconReplace', self.icon).replace('toDetailsReplace', self.details).replace('toDeveloperReplace', self.developer).replace('toColorReplace', self.color)
                f.write(page)

    def install_app(self):
        nav_obj = Navigator()
        installer = Installer(get_parent_directory(nav_obj.get_katana_dir()), self.file_path + os.sep + self.clone_name)
        installer.install()

    def remove_template(self):
        shutil.rmtree(self.file_path + os.sep + self.clone_name)

    def get_urls(self, request):
        op_path = request.POST.get('data')
        app_name = get_dir_from_path( op_path )
        urlObj = {};
        types = {'js' : op_path + '/static/' + app_name + '/js', 'python' : op_path, 'css' : op_path + '/static/' + app_name + '/css', 'html' : op_path + '/templates/' + app_name }
        for k, v in types.items():
            urlObj[k] = get_sub_files(v, abs_path=True)
        print 'test', urlObj
        return { 'data' : urlObj }

    def open_file(self, request):
        op_path = request.POST.get('data')
        with open( op_path, 'r') as f:
            lines = f.read()
        return { 'data' : lines }

    def save_file(self, request):
        obj = json.loads(request.POST.get('data'))
        with open( obj['url'], 'w') as f:
            lines = f.write( obj['file'] )
        return { 'data' : lines }

    def create_method(self, request):
        """obj = json.loads(request.POST.get('data'))
        files = get_sub_files(self.file_path + os.sep + 'method_templates', abs_path=True)
        for fileItem in files:
            with open( fileItem, 'r') as f:
                lines = f.read()"""
        pass
