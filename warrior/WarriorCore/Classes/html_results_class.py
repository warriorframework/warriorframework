import os
import xml.etree.ElementTree as ET
from collections import OrderedDict

import Tools
from Framework.Utils import xml_Utils, file_Utils
from Framework.Utils.testcase_Utils import pNote
from Framework.Utils.print_Utils import print_info
from Framework.Utils.xml_Utils import getElementWithTagAttribValueMatch

__author__ = 'Keenan Jabri'

class lineResult():
    data = {}
    html = ''

    def setDynamicContent( self, line ):
        self.data.dynamic = [ line.get("keywords"), line.get("passes"), line.get("failures"), line.get("errors"), line.get("exceptions"), line.get("skipped") ]
        self.data.timestamp = line.get("timestamp")

    def setAttributes( self, line, type ):
        self.data = {'nameAttr' : type + 'Record',
                     'type': type.replace( 'Test', '' ).replace( 'Keyword', 'step' ),
                     'name': line.get("name"),
                     'info': line.get("title"),
                     'timestamp': line.get("timestamp"),
                     'duration': line.get("time"),
                     'impact': line.get("impact"),
                     'onerror': line.get("onerror"),
                     'msc': '<span style="padding-left:10px; padding-right: 10px;"><a href="' + line.get("resultfile") + '"><i class="fa fa-line-chart"> </i></a></span><span style="padding-left:10px; padding-right: 10px;"><a href="' + line.get("logsdir") + '"><i class="fa fa-book"> </i></a></span>',
                     'static': [ 'Count', 'Passed', 'Failed', 'Errors', 'Exceptions', 'Skipped' ]
                    }
        self.keys = [ 'type', 'name', 'info', 'timestamp', 'duration', 'impact', 'onerror', 'msc', 'static', 'dynamic' ]

    def setHTML( self, line, type ):
        if self.html == '':
            self.setAttributes( line, type )
        self.setDynamicContent( line )

        topLevel = ''
        topLevelNext = ''
        for elem in self.keys:
            if elem == 'dynamic':
                for dynamicElem in self.data.elem:
                    topLevelNext += '<td><div>' + dynamicElem + '</div></td>'
            elif elem == 'static':
                for staticElem in self.data.elem:
                    topLevel += '<td><div>' + staticElem + '</div></td>'
            else:
                topLevel += '<td rowspan="2"><div>' + self.data.elem + '</div></td>'

        topLevelNext = '<tr>' + topLevelNext + '</tr>'
        self.html = '<tr name="' + self.data.nameAttr + '">' + topLevel + '</tr>' + topLevelNext


class WarriorHtmlResults():
    lineObjs = []
    lineCount = 0

    def __init__( self, junit_file=None ):
        self.junit_file = junit_file
        self.html_template = "{0}{1}Reporting{1}html_results_template.html" \
            .format(Tools.__path__[0], os.sep)
        self.junit_root = xml_Utils.getRoot(self.junit_file)

    def createLineResult( self, line, type ):
        self.lineCount += 1
        if self.lineCount > self.lineObjs:
            temp = lineResult()
            temp.setHTML( line, type )
            self.lineObjs.append( temp )
        else:
            self.lineObjs[ self.lineCount ].setHTML( line, type )

    def setLineObjs( self ):
        self.lineCount = 0
        project_node_list = [self.junit_root]
        for project_node in project_node_list:
            self.createLineResult( project_node, "Project" )
            for testsuite_node in project_node.findall("testsuite"):
                self.createLineResult( testsuite_node, "Testsuite"  )
                for testcase_node in testsuite_node.findall("testcase"):
                    self.createLineResult(testcase_node, "Testcase" )
                    for step_num, kw_node in enumerate(testcase_node.findall("keyword"), 1):
                        self.createLineResult( kw_node, "Keyword" )

    def getPath( self ):
        """Get the results path for the
        html results file"""
        filename = file_Utils.getNameOnly(os.path.basename( self.junit_file ))
        filename = filename.split( "_junit" )[0]
        html_filename = filename + ".html"
        if self.givenPath:
            html_results_path = self.givenPath + os.sep + html_filename
        else:
            results_dir = os.path.dirname( self.junit_file )
            html_results_path = results_dir + os.sep + html_filename

        return html_results_path

    def mergeHTML( self, dynamicHTML ):
        temp = open(self.html_template)
        templateHTML = temp.read().replace('\n', '')
        temp.close()
        return templateHTML.replace( '</table>', dynamicHTML + '</table>' )

    def generateHTML( self, junitObj, givenPath ):
        if junitObj:
            self.junit_file = junitObj
            self.junit_root = xml_Utils.getRoot(self.junit_file)
        if givenPath:
            self.givenPath = givenPath

        self.setLineObjs()
        html = ''
        for item in self.lineObjs:
            html += item.html
        html = self.mergeHTML( html )

        file = open( self.getPath(), 'w' )
        file.write( html )
        file.close()

