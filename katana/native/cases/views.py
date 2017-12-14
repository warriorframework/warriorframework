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

from django.shortcuts import redirect
import copy
from django.http import HttpResponse, JsonResponse
from django.template import loader
import xmltodict
from utils.directory_traversal_utils import join_path
from utils.navigator_util import Navigator
from katana_utils import *
import scanfiles

navigator = Navigator()
CONFIG_FILE = join_path(navigator.get_katana_dir(), "config.json")
All_case_action_details = py_file_details(json.loads(open(CONFIG_FILE).read())['pythonsrcdir'])
EMPTY_DATA = json.loads(
    json.dumps(xmltodict.parse(open("./native/cases/static/empty.xml").read(), process_namespaces=True)))
caseStateOptions_str = ['New', 'Draft', 'In Review', 'Released', 'Add Another']


def index(request):
    path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"
    x = json.loads(open(path_to_config_file).read())
    path_to_testcases = x['xmldir']
    template = loader.get_template("listAllCases.html")
    fpath = path_to_testcases

    jtree = navigator.get_dir_tree_json(fpath)
    jtree['state'] = {'opened': True}

    context = {
        'title': 'List of Cases',
        'dirpath': path_to_testcases,
        'treejs': jtree,
    }
    return HttpResponse(template.render(context, request))


def getCaseListTree(request):
    path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"
    x = json.loads(open(path_to_config_file).read())
    path_to_testcases = x['xmldir']
    fpath = path_to_testcases
    jtree = navigator.get_dir_tree_json(fpath)
    jtree['state'] = {'opened': True}
    return JsonResponse({'treejs': jtree})


def getSystemNames(request):
    filename = request.GET.get('filename')
    names = []
    try:
        xlines = open(filename).read()
        df = xmltodict.parse(xlines, dict_constructor=dict)
        for ms in df['credentials']['system']:
            if ms.has_key('subsystem'):
                for subsys in ms['subsystem']:
                    names.append(ms['@name'] + "[" + subsys['@name'] + "]")
            else:
                names.append(ms['@name'])
    except:
        print "Unable to get names "
    return JsonResponse({'system_names': names, 'filename': filename})


def addCaseStateOption(request):
    option = request.GET.get('option')
    try:
        x = caseStateOptions_str.index(option)
    except:
        print "Not found"
        caseStateOptions_str.append(option)
        print caseStateOptions_str
    return JsonResponse({'case_state_options': caseStateOptions_str})


def getListOfActions(request):
    """
    Returns a list of all the actions and their details using config.json.
    """
    path_to_pythonsrc = json.loads(open(CONFIG_FILE).read())['pythonsrcdir']
    jsr = scanfiles.fetch_action_file_names(path_to_pythonsrc, 'driver', 'all')
    actions = [os.path.basename(fn)[:-3] for fn in jsr['ProductDrivers']]
    # actions.insert(0,"To_Be_Developed")
    return JsonResponse({'actions': actions, 'filesinfo': All_case_action_details})


def getListOfKeywords(request):
    if 0:
        CONFIG_FILE = navigator.get_katana_dir() + os.sep + "config.json"
        x = json.loads(open(CONFIG_FILE).read())
        path_to_pythonsrc = x['pythonsrcdir']
        details = py_file_details(path_to_pythonsrc)
    else:
        details = All_case_action_details

    responseBack = {'keywords': []}
    driver = request.GET.get('driver')

    try:
        for item in details[driver][0]:
            fn = item['fn']
            if fn.find('.py') > 0: continue;
            if fn.find('ctions') > 0: continue;
            if fn.find('_init_') > 0: continue;
            responseBack['keywords'].append(item['fn'])
    except:
        print "Unable to find driver..."
    return JsonResponse(responseBack)


def getListOfComments(request):
    """
    Return information about the driver and keyword in the incoming POST request.
    """
    if 0:
        CONFIG_FILE = navigator.get_katana_dir() + os.sep + "config.json"
        x = json.loads(open(CONFIG_FILE).read())
        path_to_pythonsrc = x['pythonsrcdir']
        details = py_file_details(path_to_pythonsrc)
    else:
        details = All_case_action_details

    driver = request.GET.get('driver')
    keyword = request.GET.get('keyword')
    responseBack = {'fields': []}

    if driver == "":
        return JsonResponse(responseBack)

    try:
        items = details[driver]
    except:
        return JsonResponse(responseBack)
    try:
        for item in details[driver][0]:
            if item['fn'] == keyword:
                responseBack['fields'].append(item)
                break
    except:
        print details[driver]
    return JsonResponse(responseBack)


