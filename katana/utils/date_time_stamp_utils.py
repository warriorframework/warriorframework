from datetime import datetime


def get_current_datetime_stamp(time_format=None):
    """
    This function gets the current data and time.

    :return: current date time stamp in format 2017-08-11 21:52:31.432743
    """
    if time_format is None:
        value = datetime.now()
    else:
        timestamp = datetime.now().strftime(time_format)
    return timestamp
    
    
    return datetime.now()


def get_current_timestamp():
    """
    This function gets the current data and time.

    :return: current time stamp in format 21:52:31.433097
    """
    return datetime.now().time()

