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

import json
import sys
import difflib
import os
import re
import file_Utils
import os.path

from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import tostring
from Framework.OSS import xmltodict
from print_Utils import print_debug, print_info, print_error, print_warning, print_exception
from collections import OrderedDict

try:
    from lxml import etree, objectify
except ImportError as err:
    print_error("Module lxml is not installed, Refer to the exception trace below for more details")
    print_exception(err)

def create_subelement(parent, tag, attrib):
    """Creates a subelement with given tag
    and attributes under the parent element """
    subelement = ElementTree.SubElement(parent, tag, attrib)
    return subelement

def getValuebyTag (filename, tag):
    """Get the value from the tag name from the xml file"""
    doc = minidom.parse(filename)
    itemlist = doc.getElementsByTagName(tag)[0].toxml()
    itemvalue = itemlist.replace('<' + tag + '>', '').replace('</' + tag + '>', '')
    return itemvalue

def getValuebyAttribute (filename, attribute, tag):
    """Get the value of the attribute in a tag from the xml file"""
    doc = minidom.parse(filename)
    itemlist = doc.getElementsByTagName(tag)[0].toxml()
    return itemlist.attributes[attribute].value

def get_first_child(node):
    """Gets the first child of a given node
    Returns None if there is no child for the node."""
    element = None
    for child in node:
        element = child
    return element

def get_last_child(node):
    """Gets the last child of a given node
    Returns None if there is no child for the node."""
    element = None
    for child in node.iter():
        element = child
    return element

def getNodeCount(filename, node):
    """Get the Number of subnodes under the node specified in the xml file"""
    with open (filename, 'rt') as f:
        tree = ElementTree.parse(f)
    count = 0
    for node in tree.findall('.//' + node):
        count += 1
    return count

def get_tree_from_file(filepath):
    """ Get the tree from the xml file"""
    if file_Utils.fileExists(filepath):
            tree = ElementTree.parse(filepath)
    else:
        print_error("xml file does not exist in provided path {0}".format(filepath))
        tree = False
    return tree

def getRoot(filename):
    """ Get the Root of the xml file"""
    try:
        tree = ElementTree.parse(filename)
        root = tree.getroot()
    except ElementTree.ParseError, msg:
        print_error("The xml file: {0} is {1}".format(filename, msg))
        print_info("DONE 1")
        sys.exit(0)
    return root

def convert_element_to_string(element):
    """Converts the provided xml element to string """
    string = tostring(element)
    return string

def getNodeValuebyAttribute (filename, node, attribute):
    """ Get Node value from the Attribute from the xml fle"""
    value = None
    root = getRoot (filename)
    element = root.find(node)
    if element is not None:
        value = element.get(attribute)
    return value
#     for testdata in root.find(node):
#         value = testdata.get(attribute)
#         return value

def nodeExists (filename, node):
    """Find whether the Node exists in the xml file"""
    count = getNodeCount (filename, node)
    status = False
    if count > 0:
        status = True
    return status

def getNodeText(filename, node):
    """Get the Text of the Node"""
    root = ElementTree.parse(filename).getroot()
    node = root.find(node)
    if node is not None:
        text = node.text
        return text
    else: print_warning("node not found")


def get_node(filename, node_name):
    """Gets seraches for a node under the root and returns the node"""
    root = ElementTree.parse(filename).getroot()
    node = root.find(node_name)
    node = root.find(node_name)
    if node is not None:
        return node
    else: return False

def write_tree_to_file(root, file_path):
    """Modify/Write to the xml file(filepath) """
    tree = ElementTree.ElementTree(root)
    tree.write(file_path)


def get_matching_firstlevel_children_from_root(filename, child_tag):
    """Takes a xml file as input and returns a list of first
    child elements to the root that matches the provided tag """
    root = getRoot(filename)
    child_list = root.findall(child_tag)
    return child_list

def get_matching_firstlevel_children_from_node(node, child_tag):
    """Takes a xml file as input and returns a list of first
    child elements to the root that matches the provided tag """
    child_list = node.findall(child_tag)
    return child_list


def get_node_list_iterative(filename, node_name):
    """Find all matching subelements and returns iterable elements"""
    root = ElementTree.parse(filename).getroot()
    node_list = root.iterfind(node_name)
    return node_list

