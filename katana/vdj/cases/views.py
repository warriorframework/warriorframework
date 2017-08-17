# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
	

# Create your views here.
import os, glob, copy, json
from django.http import HttpResponse, JsonResponse
from django.template import loader
from xml.sax.saxutils import escape, unescape
import xml.dom.minidom 
import xmltodict 
from django.core.serializers import serialize
from django.db.models.query import QuerySet
import simplejson
from django.template import Library


path_to_demo="/home/khusain/Projects/xml-edit/warriorframework/katana/vdj/cases/"

def index(request):
	template = loader.get_template("cases/index.html")
	context = { 
		'myfile': 'tp.xml',
		'docSpec': 'projectSpec'
		
	}
	return HttpResponse(template.render(context, request))


def listAllCases(request):
	template = loader.get_template("cases/listAllCases.html")
	#filename = request.GET.get('fname')
	# files = next(os.walk('/home/khusain/Projects/xml-edit/warriorframework/wftests/warrior_tests/testcases'))[2]
	fpath = '/home/khusain/Projects/xml-edit/warriorframework/wftests/warrior_tests/testcases';
	#files = [ os.path.join(fpath,x) for x in (os.walk(fpath))[2]]

	files = glob.glob(fpath+"*/*/*.xml")+glob.glob(fpath+"*/*/*/*.xml")
	context = { 
		'title' : 'List of Cases',	
		'docSpec': 'caseSpec',
		'listOfFiles': files	
	}
	return HttpResponse(template.render(context, request))

def listAllSuites(request):
	template = loader.get_template("cases/listAllSuites.html")
	fpath = '/home/khusain/Projects/xml-edit/warriorframework/wftests/warrior_tests/suites';
	files = glob.glob(fpath+"*/*/*.xml")
	context = { 
		'title' : 'List of Suites',	
		'docSpec': 'suiteSpec',
		'listOfFiles': files	
	}
	return HttpResponse(template.render(context, request))

def listAllProjects(request):
	template = loader.get_template("cases/listAllProjects.html")
	fpath = '/home/khusain/Projects/xml-edit/warriorframework/wftests/warrior_tests/projects';
	files = glob.glob(fpath+"*/*.xml")
	context = { 
		'title' : 'List of Projects',	
		'docSpec': 'projectSpec',
		'listOfFiles': files	
	}
	return HttpResponse(template.render(context, request))



def getJSONfile(request):
	filename = request.GET.get('fname')
	print "---------------filename ", filename
	return JsonResponse( open(path_to_demo+filename).read(), content_type='application/xml', safe=False)


def getXMLfile(request):
	filename = request.GET.get('fname')
	print "---------------filename ", filename
	return HttpResponse( open(filename).read(), content_type='text/xml')

def editProject(request):
	"""
	Set up JSON object for editing a project file. 
	"""
	template = loader.get_template("cases/editProject.html")
	filename = request.GET.get('fname')

	xml_r = {}
	xml_r["Project"] = {}
	xml_r["Project"]["Details"] = {}
	xml_r["Project"]["Details"]["Name"] = ""
	xml_r["Project"]["Details"]["Title"] = ""
	xml_r["Project"]["Details"]["Category"] = ""
	xml_r["Project"]["Details"]["Date"] = ""
	xml_r["Project"]["Details"]["Time"] = ""
	xml_r["Project"]["Details"]["Datatype"] = ""
	xml_r["Project"]["Details"]["defaultOnError"] = ""
	xml_r["Project"]["Testsuites"] = ""
	
	
	with open(filename) as fd1:
		xml_d = xmltodict.parse(fd1.read());

	# Map the input to the response collector
	for xstr in ["Name", "Title", "Category", "Date", "Time", "Engineer", \
		"Datatype", "default_onError"]:
		xml_r["Project"]["Details"][xstr] = xml_d["Project"]["Details"].get(xstr,"")

	try:
		xml_r['Project']['Testsuites'] = copy.copy(xml_d['Project']['Testsuites']);
	except:
		xml_r["Project"]["Testsuites"] = ""


	context = { 
		'myfile': filename,
		'docSpec': 'projectSpec',
		'projectName': xml_r["Project"]["Details"]["Name"],
		'projectTitle': xml_r["Project"]["Details"]["Title"],
		'projectEngineer': xml_r["Project"]["Details"]["Engineer"],
		'projectCategory': xml_r["Project"]["Details"]["Category"],
		'projectDate': xml_r["Project"]["Details"]["Date"],
		'projectTime': xml_r["Project"]["Details"]["Time"],
		'projectdefault_onError': xml_r["Project"]["Details"]["default_onError"],
		'projectSuites': xml_r['Project']['Testsuites'],
		'fulljson': xml_r
		}
	# 
	# I have to add json objects for every test suite.
	# 


	return HttpResponse(template.render(context, request))

