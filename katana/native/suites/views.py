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
# Create your views here.

from django.shortcuts import render, redirect
from django.template.context_processors import csrf
import os, sys, glob, copy 
from django.http import HttpResponse, JsonResponse
from django.template import loader
import xmltodict
import json
from utils.navigator_util import Navigator

navigator = Navigator();

def old_index(request):
    return render(request, 'settings/index.html', {"data": controls.get_location()})


def getSuiteListTree(request):
	path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"
	x= json.loads(open(path_to_config_file).read());
	fpath = x['testsuitedir'];
	template = loader.get_template("listAllSuites.html")
	jtree = navigator.get_dir_tree_json(fpath)
	jtree['state']= { 'opened': True };
	print jtree;
	return JsonResponse({'treejs': jtree })

def getJSONSuiteData(request):
	path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"   
	x= json.loads(open(path_to_config_file).read());
	path_to_testcases = x['testsuitedir'];
	filename = request.GET.get('fname')
	print "Getting data for ", filename;
	try:
		xml_d = xmltodict.parse(open(filename).read());
	except:
		xml_d = getEmpty();

	j_data = json.loads(json.dumps(xml_d))
	responseBack = { 'fulljson': j_data , 'fname': filename }
	return JsonResponse(responseBack)

def index(request):
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['testsuitedir']
	template = loader.get_template("./listAllSuites.html")

	myfiles = []

	tt = navigator.get_dir_tree_json(fpath)
	tt['state']= { 'opened': True };
	

	context = { 
		'title' : 'List of Suites',	
		'docSpec': 'SuiteSpec',
		'myfiles': myfiles, 
		'basedir': fpath,
		'treejs'  : tt 
	}
	context.update(csrf(request))
	return HttpResponse(template.render(context, request))


def getEmpty():
	edata = {"TestSuite": 
		{"Testcases": 
			{"Testcase": 
				[{"impact": "impact",
				  "Execute": {"@ExecType": "yes", "Rule": {"@Elsevalue": "", "@Condvalue": "", "@Condition": "", "@Else": "next"}},
				 "InputDataFile": "", "onError": {"@action": "next", "@value": ""}, 
				 "runmode": {"@type": "standard", "@value": ""}, "context": "positive", "runtype": "sequential_keywords", "path": "../Cases/EDITME.xml"}, 
				 {"impact": "impact", "Execute": {"@ExecType": "Yes", "Rule": {"@Elsevalue": "", "@Condvalue": "", "@Condition": "", "@Else": "next"}}, 
				 "InputDataFile": "", "onError": {"@action": "next", "@value": ""}, 
				 "runmode": {"@type": "standard", "@value": ""}, "context": "positive", "runtype": "sequential_keywords", "path": "../Cases/EDITME.xml"}]}, 
				 "Requirements": {"Requirement": ["Requirement-demo-001", "Requirement-demo-002"]}, "Details": {"Name": "Name Here", "Title": "Title", 
				 "Resultsdir": "", 
				 "State": "Released", 
				 "Time": "23:37:23", 
				 "Date": "03/01/2017", 
				 "default_onError": {"@action": "next"}, 
				 "type": {"@exectype": "sequential_testcases", "@Number_Attempts": "", "@Max_Attempts": ""}, "Engineer": "Engineer"}}};
	return edata;


