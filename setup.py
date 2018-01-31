"""
setup file for warriorframework
"""
from setuptools import setup

PACKAGE_NAME = "warriorframework"
PACKAGE_VERSION = "3.7.0"

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author="warriorframework org",
    url="https://github.com/warriorframework/warriorframework",
    install_requires=["pexpect==4.2", "requests==2.9.1", "selenium==2.53.0"],

)
