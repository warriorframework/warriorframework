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

"""Driver utils module which handles gathers the argument
information about the keywords, executes the keywords and reports the
keyword status back to the product driver """


import inspect
import traceback
import Framework.Utils as Utils
from Framework.Utils.print_Utils import print_info, print_error, print_exception
from Framework.Utils.testcase_Utils import pNote_level
from WarriorCore.Classes.war_cli_class import WarriorCliClass

class ModuleOperations(object):
    """Module operations class has methods
    related to module operations before executing a keyword
    like
    1. getting module/class/method/function list from the
    Actions package
    2. finding the methods or functions matching the
    keyword name """

    def __init__(self, package_list, keyword):
        """ Constructor """
        self.package_list = package_list
        self.import_sub_modules()
        self.module_list = self.get_module_list_from_pkglist()
        self.class_list = self.get_class_list_from_modulelist()
        self.method_list = self.get_method_list_from_classlist()
        self.function_list = self.get_function_list_from_modlist()
        self.matching_method_list = self.search_keyword_in_list(keyword, self.method_list)
        self.matching_function_list = self.search_keyword_in_list(keyword, self.function_list)
#         print "methods"
#         for method in self.method_list:
#             print method.__name__
#         print "functions"
#         for function in self.function_list:
#             print function.__name__

    def import_sub_modules(self):
        """Import sub modules for the given package """
        try:
            for package in self.package_list:
                Utils.import_utils.import_submodules(package)
        except ImportError, err:
            print_error("{0} : \n".format(str(err)))
            print_error('unexpected error: {0}'.format(traceback.format_exc()))

    def get_module_list_from_pkglist(self):
        """Get the list of modules for the provided package list"""
        module_list = []
        for package in self.package_list:
            mod_list = self.get_module_list_from_pkg_rcrsv(package, [])
            module_list.extend(mod_list)
        return module_list

    def get_module_list_from_pkg_rcrsv(self, package, mod_list):
        """ Recursively get the list of all
        module present in the package and sub-packages"""

        for name, obj in inspect.getmembers(package, inspect.ismodule):
            #name_only = Utils.file_Utils.getNameOnly(os.path.basename(obj.__file__))
            mod_list.append(obj)
            if name == '__init__.py':
                self.get_module_list_from_pkg_rcrsv(obj, mod_list)
        return mod_list

    def get_class_list_from_modulelist(self):
        """Get the list of classes in the module """
        class_list = []
        class_name_list = []
        for module in self.module_list:
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if inspect.getmodule(obj) == module:
                    class_list.append(obj)
                    class_name_list.append(name)
        return class_list

    def get_method_list_from_classlist(self):
        """Get the list of all methods present in
        the provided class list """
        method_list = []
        method_name_list = []
        for class_object in self.class_list:
            for name, obj in inspect.getmembers(class_object, inspect.ismethod):
                method_list.append(obj)
                method_name_list.append(name)
        return method_list

    def get_function_list_from_modlist(self):
        """Gets the list of functions from the list of modules """
        function_list = []
        function_name_list = []
        for module in self.module_list:
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if inspect.getmodule(obj) == module:
                    function_list.append(obj)
                    function_name_list.append(name)
        return function_list

    @staticmethod
    def search_keyword_in_list(keyword, input_list):
        """ Searches for the keyword in the list of method or function objects
        Returns a list of matching method/function objects """

        match_list = []
        for element in input_list:
            if element.__name__ == keyword:
                match_list.append(element)
        return match_list

