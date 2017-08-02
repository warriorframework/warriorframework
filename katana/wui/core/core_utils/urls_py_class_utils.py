import os
from utils.file_utils import readlines_from_file
from utils.string_utils import remove_trailing_characters_from_list, \
    remove_trailing_characters_from_string, split_str_at_last_index


class UrlsFileDetailsClass():

    def __init__(self, file_path):
        self.file_path = file_path
        self.url_dict = {}

    def get_urls_file_path(self):
        """
        This function returns the absolute path to the urls.py file
        Returns:
            self.file_path: Absolute path to urls.py

        """
        return self.file_path

    def update_urls_file_path(self, file_path):
        """
        This function updates the file_path
        Args:
            file_path: Absolute path to the urls.py file

        """
        self.file_path = file_path

    def get_urls_from_urls_py(self, start="urlpatterns = [", end="]\n", formatting_list=None, url_formatting_list=None, include_formatting_list=None):
        """
        This function gets the urls from the urls.py file.

        Args:
            start:
            end:
            formatting_list:
            url_formatting_list:
            include_formatting_list:

        Returns:

        """
        if formatting_list is None:
            formatting_list = [" ", "url(", ",\n", ")"]
        if url_formatting_list is None:
            url_formatting_list = [" ", "r", "'", "^"]
        if include_formatting_list is None:
            include_formatting_list = [" ", "include(", ")", "'"]

        urls_list = readlines_from_file(self.file_path, start=start, end=end)
        urls_list = remove_trailing_characters_from_list(urls_list, formatting_list)

        for i in range(0, len(urls_list)):
            temp = urls_list[i].split(",")

            temp[0] = remove_trailing_characters_from_string(temp[0], url_formatting_list)
            temp[0] = os.sep + temp[0]

            temp[1] = remove_trailing_characters_from_string(temp[1], include_formatting_list)

            output = split_str_at_last_index(temp[1], ".")
            self.url_dict[output] = temp[0]

        return self.url_dict