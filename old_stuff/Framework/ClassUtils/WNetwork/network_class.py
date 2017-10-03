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

""" Warrior Network module """

from Framework.ClassUtils.WNetwork.connection import Connection
from Framework.ClassUtils.WNetwork.diagnostics import Diag
from Framework.ClassUtils.WNetwork.file_ops import FileOps
from Framework.ClassUtils.WNetwork.base_class import Base


class Network(Connection, Diag, FileOps, Base):
    """This is class that inherits all other 
    classes in the Network package.
    
    Instance of this class may be used to invoke the 
    methods of all the other classes in this package.
    
    While using the instance of this class, if the Base
    classes have same method name, then the method will be executed
    based on python's inheritance MRO (Method Resolution Order)
    
    Execute 'Network.__mro__' to find out the current MRO
    Order is from left to right of the MRO.
    
    """

    def __init__(self, *args, **kwargs):
        """ Constructor"""

        super(Network, self).__init__(*args, **kwargs)




