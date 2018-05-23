"""
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
"""
# Utility to send email using smtp
# Import smtplib for the actual sending function
import smtplib
import os
from os.path import basename
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from xml.etree import ElementTree as ET
import Tools
from Framework.Utils.print_Utils import print_debug, print_info
from Framework.Utils import file_Utils
from Framework.Utils.testcase_Utils import pNote
from WarriorCore.Classes.execution_summary_class import ExecutionSummary


def set_params_send_email(addsubject, data_repository, files, mail_on):
    """ From data_repository array constructs body of email
        using testcase/testsuite name, logs directory, results directory
        fetches smtp host, sender, receiver from w_settings.xml
        uses paramters such as: subject, body, attachments
    :Arguments:
        1. subject - email subject
        2. data_repository - array of email body lines e.g.
            1. testcase/testsuite name
            2. logs directory
            3. results directory
        3. files - list of file attachments
        4. mail_on(optional) - it is to specify when to send an email
           Supported options below:
                (1) per_execution(default)
                (2) first_failure
                (3) every_failure
    """
    body = ""
    if isinstance(data_repository, list):
        for body_elem in data_repository:
            body += body_elem+"\n"
    else:
        body = data_repository
    params = get_email_params(mail_on)
    compress = params[4]
    if compress.upper().startswith('Y'):
        print_info("compress attribute in w_settings.xml is set to Yes. "
                   "So, all the email attachments will be compressed.")
        zip_files = []
        for file_name in files:
            zip_file = file_Utils.convert_to_zip(file_name)
            zip_files.append(zip_file)
        files = zip_files
    subject = str(params[3])+addsubject
    send_email(params[0], params[1], params[2], subject, body, files)


def get_email_params(mail_on='per_execution'):
    """ Get the parameters from the w_settings.xml file.
    :Arguments:
        1.mail_on(optional) - it is to specify when to send an email.
           Supported options below:
                (1) per_execution(default)
                (2) first_failure
                (3) every_failure
    :Returns:
        1. smtp_host - smtp host name
        2. sender - sender email ID
        3. receivers - receiver email ID(s)
        4. subject - email subject line
        5. compress - compression(Yes/No)
    """
    smtp_host = ""
    sender = ""
    receivers = ""
    subject = ""
    warrior_tools_dir = Tools.__path__[0]+os.sep+'w_settings.xml'
    element = ET.parse(warrior_tools_dir)
    setting_elem = element.find("Setting[@name='mail_to']")
    if setting_elem is not None:
        mail_on_attrib = setting_elem.get("mail_on")
        mail_on_list = []
        if mail_on_attrib:
            mail_on_list = mail_on_attrib.split(",")
            mail_on_list = [x.strip(' ') for x in mail_on_list]
        if mail_on in ['first_failure', 'every_failure'] or \
           (mail_on == "per_execution" and mail_on_list != []):
            if mail_on not in mail_on_list:
                return smtp_host, sender, receivers, subject
        smtp_host_elem = setting_elem.find("smtp_host")
        if smtp_host_elem is not None:
            smtp_host = smtp_host_elem.text
        sender_elem = setting_elem.find("sender")
        if sender_elem is not None:
            sender = sender_elem.text
        receiver_elem = setting_elem.find("receiver")
        if receiver_elem is not None:
            receivers = receiver_elem.text
        subject_elem = setting_elem.find("subject")
        if subject_elem is not None:
            subject = subject_elem.text
            if subject is None:
                subject = ""
        # To support backward compatibility
        if 'compress' in setting_elem.keys():
            compress = setting_elem.get("compress")
        else:
            compress = "No"

    return smtp_host, sender, receivers, subject, compress