## MUST MOVE TO CLASS !!!!
## List all your Suite as editable UI.
##
def editSuite(request):
	"""
	Set up JSON object for editing a Suite file. 
	"""
	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"

	config = json.loads(open(path_to_config).read())
	fpath = config['testsuitedir']

	template = loader.get_template("./editSuite.html")
	filename = request.GET.get('fname')
	print "Asked for ", filename
	if filename.find("..") == 0: 
		filename = fpath + os.sep + filename
	print "Attempting to read ...", filename 


	xml_r = {}
	xml_r["TestSuite"] = {}
	xml_r["TestSuite"]["Details"] = {}
	xml_r["TestSuite"]["Details"]["Name"] = ""
	xml_r["TestSuite"]["Details"]["Title"] = ""
	xml_r["TestSuite"]["Details"]["Engineer"] = ""
	xml_r["TestSuite"]["Details"]["Date"] = ""
	xml_r["TestSuite"]["Details"]["Time"] = ""
	xml_r["TestSuite"]["Details"]["type"] = { }
	xml_r["TestSuite"]["Details"]["Logsdir"] = ""
	xml_r["TestSuite"]["Details"]["State"] = "New"
	xml_r["TestSuite"]["Details"]["Resultsdir"] = ""
	xml_r["TestSuite"]["Details"]["InputDataFile"] = ""
	xml_r["TestSuite"]["Details"]["type"]["@exectype"] = "sequential_testcases"
	xml_r["TestSuite"]["Details"]["type"]["@Number_Attempts"] = "0"
	xml_r["TestSuite"]["Details"]["type"]["@Max_Attempts"] = "0"
	
	xml_r["TestSuite"]["Details"]["default_onError"] = {}
	xml_r["TestSuite"]["Details"]["default_onError"]['@action']= ""
	xml_r["TestSuite"]["Details"]["default_onError"]['@value']= ""

	xml_r["TestSuite"]["Testcases"] = { 'Testcase' :[] }
	
	if filename.upper() == 'NEW':
		xml_d = copy.deepcopy(xml_r);
	else:
		try:
			xlines = open(filename).read()
			xml_d = xmltodict.parse(xlines, dict_constructor=dict);
		except:
			xml_d = copy.deepcopy(xml_r);
			basename = os.path.split(filename)[1];
			basename = basename.replace('.xml','')
			xml_d["TestSuite"]["Details"]['Name'] = basename
			

	# Map the input to the response collector
	for xstr in ["Name", "Title", "Category", "Date", "Time", "Engineer", "Datatype", 'Resultsdir', 'InputDataFile']:
		try: 
			xml_r["TestSuite"]["Details"][xstr] = copy.copy(xml_d["TestSuite"]["Details"].get(xstr,""))
		except:
			pass

	print xml_d["TestSuite"]['Details']


	try:
		xml_r['TestSuite']['Testcases'] = copy.deepcopy(xml_d['TestSuite']['Testcases']);
	except:
		xml_r["TestSuite"]["Testcases"] =  { 'Testcase': [] }

	try:
		xml_r["TestSuite"]["Details"]["type"] = copy.deepcopy(xml_d["TestSuite"]["Details"]["type"]);
	except:
		xml_r["TestSuite"]["Details"]["type"]['@exectype'] = "sequential_testcases"

	#xml_r["TestSuite"]["Details"]["default_onError"] = "" 

	fulljsonstring = str(json.loads(json.dumps(xml_r['TestSuite'])));
	fulljsonstring = fulljsonstring.replace('u"',"'").replace("u'",'"').replace("'",'"');
	fulljsonstring = fulljsonstring.replace('None','""').replace('""""','""')

	context = { 
		'savefilename': os.path.split(filename)[1],
		'savefilepath': os.path.split(filename)[0],
		'fullpathname': filename,
		'docSpec': 'projectSpec',
		'suiteName': xml_r["TestSuite"]["Details"]["Name"],
		'suiteTitle': xml_r["TestSuite"]["Details"]["Title"],
		'suiteDatatype': xml_r["TestSuite"]["Details"]["type"]["@exectype"],
		'suiteEngineer': xml_r["TestSuite"]["Details"]["Engineer"],
		'suiteLogsdir': xml_r["TestSuite"]["Details"]["Logsdir"],
		'suiteResultsdir': xml_r["TestSuite"]["Details"]["Resultsdir"],
		'suiteInputDataFile': xml_r["TestSuite"]["Details"]["InputDataFile"],
		'suiteEngineer': xml_r["TestSuite"]["Details"]["Engineer"],
		'suiteDatatype': xml_r["TestSuite"]["Details"]["type"]["@exectype"],
		'suite_num_attempts': xml_r["TestSuite"]["Details"]["type"].get("@Number_Attempts","0"),
		'suite_max_attempts': xml_r["TestSuite"]["Details"]["type"].get("@Max_Attempts","0"),
		'suiteDate': xml_r["TestSuite"]["Details"]["Date"],
		'suiteTime': xml_r["TestSuite"]["Details"]["Time"],
		'suiteState': xml_r["TestSuite"]["Details"]["State"],
		#'suiteType': xml_r["TestSuite"]["Details"]["type"],
		'suitedefault_onError':xml_r["TestSuite"]["Details"]["default_onError"].get('@action',""),
		'suitedefault_onError_goto':xml_r["TestSuite"]["Details"]["default_onError"].get('@value',''),
		'suiteCases': xml_r['TestSuite']['Testcases'],
		#'fulljson': xml_r['TestSuite'],
		'fulljson': fulljsonstring,
		'suiteResults': "",
		}
	# 
	# I have to add json objects for every test suite.
	# 

	return HttpResponse(template.render(context, request))


#import HTMLParser



def getSuiteDataBack(request):
	#print "Got something back in request";

	navigator = Navigator();
	path_to_config = navigator.get_katana_dir() + os.sep + "config.json"
	config = json.loads(open(path_to_config).read())
	fpath = config['testsuitedir']

	fname = request.POST.get(u'filetosave')
	ufpath = request.POST.get(u'savefilepath')
	#ijs = request.POST.get(u'json')  # This is a json string 
	
	#print "--------------TREE----------------"
	#xml = request.POST.get(u'Suite') 
	ijs = request.POST.get(u'json')  # This is a json string 
	print ijs;
	xml = xmltodict.unparse(json.loads(ijs), pretty=True)
	
	#print "---
	if fname.find(".xml") < 2: fname = fname + ".xml"
	print "save to ", ufpath + os.sep + fname 
	fd = open(fpath + os.sep + fname,'w');
	fd.write(xml);
	fd.close();
	return redirect(request.META['HTTP_REFERER'])
