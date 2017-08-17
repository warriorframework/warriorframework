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
import ast

def iter_func(node):
    '''
        Return all arguments and default values of the current function
        Also if it has inner functions, store it in a sub-dict
    '''
    status = True

    # investigate everything in a function
    # print node.name
    # print [x.id for x in node.args.args]
    # print node.args.defaults, "\n"
    for index, child in enumerate(ast.walk(node)):
        if child != node and isinstance(child, ast.FunctionDef):
            # check for private method in action file
            if kw and child.name.startswith("_"):
                print node.name, child.name, "should move to utils"
                status = False
            tmp_status = func_check(child, kw)
            status &= tmp_status
        elif child != node and isinstance(child, ast.ClassDef):
            tmp_status = class_check(child, kw)
            status &= tmp_status

    return status

def iter_class(node):
    '''
        Return all functions and sub-class functions of the current class
    '''
    status = True

    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            if kw and child.name.startswith("_") and child.name != "__init__":
                print node.name, child.name, "should move to utils"
                status = False
            tmp_status = iter_func(child)
            status &= tmp_status
        elif isinstance(child, ast.ClassDef):
            tmp_status = iter_class(child)
            status &= tmp_status

    return status

def main(file_name=None):
    """
        Read in filelist and build dictionary for all file and all functions inside each file
    """
    file_list = open(file_name).readlines()
    signs = {}
    for f in file_list:
        if f not in signs:
            signs[f] = {}
        root = ast.parse(f.read())
        for child in ast.iter_child_nodes(root):
            if isinstance(child, ast.FunctionDef):
                signs[f].update(iter_func(child))
            elif isinstance(child, ast.ClassDef):
                signs[f].update(iter_class(child))
    return signs

if __name__ == "__main__":
    if main():
        print "PASS"
        exit(0)
    else:
        print "FAIL"
        exit(1)
