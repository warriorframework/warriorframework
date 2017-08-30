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
from __future__ import unicode_literals

from django.shortcuts import render

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

path_to_demo="/home/khusain/Projects/xml-edit/warriorframework/katana/vdj/cases/"
path_to_testcases='/home/khusain/Projects/xml-edit/warriorframework/wftests/warrior_tests/';
path_to_productdrivers='/home/khusain/Projects/xml-edit/warriorframework/warrior/ProductDrivers/'
navigator = Navigator();


def index(request):
	path_to_testcases = navigator.get_warrior_dir() + "/../wftests/warrior_tests/"
	template = loader.get_template("./listAllSuites.html")
	fpath = path_to_testcases + 'suites';
	xfiles = glob.glob(fpath+"*/*/*.xml")
	dirs  = glob.glob(fpath+"*/*/");

	myfiles = [] 

	for df in dirs: 
		print df, os.path.split(df)[-1]
		files = glob.glob(df+"/*.xml");
		ff = [ os.path.basename(fn) for fn in files ] 
		myfiles.append({ 'path': df, 'dirpath': os.path.split(df[:-1])[1],  'files': ff })

	context = { 
		'title' : 'List of Suites',	
		'docSpec': 'suiteSpec',
		'listOfDirs' : dirs, 
		'listOfFiles': xfiles, 
		'myfiles': myfiles	
	}
	context.update(csrf(request))
	return HttpResponse(template.render(context, request))  

def getSuiteDataBack(request):
	print "Got something back in request";
	#response = request.readlines();   # Get the JSON response 
	ijs = request.POST.get(u'Suite')  # This is a json string 
	print ijs
	print "--------------TREE----------------"
	fname = request.POST.get(u'filetosave')
	print "save to ", fname 
	fd = open(fname,'w');
	fd.write(ijs);
	fd.close();
	return redirect(request.META['HTTP_REFERER'])


def editSuite(request):
	"""
	Set up JSON object for editing a suites file. 
	"""
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
	xml_r["TestSuite"]["Details"]["type"] = { }
	xml_r["TestSuite"]["Details"]["type"]['\@exectype'] = u"sequential_testcases"
	xml_r["TestSuite"]["Details"]["default_onError"] = {}
	xml_r["TestSuite"]["Details"]["default_onError"]["$"] = "" 
	xml_r["TestSuite"]["Details"]["default_onError"]['@action']= { "$": ""}
	xml_r["TestSuite"]["Testsuites"] = ""
	
	
	xlines = open(filename).read()
	xml_d = bf.data(fromstring(xlines)); # xmltodict.parse(fd1.read());

	# Map the input to the response collector
	for xstr in ["Name", "Title", "Category", "Date", "Time", "Engineer", \
		"Datatype", "type",  "default_onError"]:
		try: 
			xml_r["TestSuite"]["Details"][xstr] = copy.copy(xml_d["TestSuite"]["Details"].get(xstr,""))
		except:
			pass

	try:
		xml_r['TestSuite']['Testcases'] = copy.deepcopy(xml_d['TestSuite']['Testcases']);
	except:
		xml_r["TestSuite"]["Testcases"] = {}

	xml_r["TestSuite"]["Details"]["default_onError"]["$"] = "" 
	context = { 
		'myfile': filename,
		'docSpec': 'projectSpec',
		'suiteName': xml_r["TestSuite"]["Details"]["Name"]["$"],
		'suiteTitle': xml_r["TestSuite"]["Details"]["Title"]["$"],
		'suiteEngineer': xml_r["TestSuite"]["Details"]["Engineer"]["$"],
		#'suiteCategory': xml_r["TestSuite"]["Details"]["Category"]["$"],
		'suiteDate': xml_r["TestSuite"]["Details"]["Date"]["$"],
		'suiteTime': xml_r["TestSuite"]["Details"]["Time"]["$"],
		#'suiteType': xml_r["TestSuite"]["Details"]["type"]["$"],
		'suitedefault_onError':xml_r["TestSuite"]["Details"]["default_onError"]["$"] ,
		'suiteCases': xml_r['TestSuite']['Testcases'],
		'fulljson': xml_r['TestSuite'],
		'suiteResults': ""
		}
	# 
	# I have to add json objects for every test suite.
	# 

	return HttpResponse(template.render(context, request))

