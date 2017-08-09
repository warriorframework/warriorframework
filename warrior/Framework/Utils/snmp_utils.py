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
from pysnmp.smi import builder, view, compiler, rfc1902, error
from Framework.Utils import testcase_Utils

def split_mib_path(custom_mib_paths):
    """
    Split comma separated mib paths and add @mib@ at the end of the path if required.
    Argument:
    custom_mib_paths: comma separated mib paths as a string
    Return: Updated custom_mib_paths as a list
    """
    __custom_mib_paths = []
    custom_mib_paths = custom_mib_paths.split(',')
    for paths in custom_mib_paths:
        if 'http' in paths and '@mib@' not in paths:
            if paths[-1] == '/':
                paths = paths+'/@mib@'
            else:
                paths = paths+'@mib@'
        if 'http' in paths and 'browse' in paths:
            paths = paths.replace('browse', 'raw')
        __custom_mib_paths.append(paths)
    __custom_mib_paths.append('/usr/share/snmp/mibs')
    return __custom_mib_paths

def translate_mib(custom_mib_paths, load_mib_modules, name, val):
    """
    Translate OID to MIB
    custom_mib_paths: comma separated mib paths as a string
    load_mib_modules: MIB Module to load e.g. "MIB-FILE-1,MIB-FILE-2"
    Return: Translated OID string and value
    """
    if custom_mib_paths and load_mib_modules:
        try:
            mibBuilder = builder.MibBuilder()
            compiler.addMibCompiler(mibBuilder, sources=custom_mib_paths)
            mibViewController = view.MibViewController(mibBuilder)
            __load_mib_modules = load_mib_modules.split(',')
            mibBuilder.loadModules(*__load_mib_modules)
        except error.MibNotFoundError as excep:
            testcase_Utils.pNote(" {} Mib Not Found!".format(excep), "Error")
    if custom_mib_paths and load_mib_modules:
        __type = val.__class__.__name__
        output = rfc1902.ObjectType(rfc1902.ObjectIdentity(name), val).resolveWithMib(mibViewController).prettyPrint()
        op_list = output.split(" = ")
        name = op_list[0].strip()
        __val = op_list[1].strip()
        if __type == "Integer":
            testcase_Utils.pNote('%s = %s(%s): %s' %
                         (name, __type,val.prettyPrint(),
                          __val))
        else:
            if __val == '': #For empty String
                testcase_Utils.pNote('%s = %s: ""' %
                         (name, __type))
            else:
                testcase_Utils.pNote('%s = %s: %s' %
                         (name, __type, __val))            
        return name, __val
    else:
        testcase_Utils.pNote('%s = %s: %s' %
                         (name.prettyPrint(), __type,
                          val.prettyPrint()))
        return name.prettyPrint(), val.prettyPrint()