def getChildNodeTextaslist (parentnode, childnode):
    """Get all child node text of the parent node and return as a list"""
    textlist = []
    for childnode in parentnode.findall(childnode):
        textlist.append(childnode.text)
    return textlist

def get_text_from_direct_child(parentnode, childname):
    """Takes a parent node element as input
    Searches for the first child with the the provided name under the parent node
    If child is present return the text of the child (returned text will be empty if the child has no text
    Returns False if child is not found under the parent
    """
    childnode = parentnode.find(childname)
    if childnode is not None:
        return childnode.text
    else: return False

def get_child_node_list(parentnode):
    """Returns the list of children under to a provided parent node """
    child_nodelist = []
    for child in parentnode:
        child_nodelist.append(child)
    return child_nodelist

def get_attributevalue_from_directchildnode (parentnode, childname, attribute):
    """ Takes a parent node element as input
    Searches for the first child with the provided name under the parent node
    If child is present returns the value for the requested child attribute (the returns None if
    the child does not have that attributte)
    Returns False if child is not found under the parent
    """
    childnode = parentnode.find(childname)
    if childnode is not None:
        value = childnode.get(attribute)
        return value
    else: return False

def getNodeListbyAttribute (parentnode, childnode, attribute):
    """Traverse through all the child node from the parent node and get the attribute from each
    child node and return all the attrubute as a list"""
    textlist = []
    for childnode in parentnode.findall(childnode):
        text = childnode.get(attribute)
        textlist.append(text)
    return textlist

def getChildTextbyParentAttribute (datafile, pnode, patt, pattval, cnode):
    """
    Seraches XML file for the parent node with a specific value. Finds the child node and returns
    its text
    datafile = xml file searched
    pnode = parent node
    patt = parent node attribute
    patval = parent node attribute value
    cnode = child node
    """
    tree = ElementTree.parse(datafile)
    root = tree.getroot()
    value = False
    for node in root.findall(pnode):
        attribute = node.get(patt)
        if attribute == pattval:
            cnode = node.find(cnode)
            if cnode is not None:
                value = cnode.text
            else:
                return None
            break
    return value

def getChildTextbyParentTag (datafile, pnode, cnode):
    """
    Seraches XML file for the first parent. Finds the child node and returns its text
    datafile = xml file searched
    pnode = parent node
    cnode = child node
    """
    value = False
    tree = ElementTree.parse(datafile)
    root = tree.getroot()
    node = root.find(pnode)
    if node is not None:
        child = node.find(cnode)
        if child is not None:
            value = child.text
            return value
        else:
            # print_info("could not find cnode under the given pnode")
            return value
    else:
        # print_info("could not find pnode in the provided file")
        return value


def getChildAttributebyParentTag (datafile, pnode, cnode, cattrib):
    """Find the attribute in child node by traversing through the parent node
    in the given file
    datafile = xml file searched
    pnode = parent node
    cnode = child node
    cattrob = child node attrib
    """
    tree = ElementTree.parse(datafile)
    root = tree.getroot()
    node = root.find(pnode)
    if node is not None:
        child = node.find(cnode)
        if child is not None:
            value = child.get(cattrib)
            return value
        else:
            # print_info("could not find cnode under the given pnode")
            return False
    else:
        # print_info("could not find pnode in the provided file")
        return False

def getChildTextbyOtherChild (datafile, pnode, cnode, cvalue, rnode):
    """
    Searches XML file for the parent node. Finds the 1st child node and checks its value
    if value is a match, then search for second child and return its value
    datafile = xml file searched
    pnode = parent node
    cnode = child node
    cvalue = child node value
    rnode = reference node or False if doesn't exist
    """
    tree = ElementTree.parse(datafile)
    root = tree.getroot()
    rnodev = False

    for node in root.findall(pnode):
        value = node.find(cnode).text
        if value == cvalue:
            # print_debug("-D- rnode: '%s'" % rnode)
            if node.find(rnode) is not None:
                rnodev = node.find(rnode).text
                break
    return rnodev


