# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
	

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.template import loader
from xml.sax.saxutils import escape, unescape
import xml.dom.minidom 

path_to_demo="/home/khusain/Projects/xml-edit/warriorframework/katana/vdj/cases/"

def index(request):
   #return HttpResponse("Hello, world. You're at the polls index.")
   	template = loader.get_template("cases/index.html")
	context = { 
		'myfile': 'tp.xml',
		'docSpec': 'projectSpec'
		
	}
	return HttpResponse(template.render(context, request))


def getJSONfile(request):
	filename = request.GET.get('fname')
	print "---------------filename ", filename
	return JsonResponse( open(path_to_demo+filename).read(), content_type='application/xml', safe=False)


def getXMLfile(request):
	filename = request.GET.get('fname')
	print "---------------filename ", filename
	return HttpResponse( open(path_to_demo+filename).read(), content_type='text/xml')

def editProject(request):
	template = loader.get_template("cases/editProject.html")
	context = { 
		'myfile': 'tp.xml',
		'docSpec': 'projectSpec'
		
	}
	return HttpResponse(template.render(context, request))

def editSuite(request):
	template = loader.get_template("cases/editProject.html")
	context = { 
		'myfile': 'ts.xml',
		'docSpec': 'suiteSpec'
	}
	return HttpResponse(template.render(context, request))

def editCase(request):
	template = loader.get_template("cases/editProject.html")
	context = { 
		'myfile': 'tc.xml',
		'docSpec': 'caseSpec'
	}
	return HttpResponse(template.render(context, request))


