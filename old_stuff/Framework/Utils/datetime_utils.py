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
              1. Time delta = Returns time difference between the present system time and between the time
                  stamp which comes as argument in the format of seconds.
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