def verifyParentandChildrenMatch (datafile, pnode, cnode, cvalue, rnode, rvalue):
    """
    Searches XML file for the parent node. Finds the 1st child node and checks its value
    if value is a match, then search for second child and check if its value matches
    datafile = xml file searched
    pnode = parent node
    cnode = child node
    cvalue = child node value
    rnode = reference node
    rvalue = refernce node value
    """
    tree = ElementTree.parse(datafile)
    root = tree.getroot()
    status = False
    for node in root.findall(pnode):
        value = node.find(cnode).text
        if value == cvalue:

            if node.find(rnode) is not None:
                cnodev = node.find(rnode).text
                # print_debug("-D- cnodev: '%s', rvalue : '%s'" % (cnodev, rvalue))
                if cnodev == rvalue:
                    # print_debug("-D- BREAK END METHOD verifyParentandChildrenMatch_Status '%s'" % status)
                    return True
    return status


def getNodebyParentandChildrenMatch (datafile, pnode, cnode, cvalue, rnode, rvalue, lnode):
    """
    Searches XML file for the parent node. Finds the 1st child node and checks its value
    if value is a match, then search for second child and check if its value matches. If
    that is a match, then obtain the value of the third child
    datafile = xml file searched
    pnode = parent node
    cnode = child node
    cvalue = child node value
    rnode = reference node
    rvalue = refernce node value
    lnode = lastnode
    """
    tree = ElementTree.parse(datafile)
    root = tree.getroot()
    lnodev = False
    for node in root.findall(pnode):
        value = node.find(cnode).text
        if value == cvalue:
            if node.find(rnode) is not None:
                rnodev = node.find(rnode).text
                # print_debug("rnodev : '%s'" % rnodev)
                if rnodev == rvalue:
                    lnodev = node.find(lnode).text
                    break
            print_debug("getNodebyParentandChildrenMatch_Status: %s" % lnodev)
    return lnodev


def verifyNodesValueMatch (datafile, pnode, cnode, cvalue, rnode, rvalue, bnode, bvalue, dnode=None, dvalue=None):
    """
    Searches XML file for the parent node. Finds the 1st child node and checks its value
    if value is a match, then search for second child and check if its value matches
    datafile = xml file searched
    pnode = parent node
    cnode = child node
    cvalue = child node value
    rnode = reference node
    rvalue = refernce node value
    """
    try:
        tree = ElementTree.parse(datafile)
        root = tree.getroot()
    except Exception, e:
        print_error("unexpected error %s" % str(e))
        return False

    else:
        status = False

        for node in root.findall(pnode):

            value = node.find(cnode).text
            if value != cvalue:
                continue

            if node.find(rnode) == None:
                continue

            rnodev = node.find(rnode).text

            if rnodev != rvalue:
                continue


            if node.find(bnode) == None:
                continue

            bnodev = node.find(bnode).text

            if bnodev != bvalue:
                continue

            if dnode == None:
                status = True
                # print_debug("BREAK dnode = None, status '%s'" % status)
                return status

            elif node.find(dnode) is not None:
                dnodev = node.find(dnode).text
                # print_debug("Values : dnodev :%s, dvalue : %s" % (dnodev, dvalue))
                if dnodev == dvalue:
                    # print_debug("MATCH: dnode : %s, dvalue : %s, dnodev : %s" % (dnode, dvalue, dnodev))
                    status = True
                    # print_debug("BREAK END METHOD verifyParentandChildrenMatch_Status %s " % status)
                    return status

    print_debug("FINAL END METHOD verifyParentandChildrenMatch_Status %s" % status)
    return status

def getElementsListWithTagAttribValueMatch(datafile, tag, attrib, value):
    """
    This method takes an xml document as input and finds all the sub elements (parent/children)
    containing specified tag and an attribute with the specified value.

    Returns a list of matching elements.

    Arguments:
    datafile = input xml file to be parsed.
    tag = tag value of the sub-element(parent/child) to be searched for.
    attrib = attribute name for  the sub-element with above given tag should have.
    value = attribute value that the sub-element with above given tag, attribute should have.
    """
    element_list = []
    root = ElementTree.parse(datafile).getroot()
    for element in root.iterfind(".//%s[@%s='%s']" % (tag, attrib, value)):
        element_list.append(element)
    return element_list

def getElementWithTagAttribValueMatch(start, tag, attrib, value):
    """
    When start is an xml datafile, it finds the root and first element with:
        tag, attrib, value.
    Or when it's an xml element, it finds the first child element with:
        tag, attrib, value.
    If there is not a match, it returns False.
    """
    node = False
    if isinstance(start, (file, str)):
        # check if file exist here
        if file_Utils.fileExists(start):
            node = ElementTree.parse(start).getroot()
        else:
            print_warning('The file={0} is not found.'.format(start))
    elif isinstance(start, ElementTree.Element):
        node = start
    if node is not False and node is not None:
        elementName = ".//%s[@%s='%s']" % (tag, attrib, value)
        element = node.find(elementName)
    else:
        element = node
    return element

