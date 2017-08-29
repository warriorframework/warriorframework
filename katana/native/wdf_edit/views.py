# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, xmltodict
from xml.etree.ElementTree import Element, tostring, fromstring, parse
from pprint import pprint

from django.shortcuts import render

# Create your views here.
def index(request):
    data = xmltodict.parse(open('/home/ka/Desktop/warrior_fnc_tests/warrior_tests/data/cli_tests/cli_def_Data.xml').read())
    print(json.dumps(data, indent=4))

    return render(request, 'wdf_edit/index.html', {"data": data["credentials"]})

def on_post(request):
    print request.method
    return str(request.method) + " success"