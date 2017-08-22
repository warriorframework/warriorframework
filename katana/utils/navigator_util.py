
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
