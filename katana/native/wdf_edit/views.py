# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, xmltodict
from HTMLParser import HTMLParser
from xml.etree.ElementTree import parse
from pprint import pprint
from utils.navigator_util import Navigator
from collections import OrderedDict

from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def index(request):
    if request.method == "POST":
        data = request.POST
        data = xmltodict.parse(open(data["path"]).read())
    else:
        data = xmltodict.parse(open('/home/ka/Desktop/warrior_fnc_tests/warrior_tests/data/cli_tests/cli_def_Data.xml').read())

    root = data.keys()[0]

    if type(data[root]["system"]) != list:
        data[root]["system"] = [data[root]["system"]]
    for sys in data[root]["system"]:
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

# def get_json(request):
#     return JsonResponse(xmltodict.parse(open('/home/ka/Desktop/warrior_fnc_tests/warrior_tests/data/cli_tests/cli_def_Data.xml').read()))

def get_jstree_dir(request):
    data = Navigator().get_dir_tree_json("/home/ka/Desktop/warrior_fnc_tests/warrior_tests/data/")
    data["text"] = "/home/ka/Desktop/warrior_fnc_tests/warrior_tests/data/"
    # print json.dumps(data, indent=4)
    return JsonResponse(data)

def file_list(request):
    return render(request, 'wdf_edit/file_list.html', {})

def raw_parser(data):
    result = {}
    # for k, v in data.items():
    #     parts = k.split(".")
    #     if parts[0] not in result:
    #         result[parts[0]] = {}
    #     cur = result[parts[0]]
    #     for part in parts[1:-1]:
    #         if part not in cur:
    #             cur[part] = {}
    #         cur = cur[part]
    #     cur.update({parts[-1]:v})
    system_keys = [x for x in data.keys() if x.endswith("-system_name")]
    for name in system_keys:
        # Prepare all system to save data
        sys_name = name.replace("-system_name", "").split("-")[0]
        subsys_name = name.replace("-system_name", "").split("-")[1]
        if sys_name in result:
            result[sys_name][subsys_name] = {"system_name":data[name]}
        else:
            result[sys_name] = {subsys_name: {"system_name":data[name]}}
        current_sys = result[sys_name][subsys_name]
        if sys_name+"-"+subsys_name+"-subsystem_name" in data:
            current_sys.update({"subsystem_name":data[sys_name+"-"+subsys_name+"-subsystem_name"]})

        tags_keys = [x for x in data.keys() if x.startswith(sys_name + "-" + subsys_name + "-") and x.endswith("key")]
        # Parse data
        for k in tags_keys:
            parsed_k = k.split("-")
            sys_name, subsys_name, tag_ind, child_tag_ind = parsed_k[:4]

            if tag_ind in current_sys:
                current_sys[tag_ind][child_tag_ind] = (data[k], data[k[:-4]+"-value"])
            else:
                current_sys[tag_ind] = {child_tag_ind: (data[k], data[k[:-4]+"-value"])}

    print json.dumps(result, indent=4)
    return result

def locate_system(data, name):
    for ind, sys in enumerate(data):
        if sys["@name"] == name:
            return ind
    return -1

def build_xml_dict(data):
    result = []
    sys_keys = [str(y) for y in sorted([int(x) for x in data.keys()])]
    for sys_key in sys_keys:
        sys = data[sys_key]
        subsys_keys = [str(y) for y in sorted([int(x) for x in sys.keys()])]
        for subsys_key in subsys_keys:
            subsys = sys[subsys_key]
            if "subsystem_name" not in subsys:
                result.append(OrderedDict())
                current_sys = result[-1]
                current_sys["@name"] = subsys["system_name"]
            else:
                if locate_system(result, subsys["system_name"]) > -1:
                    # The system already exist in result
                    result[locate_system(result, subsys["system_name"])]["subsystem"].append(OrderedDict())
                    current_sys = result[locate_system(result, subsys["system_name"])]["subsystem"][-1]
                    current_sys["@name"] = subsys["subsystem_name"]
                    current_sys["subsystem"] = []
                else:
                    # The system doesn't exist in result
                    result.append(OrderedDict({"@name": subsys["system_name"], "subsystem":[]}))
                    result[-1]["subsystem"].append(OrderedDict())
                    current_sys = result[-1]["subsystem"][-1]
                    current_sys["@name"] = subsys["subsystem_name"]

            tag_keys = [str(y) for y in sorted([int(x) for x in subsys.keys() if x.isdigit()])]
            for tag_key in tag_keys:
                if len(subsys[tag_key]) == 1:
                    # no child tag
                    current_sys[subsys[tag_key]["1"][0]] = subsys[tag_key]["1"][1]

    print json.dumps(result, indent=4)
    return result

def on_post(request):
    data = request.POST
    # print json.dumps(sorted(data.items()), indent=4)
    data = raw_parser(data)
    data = build_xml_dict(data)
    data = {"credentials":{"system":data}}

    from xml.dom.minidom import parseString as miniparse
    print miniparse(xmltodict.unparse(data)).toprettyxml()
    # return render(request, 'wdf_edit/result.html', {"data": json.dumps(request.POST, indent=4)})
    return render(request, 'wdf_edit/file_list.html', {})