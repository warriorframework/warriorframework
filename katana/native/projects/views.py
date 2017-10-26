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
#from __future__ import unicode_literals


from native.settings.settings import Settings
# Create your views here.

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template.context_processors import csrf
import os, sys, glob, copy 
from collections import OrderedDict
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from xml.sax.saxutils import escape, unescape

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library

import json
#from katana.utils.navigator_util import get_dir_tree_json
import xmltodict
from utils.navigator_util import Navigator

navigator = Navigator();
path_to_src_python_file = navigator.get_katana_dir() + os.sep + "config.json"

def old_index(request):
    return render(request, 'settings/index.html', {"data": controls.get_location()})

def getEmpty():
	edata={"Project": 
			{"Testsuites": 
			{"Testsuite": 
				[{"onError": {"@action": "goto", "@value": "3"}, "path": "../../Warriorspace/Suites/Suite1.xml"}, 
				{"onError": {"@action": "abort"}, "path": "../../Warriorspace/Suites/Suite2.xml"},
				 {"path": "../../Warriorspace/Suites/Suite3.xml"}, {"onError": {"@action": "next"}, 
				 "path": "../../Warriorspace/Suites/Suite4.xml"}]}, "Details": {"default_onError": {"@action": "next", "@value": ""}, 
				 "Title": "Project Title or Description", "Resultsdir": "", "Name": "Project Name", "Engineer": "Engineer"}}}
	return edata;

import logging 
logger = logging.getLogger(__name__)

def getJSONProjectData(request):
	path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"   
	x= json.loads(open(path_to_config_file).read());
	path_to_testcases = x['projdir'];
	filename = request.GET.get('fname')
	logger.info("Getting data for %s "% filename);
	try:
		xml_d = xmltodict.parse(open(filename).read());
	except:
		xml_d = getEmpty();

	#print xml_d
	if (not xml_d.has_key(u'Project')):
		print "Invalid XML file"
		xml_d = getEmpty();

	j_data = json.loads(json.dumps(xml_d))
	responseBack = { 'fulljson': j_data , 'fname': filename }
	return JsonResponse(responseBack)

## MUST MOVE TO CLASS !!!!
## List all your projects ...
##
def index(request):
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['projdir']
	template = loader.get_template("./listAllProjects.html")
	files = glob.glob(fpath+"*/*.xml")

	tt = navigator.get_dir_tree_json(fpath)
	tt['state']= { 'opened': True };
	print tt

	fulljsonstring = str(json.loads(json.dumps(tt)));
	fulljsonstring = fulljsonstring.replace('u"',"'").replace("u'",'"').replace("'",'"');
	fulljsonstring = fulljsonstring.replace('None','""')

	context = { 
		'title' : 'List of Projects',	
		'docSpec': 'projectSpec',
		'treejs'  : fulljsonstring, 
		'listOfFiles': files	
	}
	context.update(csrf(request))
	return HttpResponse(template.render(context, request))


def getProjectListTree(request):
	path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"
	x= json.loads(open(path_to_config_file).read());
	fpath = x['projdir'];
	template = loader.get_template("listAllCases.html")
	jtree = navigator.get_dir_tree_json(fpath)
	jtree['state']= { 'opened': True };
	return JsonResponse({'treejs': jtree })

## MUST MOVE TO CLASS !!!!
## List all your project as editable UI.
##
def editProject(request):
	"""
	Set up JSON object for editing a project file. 
	"""
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['projdir']

	template = loader.get_template("./editProject.html")
	filename = request.GET.get('fname','NEW')

	
	# Create Mandatory empty object.
	xml_r = {} ; 
	xml_r["Project"] = {}
	xml_r["Project"]["Details"] = {}
	xml_r["Project"]["Details"]["Name"] = "" # ""
	xml_r["Project"]["Details"]["Title"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["Category"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["State"] = "" #OrderedDict([('$', 'New')])
	xml_r["Project"]["Details"]["Date"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["Time"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["Engineer"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["ResultsDir"] = "" #OrderedDict([('$', '')])
	xml_r["Project"]["Details"]["default_onError"] = { '@action': '', '@value': ''} #OrderedDict([('$', '')])
	xml_r["Project"]["Testsuites"] = []
	xml_r['Project']['filename'] = "" #OrderedDict([('$', filename)]);

	if filename != 'NEW':
		xlines = open(filename.strip()).read()
		#xml_d = bf.data(fromstring(xlines)); #
		xml_d = xmltodict.parse(xlines, dict_constructor=dict);

		# Map the input to the response collector
		for xstr in ["Name", "Title", "Category", "Date", "Time", "Engineer", "ResultsDir"]:
			try:
				xml_r["Project"]["Details"][xstr]= xml_d["Project"]["Details"][xstr];
			except: 
				pass

		try:
			xml_r['Project']['Testsuites'] = copy.copy(xml_d['Project']['Testsuites']);
		except:
			xml_r["Project"]["Testsuites"] = []
	else:
		filename = path_to_config + os.sep + "new.xml"

 	fulljsonstring = str(json.loads(json.dumps(xml_r['Project'])));
 	print fulljsonstring;
	fulljsonstring = fulljsonstring.replace('u"',"'").replace("u'",'"').replace("'",'"');
	fulljsonstring = fulljsonstring.replace('None','""')

	context = { 
		'savefilename': os.path.split(filename)[1], 
		'savefilepath': fpath,
		'fullpathname': filename, 
		'myfile': filename,
		'docSpec': 'projectSpec',
		'projectName': xml_r["Project"]["Details"]["Name"],
		'projectTitle': xml_r["Project"]["Details"]["Title"],
		'projectState': xml_r["Project"]["Details"]["State"],
		'projectEngineer': xml_r["Project"]["Details"]["Engineer"],
		'projectCategory': xml_r["Project"]["Details"]["Category"],
		'projectDate': xml_r["Project"]["Details"]["Date"],
		'projectTime': xml_r["Project"]["Details"]["Time"],
		'resultsDir': xml_r["Project"]["Details"]["ResultsDir"],	
		'project_onError_action': xml_r["Project"]["Details"]["default_onError"].get('@action','abort'),
		'project_onError_value':  xml_r["Project"]["Details"]["default_onError"].get('@avalue',""),
		#'fulljson': xml_r['Project']
		'fulljson': fulljsonstring,
		}
	# 
	# I have to add json objects for every test suite.
	# 
	return HttpResponse(template.render(context, request))



def getProjectDataBack(request):
	print "Got something back in request";
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['projdir']
	fname = request.POST.get(u'filetosave')
	ijs = request.POST.get(u'json')  # This is a json string 
	print ijs;
	#print "--------------TREE----------------"
	if fname.find(".xml") < 2: fname = fname + ".xml"

	#fd = open(fpath + os.sep + fname+ ".json",'w');
	#fd.write(ijs);
	#fd.close();
 	
	xml = xmltodict.unparse(json.loads(ijs), pretty=True)
	print "save to ", fpath + os.sep + fname 
	fd = open(fpath + os.sep + fname,'w');
	fd.write(xml);
	fd.close();
	return redirect(request.META['HTTP_REFERER'])