def getChildElementsListWithTagAttribValueMatch(parent, tag, attrib, value):
    """
    This method takes a parent element as input and finds all the sub elements (children)
    containing specified tag and an attribute with the specified value.

    Returns a list of child elements.

    Arguments:
    parent = parent element
    tag = tag value of the sub-element(child) to be searched for.
    attrib = attribute name for  the sub-element with above given tag should have.
    value = attribute value that the sub-element with above given tag, attribute should have.
    """
    child_elements = parent.findall(".//%s[@%s='%s']" % (tag, attrib, value))
    return child_elements

def getElementListWithSpecificXpath(datafile, xpath):
    """
    This method takes an xml document as input and finds all the sub elements (parent/children)
    containing specified xpath

    Returns a list of matching elements.

    Arguments:
    parent = parent element
    xpath = a valid xml path value as supported by python, refer https://docs.python.org/2/library/xml.etree.elementtree.html
    """
    element_list = []
    root = ElementTree.parse(datafile).getroot()
    for element in root.iterfind(xpath):
        element_list.append(element)
    return element_list

def getElementStringWithSpecificXpath(datafile, xpath):
    """
    This method takes an xml document as input and finds the first sub element (parent/children)
    containing specified xpath

    Returns the element as a string

    Arguments:
    parent = parent element
    xpath = a valid xml path value as supported by python, refer https://docs.python.org/2/library/xml.etree.elementtree.html
    """
    root = ElementTree.parse(datafile).getroot()
    element = root.find(xpath)
    ele_string = ElementTree.tostring(element)
    return ele_string

def getConfigElementTextWithSpecificXpath(datafile, xpath):
    """
    This method takes an xml document as input and finds the first sub element (parent/children)
    containing specified xpath which should be a filepath to a netconf config file

    Returns the element text attribute

    Arguments:
    parent = parent element
    xpath = a valid xml path value as supported by python, refer https://docs.python.org/2/library/xml.etree.elementtree.html
    """
    root = ElementTree.parse(datafile).getroot()
    elem1 = root.find(xpath).text

    elem2_root = ElementTree.parse(elem1)
    elem2 = elem2_root.find('config')
    elem2_string = ElementTree.tostring(elem2)
    return elem2_string

def getChildElementWithSpecificXpath(start, xpath):
    """
    This method takes a xml file or parent element as input and finds the first child
    containing specified xpath

    Returns the child element.

    Arguments:
    start = xml file or parent element
    xpath = a valid xml path value as supported by python, refer https://docs.python.org/2/library/xml.etree.elementtree.html
    """
    node = False
    if isinstance(start, (file, str)):
        # check if file exist here
        if file_Utils.fileExists(start):
            node = ElementTree.parse(start).getroot()
        else:
            print_warning('The file={0} is not found.'.format(start))
    elif isinstance(start, ElementTree.Element):
        node = start
    if node is not False or node is not None:
        element = node.find(xpath)
    else:
        element = False
    return element


def getChildElementsListWithSpecificXpath(parent, xpath):
    """
    This method takes a parent element as input and finds all the children
    containing specified xpath

    Returns a list of child elements.

    Arguments:
    parent = parent element
    xpath = a valid xml path value as supported by python, refer https://docs.python.org/2/library/xml.etree.elementtree.html
    """
    child_elements = parent.findall(xpath)
    return child_elements

"""Methods to create elements"""
def create_element(tagname="", text="", **kwargs):
    """create an xml element with given name and a dict of attribute"""
    elem = ElementTree.Element(tagname)
    for key, val in kwargs.items():
        elem.set(str(key), str(val))
    elem.text = text
    return elem

def safe_subelement(parent, tagname, text="", **kwargs):
    """
        create or overwrite a child element under the parent
    """
    if parent.find(tagname) is not None:
        # Overwrite the child
        ele = parent.find(tagname)
        ele.text = text
        ele.attrib = kwargs
    else:
        ele = ElementTree.SubElement(parent, tagname)
        ele.text = text
        ele.attrib = kwargs
    return ele

""" Below are xml parsing methods using python's minidom module """

