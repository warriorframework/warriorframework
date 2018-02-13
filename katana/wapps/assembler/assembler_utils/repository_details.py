import copy
import os
import re
from utils.directory_traversal_utils import get_paths_of_subfiles, get_dir_from_path, delete_dir


class RepositoryDetails:

    def __init__(self, repo_url, directory):
        self.url = repo_url
        self.base_directory = directory
        self.repo_name = self._get_repository_name()
        self.repo_directory = self._clone_repository()

    def _get_repository_name(self):
        li_temp_1 = self.url.rsplit('/', 1)
        return li_temp_1[1][:-4] if \
            li_temp_1[1].endswith(".git") else li_temp_1[1]

    def _clone_repository(self):
        repo_directory = os.path.join(self.base_directory, self.repo_name)
        if os.path.isdir(repo_directory):
            delete_dir(repo_directory)
        current_directory = os.getcwd()
        os.chdir(self.base_directory)
        os.system("git clone {0}".format(self.url))
        os.chdir(current_directory)
        return os.path.join(self.base_directory, self.repo_name)


class KwRepositoryDetails(RepositoryDetails):

    def __init__(self, repo_url, directory):
        RepositoryDetails.__init__(self, repo_url, directory)
        self.actions_dir = os.path.join(self.repo_directory, "Actions")
        self.pd_dir = os.path.join(self.repo_directory, "ProductDrivers")
        self.framework_dir = os.path.join(self.repo_directory, "Framework")
        self.driver_files_list = []
        self.actions_for_driver_dict = {}

    def get_pd_file_list(self):
        self.driver_files_list = []
        temp = get_paths_of_subfiles(self.pd_dir, extension=re.compile("\.py$"))
        for driver_file in temp:
            if not get_dir_from_path(driver_file) == "__init__.py":
                self.driver_files_list.append(driver_file)
        return self.driver_files_list

    def get_pd_names(self):
        if len(self.driver_files_list) == 0:
            self.driver_files_list = self.get_pd_file_list()
        driver_names = []
        for driver in self.driver_files_list:
            driver_names.append(get_dir_from_path(driver))
        return driver_names

    def get_actions_in_driver(self, driver_file=None):
        if not self.actions_for_driver_dict:
            self.actions_for_driver_dict = self.__map_actions_to_driver()
        if driver_file is not None:
            if driver_file in self.actions_for_driver_dict:
                return self.actions_for_driver_dict[driver_file]
            else:
                print "-- An Error Occurred -- {0} not found".format(driver_file)
                return False
        else:
            return self.actions_for_driver_dict

    def __map_actions_to_driver(self):
        actions_for_driver_dict = self.__get_action_packages()
        for driver_file, actions_package_list in actions_for_driver_dict.items():
            actions_dir_paths = []
            for actions_package in actions_package_list:
                actions_dir_paths.append(os.path.join(self.repo_directory, actions_package.replace(".", os.sep)))
            actions_file_paths = []
            for actions_package in actions_dir_paths:
                temp = get_paths_of_subfiles(actions_package, extension=re.compile("\.py$"))
                for actions_file in temp:
                    if not get_dir_from_path(actions_file) == "__init__.py":
                        actions_file_paths.append(actions_file)
            actions_for_driver_dict[driver_file] = copy.copy(actions_file_paths)
        return actions_for_driver_dict

    def __get_action_packages(self):
        actions_for_driver_dict = {}
        actions_list = []
        for driver_file in self.driver_files_list:
            with open(driver_file, "r") as load_profile:
                read_it = load_profile.read()
            import_actions = []
            for line in read_it.splitlines():
                if line.startswith("import"):
                    import_actions.append(line)
            for word in self.__words(import_actions):
                if word != "import":
                    actions_list.append(word)
            actions_for_driver_dict[driver_file] = copy.copy(actions_list)
        return actions_for_driver_dict

    def __words(self, line):
        """ This function gives out the words by splitting the lines

        :Arguments:

        1. line (list) = list of the lines

        :Returns:

        list = list of words in the line

        """
        line_stream = iter(line)
        for line in line_stream:
            for word in line.split():
                yield word
