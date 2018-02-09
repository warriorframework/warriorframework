from utils.directory_traversal_utils import join_path, get_dir_from_path, get_direct_sub_files, get_paths_of_subfiles
from utils.regex_utils import compile_regex


class GetDriversActions:

    def __init__(self, warrior_dir):
        self.warrior_dir = warrior_dir
        self.actions_dir = join_path(self.warrior_dir, "Actions")
        self.pd_dir = join_path(self.warrior_dir, "ProductDrivers")
        self.information = self._get_drivers()

    def _get_drivers(self):
        all_drivers = {}
        all_driver_files = get_direct_sub_files(self.pd_dir, abs_path=True, extension=compile_regex("^\.py$"))
        for file_path in all_driver_files:
            driver_name = get_dir_from_path(file_path).split(".")[0]
            if driver_name != "__init__":
                all_drivers[driver_name] = {"path": file_path, "actions": None}
        return all_drivers

    def get_actions(self, driver):
        flag = True
        if driver not in self.information:
            flag = False
            all_drivers = self._get_drivers()
            for key, value in all_drivers.iteritems():
                if key not in self.information:
                    self.information[key] = value
                if key == driver:
                    flag = True
        if not flag:
            print "-- An Error Occurred -- {0} does not exist in the {1} directory".format(driver, self.pd_dir)
            return False
        else:
            if self.information[driver]["actions"] is None:
                package_list = self._get_package_list(self.information[driver]["path"])
                for package in package_list:
                    actions_files = [x for x in self._get_action_files(package) if get_dir_from_path(x) != "__init__.py"]
                    for actions_file in actions_files:
                        self.information[driver]["actions"] = self._get_actions(actions_file)
            return self.information[driver]["actions"]

    def get_all_actions(self):
        for key in self.information:
            if self.information[key]["actions"] is None:
                self.information[key]["actions"] = self.get_actions(key)
        return self.information

    def _get_package_list(self, driver_path):
        with open(driver_path, 'r') as f:
            data = f.readlines()
        list_of_pkgs = []
        package_list = []
        for line in data:
            if line.strip().startswith('package_list'):
                temp = line.split("[")[1].strip()[:-1]
                list_of_pkgs = [x.strip() for x in temp.split(",")]
                break
        for pkg in list_of_pkgs:
            temp = pkg.split(".")
            path = self.warrior_dir
            for i in range(0, len(temp)):
                path = join_path(path, temp[i])
            package_list.append(path)
        return package_list

    def _get_actions(self, actions_file):
        actions = {}
        with open(actions_file, 'r') as f:
            data = f.readlines()
        start = False
        comment_start = False
        kw_blocks = []
        keyword_block = ""
        for line in data:
            if not start:
                if line.strip().startswith("wdesc"):
                    keyword_block += line
                    kw_blocks.append(keyword_block)
                if line.strip().startswith("def "):
                    if "__init__" not in line:
                        start = True
                        keyword_block = line
            else:
                keyword_block += line
                if comment_start:
                    if line.strip().endswith('"""'):
                            start = False
                            comment_start = False
                elif line.strip().startswith('"""'):
                    comment_start = True

        for block in kw_blocks:
            actions.update({self.__get_kw_name(block): {
                "wdesc": self.__get_wdesc(block),
                "comments": self.__get_comments(block),
                "arguments": self.__get_arguments(block),
                "signature": self.__get_signature(block)
                }
            })
        return actions

    @staticmethod
    def _get_action_files(actions_directory):
        return get_paths_of_subfiles(actions_directory, extension=compile_regex("^\.py$"))

    @staticmethod
    def __get_kw_name(kw_block):
        lines = kw_block.splitlines()
        return lines[0].strip().split("(")[0].split()[1]

    @staticmethod
    def __get_wdesc(kw_block):
        lines = kw_block.splitlines()
        return lines[-1].strip().split("=")[1].strip().strip('"')

    @staticmethod
    def __get_comments(kw_block):
        lines = kw_block.splitlines()
        start = False
        comments = ""
        for line in lines:
            if not start:
                if line.strip().startswith('"""'):
                    start = True
                    comments = line.strip().strip('"""') + "\n"
            elif start:
                comments += line.strip() + "\n"
                if line.strip().endswith('"""'):
                    comments = comments.strip("\n").strip('"""')
                    comments += "\n"
                    break
        return comments

    def __get_arguments(self, kw_block):
        arguments = self.__get_signature(kw_block)
        return [x.strip().split("=")[0].strip() for x in arguments[(arguments.find("(") + 1):-1].split(",")][1:]

    @staticmethod
    def __get_signature(kw_block):
        lines = kw_block.splitlines()
        signature = ""
        for line in lines:
            line = line.strip()
            signature += line
            if line.endswith("):"):
                break
        return signature.strip()[4:-1]
