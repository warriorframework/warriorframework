from Framework.Utils.testcase_Utils import pNote
from collections import OrderedDict
# For function/method that only be mocked in trialmode (not sim mode), put name here
VERIFY_ONLY = ["verify_cmd_response", "verify_inorder_cmd_response"]

def mockready(func):
    """
        Decorator function that assign a mockready attrib to input func
        the attrib will be used to decide if the func is mockable or not
    """
    from WarriorCore.Classes.war_cli_class import WarriorCliClass
    if not WarriorCliClass.mock and not WarriorCliClass.sim:
        return func

    func.__dict__["mockready"] = True
    return func

def mocked(func):
    """
        Decorator function that route function to mocked function
    """
    def inner(*args, **kwargs):
        from WarriorCore.Classes.war_cli_class import WarriorCliClass
        if (not WarriorCliClass.mock and not WarriorCliClass.sim) or\
             (WarriorCliClass.sim and func.__name__ in VERIFY_ONLY):
            return func(*args, **kwargs)

        # If it is in simulator mode, this function needs to retrieve response for command
        if func.__name__ == "get_command_details_from_testdata":
            if WarriorCliClass.sim and args[0] is not None and args[0] != "":
                from Framework.Utils.data_Utils import cmd_params
                cmd_params.update({"sim_response_list": "simresp"})
                get_response_file(args[0])
            return func(*args, **kwargs)

        # same as above function to retrieve response
        if func.__name__ == "_get_cmd_details":
            result = func(*args, **kwargs)
            pNote("The non-substituted commands:")
            for index, cmd in enumerate(result["command_list"]):
                pNote("#{}: {}".format(index+1, cmd))
                if WarriorCliClass.sim:
                    MockUtils.cli_Utils.response_reference_dict[cmd] = result["sim_response_list"][index]
            return result

        # Print extra info
        # pNote("Util {} is mocked".format(func.__name__), "WARNING")
        # for value in [str(x) + ": " + str(y) for x, y in zip(inspect.getargspec(func)[0], args)]:
        #     pNote(value)
        # for key, value in kwargs.items():
        #     pNote(str(key) + ": " + str(value))

        # mapping function to mocked function
        func_name = func.__name__
        func_module = func.__module__.split(".")[-1]
        if func_module in dir(MockUtils):
            func_module = getattr(MockUtils, func_module)
            if func_name in dir(func_module):
                function = getattr(func_module, func_name)
            else:
                print "Cannot locate {} in {}".format(func_name, dir(func_module))
                function = func
        else:
            print "Cannot locate {} in {}".format(func_module, dir(MockUtils))
            function = func
        return function(*args, **kwargs)
    return inner

def get_response_file(testdatafile):
    """
        Link response to command in testdatafile
    """
    from Framework.Utils.xml_Utils import getRoot, getElementListWithSpecificXpath
    from Framework.Utils.data_Utils import _get_row
    tmp_list = getElementListWithSpecificXpath(testdatafile, "./global/response_file")
    response_file = tmp_list[0].text if tmp_list != [] else ""
    root = getRoot(response_file)
    response_dict = {}

    for testdata in root.findall("testdata"):
        if testdata.get("execute") == "yes":
            testdata_key = "{0}{1}".format(testdata.get('title', ""), \
                                         _get_row(testdata))
            command_list = testdata.findall("command")
            for command in command_list:
                cmd_text = command.get("send", "")
                raw_response = command.get("response", "")
                response_list = raw_response.split(",")
                resp_text = OrderedDict()
                for resp_symbol in response_list:
                    if testdata.find(resp_symbol) is not None and testdata.find(resp_symbol).get("text") is not None:
                        resp_text.update({resp_symbol: testdata.find(resp_symbol).get("text")})
                    else:
                        pNote("Error resolving symbol {} in testdata block {}".format(resp_symbol, testdata_key))
                response_dict[cmd_text] = resp_text

    MockUtils.cli_Utils.response_dict = response_dict

