# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json, os, xml.etree.ElementTree as xml_controler
from distutils.version import LooseVersion
import copy
from threading import Timer

from utils.navigator_util import Navigator
from collections import OrderedDict
try:
    import xmltodict
except ImportError:
    print "Please install xmltodict"
from utils.json_utils import read_xml_get_json
import subprocess

class Settings:

    def __init__(self):
        self.navigator = Navigator()

    def get_location(self):
        pass

    def smart_analysis_handler(self, request):
        mainFile = self.navigator.get_warrior_dir() + os.sep + 'Tools' + os.sep + 'connection' + os.sep +'connect_settings.xml'
        if request.method == 'POST':
            val = xmltodict.unparse( {'credentials' : { 'system' : json.loads(request.POST.get('data')) }}, pretty = True)
            with open(mainFile,'w') as f:
                f.write(val)
        else:
            with open( mainFile,'r') as f:
                mainDict = xmltodict.parse(f)['credentials']
            if mainDict is not None and not isinstance( mainDict['system'], list):
                mainDict['system'] = [ mainDict['system'] ]

            return mainDict

    def general_setting_handler(self, request):
        json_file = self.navigator.get_katana_dir() + os.sep +'config.json'
        w_settings = self.navigator.get_warrior_dir() + 'Tools'+ os.sep + 'w_settings.xml'
        elem_file = xml_controler.parse(w_settings)
        elem_file = elem_file.getroot()
        elem = self.search_by_name('def_dir', elem_file)
        def_dir_string = xml_controler.tostring(elem)
        def_dir_xml_obj = elem

        if request.method == 'POST':
            w_settings_data = { 'Setting' : { 'Logsdir' : '', 'Resultsdir' : '', '@name' : '' } }
            returned_json = json.loads(request.POST.get('data'))
            for k, v in w_settings_data['Setting'].items():
                w_settings_data['Setting'][k] = returned_json[0][k]
                del returned_json[0][k]

            elem_file.remove(def_dir_xml_obj)
            val = xmltodict.unparse( w_settings_data, pretty = True)
            elem_file.insert( 0, xml_controler.fromstring(val) )
            with open(w_settings,'w') as f:
                f.write(xml_controler.tostring(elem_file))
            with open(json_file,'w') as f:
                f.write(json.dumps(returned_json[0], sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            with open(json_file,'r') as f:
                json_data = json.load( f, object_pairs_hook=OrderedDict)
            data = {}
            data['fromXml'] = xmltodict.parse(def_dir_string).get('Setting')
            data['fromJson'] = json_data
            return data

    def profile_setting_handler(self, request):
        json_file = self.navigator.get_katana_dir() + os.sep + 'user_profile.json'
        config_json_file = self.navigator.get_katana_dir() + os.sep + 'config.json'
        if request.method == 'POST':
            data = json.loads(request.POST.get('data'))
            with open(json_file,'w') as f:
                f.write(json.dumps(data[0], sort_keys=True, indent=4, separators=(',', ': ')))
            with open(config_json_file,'r+') as a:
                new_json = json.load(a)
                new_json['engineer'] = data[0]['firstName']
                a.seek(0)
                a.write(json.dumps(new_json, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            with open(json_file,'r') as f:
                json_data = json.load(f)

            return json_data

    def search_by_name(self, name, file):
        for elem in file.findall('Setting'):
            if elem.get('name') == name:
                return elem

    def email_setting_handler(self, request):
        w_settings = self.navigator.get_warrior_dir() + 'Tools'+ os.sep + 'w_settings.xml'
        elem_file = xml_controler.parse(w_settings)
        elem_file = elem_file.getroot()
        elem = self.search_by_name('mail_to', elem_file)
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
        jira_config = self.navigator.get_warrior_dir() + 'Tools' + os.sep + 'jira' + os.sep +'jira_config.xml'
        elem_file = xml_controler.parse(jira_config)
        elem_file = elem_file.getroot()
        xml_string = xml_controler.tostring(elem_file)
        if request.method == 'POST':
            val = xmltodict.unparse( {'jira' : { 'system' : json.loads(request.POST.get('data')) }}, pretty = True)
            with open(jira_config,'w') as f:
                f.write(val)
        else:
            xmldoc = xmltodict.parse(xml_string)
            if xmldoc is not None and xmldoc['jira'] is not None:
                if not isinstance( xmldoc['jira']['system'], list):
                    xmldoc['jira']['system'] = [ xmldoc['jira']['system']]
                for system in xmldoc['jira']['system']:
                    for k, v in system.items():
                        if k == 'issue_type':
                            v = json.dumps(v)
                            system[k] = v
            return xmldoc

    def secret_handler(self, request):
        keyDoc = self.navigator.get_warrior_dir() + os.sep + 'Tools' + os.sep + 'admin' + os.sep +'secret.key'
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

    def prerequisites_handler(self, request):
        REF_FILE = os.path.join(self.navigator.get_katana_dir(), "native", "assembler", "static", "assembler", "base_templates", "empty.xml")
        data = read_xml_get_json(REF_FILE)
        prereqs = data["data"]["warhorn"]["dependency"]
        prereq_data = []
        for prereq in prereqs:
            temp = {}
            for key, value in prereq.items():
                temp[key.strip('@')] = value

            temp["status"] = "install"
            try:
                module_name = __import__(temp["name"])
                some_var = module_name.__version__
            except ImportError:
                temp["available_version"] = "--"
                temp["installBtnText"] = "Install"
            except Exception as e:
                print "-- An Exception Occurred -- while getting details about {0}: {1}".format(temp["name"], e)
                temp["available_version"] = "--"
                temp["installBtnText"] = "Install"
            else:
                temp["available_version"] = some_var
                if LooseVersion(str(temp["version"])) <= LooseVersion(str(temp["available_version"])):
                    temp["installBtnText"] = "Installed"
                    temp["status"] = "installed"
                else:
                    temp["installBtnText"] = "Upgrade"
                    temp["status"] = "upgrade"

            prereq_data.append(copy.deepcopy(temp))
        return prereq_data

    def prereq_installation_handler(self, request):
        name = request.POST.get('name')
        admin = request.POST.get('admin')
        version = request.POST.get('version')
        status = False
        return_code = -9
        command = ["pip", "install", "{0}=={1}".format(name, version)]
        if admin == "true":
            command.insert(0, "sudo")
        else:
            command.append("--user")
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        kill = lambda process: process.kill()
        my_timer = Timer(10, kill, [p])
        try:
            my_timer.start()
            out, err = p.communicate()
            return_code = p.returncode
            if return_code == 0:
                status = True
        finally:
            if return_code == -9:
                err = "Command could not be completed."
                out = "Command could not be completed in 30 seconds - may be the user is not authorized to install {0}".format(name)
            my_timer.cancel()
        return {"status": status, "return_code": return_code, "errors": err, "output": out}
