"""" file driver """
from WarriorCore import kw_driver
import Actions.FileActions


def main(keyword, data_repository, args_repository):
    """Import all actions related to file driver and call the driver Utils
    to execute a keyword """
    # Declare a list of packages to be used by this driver,
    # if you want to add more packages import them outside the main function
    # and then add them to the package_list below
    package_list = [Actions.FileActions]

    return kw_driver.execute_keyword(keyword, data_repository, args_repository,
                                     package_list)
