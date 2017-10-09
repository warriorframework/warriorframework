# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, "black_duck/index.html")

def settings(request):
    # Setup pyjnius and load Protex SDK
    import os, jnius_config, json
    setting = json.load(open("/home/ka/Desktop/pyjnius/settings.json"))
    os.environ["CLASSPATH"] = setting["SDK-path"]
    from jnius import autoclass

    # json is unicode
    url = str(setting["server-url"])
    user = str(setting["username"])
    pwd = str(setting["password"])
    timeout = int(setting["timeout"])

    PSP = autoclass("com.blackducksoftware.sdk.protex.client.util.ProtexServerProxy")
    PR = autoclass("com.blackducksoftware.sdk.protex.project.ProjectRequest")

    protex_server = PSP(url, user, pwd, timeout)
    api = protex_server.getProjectApi()
    projects = api.getProjectsByUser(user)
    pj_info = projects.get(0)
    pj = api.getProjectById(pj_info.getProjectId())
    source_loc = pj.getAnalysisSourceLocation()

    return render(request, "black_duck/settings.html", {"project_id": pj_info.getProjectId(), "hostname": source_loc.getHostname()})
