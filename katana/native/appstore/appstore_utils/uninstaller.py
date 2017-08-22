from utils.directory_traversal_utils import get_abs_path, join_path


class Uninstaller:

    def __init__(self, base_directory, app_path):
        self.base_directory = base_directory
        self.plugin_dir = join_path(self.base_directory, "warrior", "plugins")
        self.app_dir = join_path(self.base_directory, "katana", "apps")
        self.app_path = get_abs_path(app_path, self.base_directory)

    def uninstall(self):
        output = False

        return output
