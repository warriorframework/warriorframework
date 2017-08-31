
import os

class Navigator:

    def __init__(self):
        pass

    def cut_it(self, given_str, full_str):
        i = full_str.index(given_str)
        return full_str[:i+len(given_str)]

    def get_katana_dir(self):
        """will get katanas main directory"""
        current_dir = os.getcwd()
        return self.cut_it('warriorframework/katana', current_dir)

    def get_warrior_dir(self):
        """will get warriors main directory"""
        return self.get_katana_dir().replace('warriorframework/katana', 'warriorframework/warrior')

    def search_folder_name(self, folder_name, given_dir):
        """searches for folder by name in all subdir until found or bottom level directory"""
        pass

    def get_parent_dir(self, given_dir, itter):
        """returns back the parent of given_dir and allows a user to run multipule times"""
        pass

    def get_dir_tree_json(self, start_dir_path, dir_icon=None, file_icon='jstree-file'):
        """
        Takes an absolute path to a directory(start_dir_path)  as input and creates a
        json tree having the start_dir as the root. 
        
        This json tree can be consumed as it is by the jstree library hence the default icons
        are mapped to jstree icons.
        
        
        Eg of how the json tree will look like with default key value pairs supported by this function today.
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
               
        layout = {'text': os.path.basename(start_dir_path)}
        if os.path.isdir(start_dir_path):        
            layout['li_attr'] = {'data-path': start_dir_path}
            layout['icon'] = dir_icon if dir_icon else ""        
            layout['children'] = [self.get_dir_tree_json(os.path.join(start_dir_path, x))\
                                  for x in os.listdir(start_dir_path)]
        else:
            layout['icon'] = file_icon
        return layout
    