def get_document_root(filename):
    """Returns the root element of a xml document """
    doc = minidom.parse(filename)
    root = doc.documentElement
    return root

def get_all_child_nodes(parent_node):
    """Takes a minidom parent node as input and returns a list of all child nodes """

    child_node_list = parent_node.childNodes
    return child_node_list


def get_elements_by_tagname_ignore_ns(filename, element_tag):
    """"Parses an xml using minidom and gets all the elements with matching tag names in the file, ignores namespaces in the tag names """
    doc = minidom.parse(filename)
    element_list = doc.getElementsByTagNameNS('*', element_tag)
    if len(element_list) == 0:
            print_info('element with tagname "%s" not found in file' % element_tag)
            return False
    return element_list



#2015/12/09 ymizugaki add begin
def getValuebyTagFromResponse (response, tag):
    """Given a xml response object, returns the value for a particular tag"""
    doc = minidom.parseString(response)
    item = doc.getElementsByTagName(tag)
    if len(item) != 0:
        itemlist = doc.getElementsByTagName(tag)[len(item)-1].toxml()
    else:
        itemlist = ""
    if itemlist == "<" + tag + "/>":
        itemvalue = ""
    else:
        itemvalue = itemlist.replace('<' + tag + '>','').replace('</' + tag + '>', '')
    return itemvalue

def get_last_level_children(node, tag):
    """Find and return the last level children"""
    ele = None
    for sub in node.iter(tag):
        ele = sub
    return ele


#2015/12/09 ymizugaki add end

def get_element_by_attribute(xml_file, tag_name, attr_name, attr_value):
    """
    Gets the element with matching tag_name, attribute name and attribute value
    """
    element= ""
    doc = minidom.parse(xml_file)
    element_list = doc.getElementsByTagName(tag_name)
    found = "No"
    for element in element_list:
        if element.getAttribute(attr_name) == attr_value:
            found = "Yes"
            break
    if found == "Yes":
        return element
    else:
        return False

def get_child_with_matching_tag(parent, tag_name):
    """ Find whether Child node with tag = tag_name exists, if exists then return the child node"""
    child_node = ""
    try:
        child_node = parent.getElementsByTagName(tag_name)[0]
    except Exception as exception:
        child_node = ""
    return child_node


def convert_dom_to_string(element):
    """
    Converts a dom element into a string
    """
    domstring = ""
    try:
        domstring = str(element.toxml())
    except Exception as exception:
        print_exception(exception)
    return domstring

def get_child_with_matching_tags(parent, tag_name):
    """
    Gets the list of elements with matching tag_name
    """
    child_node = ""
    try:
        child_node = parent.getElementsByTagName(tag_name)
    except Exception as exception:
        child_node = ""
    return child_node

def removenms(xml):
    """
        It accepts the xml file path or string as input and remove
            the name spaces.

        Arguments:
            xml: An input xml file path or xml string in which the name spaces
                    needs to be removed
        Returns:
            xml_string
    """
    if os.path.exists(xml):
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(xml, parser)
        root = tree.getroot()
    else:
        root = ElementTree.fromstring(xml)
    for elem in list(root):
        if not hasattr(elem.tag, 'find'):
            continue
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i+1:]
    xml_string = ElementTree.tostring(root, encoding='utf-8', method='xml')

    return xml_string


def recursive_delete_among_children(root, element):
    """
        It performs a recursive operation among the children in the xml file
         and finds the child that matches with the element and deletes it.
        Arguments:
            1.parent: It takes the root element in the xml file as input
            2.element: It is the tag which we want to delete
        Returns:
            True
    """
    childs = root.getchildren()
    for child in childs:
        if child in element:
            childs.remove(child)
        else:
            recursive_delete_among_children(child, element)
    return True

def del_tag_from_element(ele, tag):
    """
        Delete a subelement with specific tag from an xml element object
        return the deleted subelement if pass
        return False if subelement not found
    """
    if ele.find(tag) is not None:
        ele.remove(ele.find(tag))
        return ele
    else:
        print_warning("cannot found {0} in element".format(str(tag)))
    return False

