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

class ElseException(Exception):
    def __init__(self, else_action):
        self.action = else_action

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

def logical_decision(exec_condition, exec_cond_var, operator="equal"):
    """
        Handle the logical decision for the value comparison
        :param:
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
        pNote("Comparing non-numerical value using numerical operator,"\
            "please check value and operator type", "ERROR")
        status = False

    if status and operator == "equal":
        result = True if get_object_from_datarepository(exec_condition) == exec_cond_var else False
    elif status and operator == "not_equal":
        result = True if get_object_from_datarepository(exec_condition) != exec_cond_var else False
    elif status and operator in ["greater_equal", "greater", "smaller_equal", "smaller"]:
        result = math_decision(exec_condition, exec_cond_var, operator)
    else:
        pNote("Execution condition failed for expected value: {} , operator: {}, actual value: {}"\
              .format(exec_cond_var, operator,
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
    if isinstance(rule, str):
        if rule.lower() == True:
            return True
        elif rule.lower() == False:
            return False
        else:
            raise Exception("rule value is wrong")
    exec_condition = rule.get("Condition", None)
    exec_cond_var = rule.get("Condvalue", None)
    else_action = rule.get("Else", None)
    if else_action is not None and else_action.upper() == "GOTO":
        else_action = rule.get("Elsevalue")

    # Check for math operator
    support_operators = ["greater_equal", "greater", "smaller_equal",
                         "smaller", "equal", "not_equal"]
    operator = rule.get("Operator", "equal")
    if operator is not None and operator.lower() not in support_operators:
        pNote("Invaid Operator value, please use the following: {}".format(support_operators))
        operator = None

    # Parse value with prefix
    supported_prefix = ["bool_", "str_", "int_", "float_", "list_", "tuple_", "dict_"]
    if any([exec_condition.startswith(i) for i in supported_prefix]):
        exec_condition = exec_condition[exec_condition.find('_')+1:]

    arg_datatype_object = ArgumentDatatype(exec_condition, exec_cond_var)
    exec_cond_var = arg_datatype_object.convert_arg_to_datatype()

    status = logical_decision(exec_condition, exec_cond_var, operator)
    if status is False and else_action is not None:
        raise ElseException(else_action)
    else:
        return status

def int_split(expression_str):
    elements = expression_str.split()
    for ind, ele in enumerate(elements):
        if str.isdigit(ele):
            elements[ind] = int(ele)
    return elements

def simple_exp_parser(expression_str, rules):
    elements = int_split(expression_str)
    status = None
    if not elements:
        # illegal expression
        raise Exception("expression_str invalid or not found")
    elif len(elements) == 1:
        status = rule_parser(rules[elements[0]])
    else:
        status = rule_parser(rules[elements[0]])
        for x in range(0, len(elements) - 2, 2):
            if elements[x+1].lower() == "and" or elements[x+1] == "&":
                status = status & rule_parser(rules[elements[x+2]])
            elif elements[x+1].lower() == "or" or elements[x+1] == "|":
                status = status | rule_parser(rules[elements[x+2]])
            else:
                # invalid operator
                raise Exception("invalid operator in expression_str: {}".format(expression_str))
    return status

def special_exp_parser(expression_str, rules, status_first, status_last):
    status = status_first
    elements = int_split(expression_str)
    if not elements or len(elements) < 3:
        # illegal expression or no rule in expression
        raise Exception("expression_str invalid or not found")
    else:
        for x in range(0, len(elements)-1, 2):
            if elements[x].lower() == "and" or elements[x] == "&":
                status = status & rule_parser(rules[elements[x+1]])
            elif elements[x].lower() == "or" or elements[x] == "|":
                status = status | rule_parser(rules[elements[x+1]])
            else:
                # invalid operator
                raise Exception("invalid operator in expression_str: {}".format(expression_str))
        # at this point we should have the last operator left to be processed
        if elements[-1].lower() == "and" or elements[-1] == "&":
            status = status & status_last
        elif elements[-1].lower() == "or" or elements[-1] == "|":
            status = status | status_last
        else:
            # invalid operator
            raise Exception("invalid operator in expression_str: {}".format(expression_str))
    return status

def expression_split(src):
    result = []
    open_index = []
    for x in range(len(src)):
        if src[x] == "(":
            open_index.append(x)
        if src[x] == ")":
            result.append((open_index.pop(), x))
    return result

def expression_parser(src, rules):
    src = src.strip()
    opening = src.count("(")
    closing = src.count(")")
    if opening != closing:
        raise Exception("expression invalid")
    exps = expression_split(src)
    status = None
    if not exps:
        status = simple_exp_parser(src, rules)
    elif len(exps) == 1:
        # handle expression outside of parenthesis
        status = simple_exp_parser(src[exps[0][0]+1:exps[0][1]], rules)
        if exps[0][0] != 0:
            # Left side has expression
            status = special_exp_parser(" & "+src[:exps[0][0]-1], rules, True, status)
        if exps[0][1]+1 != len(src):
            # Right side has expression
            status = special_exp_parser(src[exps[0][1]+1:]+" & ", rules, status, True)
    else:
        status = simple_exp_parser(src[exps[0][0]+1:exps[0][1]], rules)
        for x in range(len(exps) - 1):
            # if next exp is in a same level paren
            if exps[x+1][0] > exps[x][1]:
                operator = src[exps[x][1]+1:exps[x+1][0]].strip()
                if operator.lower() == "and" or operator == "&":
                    status = status & simple_exp_parser(src[exps[x+1][0]+1:exps[x+1][1]], rules)
                elif operator.lower() == "or" or operator == "|":
                    status = status | simple_exp_parser(src[exps[x+1][0]+1:exps[x+1][1]], rules)
                elif any([x.isdigit() for x in operator]):
                    # actually have rules in between,
                    status_2 = simple_exp_parser(src[exps[x+1][0]+1:exps[x+1][1]], rules)
                    status = special_exp_parser(operator, rules, status, status_2)
                else:
                    # invalid operator
                    raise Exception("invalid operator in expression string: {}".format(src))
            # if next exp is a wrapper of the current paren
            else:
                # Check the left side, should only have simple expression left
                if src[exps[x+1][0]+1:exps[x][0]].strip() != "":
                    status = special_exp_parser(" & "+src[exps[x+1][0]+1:exps[x][0]], rules, True, status)
                # Check the right side, should only have simple expression left
                if src[exps[x][1]+1:exps[x+1][1]].strip() != "":
                    status = special_exp_parser(src[exps[x][1]+1:exps[x+1][1]]+" & ", rules, status, True)

        if src[0] != "(":
            # Left side has expression
            status = special_exp_parser(" & "+src[:src.find("(")], rules, True, status)
        if src[-1] != ")":
            # Right side has expression
            status = special_exp_parser(src[src.rfind(")")+1:]+" & ", rules, status, True)

    return status

def decision_maker(exec_node):
    exec_type = exec_node.get("ExecType", "")
    expression = exec_node.get("Expression", "")
    action = exec_node.get("Else", "next")
    if exec_node.get("Elsevalue", "") != "":
        action = exec_node.get("Elsevalue")
    rules = exec_node.findall("Rule")
    rules.insert(0, '')

    if expression == "":
        expression = ' & '.join([str(x) for x in range(1, len(rules))])
    try:
        status = expression_parser(expression, rules)
        if exec_type.upper() == 'IF NOT':
            status = not status
    except ElseException, else_action:
        # do something
        status = False
        if else_action.action is not None:
            action = else_action.action
    # except Exception, err:
    #     # do something else
    #     status = False
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", err

    return status, action

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
    if exec_node is None:
        return True, None

    decision = True
    trigger_action = None
    exec_type = exec_node.get("ExecType", "")
    if exec_type.upper() == 'IF' or exec_type.upper() == 'IF NOT':
        decision, trigger_action = decision_maker(exec_node)
    elif exec_type.upper() == 'NO':
        decision = False
        trigger_action = "SKIP"
    elif exec_type.upper() == 'YES':
        decision = True
    else:
        decision = False
        supported_values = ['no', 'yes', 'if', 'if not']
        print_error("Unsupported value used for ExecType, supported values are: {0} and case-insensitive".format(supported_values))

    return decision, trigger_action
