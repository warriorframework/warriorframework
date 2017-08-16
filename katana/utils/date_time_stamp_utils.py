from datetime import datetime


def get_current_datetime_stamp():
    """
    This function gets the current data and time.

    :return: current date time stamp in format 2017-08-11 21:52:31.432743
    """
    return datetime.now()


def get_current_timestamp():
    """
    This function gets the current data and time.

    :return: current time stamp in format 21:52:31.433097
    """
    return datetime.now().time()

