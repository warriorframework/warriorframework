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

import logging
import re
import xml.etree.ElementTree as eT

from Framework.ClassUtils.TL1Parser.command import Command


class TL1Parser(object):
    """ Parse TL1 data and return dictionaries of results."""

    def __init__(self, command_files):
        """
        Initialize a TL1Parser object
        Args:
            command_files (dict): dictionary of format {eqpt_type: filename}
            pointing to XML files containing command formats for each type
        """
        self.commands = {}
        self.command_files = command_files
        self.models = command_files.keys()
        last_read = ''
        try:
            for eqpt_type, filename in self.command_files.iteritems():
                last_read = filename
                self.read_commands(eqpt_type, filename)
        except:
            logging.error('Error in command file ' + last_read)
            raise IOError('Error in command file ' + last_read)

    def add_model(self, model, command_file):
        """
        Add commands for a new equipment type to the TL1Parser
        Args:
            model (str): Equipment type that commands are valid for
            command_file (str): XML file containing command formats
        """
        self.read_commands(model, command_file)
        self.models.append(model)

    def read_commands(self, model, command_file):
        """
        Read commands from self.command_file and store in self.commands
        Args:
            model (str): Equipment type that commands are valid for
            command_file (str): XML file containing command formats
        """
        logging.info('Parsing commands from %s...' % command_file)
        tree = eT.parse(command_file)
        command_tree = tree.getroot()
        self.commands[model] = []
        for node in command_tree.iter('command'):
            cmd = Command()
            cmd.name = node.get('type')
            cmd.regex = node.find('regex').text
            for arg in node.iter('arg'):
                optional = arg.get('optional')
                if optional == '1':
                    cmd.add_arg(arg.text, optional=True)
                else:
                    cmd.add_arg(arg.text)

                if node.find('keywords') is not None:
                    cmd.keyword_pos = node.find('keywords').get('pos')
                    for keyword in node.find('keywords'):
                        cmd.add_keyword(keyword.text)
                self.commands[model].append(cmd)

        logging.info('done')

    def parse(self, model, tid, command, line):
        """
        Parse given response line and return dictionary containing the results
        Args:
            model (str): Equipment type that response is from
            tid (str): TID that response is from
            command (str): name of the command (RTRV-VERSION, etc)
            line (str): response line returned from TL1 execution

        Returns:
            parsed (dict): contains all the parsed arguments as key/value
        """
        # Remove any quotes around line
        line = line.strip('"')
        line = line.strip('\\')
        # Check to make sure command is loaded from file
        if not any(cmd.name == command for cmd in self.commands[model]):
            logging.error('Command "%s" not found in XML' % command)
            raise KeyError('Command "%s" not found in XML' % command)

        # Find corresponding xml command data for line
        cmd_index = (cmd for cmd in self.commands[model]
                     if cmd.name == command).next()

        if re.match(cmd_index.regex, line) is None:
            logging.error('Command %s does not match expected format %s' %
                          (line, cmd_index.regex))
            raise StandardError('Command %s does not match expected format %s' %
                                (line, cmd_index.regex))

        result = re.search(cmd_index.regex, line)

        parsed = {
            'TID': tid,
            'command': command,
        }
        # Process arguments, RE groups indexed starting at 1
        group = 1
        keyword_pos = int(cmd_index.keyword_pos)
        for i, arg in enumerate(cmd_index.args, start=1):
            # Keywords will be processed in next step, skip for now
            if i == keyword_pos:
                group += 1
            # Remove escape character from quotes in line
            name, optional = arg
            count = 0
            try:
                while result.group(group) is None:
                    group += 1
                    count += 1
            except IndexError:
                if optional:
                    continue
                else:
                    logging.error('Error parsing %s in %s' % (arg, line))
            try:
                parsed[name] = result.group(group).replace('\\"', '"')
            except:
                if optional:
                    continue
                else:
                    logging.error('Error parsing %s in %s' % (arg, line))
                    raise StandardError('Error parsing %s in %s' % (arg, line))
            group += 1

        # Process keywords
        if keyword_pos != 0:
            keyword_block = result.group(keyword_pos).split(',')
        else:
            keyword_block = ''
        for keyword in keyword_block:
            # Key=value
            if '=' in keyword:
                keyword = keyword.split('=')
                key = keyword[0]
                value = keyword[1]
                # Remove escape character from quotes in log
                value = value.replace('\\"', '"').strip()
                parsed[key] = value

        return parsed

    def parse_raw(self, model, raw_data):
        """
        Parse raw response from TL1 connection
        Args:
            model (str): Equipment type that this response is from
            raw_data (str): raw, multi-line response from TL1 connection

        Returns:
            parsed_data (dict): contains all the parsed arguments as key/value
        """

        if model not in self.models:
            raise KeyError('Model %s not loaded' % model)
        
        lines = [line.strip() for line in raw_data.split('\n')
                 if line.strip() is not '' and line is not '>']
       
        command_line, tid_line = lines[:2]

        responses = [line for line in lines
                     if line[0] == '"']
        
        
        command = command_line.split(':')[0]
        tid, date, time = tid_line.split()
        parsed = []
        for response in responses:
            # print response
            parsed.append(
                self.parse(model, tid, command.upper(), response))

        return parsed