def editSuite(request):
	"""
	Set up JSON object for editing a suites file. 
	"""
	template = loader.get_template("cases/editSuite.html")
	filename = request.GET.get('fname')
	
	xml_r = {}
	xml_r["TestSuite"] = {}
	xml_r["TestSuite"]["Details"] = {}
	xml_r["TestSuite"]["Details"]["Name"] = ""
	xml_r["TestSuite"]["Details"]["Title"] = ""
	xml_r["TestSuite"]["Details"]["Engineer"] = ""
	xml_r["TestSuite"]["Details"]["Date"] = ""
	xml_r["TestSuite"]["Details"]["Time"] = ""
	xml_r["TestSuite"]["Details"]["type"] = { }
	xml_r["TestSuite"]["Details"]["type"]['\@exectype'] = u"sequential_testcases"
	xml_r["TestSuite"]["Details"]["default_onError"] = {}
	xml_r["TestSuite"]["Details"]["default_onError"]['@action']= ""
	xml_r["TestSuite"]["Testsuites"] = ""
	
	
	with open(filename) as fd1:
		xml_d = xmltodict.parse(fd1.read());

	# Map the input to the response collector
	for xstr in ["Name", "Title", "Category", "Date", "Time", "Engineer", \
		"Datatype", "type",  "default_onError"]:
		xml_r["TestSuite"]["Details"][xstr] = xml_d["TestSuite"]["Details"].get(xstr,"")

	try:
		xml_r['TestSuite']['Testcases'] = copy.deepcopy(xml_d['TestSuite']['Testcases']);
	except:
		xml_r["TestSuite"]["Testcases"] = {}


	context = { 
		'myfile': filename,
		'docSpec': 'projectSpec',
		'suiteName': xml_r["TestSuite"]["Details"]["Name"],
		'suiteTitle': xml_r["TestSuite"]["Details"]["Title"],
		'suiteEngineer': xml_r["TestSuite"]["Details"]["Engineer"],
		'suiteCategory': xml_r["TestSuite"]["Details"]["Category"],
		'suiteDate': xml_r["TestSuite"]["Details"]["Date"],
		'suiteTime': xml_r["TestSuite"]["Details"]["Time"],
		'suiteType': xml_r["TestSuite"]["Details"]["type"],
		'suitedefault_onError': xml_r["TestSuite"]["Details"]["default_onError"],
		'suiteCases': xml_r['TestSuite']['Testcases'],
		'fulljson': xml_r,
		'suiteResults': ""
		}
	# 
	# I have to add json objects for every test suite.
	# 

	return HttpResponse(template.render(context, request))

def editCase(request):
	""" 
	Set up JSON object for editing a suites file. 
	"""
	template = loader.get_template("cases/editCase.html")
	filename = request.GET.get('fname')

	# Open the XML file and get it's dictionary...
	# Make exceptions for missing or badly formatted files. 
	
	# Set up defaults for an xml_r object

	xml_r = {}
	xml_r["Testcase"] = {}
	xml_r["Testcase"]["Details"] = {}
	xml_r["Testcase"]["Details"]["Name"] = ""
	xml_r["Testcase"]["Details"]["Title"] = ""
	xml_r["Testcase"]["Details"]["Category"] = ""
	xml_r["Testcase"]["Details"]["Date"] = ""
	xml_r["Testcase"]["Details"]["Time"] = ""
	xml_r["Testcase"]["Details"]["State"] = ""
	xml_r["Testcase"]["Details"]["InputDataFile"] = ""
	xml_r["Testcase"]["Details"]["Datatype"] = ""
	xml_r["Testcase"]["Details"]["defaultOnError"] = ""
	xml_r["Testcase"]["Details"]["Logsdir"] = ""
	xml_r["Testcase"]["Details"]["Resultsdir"] = ""
	xml_r["Testcase"]["Details"]["ExpectedResults"] = ""
	xml_r["Testcase"]["Requirements"] = {} 
	xml_r["Testcase"]["Steps"] = {} 
	
	
	with open(filename) as fd1:
		xml_d = xmltodict.parse(fd1.read());

	# Map the input to the response collector
	for xstr in ["Name", "Title", "Category", "Date", "Time", "InputDataFile", "Engineer", \
		"Datatype", "default_onError", "Logsdir", "Resultsdir", "ExpectedResults"]:
		xml_r["Testcase"]["Details"][xstr] = xml_d["Testcase"]["Details"].get(xstr,"")

	caseStateOptions_str = ['New','Draft','In Review','Released']

	try:
		xml_r['Testcase']['Steps'] = copy.deepcopy(xml_d['Testcase']['Steps']);
	except:
		xml_r["Testcase"]["Steps"] = {}

	try:
		xml_r['Testcase']['Requirements'] = copy.deepcopy(xml_d['Testcase']['Requirements']);
	except:
		xml_r["Testcase"]["Requirements"] = {}

	context = { 
		'myfile': filename,
		'docSpec': 'caseSpec',
		'caseName': xml_r["Testcase"]["Details"]["Name"],
		'caseTitle': xml_r["Testcase"]["Details"]["Title"],
		'caseEngineer': xml_r["Testcase"]["Details"]["Engineer"],
		'caseCategory': xml_r["Testcase"]["Details"]["Category"],
		'caseDate': xml_r["Testcase"]["Details"]["Date"],
		'caseTime': xml_r["Testcase"]["Details"]["Time"],
		'caseState': xml_r["Testcase"]["Details"]["State"],
		'caseStateOptions': caseStateOptions_str, 
		'caseDatatype': xml_r["Testcase"]["Details"]["Datatype"],
		'caseInputDataFile': xml_r["Testcase"]["Details"]["InputDataFile"],
		'casedefault_onError': xml_r["Testcase"]["Details"]["default_onError"],
		'caseLogsdir': xml_r["Testcase"]["Details"]["Logsdir"],
		'caseResultsdir': xml_r["Testcase"]["Details"]["Resultsdir"],
		'caseExpectedResults': xml_r["Testcase"]["Details"]["ExpectedResults"],
		'caseSteps': xml_r["Testcase"]["Steps"],
		'caseRequirements': xml_r['Testcase']['Requirements'],
		'fulljson': xml_r['Testcase']
	}

	return HttpResponse(template.render(context, request))


