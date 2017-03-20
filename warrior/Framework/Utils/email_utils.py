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

"""Utility to send email using smtp"""

#Import smtplib for the actual sending function
import smtplib
import os
from os.path import basename
from email import encoders
from email.MIMEBase import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from xml.etree import ElementTree as ET
import Tools
from Framework.Utils.print_Utils import print_debug
from Framework.Utils import file_Utils
from Framework.Utils.testcase_Utils import pNote

def set_params_send_email(addsubject, data_repository, files):
    """From data_repository array constructs body of email
        using testcase/testsuite name, logs directory, results directory
        fetches smtp host, sender, receiver from w_settings.xml
        uses paramters such as: subject, body, attachments
    Arguments:
        1. subject - email subject
        2. data_repository - array of email body lines e.g.
            1. testcase/testsuite name
            2. logs directory
            3. results directory
        3. files - list of file attachments
    """
    body = ""
    if type(data_repository) is list:
        for body_elem in data_repository:
            body += body_elem+"\n"
    else:
        body = data_repository

    params = get_email_params()
    subject = str(params[3])+addsubject
    send_email(params[0], params[1], params[2], subject, body, files)

def get_email_params():
    """ initialize all parameters needed to send email from w_settings.xml"""
    smtp_host = ""
    sender = ""
    receivers = ""
    subject = ""
    warrior_tools_dir = Tools.__path__[0]+os.sep+'w_settings.xml'
    element = ET.parse(warrior_tools_dir)
    sub_element = element.findall("Setting[@name='mail_to']/smtp_host")
    for sub_elem_value in sub_element:
        smtp_host = sub_elem_value.text
    sub_element = element.findall("Setting[@name='mail_to']/sender")
    for sub_elem_value in sub_element:
        sender = sub_elem_value.text
    sub_element = element.findall("Setting[@name='mail_to']/receiver")
    for sub_elem_value in sub_element:
        receivers = sub_elem_value.text
    sub_element = element.findall("Setting[@name='mail_to']/subject")
    for sub_elem_value in sub_element:
        subject = sub_elem_value.text
    return smtp_host, sender, receivers, subject

def compose_send_email(type, abs_filepath, logs_dir, results_dir, result):
    """ compose and sends email from smtp server using input arguments as:
    type of test case/suite/project 
    full path of logs directory
    full path of results directory
    subject line
    """
    resultconverted = {"True":"Pass", "False":"Fail"}.get(str(result))
    subject = str(resultconverted)+": "+file_Utils.getFileName(abs_filepath)
    body = [type+abs_filepath, "Logs directory: "+logs_dir,\
            "Results directory: "+results_dir]
    report_attachment = results_dir + \
            "/"+file_Utils.getNameOnly(file_Utils.getFileName(abs_filepath))\
            +".html"
    set_params_send_email(subject, body, {report_attachment})

def send_email(smtp_host, sender, receivers, subject, body, files):
    """ sends email from smtp server using input arguments as:
    smtp host
    sender email
    receiver email
    subject line
    attached files (optional) can be None
    """
    if not smtp_host:
        print_debug("No smtp host defined in w_settings, no email sent")
        return
    if not receivers:
        print_debug("No receiver defined in w_settings, no email sent")
        return

    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receivers
    message['Subject'] = subject

    part = MIMEText(body, 'plain')
    message.attach(part)

    for attach_file in files or []:
        with open(attach_file, "rb") as fil:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((fil).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment;\
				filename= %s" % basename(attach_file))
            message.attach(part)

    try:
        smtp_obj = smtplib.SMTP(smtp_host)
        smtp_obj.sendmail(sender, receivers, message.as_string())
        pNote('Execution results emailed to receiver(s): {}'.format(receivers))
        smtp_obj.close()
        
    except BaseException:
        pNote("Error occurred while sending email, "\
        "check w_settings.xml configuration for "\
        "correct smtp host, receiver email address etc.")
