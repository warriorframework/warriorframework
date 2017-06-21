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
from Framework.Utils.testcase_Utils import pNote

def math_decision(exec_condition, exec_cond_var, operator):
    """
        Handle the math operator decision
        :param:
            exec_condition: value from data_repo to be compared
            exec_cond_var: user provided value to be compared
            operator: math operator in plain English
        :return:
            True if operator condition match 
            for repo value on left and user value on right
            Else False
    """
    operator = operator.lower()
    if operator == "greater_equal":
        return True if get_object_from_datarepository(exec_condition) >= exec_cond_var else False
    elif operator == "greater":
        return True if get_object_from_datarepository(exec_condition) > exec_cond_var else False
    elif operator == "smaller_equal":
        return True if get_object_from_datarepository(exec_condition) <= exec_cond_var else False
    elif operator == "smaller":
        return True if get_object_from_datarepository(exec_condition) < exec_cond_var else False

    pNote("Unknown error occur when deciding value, please check condition value of the step", "Error")
    return False

def logical_decision(exec_type, exec_condition, exec_cond_var, operator):
    """
        Handle the logical decision for the value comparison
        :param:
            exec_type: If or If Not (== or !=)
            exec_condition: value from data_repo to be compared
            exec_cond_var: user provided value to be compared
            operator: math operator in plain English
        :return:
            True if condition match, else return False
    """
    status = None
    if type(get_object_from_datarepository(exec_condition)) != type(exec_cond_var):
        print_error("Comparing different type of value, please check the conditional value type")
        status = False

    if status is None and operator is not None:
        result = math_decision(exec_condition, exec_cond_var, operator)
        status = result if exec_type.upper() == 'IF' else not result

    if status is None and exec_type.upper() == 'IF':
        status = True if get_object_from_datarepository(exec_condition) == exec_cond_var else False
        
    elif status is None and exec_type.upper() == 'IF NOT':
        status = False if get_object_from_datarepository(exec_condition) == exec_cond_var else True
    
    elif status is None:
        supported_values = ['no', 'yes', 'if', 'if not']
        print_error("Unsupported value used for ExecType, supported values are: {0} and case-insensitive".format(supported_values))
        status = False

    if not status:
        pNote("Execution condition failed for exec type: {}, "\
            "expected value: {} , condition: {}, actual value: {}"\
            .format(exec_type, exec_cond_var, operator, 
                get_object_from_datarepository(exec_condition)), "WARNING")
    return status if status is not None else False

def main(step):
    """
        Entry function for execute nodes in a step
        Handle checking and call the logical decision functions
        combine the final result and return
        :param:
            step: the step Element
        :return:
            decision: Whether the step should be executed or not
            trigger_action: When decision failed, what kind of action to perform
    """
    exec_nodes = step.findall("Execute")
    if exec_nodes == []:
        return True, None
    if len(exec_nodes) > 1:
        exec_types = [node.get("ExecType").upper() for node in exec_nodes if node.get("ExecType") is not None]

        if "YES" in exec_types and "NO" in exec_types:
            pNote("Multiple conflicted ExecType conditions found, please check xml", "WARNING")
            pNote("Cannot have YES and NO statement together", "WARNING")
            pNote("Proceed with using the 1st ExecType condition", "WARNING")
            exec_nodes = [exec_nodes[0]]
        if any(["IF" in exec_types or "IF NOT" in exec_types]) and any(["YES" in exec_types or "NO" in exec_types]):
            pNote("Multiple conflicted ExecType conditions found, please check xml", "WARNING")
            pNote("Cannot have YES/NO with any IF statement", "WARNING")
            pNote("Proceed with using the 1st ExecType condition", "WARNING")
            exec_nodes = [exec_nodes[0]]
        if len(exec_types) != len(set(exec_types)):
            pNote("Multiple same ExecType conditions found", "WARNING")
            pNote("Proceed with using the 1st ExecType condition", "WARNING")
            exec_nodes = [exec_nodes[0]]

    decision = True
    trigger_action = None
    for exec_node in exec_nodes:
        exec_type = exec_node.get("ExecType", "")
        if exec_type.upper() == 'IF' or exec_type.upper() == 'IF NOT':
            rules = exec_node.findall("Rule")
            # Sanity check for multiple else
            if len([True for rule in rules if rule.get("Else", None) is not None]) > 1:
                pNote("Multiple else statement find in rules", "WARNING")
                pNote("Proceed with using the 1st else statement", "WARNING")

            else_node = exec_node.find("./Rule[@Else]") if exec_node.find("./Rule[@Else]") is not None else {}
            else_action = else_node.get("Else", None)
            if else_action is not None and else_action.upper() == "GOTO":
                else_action = else_node.get("Elsevalue")

            for rule in rules:
                exec_condition = rule.get("Condition", None)
                exec_cond_var = rule.get("Condvalue", None)

                # Check for math operator
                support_operators = ["greater_equal", "greater", "smaller_equal", "smaller"]
                operator = rule.get("Operator", None)
                if operator is not None and operator.lower() not in support_operators:
                    pNote("Invaid Operator value, please use the following: {}".format(support_operators))
                    operator = None

                arg_datatype_object = ArgumentDatatype(exec_condition, exec_cond_var)
                exec_cond_var = arg_datatype_object.convert_arg_to_datatype()

                supported_prefix = ["bool_", "str_", "int_", "float_", "list_", "tuple_", "dict_"]
                if any([exec_condition.startswith(i) for i in supported_prefix]):
                    exec_condition = exec_condition[exec_condition.find('_')+1:]

                decision = decision and logical_decision(exec_type, exec_condition, exec_cond_var, operator)

            if not decision:
                trigger_action = else_action if else_action is not None else "SKIP"
                pNote("Failed action: {}".format(trigger_action))
                break
        elif exec_type.upper() == 'NO':
            decision = False
            trigger_action = "SKIP"
            break
        elif exec_type.upper() != 'YES':
            decision = False
            supported_values = ['no', 'yes', 'if', 'if not']
            print_error("Unsupported value used for ExecType, supported values are: {0} and case-insensitive".format(supported_values))
            break

    return decision, trigger_action
