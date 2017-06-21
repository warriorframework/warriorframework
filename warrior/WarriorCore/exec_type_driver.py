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

def logical_decision(exec_type, exec_condition, exec_cond_var, operator="equal"):
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
    status = True
    result = None
    if type(get_object_from_datarepository(exec_condition)) != type(exec_cond_var):
        pNote("Comparing different type of value, please check the conditional value type", "ERROR")
        status = False
    elif operator in ["greater_equal", "greater", "smaller_equal", "smaller"] and\
         not isinstance(exec_condition, int) and not isinstance(exec_condition, float):
        pNote("Comparing non-numerical value using numerical operator, please check value and operator type", "ERROR")
        status = False

    if status and operator == "equal":
        result = True if get_object_from_datarepository(exec_condition) == exec_cond_var else False
    elif status and operator == "not_equal":
        result = True if get_object_from_datarepository(exec_condition) != exec_cond_var else False
    elif status and operator in ["greater_equal", "greater", "smaller_equal", "smaller"]:
        result = math_decision(exec_condition, exec_cond_var, operator)
    else:
        pNote("Execution condition failed for exec type: {}, "\
              "expected value: {} , condition: {}, actual value: {}"\
              .format(exec_type, exec_cond_var, operator,
                      get_object_from_datarepository(exec_condition)), "WARNING")

    return result

# Expression parsing and handling
    # parse (),each parenthesis becomes a new layer of conditions
    # priority will base on order or )
    # for each layer, do split and get list of rules num and logical operator
        # get value of each rule
        # use logical operator to combine each value
        # return result
# Else statement builder
    # Once else is triggered, build the return status and action
# AND/OR logic handling

def rule_parser(rule):
    # Get data
    exec_condition = rule.get("Condition", None)
    exec_cond_var = rule.get("Condvalue", None)
    else_action = rule.get("Else", None)
    if else_action is not None and else_action.upper() == "GOTO":
        else_action = rule.get("Elsevalue")

    # Check for math operator
    support_operators = ["greater_equal", "greater", "smaller_equal", "smaller", "equal", "not_equal"]
    operator = rule.get("Operator", None)
    if operator is not None and operator.lower() not in support_operators:
        pNote("Invaid Operator value, please use the following: {}".format(support_operators))
        operator = None

    # Check for value prefix
    supported_prefix = ["bool_", "str_", "int_", "float_", "list_", "tuple_", "dict_"]
    if any([exec_condition.startswith(i) for i in supported_prefix]):
        exec_condition = exec_condition[exec_condition.find('_')+1:]

    arg_datatype_object = ArgumentDatatype(exec_condition, exec_cond_var)
    exec_cond_var = arg_datatype_object.convert_arg_to_datatype()

    status = logical_decision(exec_type, exec_condition, exec_cond_var, operator)

def simple_expression_parser(expression_str):
    elements = expression_str.split()
    if len(elements) == 0:
        # illegal expression
        raise Exception("element ")
    elif len(elements) == 1:
        return rule_parser(elements[0])
    else:
        status = rule_parser(elements[0])
        for x in range(1, len(elements) - 2):
            if elements[x+1].lower() == "and" or elements[x+1] == "&":
                status = status & rule_parser(elements[x+2])
            elif elements[x+1].lower() == "or" or elements[x+1] == "|":
                status = status | rule_parser(elements[x+2])
            else:
                # invalid operator
                raise Exception

def expression_parser(expression_str):
    return True

def decision_maker(exec_node):
    decision = True
    exec_type = exec_node.get("ExecType", "")
    expression = exec_node.get("Expression", "")
    rules = exec_node.findall("Rule")
    # Sanity check for multiple else

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
    exec_node = step.find("Execute")
    if exec_node == []:
        return False, None

    decision = True
    trigger_action = None
    exec_type = exec_node.get("ExecType", "")
    if exec_type.upper() == 'IF' or exec_type.upper() == 'IF NOT':
        decision, trigger_action = decision_maker(exec_node)
    elif exec_type.upper() == 'NO':
        decision = False
        trigger_action = "SKIP"
    elif exec_type.upper() != 'YES':
        decision = False
        supported_values = ['no', 'yes', 'if', 'if not']
        print_error("Unsupported value used for ExecType, supported values are: {0} and case-insensitive".format(supported_values))

    return decision, trigger_action
