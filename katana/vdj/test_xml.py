


import os, sys
from lxml import etree
import xmltodict, json
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring


xlines = open('/home/khusain/Projects/xml-edit/warriorframework/wftests/warrior_tests/projects/pj_cond_var.xml').read();
xx = bf.data(fromstring(xlines));

print xx['Project']['Details']['Name']['$']
print xx['Project']['Details']['Engineer']
#print json.dumps(xx)
