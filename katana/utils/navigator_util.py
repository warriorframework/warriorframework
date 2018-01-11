import os
from directory_traversal_utils import get_parent_directory, join_path
import subprocess


class Navigator(object):

    def __init__(self):
        self.git_url = "https://github.com/warriorframework/warriorframework.git"

    def get_katana_dir(self):
        """will get katanas main directory"""
        katana_dir = get_parent_directory(__file__, 3) + os.sep + 'katana' + os.sep
        return katana_dir

    def get_warrior_dir(self):
        """will get warriors main directory"""
        warrior_dir = get_parent_directory(__file__, 3) + os.sep + 'warrior' + os.sep
        return warrior_dir

    def get_wf_version(self):
        wf_dir = get_parent_directory(__file__, 3)
        version_file = join_path(wf_dir, "version.txt")
        with open(version_file, 'r') as f:
            data = f.readlines()
        version_line = False
        for line in data:
            if line.strip().startswith("Version"):
                version_line = line.strip()
                break
        if version_line:
            return version_line.split(":")[1].strip()
        return version_line

    def get_all_wf_versions(self):
        tags_list = False
        p = subprocess.Popen(["git", "ls-remote", "--tags", self.git_url], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        output, errors = p.communicate()
        if p.returncode != 0:
            print "-- An Error Occurred -- WarriorFramework versions could not be retrieved"
            print "-- Output -- {0}".format(output)
            print "-- Errors -- {0}".format(errors)
        else:
            temp_list = output.strip().split("\n")
            tags_list = []
            for el in temp_list:
                temp = el.split()[1].strip().split('/')[2]
                if temp.startswith("warrior"):
                    if "^" in temp:
                        temp = temp.split('^')[0]
                    tags_list.append(temp)
        return tags_list

    def search_folder_name(self, folder_name, given_dir):
        """searches for folder by name in all subdir until found or bottom level directory"""
        pass

    def get_parent_dir(self, given_dir, itter):
        """returns back the parent of given_dir and allows a user to run multipule times"""
        pass

    def get_dir_tree_json(self, start_dir_path, dir_icon=None, file_icon='jstree-file', fl=False):
        """
        Takes an absolute path to a directory(start_dir_path)  as input and creates a
        json tree having the start_dir as the root.

        This json tree can be consumed as it is by the jstree library hence the default icons
        are mapped to jstree icons.

        By default the first node in the tree will be opened


        Eg of how the json tree will look like
        {
          "text" : "Root node",
          "li_attr": {'data-path': '/path/to/node'},
          "children" : [
                            { "text" : "Child file 1",
                             "icon": "jstree-file",
                             "li_attr": {'data-path': '/path/to/node'}
                             },

                            { "text" : "Child node 2",
                             "li_attr": {'data-path': '/path/to/node'}
                             },

                            { "text" : "Child node 3",
                             "li_attr": {'data-path': '/path/to/node'},
                             "children": [
                                { "text" : "file1", "icon": "jstree-file", "li_attr": {'data-path': '/path/to/node'}},
                                { "text" : "file2", "icon": "jstree-file", "li_attr": {'data-path': '/path/to/node'}},
                                { "text" : "file3", "icon": "jstree-file", "li_attr": {'data-path': '/path/to/node'}}
                                ]
                             },

                        ]
        }


        """
        base_name = os.path.basename(start_dir_path)
        layout = {'text': base_name}
        layout['li_attr'] = {'data-path': start_dir_path}
        if not fl:
            layout["state"] = {"opened" : 'true' }
            fl = 'false'
        if os.path.isdir(start_dir_path):
            for x in os.listdir(start_dir_path):
                try:
                    children = self.get_dir_tree_json(os.path.join(start_dir_path, x), fl=fl)
                except IOError:
                    pass
                except Exception as e:
                    print "-- An Error Occurred -- {0}".format(e)
                else:
                    if "children" in layout:
                        layout['children'].append(children)
                    else:
                        layout['children'] = [children]
        else:
            layout['icon'] = file_icon
        return layout
