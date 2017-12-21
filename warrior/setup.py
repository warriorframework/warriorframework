import os
from setuptools import setup , find_packages 

__packagename__ = 'warrior'
data_files = [] 
data_point = "./warrior"
for root,dirs,fn in os.walk(data_point):
    r_files = [ os.path.join(root,x) for x in fn ] 
    data_files.append((root,r_files))

setup(name=__packagename__, 
    version="3.3.0", 
    description="Warrior framework - Please read the README files", 
    url="https://github.com/warriorframework/warriorframework", 
    author="Fujitsu - All Rights Reserved", 
    author_email="support@us.fujitsu.com", 
    license="MIT", 
    packages=find_packages(__packagename__),
    package_dir={"":__packagename__},
    data_files = data_files,
    zip_safe=False)
