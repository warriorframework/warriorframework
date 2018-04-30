'''
Copyright 2017, Fujitsu Network Communications, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


import datetime
import time
from Framework.Utils.print_Utils import print_without_logging, print_error, print_warning


def wait_for_timeout(wait_time, unit="SECONDS"):
    """
    Warrior, Wait till the time is a generic wait. The Wait is informed to the user as a countdown.

    :Arguments:
        1.wait_time: Time for Warrior wait.
        2.unit: The unit of Time supported are
                  1. Second (default)
                  2. Minute
                  3. Hour
                  4. Day
                  5. Month (30 days is assumed for one Month)
                  6. Year (365 days is assumed for one Year)
    :return:
        Status = Bool
    """
    try:
        wait_time = float(wait_time)
        if unit.upper() in ["SECOND", "SECONDS", "SEC", "SECS"]:
            seconds = wait_time
        elif unit.upper() in ["MINUTE", "MINUTES", "MIN", "MINS"]:
            seconds = 60 * wait_time
        elif unit.upper() in ["HOUR", "HOURS"]:
            seconds = 60 * 60 * wait_time
        elif unit.upper() in ["DAY", "DAYS"]:
            seconds = 24 * 60 * 60 * wait_time
        elif unit.upper() in ["MONTH", "MONTHS"]:
            seconds = 30 * 24 * 60 * 60 * wait_time
        elif unit.upper() in ["YEAR", "YEARS"]:
            seconds = 365 * 24 * 60 * 60 * wait_time
        else:
            print_warning('The supported unit of seconds is Seconds/Minutes/Hours/Months/Years'
                          'The default unit of Seconds would be used')
        for sec in range(int(seconds), 0, -1):
            print_without_logging("Remaining time available is {0} seconds {1}"
                                  .format(sec, '\033[1A\r'))
            time.sleep(1)
        return True
    except TypeError:
        print_warning('Unable to parse wait_time value, Please use int/float as wait_time value.')
        return False
    except Exception as e:
        print_error('Encountered unexpected error {0} Unable to wait as requested'.format(e))
        return False


def get_current_timestamp():
    """Returns system current timestamp with date and month
     Arguments:
        No args

        Returns:
              1. Current System Time in the format of Year, Month, Date, Time(without microseconds)
                     eg: 2015-04-27 09:48:21
    """

    currentdate = datetime.datetime.now().replace(microsecond=0)
    return currentdate


def get_time_delta(start_time, end_time=None):
    """Returns system current timestamp with date and month
      Arguments:
              1. time_stamp = time stamp in the format of system datetime(without microseconds)
                        eg: 2015-04-27 09:48:21

        Returns:
              1. Time delta = Returns time difference between the present system time and between
                 the time stamp which comes as argument in the format of seconds.
                     eg: 212342.0
    """
    if end_time is None:
        end_time = datetime.datetime.now().replace(microsecond=0)
    time_delta = end_time - start_time
    return time_delta.total_seconds()


def get_hms_for_seconds(seconds):
    """ prints number of seconds in hours:minutes:seconds format"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    hms = "%d hours: %02d min: %02d sec" % (h, m, s)
    return hms
