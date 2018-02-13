from collections import OrderedDict
from datetime import datetime
from utils.json_utils import read_xml_get_json
from utils.navigator_util import Navigator
from wapps.cases.cases_utils.defaults import inverted_contexts_list, inverted_impacts_list, \
    inverted_iteration_types_list, inverted_runmodes_list


def inverted_on_error_list():
    pass


class VerifyCaseFile:

    def __init__(self, template, file_path):
        self.navigator = Navigator()
        self.template = template
        self.file_path = file_path
        self.template_data = read_xml_get_json(template, ordered_dict=True)
        self.data = read_xml_get_json(file_path, ordered_dict=True)
        self.output = {"status": True, "message": ""}
        self.root = "Testcase"
        self.major = ("Details", "Requirements", "Steps")
        self.defaults = {
            "context": inverted_contexts_list(),
            "impact": inverted_impacts_list(),
            "Iteration_type": inverted_iteration_types_list(),
            "onError": inverted_on_error_list(),
            "runmode": inverted_runmodes_list()
        }

    def verify_file(self):
        self.output = self.__verify_root()

        if self.output["status"]:
            self.__verify_details()
            self.__verify_requirements()
            self.__verify_steps()

        return self.output, self.data

    def __verify_root(self):
        output = self.output
        for key in self.data:
            if key != self.root:
                output["status"] = False
                output["message"] = "{0} is not is the correct format."
                print "-- An Error Occurred -- {0}".format(output["message"])
            break
        return output

    def __verify_details(self):
        if self.major[0] not in self.data[self.root]:
            self.data[self.root][self.major[0]] = {}
        for key, value in self.template_data[self.root][self.major[0]].iteritems():
            key, value = self.__verified_details_key_value(key, value)
            self.data[self.root][self.major[0]][key] = self.__verify_values(key, value, self.data[self.root][self.major[0]])

    def __verified_details_key_value(self, key, value):
        if value is None:
            value = ""
        if value == "":
            if key == "Engineer":
                value = self.navigator.get_engineer_name()
            if key == "Date":
                now = datetime.now()
                value = "{0}-{1}-{2}".format(now.year, now.month, now.day)
            if key == "Time":
                now = datetime.now()
                value = "{0}:{1}".format(now.hour, now.minute)
        return key, value

    def __verify_requirements(self):
        if self.major[1] not in self.data[self.root] or self.data[self.root][self.major[1]] is None:
            self.data[self.root][self.major[1]] = {"Requirement": []}
        elif "Requirement" not in self.data[self.root][self.major[1]] or self.data[self.root][self.major[1]]["Requirement"] is None:
            self.data[self.root][self.major[1]]["Requirement"] = []
        elif not isinstance(self.data[self.root][self.major[1]]["Requirement"], list):
            self.data[self.root][self.major[1]]["Requirement"] = [self.data[self.root][self.major[1]]["Requirement"]]

    def __verify_steps(self):
        if self.major[2] not in self.data[self.root]:
            self.data[self.root][self.major[2]] = {"step": []}
        elif not isinstance(self.data[self.root][self.major[2]]["step"], list):
            self.data[self.root][self.major[2]]["step"] = [self.data[self.root][self.major[2]]["step"]]

        for i in range(0, len(self.data[self.root][self.major[2]]["step"])):
            for key, value in self.template_data[self.root][self.major[2]]["step"].iteritems():
                key, value, self.data[self.root][self.major[2]]["step"][i] = \
                    self.__verified_steps_key_value(key, value, self.data[self.root][self.major[2]]["step"][i])
                self.data[self.root][self.major[2]]["step"][i][key] = \
                    self.__verify_values(key, value, self.data[self.root][self.major[2]]["step"][i])

    @staticmethod
    def __verified_steps_key_value(key, value, verify_data):
        if value is None:
            value = ""

        if key == "Arguments":
            if "argument" not in verify_data[key] or verify_data[key]["argument"] is None:
                verify_data[key]["argument"] = [{}]
            elif not isinstance(verify_data[key]["argument"], list):
                verify_data[key]["argument"] = [verify_data[key]["argument"]]

        if key == "Execute":
            if "Rule" not in verify_data[key] or verify_data[key]["Rule"] is None:
                verify_data[key]["Rule"] = [{}]
            elif not isinstance(verify_data[key]["Rule"], list):
                verify_data[key]["Rule"] = [verify_data[key]["Rule"]]

        return key, value, verify_data

    def __verify_values(self, tmpl_key, tmpl_value, parent):
        if tmpl_key not in parent:
            output = tmpl_value
        elif parent[tmpl_key] is None:
            output = tmpl_value
        else:
            if isinstance(parent[tmpl_key], list):
                for i in range(0, len(parent[tmpl_key])):
                    for k, v in tmpl_value.items():
                        parent[tmpl_key][i][k] = self.__verify_values(k, v, parent[tmpl_key][i])
                    output = parent[tmpl_key]
            elif isinstance(tmpl_value, OrderedDict):
                for k, v in tmpl_value.items():
                    parent[tmpl_key][k] = self.__verify_values(k, v, parent[tmpl_key])
                output = parent[tmpl_key]
            else:
                output = parent[tmpl_key]
        return output
