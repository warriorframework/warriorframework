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

"""This is utility for data encryption """

import os
import base64

from Framework.Utils import file_Utils
from Framework.Utils.print_Utils import print_exception, print_error, print_info
from Framework.Utils.testcase_Utils import pNote
import Tools

try:
    MOD = 'Pycryptodome'
    from Crypto.Cipher import AES
    from Crypto import Random
except ImportError, err:
    pNote("Please Install Pycryptodome 3.6.1 and above", "error")

from Framework.Utils.print_Utils import print_error

def get_key(encoded_key):
    """
    Function that returns enc instance using
    secret key, passed to this
    function or read from secret.key file

    Args:
        encoded_key - False or base64 secrety key for encryption

    Return:
        IV - Random seed used to enc
        CIPHER - Enc instance used to for encryption
    """
    IV = None
    CIPHER = None
    if encoded_key is False:
        try:
            MYFILE = Tools.__path__[0]+os.sep+"admin"+os.sep+'secret.key'
            with open(MYFILE, 'r') as myfileHandle:
                encoded_key = myfileHandle.read()
        except IOError:
            print_error("Could not find the secret.key file in Tools/Admin!")
    try:
        IV = Random.new().read(AES.block_size)
        CIPHER = AES.new(base64.b64decode(encoded_key), AES.MODE_CFB, IV)
    except Exception as e:
        print_exception("Some problem occured: {0}".format(e))

    return IV, CIPHER


"""This is encryption"""
def encrypt(message, encoded_key=False):
    """This is encryption"""
    IV, CIPHER = get_key(encoded_key)
    msg = "Encrypted text could not be generated because the secret key in " \
          "the secret.key file seems to be incorrect."
    if IV is not None and CIPHER is not None:
        msg = IV+CIPHER.encrypt(message)
        msg = msg.encode("hex")
    return msg

"""This is decryption"""
def decrypt(message, encoded_key=False):
    """This is decryption"""
    IV, CIPHER = get_key(encoded_key)
    try:
        return CIPHER.decrypt(message.decode("hex"))[len(IV):]
    except BaseException:
        return message

def set_secret_key(plain_text_key):
    """
    Function that saves base64 encoded
    format of  secret key, passed to this
    function and saved to secret.key file

    Args:
        plain_text_key - Plain text key, that is is used for encryption

    Return:
        status - True if key is base64 encoded and saved
                 False if not saved
        key - base64 endoced key
    """
    encoded_key = False
    # Checks the length of the plain text secret key
    if not len(plain_text_key) == 16:
        print_error("The secret key needs to be exactly 16 characters in length"
                    ". {0} is {1} characters in length."
                    .format(plain_text_key, len(plain_text_key)))
        status = False
    else:
        # Gets base 64 encoding for the plain text secret key
        encoded_key = base64.b64encode(plain_text_key)

        # Gets path to Tools
        path = Tools.__path__[0]

        # creates admin directory if that does not exist
        path = file_Utils.createDir(path, "admin")

        # creates secret.key file if it does not exists. Writes the base 64
        # encoded key to it.
        path = os.path.join(path, "secret.key")
        with open(path, 'w') as f:
            f.write(encoded_key)

        status = True
    return status, encoded_key
