import copy
import os
from wapps.assembler.assembler_utils.repository_details import KwRepositoryDetails
from utils.directory_traversal_utils import delete_dir, join_path
from utils.git_utils import get_repository_name, check_url_is_a_valid_repo
from utils.json_utils import read_xml_get_json
from utils.navigator_util import Navigator


class VerifyFileContents:

    def __init__(self, data_file, ref_data_file):
        self.data_file = data_file
        self.data = read_xml_get_json(data_file)
        self.ref_data_file = ref_data_file
        self.nav_obj = Navigator()
        self.dependency_template = join_path(self.nav_obj.get_katana_dir(), "native", "settings", "static",
                                             "settings", "base_templates", "empty.xml")
        self.ref_data = self._get_ref_data()
        self.dependency_dict = self.__get_dependency_dict()

    def _get_ref_data(self):
        data = read_xml_get_json(self.ref_data_file)
        dependency_data = read_xml_get_json(self.dependency_template)
        data["data"]["warhorn"] = copy.deepcopy(dependency_data["data"]["warhorn"])
        return data

    def __get_dependency_dict(self):
        output = {}
        for el in self.ref_data["data"]["warhorn"]["dependency"]:
            output[el["@name"]] = {"version": el["@version"], "description": el["@description"]}
        return output

    def verify_file(self):
        output = {"status": True, "message": ""}

        if self.data is None:
            output["status"] = False
            output["message"] = "An error occurred while trying to read {0}".format(self.data_file)
        elif "data" not in self.data:
            output["status"] = False
            output["message"] = "{0} does not seem to be in correct format".format(self.data_file)

        if output["status"]:
            self.verify_dependency_json()
            self.verify_tools_data()
            self.verify_drivers_json()
            self.verify_warriorspace_data()

        return output

    def verify_dependency_json(self,):
        flag = True
        if "warhorn" not in self.data["data"]:
            self.data["data"]["warhorn"] = copy.deepcopy(self.ref_data["data"]["warhorn"])
            flag = False
        if "dependency" not in self.data["data"]["warhorn"]:
            self.data["data"]["warhorn"]["dependency"] = copy.deepcopy(self.ref_data["data"]["warhorn"]["dependency"])
            flag = False
        if not isinstance(self.data["data"]["warhorn"]["dependency"], list):
            self.data["data"]["warhorn"]["dependency"] = [self.data["data"]["warhorn"]["dependency"]]

        if flag:
            data = copy.deepcopy(self.data["data"]["warhorn"]["dependency"])
            extra_dependencies = set()
            for i in range(0, len(data)):
                for key, value in data[i].items():
                    if key == "@name":
                        if value in self.dependency_dict:
                            data[i]["version"] = self.dependency_dict[value]["version"]
                            data[i]["description"] = self.dependency_dict[value]["description"]
                            try:
                                module_name = __import__(value)
                                some_var = module_name.__version__
                            except ImportError:
                                data[i]["installed"] = False
                                data[i]["matched"] = False
                            except Exception as e:
                                print "-- An Exception Occurred -- while getting details about " \
                                      "{0}: {1}".format(value, e)
                                data[i]["installed"] = False
                                data[i]["matched"] = False
                            else:
                                data[i]["installed"] = some_var
                                if self.dependency_dict[value] == some_var:
                                    data[i]["matched"] = True
                                elif self.dependency_dict[value] > some_var:
                                    data[i]["matched"] = "lower"
                                else:
                                    data[i]["matched"] = "higher"
                            break
                        else:
                            extra_dependencies.add(i)
            dependency_list = []
            for i in range(0, len(data)):
                if i not in extra_dependencies:
                    dependency_list.append(copy.deepcopy(data[i]))
            self.data["data"]["warhorn"]["dependency"] = copy.deepcopy(dependency_list)

    def verify_tools_data(self):
        if "tools" not in self.data["data"]:
            self.data["data"]["tools"] = copy.deepcopy(self.ref_data["data"]["tools"])
        else:
            for key, value in self.ref_data["data"]["tools"].items():
                if key not in self.data["data"]["tools"]:
                    self.data["data"]["tools"][key] = self.ref_data["data"]["tools"][key]

            url = self.data["data"]["tools"]["@url"]
            if url != "":
                self.data["data"]["tools"]["name"] = get_repository_name(url=url)
                self.data["data"]["tools"]["available"] = check_url_is_a_valid_repo(url=url)
            else:
                self.data["data"]["tools"]["available"] = False

    def verify_drivers_json(self):
        flag = True
        if "drivers" not in self.data["data"]:
            self.data["data"]["drivers"] = copy.deepcopy(self.ref_data["data"]["drivers"])
            flag = False

        if "repository" not in self.data["data"]["drivers"]:
            self.data["data"]["drivers"]["repository"] = copy.deepcopy(self.ref_data["data"]["drivers"]["repository"])
            flag = False

        if not isinstance(self.data["data"]["drivers"]["repository"], list):
            self.data["data"]["drivers"]["repository"] = [
                self.data["data"]["drivers"]["repository"]]

        if flag:
            for i in range(0, len(self.data["data"]["drivers"]["repository"])):
                for key, value in self.ref_data["data"]["drivers"]["repository"].items():
                    if key not in self.data["data"]["drivers"]["repository"][i]:
                        if key != "driver":
                            self.data["data"]["drivers"]["repository"][i][key] = self.ref_data["data"]["drivers"]["repository"]["key"]
                        else:
                            self.data["data"]["drivers"]["repository"][i][key] = copy.deepcopy(self.ref_data["data"]["drivers"]["repository"][key])

                            if not isinstance(self.data["data"]["drivers"]["repository"][i][key], list):
                                self.data["data"]["drivers"]["repository"][i][key] = [self.data["data"]["drivers"]["repository"][i][key]]

                url = self.data["data"]["drivers"]["repository"][i]["@url"]
                if url != "":
                    self.data["data"]["drivers"]["repository"][i]["name"] = get_repository_name(url=url)
                    available = check_url_is_a_valid_repo(url=url)
                    self.data["data"]["drivers"]["repository"][i]["available"] = available
                    if available:
                        drivers_data = []
                        drivers_index = set()
                        temp_directory = os.path.join(self.nav_obj.get_katana_dir(), "wapps", "assembler",
                                                      ".data")
                        kw_repo_obj = KwRepositoryDetails(url, temp_directory)
                        drivers = set(kw_repo_obj.get_pd_names())

                        if not isinstance(self.data["data"]["drivers"]["repository"][i]["driver"], list):
                            self.data["data"]["drivers"]["repository"][i]["driver"] = [self.data["data"]["drivers"]["repository"][i]["driver"]]

                        for j in range(0, len(self.data["data"]["drivers"]["repository"][i]["driver"])):
                            if "@name" not in self.data["data"]["drivers"]["repository"][i]["driver"][j]:
                                self.data["data"]["drivers"]["repository"][i]["driver"][j]["@name"] = self.ref_data["data"]["drivers"]["repository"]["driver"]["@name"]
                            else:
                                if self.data["data"]["drivers"]["repository"][i]["driver"][j]["@name"] in drivers:
                                    drivers.remove(self.data["data"]["drivers"]["repository"][i]["driver"][j]["@name"])
                                else:
                                    drivers_index.add(j)
                            if "@clone" not in self.data["data"]["drivers"]["repository"][i]["driver"][
                                j]:
                                self.data["data"]["drivers"]["repository"][i]["driver"][j]["@clone"] = self.ref_data["data"]["drivers"]["repository"]["driver"]["@clone"]

                        for j in range(0, len(self.data["data"]["drivers"]["repository"][i]["driver"])):
                            if j not in drivers_index:
                                drivers_data.append(copy.deepcopy(self.data["data"]["drivers"]["repository"][i]["driver"][j]))
                        self.data["data"]["drivers"]["repository"][i]["driver"] = copy.deepcopy(drivers_data)

                        for driver_name in drivers:
                            self.data["data"]["drivers"]["repository"][i]["driver"].append({"@name": driver_name, "@clone": "no"})

                        if os.path.isdir(kw_repo_obj.repo_directory):
                            delete_dir(kw_repo_obj.repo_directory)
                else:
                    self.data["data"]["drivers"]["repository"][i]["available"] = False

    def verify_warriorspace_data(self):
        flag = True
        if "warriorspace" not in self.data["data"]:
            flag = False
            self.data["data"]["warriorspace"] = copy.deepcopy(self.ref_data["data"]["warriorspace"])

        if "repository" not in self.data["data"]["warriorspace"]:
            flag = False
            self.data["data"]["warriorspace"]["repository"] = copy.copy(self.ref_data["data"]["warriorspace"]["repository"])

        if not isinstance(self.data["data"]["warriorspace"]["repository"], list):
            self.data["data"]["warriorspace"]["repository"] = [self.data["data"]["warriorspace"]["repository"]]

        if flag:
            for i in range(0, len(self.data["data"]["warriorspace"]["repository"])):
                for key, value in self.ref_data["data"]["warriorspace"]["repository"].items():
                    if key not in self.data["data"]["warriorspace"]["repository"][i]:
                        self.data["data"]["warriorspace"]["repository"][i][key] = self.ref_data["data"]["warriorspace"]["repository"][key]

                url = self.data["data"]["warriorspace"]["repository"][i]["@url"]
                if url != "":
                    self.data["data"]["warriorspace"]["repository"][i]["name"] = get_repository_name(url=url)
                    self.data["data"]["warriorspace"]["repository"][i]["available"] = check_url_is_a_valid_repo(url=url)
                else:
                    self.data["data"]["warriorspace"]["repository"][i]["available"] = False
