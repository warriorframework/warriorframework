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
from Framework.Utils.testcase_Utils import pNote

def lab_eqpt_status (orig_date, check_criteria, pass_msg, fail_msg):
    """
    This is meant to be use for Demo purpose only. Do not use
    for project related KW.
    Check if delta time between input orig_date to now is less
    than check_criteria in yr, then it passes
    """
    status = True
    yr = int(orig_date.split("-")[0])
    mo = int(orig_date.split("-")[1])
    dy = int(orig_date.split("-")[2])
    diff = datetime.datetime.today()-datetime.datetime(yr, mo, dy)
    year, days = divmod(diff.days, 365)
    if year >= check_criteria and days >= 0:
        pNote(fail_msg)
        status = False
    else:
        pNote(pass_msg)
    return status