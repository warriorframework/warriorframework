# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
	

# Create your views here.
import os, glob
from django.http import HttpResponse, JsonResponse
from django.template import loader
from xml.sax.saxutils import escape, unescape
import xml.dom.minidom 

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
	template = loader.get_template("cases/editProject.html")
	filename = request.GET.get('fname')
	context = { 
		'myfile': filename,
		'docSpec': 'projectSpec'
		
	}
	print "EDIT PROJECT ", template.render(context,request)
	
	return HttpResponse(template.render(context, request))

def editSuite(request):
	template = loader.get_template("cases/editProject.html")
	filename = request.GET.get('fname')
	context = { 
		'myfile': filename,
		'docSpec': 'suiteSpec'
	}
	return HttpResponse(template.render(context, request))

def editCase(request):
	template = loader.get_template("cases/editProject.html")
	filename = request.GET.get('fname')
	
	context = { 
		'myfile': filename,
		'docSpec': 'caseSpec'
	}
	return HttpResponse(template.render(context, request))


