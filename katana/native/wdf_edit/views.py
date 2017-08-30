# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, xmltodict
from HTMLParser import HTMLParser
from xml.etree.ElementTree import parse
from pprint import pprint

from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def index(request):
    data = xmltodict.parse(open('/home/ka/Desktop/warrior_fnc_tests/warrior_tests/data/cli_tests/cli_def_Data.xml').read())
    for sys in data["credentials"]["system"]:
        sys["name"] = sys["@name"]
        del sys["@name"]
        if "subsystem" in sys:
            if type(sys["subsystem"]) == list:
                for subsys in sys["subsystem"]:
                    for k, v in subsys.items():
                        if k.startswith("@"):
                            subsys[k[1:]] = v
                            del subsys[k]
                        elif k == "#text":
                            del subsys[k]
            else:
                subsys = sys["subsystem"]
                for k, v in subsys.items():
                    if k.startswith("@"):
                        subsys[k[1:]] = v
                        del subsys[k]
                    elif k == "#text":
                        del subsys[k]
        else:
            for k, v in sys.items():
                if k.startswith("@"):
                    sys[k[1:]] = v
                    del sys[k]
                elif k == "#text":
                    del sys[k]
    # print(json.dumps(data, indent=4))

    return render(request, 'wdf_edit/index.html', {"data": data["credentials"]})

def get_json(request):
    return JsonResponse(xmltodict.parse(open('/home/ka/Desktop/warrior_fnc_tests/warrior_tests/data/cli_tests/cli_def_Data.xml').read()))

def raw_parser(data):
    result = {}
    for k, v in data.items():
        parts = k.split(".")
        if parts[0] not in result:
            result[parts[0]] = {}
        cur = result[parts[0]]
        for part in parts[1:-1]:
            if part not in cur:
                cur[part] = {}
            cur = cur[part]
        cur.update({parts[-1]:v})
    # print json.dumps(result, indent=4)
    return result


def on_post(request):
    data = request.POST
    # print json.dumps(data, indent=4)
    data = raw_parser(data)
    print xmltodict.unparse({"systems":data})
    return render(request, 'wdf_edit/result.html', {"data": json.dumps(request.POST, indent=4)})