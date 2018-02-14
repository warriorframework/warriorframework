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
import inspect
import traceback
import Framework.Utils as Utils
from Framework.Utils import data_Utils
from Framework.Utils.print_Utils import print_info, print_error, print_exception
from Framework.Utils.testcase_Utils import pNote_level
from WarriorCore.Classes.war_cli_class import WarriorCliClass
"""Driver utils module which handles gathers the argument
information about the keywords, executes the keywords and reports the
keyword status back to the product driver """


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
            # name_only = Utils.file_Utils.getNameOnly(os.path.basename(obj.__file__))
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
                if WarriorCliClass.mock or WarriorCliClass.sim:
                    if element.__dict__.get("mockready") is None:
                        pNote_level("The selected keyword {} isn't supported in trial mode".format(element.__name__), "ERROR")
                    else:
                        pNote_level("Keyword {} is being mocked".format(element.__name__), "INFO")
                        match_list.append(element)
                else:
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
        self.default_dict = self.get_defaults()

    def get_all_arguments(self):
        """Returns a list of all arguments required for
        the provided function/method object """
        args, varargs, keyword, defaults = inspect.getargspec(self.exec_obj)
        if args.count('self') > 0:
            args.remove('self')
        return args

    def get_defaults(self):
        """Returns a dictionary of optional arguments with their default values for
        the provided function/method object """
        default_dict = {}
        args, varargs, keyword, defaults = inspect.getargspec(self.exec_obj)
        if defaults:
            default_dict = dict(zip(args[-len(defaults):], defaults))
        return default_dict

    def get_mandatory_arguments(self):
        """Returns a list of mandatory arguments required for the provided function/method
        """
        args, varargs, keyword, defaults = inspect.getargspec(self.exec_obj)

        if defaults is not None:
            args = args[:-len(defaults)]

        if args.count('self') > 0:
            args.remove('self')
        return args

    def get_credential_value(self, arg, system):
        """get the value of arg in data file corresponding to system
        """
        datafile = self.data_repository['wt_datafile']
        var = arg
        if not hasattr(self, 'tag_dict'):
            self.tag_dict = data_Utils.get_credentials(datafile, system)
        if isinstance(arg, basestring) and arg.startswith("wtag"):
            var = arg.split("=")[1].strip()
            if var in self.tag_dict:
                value = self.tag_dict[var]
                # substitute environment/datarepo variables in the value and return
                if isinstance(value, (basestring, list, dict)):
                    return data_Utils.substitute_var_patterns(value)
                else:
                    return value
        return var

    def get_values_for_mandatory_args(self):
        """The values for mandatory arguments as a python dictionary
        """
        def get_value(arg):
            """get the value for arg from args or data repository
            """
            if arg in self.args_repository:
                return self.args_repository[arg]
            if arg in self.data_repository:
                return self.data_repository[arg]
            print_error("value for mandatory argument '{0}' not available in "
                        "data_repository/args_repository".format(args))
            return None
        print_info("getting values for mandatory arguments")
        arg_kv = {}
        sysname = 'system_name'
        args_list = self.req_args_list[:]
        if sysname in args_list:
            arg_kv[sysname] = get_value(sysname)
            if arg_kv[sysname] is None:
                del arg_kv[sysname]
            args_list.remove(sysname)
        for args in args_list:
            value = get_value(args)
            if value is None:
                continue
            if sysname in arg_kv:
                # the args can be direct values or mentioned as
                # wtag var (except system_name) like 'wtag=<wtag var>',
                # which would be fetched from the input data file
                value = self.get_credential_value(value, arg_kv[sysname])
                if value is not None:
                    arg_kv[args] = value
            else:
                arg_kv[args] = value
        return arg_kv

    def get_values_for_optional_args(self, arg_kv):
        """The values for optional arguments as a python dictionary
        """
        print_info("getting values for optional arguments")
        for args in self.optional_args_list:
            if args in self.args_repository:
                arg_kv[args] = self.args_repository[args]
            elif args in self.data_repository:
                arg_kv[args] = self.data_repository[args]
            else:
                arg_kv[args] = self.default_dict[args]
                print_info("executing with default value '{0}' for optional "
                           "argument '{1}'".format(arg_kv[args], args))
        for args in self.optional_args_list:
            # requires another loop since system_name may not be at beginning
            if args != 'system_name' and 'system_name' in arg_kv:
                # the args can be direct values or mentioned as
                # wtag var (except system_name) like 'wtag=<wtag var>',
                # which would be fetched from the input data file
                value = self.get_credential_value(arg_kv[args], arg_kv['system_name'])
                if value is not None:
                    arg_kv[args] = value
        else:
            if hasattr(self, 'tag_dict'):
                del self.tag_dict
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
        print_info("The Arguments passed for the current Step is: '{0}'".format(kwargs))
        if kw_status:
            # Execute the corresponding method
            method_loader = self.exec_obj.im_class()
            try:
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
        kwargs, kw_status = self.get_argument_as_keywords()

        print_info("The Arguments passed for the current Step is: '{0}'".format(kwargs))
        if kw_status:
            # Execute the corresponding function
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
        """updates the datarepository based on the return from the keyword execution
        """

        step_num = data_repository['step_num']

        if keyword_result is None:
            pNote_level("Keyword '{0}' did not return anything".format(keyword),
                        "debug", "kw")
            data_repository['step-%s_status' % step_num] = 'ERROR'

        elif isinstance(keyword_result, str):
            if keyword_result.upper() in ["ERROR", "EXCEPTION", "RAN"]:
                pNote_level("Keyword '{0}' returned an {1}".format(keyword, keyword_result),
                            "debug", "kw")
                data_repository['step-%s_status' % step_num] = keyword_result.upper()

        elif isinstance(keyword_result, bool):
            pNote_level("Keyword '{0}' returned a status only....".format(keyword),
                        "debug", "kw")
            data_repository['step-%s_status' % step_num] = keyword_result

        elif isinstance(keyword_result, dict):
            pNote_level("Keyword '{0}' returned only a dictionary .. "
                        "updating data_repository".format(keyword), "debug", "kw")
            pNote_level("Keyword '{0}' did not return any status ".format(keyword),
                        "debug", "kw")
            data_repository.update(keyword_result)
            data_repository['step-%s_status' % step_num] = 'Error'

        elif isinstance(keyword_result, tuple):
            if isinstance(keyword_result[0], str) and keyword_result[0] == "EXCEPTION":
                pNote_level("Keyword  '{0}' execution raised an"
                            "exception".format(keyword), "debug", "kw")
                data_repository['step-%s_status' % step_num] = keyword_result[0]
                data_repository['step-%s_exception' % step_num] = keyword_result[1]
            elif isinstance(keyword_result[0], str) and keyword_result[0].upper() == "RAN":
                pNote_level("Keyword '{0}' returned "\
                            "a status..".format(keyword), "debug", "kw")
                data_repository['step-%s_status' % step_num] = "RAN"
            else:
                pNote_level("Keyword '{0}' returned multiple"
                            "values ".format(keyword), "debug", "kw")
                data_repository['step-%s_status' % step_num] = 'Error'
                for element in keyword_result:
                    if isinstance(element, bool):
                        pNote_level("Keyword '{0}' returned"
                                    "a status..".format(keyword), "debug", "kw")
                        data_repository['step-%s_status' % step_num] = element
                    elif isinstance(element, dict):
                        pNote_level("Keyword '{0}' returned a dictionary.. "
                                    "will update data_repository".format(keyword),
                                    "debug", "kw")
                        data_repository.update(element)
                    else:
                        pNote_level("unexpected return type form keyword '{0}'... "
                                    "expecting bool or dict ".format(keyword),
                                    "debug", "kw")
        else:
            pNote_level("unexpected return type form keyword '{0}'... "
                        "expecting bool/dict/error/exception".format(keyword),
                        "debug", "kw")
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
