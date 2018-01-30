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

""" Base class for Network package """

class Base(object):
    """This is a Base class.
    
    This class in inherited in all classes
    of the Network package. 
    
    Inheriting this class avoids the problem of 
    calling object with **args/**kwargs while 
    using super method (while invoking 
    the methods of the Network package using
    an instance of Network class) """
    
    def __init__(self, *args, **kwargs):
        pass
