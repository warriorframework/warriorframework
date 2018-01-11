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
        json_data["data"] = self.__verify_global_verify_pattern(json_data["data"])
        json_data["data"] = self.__verify_global_others(json_data["data"])

        json_data["data"] = self.__verify_testdata_block(json_data["data"])

        for i in range(0, len(json_data["data"]["testdata"])):
            json_data["data"]["testdata"][i] = self.__verify_testdata_contents(json_data["data"]["testdata"][i])

        self.json_data = copy.deepcopy(json_data)
        return json_data

    def __verify_global_block(self, json_data):
        if "global" not in json_data:
            json_data["global"] = copy.deepcopy(self.defaults["data"]["global"])
        elif json_data["global"] is None:
            json_data["global"] = copy.deepcopy(self.defaults["data"]["global"])
        return json_data

    def __verify_global_cmd_parameters(self, json_data):
        flag = True
        if "command_params" not in json_data["global"] or json_data["global"]["command_params"] is None:
            json_data["global"]["command_params"] = copy.deepcopy(self.defaults["data"]["global"]["command_params"])
            flag = False
        if flag:
            for key, value in self.defaults["data"]["global"]["command_params"].items():
                if key not in json_data["global"]["command_params"]:
                    json_data["global"]["command_params"][key] = value
        return json_data

    def __verify_global_verify_pattern(self, json_data):
        flag = True
        if "variable_pattern" not in json_data["global"]:
            json_data["global"]["variable_pattern"] = self.defaults["data"]["global"]["variable_pattern"]
            flag = False
        if isinstance(json_data["global"]["variable_pattern"], list):
            json_data["global"]["variable_pattern"] = json_data["global"]["variable_pattern"][0]
        if flag:
            for key, value in self.defaults["data"]["global"]["variable_pattern"].items():
                if key not in json_data["global"]["variable_pattern"]:
                    json_data["global"]["variable_pattern"][key] = value
        for key, value in json_data["global"]["variable_pattern"].items():
            self.defaults["data"]["testdata"]["variable_pattern"][key] = value
        return json_data

    def __verify_global_others(self, json_data):
        if "verifications" not in json_data["global"] or json_data["global"]["verifications"] is None:
            json_data["global"]["verifications"] = copy.deepcopy(self.defaults["data"]["global"]["verifications"])
        json_data["global"]["verifications"] = self.__verify_global_vers(json_data["global"]["verifications"])
        if "keys" not in json_data["global"] or json_data["global"]["keys"] is None:
            json_data["global"]["keys"] = copy.deepcopy(self.defaults["data"]["global"]["keys"])
        json_data["global"]["keys"] = self.__verify_global_keys(json_data["global"]["keys"])
        return json_data

    def __verify_global_vers(self, verifications_json):
        if not isinstance(verifications_json, list):
            verifications_json = [verifications_json]
        final_json = []
        for i in range(0, len(verifications_json)):
            for child_key, child_value in verifications_json[i].items():
                for key in child_value:
                    if key in self.defaults["data"]["global"]["verifications"]["combination"]:
                        combo_tag = {child_key: self.__verify_global_verifications(child_value, "combination")}
                        final_json.append(copy.deepcopy(combo_tag))
                    elif key in self.defaults["data"]["global"]["verifications"]["verification"]:
                        ver_tag = {child_key: self.__verify_global_verifications(child_value, "verification")}
                        final_json.append(copy.deepcopy(ver_tag))
                    break
        return final_json

    def __verify_global_verifications(self, json_data, key):
        json_data["type"] = key
        for key, value in self.defaults["data"]["global"]["verifications"][key].items():
            if key not in json_data:
                json_data[key] = value
        return json_data

    def __verify_global_keys(self, keys_json):
        for key, value in self.defaults["data"]["global"]["keys"]["key"].items():
            for child_key, child_value in keys_json.items():
                keys_json[child_key]["type"] = "key"
                if key not in child_value:
                    keys_json[child_key][key] = value
        return keys_json

    def __verify_testdata_block(self, json_data):
        if "testdata" not in json_data or json_data["testdata"] is None:
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
        cmd_flag = True
        var_pat_flag = True
        ver_flag = True
        key_flag = True
        for key in testdata_json:
            if key == "command":
                cmd_flag = False
                final_json["command"] = self.__verify_testdata_command(testdata_json["command"])
            elif key == "variable_pattern":
                var_pat_flag = False
                final_json["variable_pattern"] = self.__verify_testdata_variable_pattern(testdata_json["variable_pattern"])
            elif key.startswith("@"):
                final_json[key] = testdata_json[key]
            else:
                validated_contents = self.__verify_testdata_others(testdata_json[key])
                if validated_contents["type"] == "verification":
                    ver_flag = False
                elif validated_contents["type"] == "key":
                    key_flag = False
                if validated_contents:
                    final_json[key] = copy.deepcopy(validated_contents)
        if cmd_flag:
            final_json["command"] = [copy.deepcopy(self.defaults["data"]["testdata"]["command"])]
        if var_pat_flag:
            final_json["variable_pattern"] = copy.deepcopy(self.defaults["data"]["testdata"]["variable_pattern"])
        if ver_flag:
            final_json["verification"] = copy.deepcopy(self.defaults["data"]["testdata"]["verification"])
            final_json["verification"]["type"] = "verification"
        if key_flag:
            final_json["key"] = copy.deepcopy(self.defaults["data"]["testdata"]["key"])
            final_json["key"]["type"] = "key"
        return final_json

    def __verify_testdata_command(self, json_data):
        if not isinstance(json_data, list):
            json_data = [json_data]
        for i in range(0, len(json_data)):
            for key, value in self.defaults["data"]["testdata"]["command"].items():
                if key not in json_data[i]:
                    json_data[i][key] = value
        return json_data

    def __verify_testdata_variable_pattern(self, json_data):
        if isinstance(json_data, list):
            json_data = json_data[0]
        for key, value in self.defaults["data"]["testdata"]["variable_pattern"].items():
            if key not in json_data:
                json_data[key] = value
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
        other_json["type"] = type_of_other
        for key, value in self.defaults["data"]["testdata"][type_of_other].items():
            if key not in other_json:
                other_json[key] = value
        return other_json
