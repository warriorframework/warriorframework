'''
Copyright 2017, Fujitsu Network Communications, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import time
from WarriorCore.Classes import war_print_class 

console_logfile = None
junit_resultfile = None
resultfile = None
datafile= None
logsdir = None
filename = None
data_repository = None
logfile = None
par_data_repository={}
redirect_print = war_print_class.RedirectPrint(console_logfile)
tc_path = None

def debug_file(console_filepath):
    global console_logfile

    try:
        console_logfile = open(console_filepath, 'a')
        redirect_print.get_file(console_logfile)
    except Exception,e:
        print "unexpected error %s" % str(e)
        console_logfile = None

def junit_file(junit_filepath):
    global junit_resultfile
    junit_resultfile = junit_filepath
    
def set_resultfile(filepath):
    global resultfile
    resultfile = filepath
    
def set_datafile(filepath):
    global datafile
    datafile = filepath

def set_logsdir(filepath):
    global logsdir
    logsdir = filepath

def set_logfile(filepath):
    global logfile
    logfile = filepath

def set_filename(name):
    global filename
    filename = name
    
    
def set_datarepository(repository):
    global data_repository
    data_repository = repository


def set_data_repository_for_parallel(repository):
    global par_data_repository
    par_data_repository.update(repository)
    print par_data_repository

def set_testcase_path(testcase_file_path):
    global tc_path
    tc_path = testcase_file_path
