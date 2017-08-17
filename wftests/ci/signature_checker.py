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

"""
Use ast module to check custom rules enforced by warrior dev team
"""
import sys
import ast

def iter_func(node):
    '''
        Return all arguments and default values of the current function
        Also if it has inner functions, store it in a sub-dict
    '''
    result = {"args":[x.id for x in node.args.args], "def_value":node.args.defaults}
    # investigate everything in a function
    for child in ast.walk(node):
        if child != node and isinstance(child, ast.FunctionDef):
            # check for private method in action file
            tmp = iter_func(child)
            if "funcs" in result:
                result["funcs"].update(tmp)
            else:
                result["funcs"] = tmp
        elif child != node and isinstance(child, ast.ClassDef):
            tmp = iter_class(child)
            if "classes" in result:
                result["classes"].update(tmp)
            else:
                result["classes"] = tmp

    return {node.name:result}

def iter_class(node):
    '''
        Return all functions and sub-class functions of the current class
    '''
    result = {"funcs":{}}

    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            tmp = iter_func(child)
            result["funcs"].update(tmp)
        elif isinstance(child, ast.ClassDef):
            tmp = iter_class(child)
            result.update(tmp)

    return {node.name:result}

def main(file_name=None):
    """
        Read in filelist and build dictionary for all file and all functions inside each file
    """
    file_list = open(file_name).readlines()
    file_list = [x[:-1] if x.endswith("\n") else x for x in file_list]
    signs = {}
    for f in file_list:
        if f not in signs:
            signs[f] = {}
        root = ast.parse(open(f).read())
        for child in ast.iter_child_nodes(root):
            if isinstance(child, ast.FunctionDef):
                signs[f].update(iter_func(child))
            elif isinstance(child, ast.ClassDef):
                signs[f].update(iter_class(child))
    from pprint import pprint
    pprint(signs)
    return signs

if __name__ == "__main__":
    if main(sys.argv[1]):
        print "PASS"
        exit(0)
    else:
        print "FAIL"
        exit(1)
