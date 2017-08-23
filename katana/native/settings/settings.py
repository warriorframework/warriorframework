
from utils.navigator_util import Navigator
import xmltodict, json, xml.etree.ElementTree as xml_controler

class Settings:

    def __init__(self):
        self.navigator = Navigator()

    def get_location(self):
        pass

    def email_setting_handler(self, request):
        w_settings = self.navigator.get_warrior_dir() + '/Tools/w_settings.xml'
        elem_file = xml_controler.parse(w_settings)
        elem_file = elem_file.getroot()
        for elem in elem_file.findall('Setting'):
            if elem.get('name') == 'mail_to':
                email_string = xml_controler.tostring(elem)
                email_xml_obj = elem

        if request.method == 'POST':
            elem_file.remove(email_xml_obj)
            print('tuz', elem_file)
            val = xmltodict.unparse({ 'Setting' : json.loads(request.POST.get('data')) }, pretty = True)
            print('tyz', xml_controler.fromstring(val))
            elem_file.append(xml_controler.fromstring(val) )
            with open(w_settings,'w') as f:
                f.write(xml_controler.tostring(elem_file))
        else:
            xmldoc = xmltodict.parse(email_string)
            return xmldoc

    def set_general(self):
        pass

    def secret_handler(self, request):
        keyDoc = self.navigator.get_warrior_dir() + '/Tools/admin/secret.key'
        if request.method == 'POST':
            val = request.POST.get("data[0][value]")
            elem_file = open(keyDoc, 'w')
            elem_file.write(val)
            elem_file.close()
        else:
            elem_file = open(keyDoc, 'r')
            key_data = elem_file.read()
            elem_file.close()
            return key_data
