
from utils.navigator_util import Navigator
import xmltodict, json

class Settings:

    def __init__(self):
        self.navigator = Navigator()

    def get_location(self):
        pass

    def get_general(self):
        w_settings = self.navigator.get_warrior_dir() + '/Tools/w_settings.xml'
        elem_file = open(w_settings, 'r')
        xmldoc = xmltodict.parse(elem_file)['Default']['Setting']
        elem_file.close()
        return xmldoc

    def set_general(self):
        pass