class MockUtils(object):
    """
        This class contains all the mocked Utils
    """
    def __init__(self):
        return None

    class cli_Utils():
        """
            Mocked cli_Utils
        """
        response_dict = {}
        response_reference_dict = {}

        @staticmethod
        def connect_ssh(ip, port="22", username="", password="", logfile=None, timeout=60,
                prompt=".*(%|#|\$)", conn_options="", custom_keystroke="", **kwargs):
            """
                This function doesn't actually connect to the server
            """
            pNote("Mocking connect_ssh")
            sshobj = "Mocking connect_ssh"
            conn_string = ""
            conn_options = "" if conn_options is False or conn_options is None else conn_options
            # delete -o StrictHostKeyChecking=no and put them in conn_options
            if not conn_options or conn_options is None:
                conn_options = ""
            command = 'ssh -p {0} {1}@{2} {3}'.format(port, username, ip, conn_options)
            #command = ('ssh -p '+ port + ' ' + username + '@' + ip)
            pNote("connectSSH: cmd = %s" % command, "DEBUG")
            pNote("MOCK MODE: No connection is made to the server")

            return sshobj, conn_string

        @staticmethod
        def connect_telnet(ip, port="23", username="", password="",
                logfile=None, timeout=60, prompt=".*(%|#|\$)",
                conn_options="", custom_keystroke="", **kwargs):
            """
                This function doesn't actually connect to the server
            """
            pNote("Mocking connect_telnet")
            conn_options = "" if conn_options is False or conn_options is None else conn_options
            pNote("timeout is: %s" % timeout, "DEBUG")
            pNote("port num is: %s" % port, "DEBUG")
            command = ('telnet '+ ip + ' '+ port)
            if not conn_options or conn_options is None:
                conn_options = ""
            command = command + str(conn_options)
            pNote("connectTelnet cmd = %s" % command, "DEBUG")
            pNote("MOCK MODE: No connection is made to the server")
            conn_string = ""
            telnetobj = "Mocking connect_ssh"

            return telnetobj, conn_string

        @classmethod
        def _send_cmd(cls, *args, **kwargs):
            """
                This function pass the command to the mocked send_command function
            """
            command = kwargs.get('command')
            startprompt = kwargs.get('startprompt', ".*")
            endprompt = kwargs.get('endprompt', None)
            cmd_timeout = kwargs.get('cmd_timeout', None)
            result, response = cls.send_command("session_obj", startprompt, endprompt, command, cmd_timeout)
            return result, response

        @classmethod
        def send_command(cls, *args, **kwargs):
            """
                Get response from the processed response dict
            """
            from WarriorCore.Classes.war_cli_class import WarriorCliClass
            pNote(":CMD: %s"%(args[3]))
            specific_response = MockUtils.cli_Utils.response_reference_dict.get(args[3], True) if WarriorCliClass.sim else False
            if specific_response:
                response = MockUtils.cli_Utils.response_dict.get(args[3], {}).get(specific_response, "")
            else:
                response = MockUtils.cli_Utils.response_dict.get(args[3], {}).values()[0] if WarriorCliClass.sim else ""
            pNote("Response:\n{0}\n".format(response))
            return True, response

        @classmethod
        def _send_cmd_by_type(cls, *args, **kwargs):
            pNote(":CMD: %s"%(args[3]))

        @classmethod
        def _send_command_retrials(cls, *args, **kwargs):
            pNote("_send_command_retrials shouldn't be called in this mode")
            return True, ""

        @classmethod
        def send_command_and_get_response(cls, *args, **kwargs):
            """
                Get response from the processed response dict
            """
            from WarriorCore.Classes.war_cli_class import WarriorCliClass
            response = MockUtils.cli_Utils.response_dict.get(args[3], [""])[0] if WarriorCliClass.sim else ""
            pNote(":CMD: %s"%(args[3]))
            return response

    class data_Utils():
        @staticmethod
        def get_td_vc(datafile, system_name, td_tag, vc_tag):
            """
                This function is called in another mocked function
            """
            print "Mocked data_Utils.get_td_vs"
            return None, None

        @staticmethod
        def verify_cmd_response(match_list, context_list, command, response,
                        verify_on_system, varconfigfile=None, endprompt="",
                        verify_group=None):
            """
                Trialmode only: it prints the verify text instead of doing actual verification
            """
            from Framework.Utils import string_Utils
            from Framework.Utils.data_Utils import get_no_impact_logic
            from Framework.Utils import testcase_Utils

            if varconfigfile and varconfigfile is not None:
                match_list = string_Utils.sub_from_varconfig(varconfigfile, match_list)

            for i in range(0, len(match_list)):
                if context_list[i] and match_list[i]:
                    noiimpact, found = get_no_impact_logic(context_list[i])
                    found = testcase_Utils.pConvertLogical(found)
                    if found:
                        pNote("Looking for '{}' in response to command '{}'".format(match_list[i], command))
                    else:
                        pNote("Not Looking for '{}' in response to command '{}'".format(match_list[i], command))
            return "RAN"

        @staticmethod
        def verify_inorder_cmd_response(match_list, verify_list, system, command,
                                verify_dict):
            """
                Trialmode only: it prints the verify text instead of doing actual verification
            """
            pNote("Verifying {} on system {}".format(command, system))
            pNote("match list: {}".format(str(match_list)))
            pNote("verify_list: {}".format(str(verify_list)))
            return "RAN"