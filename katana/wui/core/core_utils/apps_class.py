import os
from wui.core.core_utils.core_utils import get_app_path_from_name
from utils.directory_traversal_utils import get_abs_path, get_parent_directory
import json

class App:
    data = ''

    def __init__(self):
        pass

    def setValues(self, json):
        """ sets json to data var """
        self.data = json

class Apps:
    paths = []
    apps = []

    def __init__(self):
        pass

    def setApps(self, data):
        """ call this to build Apps array and make app objects """
        self.apps = []
        self.paths = []
        self.get_config_paths( data )
        for url in self.paths:
            app = App()
            app.setValues( self.get_json( url ) )
            self.apps.append( app )
        return self.apps


    def get_json(self, url):
        """ retrives json data """
        with open( url ) as configFile:
            self.jObj = json.load(configFile)
            return self.jObj

    def get_config_paths(self, data ):
        """ sets paths array to paths of json files"""
        base_directory = get_parent_directory(os.path.dirname(os.path.realpath(__file__)), 3)
        for app1 in data['available_apps']:
            for app2 in data['settings_installed_apps']:
                if app1 == app2:
                    self.paths.append( get_app_path_from_name(app1, data['config_file_name'], base_directory) )
