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


"""Module that handles the actions to be performed for 
conditional execution of a step in Testcase/Suite/Project """

import sys
from Framework.Utils.data_Utils import get_object_from_datarepository
from Framework.Utils.print_Utils import print_error, print_info
from Classes.argument_datatype_class import ArgumentDatatype

def main(exectype_elem_node):
    exec_node = exectype_elem_node.find('Execute')
    if exec_node is None or exec_node is False:
        return True, None

    exec_params = exec_node.attrib 
    exec_type = exec_params['ExecType']
    
    try:
        if exec_type.upper() == 'IF' or exec_type.upper() == 'IF NOT':
            exec_rule_param = exec_node.find('Rule').attrib
            exec_condition = exec_rule_param['Condition']
            exec_cond_var = exec_rule_param['Condvalue']
            arg_datatype_object = ArgumentDatatype(exec_condition, exec_cond_var)
            exec_cond_var = arg_datatype_object.convert_arg_to_datatype()
            if exec_rule_param['Else'].upper() == 'GOTO':
                exec_next = exec_rule_param['Elsevalue']
            supported_prefix = ["bool_", "str_", "int_", "float_", "list_", "tuple_", "dict_"]
            if any([exec_condition.startswith(i) for i in supported_prefix]):
                exec_condition = exec_condition[exec_condition.find('_')+1:]
                
    except KeyError, err:
        print_error ("Incorrect condition key used: {0}".format(err.message))

    
    #Decide the execution type      
    if exec_type.upper() == 'NO':
        return 'SKIP', 'SKIP'

    elif exec_type.upper() == 'YES':
        return True, None
        
    elif exec_type.upper() == 'IF':
        if get_object_from_datarepository(exec_condition) == exec_cond_var:
            return True, None
        else:
            if type(get_object_from_datarepository(exec_condition)) != type(exec_cond_var):
                print_error("Comparing different type of value, please check the conditional value type")
            return False, 'SKIP'
        
    elif exec_type.upper() == 'IF NOT':
        if get_object_from_datarepository(exec_condition) == exec_cond_var:
            return False, 'SKIP'
        else:
            if type(get_object_from_datarepository(exec_condition)) != type(exec_cond_var):
                print_error("Comparing different type of value, please check the conditional value type")
            return True, None
    
    else:
        supported_values = ['no', 'yes', 'if', 'ifnot']
        print_error("Unsupported value used for ExecType, supported values are: {0} and case-insensitive".format(supported_values))
        return 'SKIP', 'SKIP'
    
