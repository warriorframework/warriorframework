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
import xml.dom.minidom 
import xmltodict , dicttoxml
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring, tostring
import xml.etree.ElementTree

from utils.navigator_util import Navigator

path_to_demo="/home/khusain/Suites/xml-edit/warriorframework/katana/vdj/cases/"
path_to_testcases='/home/khusain/Suites/xml-edit/warriorframework/wftests/warrior_tests/';
path_to_productdrivers='/home/khusain/Suites/xml-edit/warriorframework/warrior/ProductDrivers/'
navigator = Navigator();

def old_index(request):
    return render(request, 'settings/index.html', {"data": controls.get_location()})

## MUST MOVE TO CLASS !!!!
## List all your Suites ...
##
def index(request):
	path_to_testcases = navigator.get_warrior_dir() + "/../wftests/warrior_tests/"
	template = loader.get_template("./listAllSuites.html")
	fpath = path_to_testcases + 'suites';
	#files = glob.glob(fpath+"*/*.xml")
	print path_to_testcases
	print fpath
	

	myfiles = []
	dirs = os.listdir(fpath);
	k = 0
	for dr in dirs:
		dirpath = fpath + os.sep + dr

		if os.path.isdir(dirpath):
			
			myfiles.append({ 'dirpath': dirpath, 'files' : [] })
			files = os.listdir(dirpath)
			print dirpath
			print files
			for fn in files: 
				fullname = dirpath + os.sep + fn
				if os.path.isfile(fullname) and os.path.splitext(fullname)[1] == ".xml":
					myfiles[k]['files'].append( { "filename": fn, "fullname" : fullname, 'displayName': os.path.split(fullname)[1]})
		k = k + 1
	print myfiles


	context = { 
		'title' : 'List of Suites',	
		'docSpec': 'SuiteSpec',
		'myfiles': myfiles	
	}
	context.update(csrf(request))
	return HttpResponse(template.render(context, request))

## MUST MOVE TO CLASS !!!!
## List all your Suite as editable UI.
##
def editSuite(request):
	"""
	Set up JSON object for editing a Suite file. 
	"""
	path_to_testcases = navigator.get_warrior_dir() + "/../wftests/warrior_tests/"
	template = loader.get_template("./editSuite.html")
	filename = request.GET.get('fname')
	
	xml_r = {}
	xml_r["TestSuite"] = {}
	xml_r["TestSuite"]["Details"] = {}
	xml_r["TestSuite"]["Details"]["Name"] = { "$": ""}
	xml_r["TestSuite"]["Details"]["Title"] = { "$": ""}
	xml_r["TestSuite"]["Details"]["Engineer"] = { "$": ""}
	xml_r["TestSuite"]["Details"]["Date"] = { "$": ""}
	xml_r["TestSuite"]["Details"]["Time"] = { "$": ""}
	xml_r["TestSuite"]["Details"]["type"] = { "$": "" }
	xml_r["TestSuite"]["Details"]["Logsdir"] = { "$": "" }
	xml_r["TestSuite"]["Details"]["Resultsdir"] = { "$": "" }
	xml_r["TestSuite"]["Details"]["InputDataFile"] = { "$": "" }
	xml_r["TestSuite"]["Details"]["type"]["@exectype"] = "sequential_testcases"
	xml_r["TestSuite"]["Details"]["default_onError"] = {}
	xml_r["TestSuite"]["Details"]["default_onError"]["$"] = "" 
	xml_r["TestSuite"]["Details"]["default_onError"]['@action']= { "$": ""}
	xml_r["TestSuite"]["Testsuites"] = ""
	
	
	xlines = open(filename).read()
	xml_d = bf.data(fromstring(xlines)); # xmltodict.parse(fd1.read());

	# Map the input to the response collector
	for xstr in ["Name", "Title", "Category", "Date", "Time", "Engineer", \
		"Datatype",  "default_onError"]:
		try: 
			xml_r["TestSuite"]["Details"][xstr] = copy.copy(xml_d["TestSuite"]["Details"].get(xstr,""))
		except:
			pass

	try:
		xml_r['TestSuite']['Testcases'] = copy.deepcopy(xml_d['TestSuite']['Testcases']);
	except:
		xml_r["TestSuite"]["Testcases"] = {}

	try:
		xml_r["TestSuite"]["Details"]["type"]['@exectype'] = copy.deepcopy(xml_d["TestSuite"]["Details"]["type"]['@exectype']);
	except:
		xml_r["TestSuite"]["Details"]["type"]['@exectype'] = "sequential_testcases"

	xml_r["TestSuite"]["Details"]["default_onError"]["$"] = "" 

	context = { 
		'myfile': filename,
		'docSpec': 'projectSpec',
		'suiteName': xml_r["TestSuite"]["Details"]["Name"]["$"],
		'suiteTitle': xml_r["TestSuite"]["Details"]["Title"]["$"],
		'suiteDatatype': xml_r["TestSuite"]["Details"]["type"]["@exectype"],
		'suiteEngineer': xml_r["TestSuite"]["Details"]["Engineer"]["$"],
		'suiteLogsdir': xml_r["TestSuite"]["Details"]["Logsdir"]["$"],
		'suiteResultsdir': xml_r["TestSuite"]["Details"]["Resultsdir"]["$"],
		'suiteInputDataFile': xml_r["TestSuite"]["Details"]["InputDataFile"]["$"],
		'suiteEngineer': xml_r["TestSuite"]["Details"]["Engineer"]["$"],
		'suiteDatatype': xml_r["TestSuite"]["Details"]["type"]["@exectype"],
		'suiteDate': xml_r["TestSuite"]["Details"]["Date"]["$"],
		'suiteTime': xml_r["TestSuite"]["Details"]["Time"]["$"],
		#'suiteType': xml_r["TestSuite"]["Details"]["type"]["$"],
		'suitedefault_onError':xml_r["TestSuite"]["Details"]["default_onError"]["$"] ,
		'suiteCases': xml_r['TestSuite']['Testcases'],
		'fulljson': xml_r['TestSuite'],
		'suiteResults': "",
		}
	# 
	# I have to add json objects for every test suite.
	# 

	return HttpResponse(template.render(context, request))


#import HTMLParser



def getSuiteDataBack(request):
	print "Got something back in request";
	#response = request.readlines();   # Get the JSON response 
	#template = loader.get_template("cases/editSuite.html")  # get another one?
	fname = request.POST.get(u'filetosave')
	#ijs = request.POST.get(u'json')  # This is a json string 


	#print "--------------TREE----------------"
	xml = request.POST.get(u'Suite') 
	print "save to ", fname 
	fd = open(fname,'w');
	fd.write(xml);
	fd.close();
	return redirect(request.META['HTTP_REFERER'])
