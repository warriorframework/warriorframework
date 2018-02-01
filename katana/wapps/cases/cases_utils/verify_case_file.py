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
            if key not in self.data[self.root][self.major[0]]:
                self.data[self.root][self.major[0]][key] = value
            elif self.data[self.root][self.major[0]][key] is None:
                self.data[self.root][self.major[0]][key] = value

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
        if self.major[1] not in self.data[self.root]:
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
                key, value = self.__verified_steps_key_value(key, value)
                if key not in self.data[self.root][self.major[2]]["step"][i]:
                    self.data[self.root][self.major[2]]["step"][i][key] = value
                elif self.data[self.root][self.major[2]]["step"][i][key] is None:
                    self.data[self.root][self.major[2]]["step"][i][key] = value

    def __verified_steps_key_value(self, key, value):
        if value is None:
            value = ""

        if isinstance(value, dict):
            for k, v in value.iteritems():
                value[k] = self.__verified_steps_key_value(k, v)

        return key, value
