from utils.navigator_util import Navigator
import xmltodict, json, xml.etree.ElementTree as xml_controler

class Settings:

    def __init__(self):
        self.navigator = Navigator()

    def get_location(self):
        pass

    def general_setting_handler(self, request):
        json_file = self.navigator.get_katana_dir() + '/config.json'
        if request.method == 'POST':
            with open(json_file,'w') as f:
                f.write(json.dumps(json.loads(request.POST.get('data'))[0], sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            with open(json_file,'r') as f:
                json_data = json.load(f)
            return json_data

    def profile_setting_handler(self, request):
        json_file = self.navigator.get_katana_dir() + '/user_profile.json'
        if request.method == 'POST':
            with open(json_file,'w') as f:
                f.write(json.dumps(json.loads(request.POST.get('data'))[0], sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            with open(json_file,'r') as f:
                json_data = json.load(f)
            print 'tuz', json_data
            return json_data

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
            val = xmltodict.unparse({ 'Setting' : json.loads(request.POST.get('data')) }, pretty = True)
            elem_file.append(xml_controler.fromstring(val) )
            with open(w_settings,'w') as f:
                f.write(xml_controler.tostring(elem_file))
        else:
            xmldoc = xmltodict.parse(email_string)
            return xmldoc

    def jira_setting_handler(self, request):
        jira_config = self.navigator.get_warrior_dir() + '/Tools/jira/jira_config.xml'
        elem_file = xml_controler.parse(jira_config)
        elem_file = elem_file.getroot()
        xml_string = xml_controler.tostring(elem_file)
        if request.method == 'POST':
            val = xmltodict.unparse( {'jira' : { 'system' : json.loads(request.POST.get('data')) }}, pretty = True)
            with open(jira_config,'w') as f:
                f.write(val)
        else:
            xmldoc = xmltodict.parse(xml_string)
            for system in xmldoc['jira']['system']:
                for k, v in system.items():
                    if k == 'issue_type':
                        v = json.dumps(v)
                        system[k] = v
            return xmldoc

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
