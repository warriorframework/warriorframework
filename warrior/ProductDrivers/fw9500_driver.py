"""" fw9500 driver """
from WarriorCore import kw_driver
import Actions.Fw9500Actions


def main(keyword, data_repository, args_repository):
    """Import all actions related to cisco driver and call the driver Utils
    to execute a keyword """
    # Declare a list of packages to be used by this driver,
    # if you want to add more packages import them outside the main function
    # and then add them to the package_list below
    package_list = [Actions.Fw9500Actions]

    return kw_driver.execute_keyword(keyword, data_repository, args_repository, package_list)
