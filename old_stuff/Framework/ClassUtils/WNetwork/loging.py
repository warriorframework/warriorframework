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

"""
Module to collect the response on a connected session
as a separate thread
"""

import threading
import time
import sys
import os

from Framework.ClassUtils.WNetwork.base_class import Base
from Framework.Utils.print_Utils import print_exception, print_error, \
 print_info, print_warning

try:
    if 'linux' in sys.platform:
        import pexpect
except Exception:
    print_info("{0}: {1} module is not installed".format(
     os.path.abspath(__file__), 'pexpect'))


class ThreadedLog(Base):
    """
    Collect the response from a connected session
    as a separate thread
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        super(ThreadedLog, self).__init__(*args, **kwargs)
        self.data = None
        self.stop_thread_flag = False
        self.current_thread = None
        self.stop_thread_err_msg = ""

    def start_thread(self, session):
        """
        Starts a thread using the value self.function
        if self.function is false throws an error that
        self.function is not available.
        """
        value = False
        try:
            if session:
                self.current_thread = threading.Thread(target=self.collect_log,
                                                       args=(session,))
                self.current_thread.start()
            else:
                print_error("Need a valid session to start collecting logs")
        except Exception as exception:
            print_exception(exception)
        else:
            value = True
        return value

    def stop_thread(self):
        """
        stops the thread by setting the self.stop_thread as True
        """
        self.stop_thread_flag = True
        self.stop_thread_err_msg = ""
        return

    def thread_status(self):
        """
        Returns the status of the thread
        """
        return self.current_thread.isAlive()

    def join_thread(self, timeout=30, retry=1):
        """
        Call join method of Thread class to block caller thread until
        the current_thread terminates or until the retry counter expires
        """
        if self.current_thread is not None and retry > 0:
            try:
                self.current_thread.join(timeout)
            except Exception as err_msg:
                print_warning("Joining thread failed : {}".format(err_msg))
                self.stop_thread_err_msg += str(err_msg) + "\n"

            retry -= 1
            if self.thread_status() is True and retry > 0:
                print_warning("Thread is still alive, retry joining thread."
                              "Remaining retrial attempts: {}".format(retry))
                self.join_thread(timeout, retry)

    def collect_log(self, session):
        """
        Collects the response from a connected session
        till the tread is stopped

        This function currently collects response from
        a connected pexpect spawn object using the
        pexpect read_nonblocking method
        """
        response = " "
        while not self.stop_thread_flag:
            try:
                # default timeout for pexpect-spawn object is 30s
                string = session.read_nonblocking(1024, timeout=30)
                response = response + string
                time.sleep(0.5)
                self.data = response
            # continue reading data from 'session' until the thread is stopped
            except pexpect.TIMEOUT:
                continue
            except Exception as exception:
                print_exception(exception)
                break