def del_tags_from_xml(xml, tag_list=[]):
    """
        It deletes the tags either by their names or xpath

        Arguments:
            1.xml: It takes xml file path or xml string as input
            2.tag_list: It contains list of tags which needs to be removed
        Returns:
            It returns xml string
    """
    if os.path.exists(xml):
        tree = ElementTree.parse(xml)
        root = tree.getroot()
    else:
        root = ElementTree.fromstring(xml)
    for tag in tag_list:
        if 'xpath=' in tag:
            tag = tag.strip('xpath=')
            req_tags = getChildElementsListWithSpecificXpath(root, tag)
        else:
            req_tags = getChildElementsListWithSpecificXpath(root, ".//{0}".format(tag))
        recursive_delete_among_children(root, req_tags)

    xml_string = ElementTree.tostring(root, encoding='utf-8', method='xml')
    return xml_string


def del_attributes_from_xml(xml, attrib_list=[]):
    """
        It deletes the attributes either by their names or xpath

        Arguments:
            1.xml: It takes xml file path or xml string as input
            2.attrib_list: It contains list of attributes
            which needs to be removed
        Returns:
            It returns xml string
    """
    if os.path.exists(xml):
        tree = ElementTree.parse(xml)
        root = tree.getroot()
    else:
        root = ElementTree.fromstring(xml)
    for attr in attrib_list:
        if 'xpath=' in attr:
            attr = attr.strip('xpath=')
            req_tags = getChildElementsListWithSpecificXpath(root, attr)
        else:
            req_tags = getChildElementsListWithSpecificXpath(root, ".//*[@{0}]".format(attr))
        for ele in req_tags:
            ele.attrib.pop(attr)

    xml_string = ElementTree.tostring(root, encoding='utf-8', method='xml')
    return xml_string


def compare_xml(xml1, xml2, output_file=False, sorted_json=True,
                remove_namespaces=False, tag_list=[], attrib_list=[]):
    """
    This will compare two xml files or strings by converting to json
    and then sorting and by default giving the sorted files
    and writing the difference to a diff file.

    Arguments:
        1. xml1 : The first xml among the two xml's which
            needs to be compared
        2. xml2 : The second xml among the two xml's
            which needs to be compared
        3. output_file : It contains the difference between
            the two sorted json objects
        4. sorted_json : By default we are returning the sorted json
            files and if the user selects sorted_json as False,
            not returning the fileS
        5. remove_namespaces: If the user specifies remove_namespaces
            as True will remove namespaces and then compare xml's
        6. tag_list: If user specifies tag names in tag_list,
            will remove those tags and then compare xml's
        7. attrib_list: If user specifies attribute names in the
        attrib_list, will remove those attributes and then compare xml's

    Returns:
        Returns a tuple that contains
            comparison status
            two sorted json files or two None depends on sorted_json value
            output file path or diff_output depends on output_file value
    """
    try:
        from Framework.ClassUtils.json_utils_class import JsonUtils
        if remove_namespaces:
            xml1 = removenms(xml1)
            xml2 = removenms(xml2)

        xml1 = del_tags_from_xml(xml1, tag_list)
        xml2 = del_tags_from_xml(xml2, tag_list)

        xml1 = del_attributes_from_xml(xml1, attrib_list)
        xml2 = del_attributes_from_xml(xml2, attrib_list)

        output1 = json.loads(json.dumps(
                    (xmltodict.parse(xml1, xml_attribs=True))))
        output2 = json.loads(json.dumps(
                    (xmltodict.parse(xml2, xml_attribs=True))))

        sorted_json1 = JsonUtils().sort_json_object(output1)
        sorted_json2 = JsonUtils().sort_json_object(output2)

        json_obj1 = json.dumps(
            sorted_json1, indent=4, separators=(',', ':'), encoding="utf-8")
        json_obj2 = json.dumps(
            sorted_json2, indent=4, separators=(',', ':'), encoding="utf-8")

        if sorted_json:
            sorted_file1 = "sorted_file1.json"
            sorted_file2 = "sorted_file2.json"
            sorted_file1 = file_Utils.addTimeDate(sorted_file1)
            sorted_file2 = file_Utils.addTimeDate(sorted_file2)

            f = open(sorted_file1, 'w')
            f1 = open(sorted_file2, 'w')
            f.write(json_obj1)
            f1.write(json_obj2)
            f.close()
            f1.close()
        else:
            sorted_file1 = None
            sorted_file2 = None

        if output1 == output2:
            return True, sorted_file1, sorted_file2, None

        diff = ("\n".join(
            difflib.ndiff(json_obj1.splitlines(), json_obj2.splitlines())))

        if output_file:
            output_file = file_Utils.addTimeDate(output_file)
            te = open(output_file, 'w')
            te.write(diff)
            te.close()
        else:
            output_file = diff

        return False, sorted_file1, sorted_file2, output_file

    except Exception as exception:
        print_exception(exception)
        return False, None, None, output_file