def construct_mail_body(exec_type, abs_filepath, logs_dir, results_dir):
    """ construct e-mail body with Project, Logs/Results directory & Execution summary
    :Arguments:
        1. exec_type - type of test(case/suite/project)
        2. abs_filepath - full path of case/suite/project
        3. logs_dir - full path of logs directory
        4. results_dir - full path of results directory
    :Returns:
        1. body - return mail body
    """
    junit_result_file = os.path.join(
        results_dir, file_Utils.getNameOnly(file_Utils.getFileName(abs_filepath))) + "_junit.xml"
    junit_object = ExecutionSummary(junit_result_file)
    project_sum = junit_object.project_summary(junit_result_file)
    suite_tc_sum = junit_object.suite_summary(junit_result_file)
    suite_tc, body = "", ""
    body_arg = ('<html><body><p><b>{0}</b>{1}</p>'
                '<p><b>Logs directory:</b>{2}</p>'
                '<p><b>Results directory:</b>{3}</p>'
                '<p><b>Execution Summary:</b></p>'
                '<table cellspacing="10" cellpadding="0"><tr><td><b>Type</b>'
                '</td><td><b>Name</b></td><td><b>Status</b></td>'
                '<td><b>Path</b></td></tr>').format(exec_type, abs_filepath,
                                                    logs_dir, results_dir)
    # complete html body that will be sent through mail
    if exec_type == 'Project: ':
        project = ""
        for proj in project_sum:
            project = project + ('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>\n'
                                 .format(proj[0], proj[1], proj[2], proj[3]))
        for value in suite_tc_sum:
            suite_tc = suite_tc + ('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>\n'
                                   .format(value[0], value[1], value[2], value[3]))
        body = body_arg + project + suite_tc + "</table></body></html>"
    elif exec_type == 'Test Suite: ' or exec_type == 'Test Case: ':
        for value in suite_tc_sum:
            suite_tc = suite_tc + ('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>\n'
                                   .format(value[0], value[1], value[2], value[3]))
        body = body_arg + suite_tc + "</table></body></html>"
    return body


def compose_send_email(exec_type, abs_filepath, logs_dir, results_dir, result,
                       mail_on="per_execution"):
    """ compose and sends email from smtp server using input arguments as:
    :Arguments:
        1. exec_type - type of test(case/suite/project)
        2. abs_filepath - full path of case/suite/project
        3. logs_dir - full path of logs directory
        4. results_dir - full path of results directory
        5. result - execution result
        6. mail_on(optional) - it is to specify when to send an email
           Supported options below:
                (1) per_execution(default)
                (2) first_failure
                (3) every_failure
    """
    resultconverted = {"True": "Pass", "False": "Fail", "ERROR": "Error",
                       "EXCEPTION": "Exception", "RAN": "Ran"}.get(str(result))
    subject = str(resultconverted)+": "+file_Utils.getFileName(abs_filepath)
    body = construct_mail_body(exec_type, abs_filepath, logs_dir, results_dir)
    report_attachment = results_dir + os.sep + \
        file_Utils.getNameOnly(file_Utils.getFileName(abs_filepath)) + ".html"
    if mail_on in ["per_execution", "first_failure", "every_failure"]:
        files = [report_attachment]
    else:
        files = []
    set_params_send_email(subject, body, files, mail_on)


def send_email(smtp_host, sender, receivers, subject, body, files):
    """ sends email from smtp server using input arguments:
    :Arguments:
        1. smtp_host - smtp host name
        2. sender - sender email ID
        3. receivers - receiver email ID(s)
        4. subject - email subject line
        5. body - email body
        6. files - files to be attached
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
    receivers_list = [receiver.strip() for receiver in receivers.split(',')]
    message['Subject'] = subject
    # HTML is used for better formatting of mail body
    part = MIMEText(body, 'html')
    message.attach(part)
    for attach_file in files or []:
        with open(attach_file, "rb") as fil:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((fil).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment;filename= %s"
                            % basename(attach_file))
            message.attach(part)
    try:
        smtp_obj = smtplib.SMTP(smtp_host)
        smtp_obj.sendmail(sender, receivers_list, message.as_string())
        pNote('Execution results emailed to receiver(s): {0}'.format(receivers))
        smtp_obj.close()

    except BaseException:
        pNote("Error occurred while sending email, check w_settings.xml"
              "configuration for correct smtp host, "
              "receiver email address etc.")