def editCase(request):
    """
    Set up JSON object for editing a suites file.
    """
    path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"
    x = json.loads(open(path_to_config_file).read())
    path_to_testcases = x['xmldir']
    template = loader.get_template("editCase.html")
    filename = request.GET.get('fname')

    # Open the XML file and get it's dictionary...
    # Make exceptions for missing or badly formatted files.

    # Set up defaults for an xml_r object

    if filename.find("..") == 0:
        f = filename.find('testcases')
        if f > -1:
            filename = os.path.dirname(path_to_testcases) + os.sep + filename[f:]
        else:
            filename = path_to_testcases + os.sep + filename

    xml_r = {"Testcase": {}}
    xml_r["Testcase"]["Details"] = {}
    xml_r["Testcase"]["Details"]["Name"] = ""
    xml_r["Testcase"]["Details"]["Title"] = ""
    xml_r["Testcase"]["Details"]["Category"] = ""
    xml_r["Testcase"]["Details"]["Engineer"] = ""
    xml_r["Testcase"]["Details"]["Date"] = ""
    xml_r["Testcase"]["Details"]["Time"] = ""
    xml_r["Testcase"]["Details"]["State"] = ""
    xml_r["Testcase"]["Details"]["InputDataFile"] = ""
    xml_r["Testcase"]["Details"]["Datatype"] = ""
    xml_r["Testcase"]["Details"]["default_onError"] = ""
    xml_r["Testcase"]["Details"]["Logsdir"] = ""
    xml_r["Testcase"]["Details"]["Resultsdir"] = ""
    xml_r["Testcase"]["Details"]["ExpectedResults"] = ""
    xml_r["Testcase"]["Requirements"] = {}
    xml_r["Testcase"]["Steps"] = {}

    # edata = getEmpty()

    if filename == 'NEW':
        subdir = path_to_testcases
        filename = 'new.xml'
        fn = 'new.xml'
        xml_d = copy.deepcopy(xml_r)
    else:
        xlines = open(filename).read()
        xml_d = xmltodict.parse(xlines, dict_constructor=dict);
        subdir = os.path.split(filename)[0]
        fn = os.path.split(filename)[1]

    if (not xml_d.has_key('Testcase')):
        subdir = path_to_testcases
        filename = 'new.xml'
        fn = 'new.xml'
        print "Invalid XML file"
        xml_d = copy.deepcopy(xml_r)

    emptyCaseString = str(json.loads(json.dumps(EMPTY_DATA['Testcase'])));
    emptyCaseString = emptyCaseString.replace('u"', "'").replace("u'", '"').replace("'", '"')
    emptyCaseString = emptyCaseString.replace('None', '""').replace('""""', '""')

    # Map the input to the response collector
    for xstr in ["Name", "Title", "Category", "Date", "Time", "InputDataFile", "Engineer",
                 "Datatype", "default_onError", "Logsdir", "Resultsdir", "ExpectedResults"]:
        try:
            if not xml_r["Testcase"]["Details"].has_key(xstr):
                xml_r["Testcase"]["Details"][xstr] = ""
            xml_r["Testcase"]["Details"][xstr] = copy.copy(
                xml_d["Testcase"]["Details"].get(xstr, ""))
        except:
            pass

    # caseStateOptions_str = ['New','Draft','In Review','Released', 'Add Another']

    try:
        xml_r['Testcase']['Steps'] = copy.deepcopy(xml_d['Testcase']['Steps'])
    except:
        xml_r["Testcase"]["Steps"] = {}

    try:
        xml_r['Testcase']['Requirements'] = copy.deepcopy(xml_d['Testcase']['Requirements'])
    except:
        xml_r["Testcase"]["Requirements"] = {}

    fulljsonstring = str(json.loads(json.dumps(xml_d['Testcase'])))
    fulljsonstring = fulljsonstring.replace('u"', "'").replace("u'", '"').replace("'", '"')
    fulljsonstring = fulljsonstring.replace('None', '""').replace('""""', '""')
    context = {
        'fullpathname': filename,
        'savefilename': fn,
        'savesubdir': subdir,
        'savefilepath': path_to_testcases,
        'fulljsonstring': fulljsonstring,
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
        'emptyTestCase': emptyCaseString,
        'fulljson': xml_r['Testcase']
    }

    return HttpResponse(template.render(context, request))


def getJSONcaseDataBack(request):
    path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"
    x = json.loads(open(path_to_config_file).read())
    filename = request.GET.get('fname')
    try:
        xml_d = xmltodict.parse(open(filename).read())
    except:
        xml_d = EMPTY_DATA

    j_data = json.loads(json.dumps(xml_d))
    responseBack = {'fulljson': j_data, 'fname': filename}
    return JsonResponse(responseBack)


def getCaseDataBack(request):
    """
    Return edited case data back as JSON and a file name to write to.
    Use the config.json file to get the path to the testcases directory and
    the savesubdir parameter to save to the (sub)directory under the main
    directory.
    """
    path_to_config_file = navigator.get_katana_dir() + os.sep + "config.json"
    x = json.loads(open(path_to_config_file).read())
    ijs = request.POST.get(u'json')
    fn = request.POST.get(u'filetosave')
    sb = request.POST.get(u'savesubdir')
    fname = sb + os.sep + fn
    if fname.find(".xml") < 2: fname = fname + ".xml"



    xml = xmltodict.unparse(json.loads(ijs), pretty=True)
    fd = open(fname, 'w')
    fd.write(xml)
    fd.close()

    return redirect(request.META['HTTP_REFERER'])
