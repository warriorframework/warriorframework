import copy
from utils.json_utils import read_xml_get_json


class VerifyCliDataClass:

    def __init__(self, filepath, base_filepath):
        self.filepath = filepath
        self.base_filepath = base_filepath
        self.json_data = read_xml_get_json(self.filepath)
        self.defaults = read_xml_get_json(self.base_filepath)

    def verify_contents(self):
        json_data = copy.deepcopy(self.json_data)
        json_data["data"] = self.__verify_global_block(json_data["data"])
        json_data["data"] = self.__verify_global_cmd_parameters(json_data["data"])
        json_data["data"] = self.__verify_global_others(json_data["data"])

        json_data["data"] = self.__verify_testdata_block(json_data["data"])

        for i in range(0, len(json_data["data"]["testdata"])):
            json_data["data"]["testdata"][i] = self.__verify_testdata_contents(json_data["data"]["testdata"][i])

        self.json_data = copy.deepcopy(json_data)
        return json_data

    def __verify_global_block(self, json_data):
        if "global" not in json_data:
            json_data["global"] = copy.deepcopy(self.defaults["data"]["global"])
        return json_data

    def __verify_global_cmd_parameters(self, json_data):
        flag = True
        if "command_params" not in json_data["global"]:
            json_data["global"]["command_params"] = copy.deepcopy(self.defaults["data"]["global"]["command_params"])
            flag = False
        if flag:
            for key, value in self.defaults["data"]["global"]["command_params"].items():
                if key not in json_data["global"]["command_params"]:
                    json_data["global"]["command_params"][key] = value
        return json_data

    def __verify_global_others(self, json_data):
        return json_data

    def __verify_testdata_block(self, json_data):
        if "testdata" not in json_data:
            json_data["testdata"] = copy.deepcopy(self.defaults["data"]["testdata"])
        if not isinstance(json_data["testdata"], list):
            json_data["testdata"] = [json_data["testdata"]]
        for i in range(0, len(json_data["testdata"])):
            for key, value in self.defaults["data"]["testdata"].items():
                if key.startswith("@") and key not in json_data["testdata"][i]:
                    json_data["testdata"][i][key] = value
        return json_data

    def __verify_testdata_contents(self, testdata_json):
        final_json = {}
        for key in testdata_json:
            if key == "command":
                final_json["command"] = self.__verify_testdata_command(testdata_json["command"])
            elif key.startswith("@"):
                final_json[key] = testdata_json[key]
            else:
                validated_contents = self.__verify_testdata_others(testdata_json[key])
                if validated_contents:
                    final_json[key] = copy.deepcopy(validated_contents)
        return final_json

    def __verify_testdata_command(self, json_data):
        if not isinstance(json_data, list):
            json_data = [json_data]
        for i in range(0, len(json_data)):
            for key, value in self.defaults["data"]["testdata"]["command"].items():
                if key not in json_data[i]:
                    json_data[i][key] = value
        return json_data

    def __verify_testdata_others(self, other_json):
        final_json = False
        for key in other_json:
            if key in self.defaults["data"]["testdata"]["verification"]:
                final_json = self.__verify_testdata_others_contents(other_json, "verification")
                break
            elif key in self.defaults["data"]["testdata"]["key"]:
                final_json = self.__verify_testdata_others_contents(other_json, "key")
                break
        return final_json

    def __verify_testdata_others_contents(self, other_json, type_of_other):
        for key, value in self.defaults["data"]["testdata"][type_of_other].items():
            if key not in other_json:
                other_json[key] = value
        return other_json
