from setuptools import setup, find_packages

package_name = "warriorframework"
package_version = "3.7.0"

setup(
    name=package_name,
    version=package_version,
    author="warriorframework org",
    url="https://github.com/warriorframework/warriorframework",
    install_requires=["pexpect==4.2", "requests==2.9.1", "selenium==2.53.0"],

)
