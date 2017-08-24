class Installer:

    def __init__(self, base_directory, path_to_app):
        self.base_directory = base_directory
        self.path_to_app = path_to_app

    def install(self):
        output = self.__validate_app()

        if output:
            output = self.__add_app_directory()

        if output:
            output = self.__edit_urls_py()

        if output:
            output = self.__edit_settings_py()

        if not output:
            self.__revert_installation()

        return output

    def __validate_app(self):
        # validate if wf_config exists and is in the correct format
        # validate if static dir exists - and if it does, it is in the correct structure
        # validate if the include in the wf_config checks out (maps to the correct file)
        return False

    def __add_app_directory(self):
        # add app directory in warriorframework/katana/apps
        return False

    def __edit_urls_py(self):
        return False

    def __edit_settings_py(self):
        return False

    def __revert_installation(self):
        # check at which point the instalation failed
        # revert all the necessary changes
        return False