def get_children_as_dict(parent):
    """For a given parent object, return all children as a dictionary with the childs tag as key"""
    child_list = getChildElementsListWithSpecificXpath(parent, "*")
    child_dict = {}
    for child in child_list:
        value = get_children_as_dict(child)
        if child.tag not in child_dict:
            child_dict[child.tag] = [value] if value != {} else [child.text]
        else:
            child_dict[child.tag].append(value if value != {} else child.text)
    return child_dict

def convert_xml_to_list_of_dict(file_name):
    """
        Takes xml file path as input and
        converts to list of dictionaries
        Arguments:
            file_name : It takes xml file path as input
        Returns:
            list_of_dict: list of dictionaries where keys
            are tag names and values are respective text of the tag.
    """
    tree = ElementTree.parse(file_name)
    root = tree.getroot()
    list_of_dict = []
    for child in root:
        subchild_dict = OrderedDict()
        for subchild in child:
            subchild_dict[subchild.tag] = subchild.text
        list_of_dict.append(subchild_dict)

    return list_of_dict

#2016/06/22 ymizugaki add begin
def getValuebyTagFromStringWithXpath(response, xpathString, ns):
    """Given a response object, return the value from the xpath and namespace combination"""
    xml = etree.fromstring(response)
    item = xml.xpath(xpathString, namespaces=ns)
    if len(item) != 0:
        itemValue = item[0]
    else:
        itemValue = ""
    return itemValue

def getValueListbyTagFromString(response, tag):
    """Given a response object, return the list of value tag present in the object"""
    doc = minidom.parseString(response)
    item = doc.getElementsByTagName(tag)
    itemlist = []
    if len(item) != 0:
        for i in item:
            temp = i.toxml()
            temp = temp.replace("<" + tag + ">", "").replace("</" + tag + ">", "")
            itemlist.append(temp)
    return itemlist
#2016/06/22 ymizugaki add end

def compare_xml_using_xpath(response, list_of_xpath, list_of_expected_api_responses):
    """
        Will get each xpath in list of xpath and get the value of
        that xpath in xml response
        Compares the value with the expected_api_response
        If all values matches returns True else False
    """
    status = True
    if len(list_of_xpath) != len(list_of_expected_api_responses):
        print_error("The number of xpath given is different"
                    "from the number of expected response"
                    "Please check the value"
                    "\nlist_of_xpath: {}"
                    "\nlist_of_expected_response: {}".format(
                        list_of_xpath, list_of_expected_api_responses))
        status = False

    if status:
        for index, xpath_pattern in enumerate(list_of_xpath):
            xpath = xpath_pattern.strip("xpath=")
            value = getValuebyTagFromStringWithXpath(response, xpath, None)
            # Equality_match: Check if the expected response is equal to API response
            match = True if value == list_of_expected_api_responses[index] else False
            # Perform Regex_search if equality match fails
            if match is False:
                try:
                    # Regex_search: Check if the expected response pattern is in API response
                    match = re.search(list_of_expected_api_responses[index], value)
                except Exception:
                    print_warning("Python regex search failed, invalid "
                                  "expected_response_pattern '{}' is "
                                  "provided".format(list_of_expected_api_responses[index]))
            if not match:
                status = False
                print_error("For the given '{0}' the expected response value is '{1}'. "
                            "It doesn't match or available in the actual response value "
                            "'{2}'".format(xpath_pattern, list_of_expected_api_responses[index],
                                           value))
    return status

def list_path_responses_datafile(datafile, system_name):
    """
        Returns the path_list and responses_list
        path_list contains list of response_path tags under the comparison_mode
        under the system with given system_name in the datafile
        responses_list contains list of response_value tags under the
        expected_api_response under the system with given system_name in datafile
    """
    path_element_list = getElementListWithSpecificXpath(datafile,
        "./*[@name='"+system_name+"']/comparison_mode/*")
    path_list = [x.text for x in path_element_list]
    resp_element_list = getElementListWithSpecificXpath(datafile,
        "./*[@name='"+system_name+"']/expected_api_response/*")
    responses_list = [x.text for x in resp_element_list]
    return path_list, responses_list
