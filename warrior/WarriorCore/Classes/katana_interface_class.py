from xml.dom import minidom
import os
import json
try:
    import requests
    has_requests = True
except ImportError:
    has_requests = False
    print("warrior can not communicate with katana please install requests and try again")

__author__ = 'Keenan Jabri'


class KatanaInterface:
    katanaLocation = ''

    def __init__(self):
        if has_requests:
            self.get_location()

    def get_location(self):
        l_dir = os.path.dirname(__file__)
        filename = os.path.join(l_dir, '../../Tools/w_settings.xml')
        settings_xml = minidom.parse(filename)
        setting_elems = settings_xml.getElementsByTagName('Setting')
        for i in setting_elems:
            if i.attributes['name'].value == 'katana':
                self.katanaLocation = i.attributes['location'].value

    def send_file(self, fileLocation, toCall):
        if self.katanaLocation != '':
            jsonObj = {'fileUrl': fileLocation, 'toCall': toCall}
            requests.post(self.katanaLocation, json=jsonObj)

    def end_comunication(self):
        if self.katanaLocation != '':
            jsonObj = {}
            jsonObj['toCall'] = 'setLocation'
            requests.post(self.katanaLocation, json=jsonObj)
