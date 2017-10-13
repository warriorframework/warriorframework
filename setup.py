
from setuptools import setup 

__packagename__ = 'warriorframework'
data_files = [] 
data_point = os.path.join(__packagename__,'warrior') 
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
    packages=[__packagename__], 
    data_files = data_files,
    zip_safe=False)
