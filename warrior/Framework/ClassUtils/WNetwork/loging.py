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
from Framework.ClassUtils.WNetwork.base_class import Base
from Framework.Utils.print_Utils import print_exception, print_error

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
        return

    def thread_status(self):
        """
        Returns the status of the thread
        """
        return self.current_thread.isAlive()

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
                string = session.read_nonblocking(1024, timeout=None)
                response = response + string
                time.sleep(0.5)
                self.data = response
            except Exception as exception:
                print_exception(exception)
                break