class KeywordOperations(object):
    """KeywordOperations class has methods that
    gets the mandatory/optional args requored to execute
    a keyword and their values"""

    def __init__(self, keyword, exec_obj, args_repository, data_repository):
        """Constructor """

        self.keyword = keyword
        self.exec_obj = exec_obj
        self.args_repository = args_repository
        self.data_repository = data_repository

        self.all_args_list = self.get_all_arguments()
        self.req_args_list = self.get_mandatory_arguments()
        self.optional_args_list = list(set(self.all_args_list) - set(self.req_args_list))

    def get_all_arguments(self):
        """Returns a list of all arguments required for
        the provided function/method object """
        args, varargs, keyword, defaults = inspect.getargspec(self.exec_obj)
        if args.count('self') > 0:
            args.remove('self')
        return args

    def get_mandatory_arguments(self):
        """Returns a list of mandatory arguments required for the provided function/method """
        args, varargs, keyword, defaults = inspect.getargspec(self.exec_obj)

        if defaults is not None:
            args = args[:-len(defaults)]

        if args.count('self') > 0:
            args.remove('self')
        return args

    def get_values_for_mandatory_args(self):
        """The th values for mandatory arguments as a
        python dictionary """
        print_info("getting values for mandatory arguments")
        arg_kv = {}
        for args in self.req_args_list:
            if self.args_repository.has_key(args) is True:
                arg_kv[args] = self.args_repository[args]
            elif  self.data_repository.has_key(args) is True:
                arg_kv[args] = self.data_repository[args]
            else:
                print_error("value for mandatory argument '%s' "\
                                  "not available in data_repository/args_repository" % args)
        return arg_kv

    def get_values_for_optional_args(self, arg_kv):
        """The th values for optional arguments as a
        python dictionary """
        print_info("getting values for optional arguments")
        for args in self.optional_args_list:
            if self.args_repository.has_key(args) is True:
                arg_kv[args] = self.args_repository[args]
            elif self.data_repository.has_key(args) is True:
                arg_kv[args] = self.data_repository[args]
            else:
                print_info("executing with default values "\
                                 "for optional argument '{0}'".format(args))
        return arg_kv

    def get_argument_as_keywords(self):
        """Get a python dictionary containing
        arguments and their values"""
        status = True
        arg_kv = self.get_values_for_mandatory_args()
        if len(arg_kv) != len(self.req_args_list):
            msg = 'could not execute %s without mandatory arguments' % (object)
            self.data_repository = skip_and_report_status(self.data_repository, msg)
            status = False
        arg_kv = self.get_values_for_optional_args(arg_kv)
        return arg_kv, status

    def execute_method_for_keyword(self):
        """Executes a method corresponding to keyword """

        kwargs, kw_status = self.get_argument_as_keywords()
        if kw_status:
            # Execute the corresponding method
            method_loader = self.exec_obj.im_class()
            try:
                if WarriorCliClass.cmdprint:
                    sessid = kwargs['system_name']
                    if 'session_name' in kwargs: sessid += kwargs['session_name']
                    print_info("{:*^80}".format(' System: '+sessid+' '))
                    self.data_repository.update({sessid : sessid, sessid+'_td_response' : {}})
                keyword_result = self.exec_obj(method_loader, **kwargs)
            except Exception as exception:
                trcback = print_exception(exception)
                keyword_result = ("EXCEPTION", trcback)

            self.data_repository = self.update_data_repository(self.keyword,
                                                               keyword_result,
                                                               self.data_repository)
        return self.data_repository

    def execute_function_for_keyword(self):
        """Executes a function for a keyword"""
        Utils.config_Utils.set_datarepository(self.data_repository)
        kwargs, kw_status = self.get_argument_as_keywords()

        if kw_status:
            # Execute the corresponding function
            # print_info ( 'kwargs: ', kwargs)
            try:
                keyword_result = self.exec_obj(**kwargs)
            except Exception as exception:
                trcback = print_exception(exception)
                keyword_result = ("EXCEPTION", trcback)

            self.data_repository = self.update_data_repository(self.keyword,
                                                               keyword_result,
                                                               self.data_repository)

        return self.data_repository

    @staticmethod
    def update_data_repository(keyword, keyword_result, data_repository):
        """updates the datarepository based on the return from the keyword execution"""

        step_num = data_repository['step_num']

        if keyword_result is None:
            pNote_level("Keyword '{0}' did not return anything".format(keyword), "debug", "kw")
            data_repository['step-%s_status' % step_num] = 'ERROR'

        elif isinstance(keyword_result, str):
            if keyword_result.upper() == "ERROR" or \
            keyword_result.upper() == "EXCEPTION":
                pNote_level("Keyword '{0}' returned an {1}".format(keyword, keyword_result),
                            "debug", "kw")
                data_repository['step-%s_status' % step_num] = keyword_result.upper()
        
        elif isinstance(keyword_result, bool):
            pNote_level("Keyword '{0}' returned a status only....".format(keyword), "debug", "kw")
            data_repository['step-%s_status' % step_num] = keyword_result

        elif isinstance(keyword_result, dict):
            pNote_level("Keyword '{0}' returned only a dictionary .. "\
                        "updating data_repository".format(keyword), "debug", "kw")
            pNote_level("Keyword '{0}' did not return any status ".format(keyword), "debug", "kw")
            data_repository.update(keyword_result)
            data_repository['step-%s_status' % step_num] = 'Error'

        elif isinstance(keyword_result, tuple):
            if isinstance(keyword_result[0], str) and keyword_result[0] == "EXCEPTION":
                pNote_level("Keyword  '{0}' execution raised an"\
                            "exception".format(keyword), "debug", "kw")
                data_repository['step-%s_status' % step_num] = keyword_result[0]
                data_repository['step-%s_exception' % step_num] = keyword_result[1]
            else:
                pNote_level("Keyword '{0}' returned multiple"\
                            "values ".format(keyword), "debug", "kw")
                data_repository['step-%s_status' % step_num] = 'Error'
                for element in keyword_result:
                    if isinstance(element, bool):
                        pNote_level("Keyword '{0}' returned"\
                                    "a status..".format(keyword), "debug", "kw")
                        data_repository['step-%s_status' % step_num] = element
                    elif isinstance(element, dict):
                        pNote_level("Keyword '{0}' returned a dictionary.. "\
                                    "will update data_repository".format(keyword), "debug", "kw")
                        data_repository.update(element)
                    else:
                        pNote_level("unexpected return type form keyword '{0}'... "\
                                    "expecting bool or dict ".format(keyword), "debug", "kw")
        else:
            pNote_level("unexpected return type form keyword '{0}'... "\
                        "expecting bool/dict/error/exception".format(keyword), "debug", "kw")
            data_repository['step-%s_status' % step_num] = False

        return data_repository


def skip_and_report_status(data_repository, msg):
    """Skip step execution and report status """

    step_num = data_repository['step_num']
    print_info(msg)
    Utils.testcase_Utils.pNote(msg)
#     Utils.testcase_Utils.reportStatus('Skip', level='Step')
    data_repository['step-%s_status' % step_num] = 'ERROR'
    return data_repository
