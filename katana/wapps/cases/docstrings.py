#!/usr/bin/env python

'''Read in docstring for the module & all functions in given python file.'''

import sys
import json


def read_lines(pyfile):
    """Read all lines from given python file: pyfile."""
    with open(pyfile, 'r') as f:
        lines = f.readlines()
    lines = map(lambda r: r.strip(), lines)
    return lines


def read_arg(s):
    """Chop ending parenthesis from end of line, and return a trimmed string."""
    if s.endswith(')'):
        return s[:-1].strip()
    elif s.endswith('):'):
        return s[:-2].strip()
    else:
        return s.strip()


def args_to_map(args):
    """
    Transform:
        ['resultfile', 'client_list', 'capturexml_path', 'step_num', \
         'ref_inpackets=0', 'ref_outpackets=0', "of_version='openflow_v4'"]
    To:
        {'client_list': '', 'ref_inpackets': '0', 'resultfile': '', \
        'capturexml_path': '', 'of_version': "'openflow_v4'", 'step_num': '', \
        'ref_outpackets': '0'}

    Note the order is not preserved.

    """
    res = {}
    for a in args:
        param = a.split('=')
        res[param[0]] = param[1] if len(param) > 1 else ''
    return res


def nameType(name, type, lno):
    """
    Return a nice structure from given parameters.
    Also, calculates the arguments, & the the function name.
    """

    args = []
    fndef = ''
    argsmap = {}
    if type == 'package':
        fndef = name.split('.')[0]  # 'cli_actions.py' => cli_actions
    if type == 'class':
        fndef = name.split('(')[0]
    if type == 'fn':
        parts = name.partition('(')
        fndef = name.split()[1].split('(')[0].strip()

        args = map(read_arg, parts[2].split(','))
        argsmap = args_to_map(args)
    return {'type': type, 'def': name, 'line': lno,
            'comment': '', 'args': args, 'fn': fndef,
            'argsmap': argsmap}


def closeParaentheses(lines):
    result_str = ""
    count = 0
    for line in lines:
        for char in line:
            if char == '(':
                count += 1
            if char == ')':
                count -= 1
        if line.endswith('\\'):
            line = line[:-1] + " "
        result_str += line
        if count == 0:
            return result_str


def class_defs(ls, pyfile):
    """Figure out the line numbers of the module, class and fn definition
    within the pyfile.

    Sample output is an array such as the following:
    [{
        "comment": "",
        "line": 12,
        "type": "class",
        "name": "CliActions"
      },
      {
        "comment": "",
        "line": 14,
        "type": "fn",
        "name": "def __init__(self):"
      },
      {
        "comment": "",
        "line": 20,
        "type": "fn",
        "name": "def dumpConfig(self):"
      }]
    """
    defs = []
    defs.append(nameType(pyfile.rpartition('/')[-1], 'package', 1))
    for lno, l in enumerate(ls):
        m = l.split()
        if l.startswith('class') and m[0] == 'class':
            defs.append(nameType(l.split()[1], 'class', lno))
        if l.startswith('def') and m[0] == 'def':
            defs.append(nameType(closeParaentheses(ls[lno:]), 'fn', lno))
    return defs


SINGLE = "'''"
DOUBLE = '"""'


def strip_comments(comments):
    """Drop empty lines, at start & end of the comments block."""
    cs = comments[:]
    while len(cs) > 0 and cs[0].strip() == '':
        del cs[0]
    while len(cs) > 0 and cs[-1].strip() == '':
        del cs[-1]
    return cs


def strip_quotes(qs):
    """From string qs, remove starting & ending quote characters."""
    s = qs.strip()
    if s[0] == '"' or s[0] == "'":
        s = s[1:]
    if s[-1] == '"' or s[-1] == "'":
        s = s[:-1]
    return s


def parse_docs(lines, defs, pyfile):
    """Read through the file and at the lines as defined in the defs,
    parse the corresponding comments.

    Update defs with the comments variable for all the methods, fns & module.

    Also, update the wdesc field for the function definitions.
    """
    lineindex = map(lambda r: r['line'], defs)
    dists = map(lambda r: r[0] - r[1], zip(lineindex[1:], lineindex[:-1]))
    if len(lines): dists.append(len(lines) - lineindex[-1])
    defi = 0
    started_comment = False
    ignore_method = []
    for d in dists:
        comments = []
        for i in range(0, d):
            pointer = 0
            curline = lines[lineindex[defi] + i]
            if "useaskeyword=no" in curline.lower():
                ignore_method.append(defi)
            if curline.startswith(SINGLE) or curline.startswith(DOUBLE):
                if not started_comment:
                    pointer = 1
                started_comment = True
            if started_comment:
                comments.append(curline.replace(SINGLE, '').replace(DOUBLE, ''))
            if curline.endswith(SINGLE) or curline.endswith(DOUBLE):
                if pointer == 0:
                    started_comment = False

        comments = strip_comments(comments)
        defs[defi]['comment'] = comments

        if defs[defi]['type'] == 'fn':
            wdesc = ''
            for i in range(0, d):
                curline = lines[lineindex[defi] + i].strip()
                if curline.startswith('WDesc') or curline.startswith('wdesc'):
                    parts = curline.split('=')
                    if len(parts) > 1:
                        if '"""' in parts[1] or "'''" in parts[1]:
                            s = parts[1].strip()
                            if s[0:3] == '"""' or s[0:3] == "'''":
                                s = s[3:]
                                wdesc = s + '\n'
                                nextline = lines[lineindex[defi] + i + 1].strip()
                                s = nextline.strip()
                                line = 1
                                while s[-3:] != '"""' and s[-3:] != "'''":
                                    line = line + 1
                                    wdesc = wdesc + s + '\n'
                                    nextline = lines[lineindex[defi] + i + line].strip()
                                    s = nextline.strip()
                                if s[-3:] == '"""' or s[-3:] == "'''":
                                    s = s[:-3]
                                    wdesc = wdesc + s
                        elif '"' in parts[1] or "'" in parts[1]:
                            wdesc = strip_quotes(parts[1])

            defs[defi]['wdesc'] = defs[defi]['fn'] if wdesc == '' else wdesc

        defi += 1
    for offset, index in enumerate(sorted(ignore_method)):
        del defs[index - offset]


def parse_py_file(filename):
    lines = read_lines(filename)
    defs = class_defs(lines, filename)
    parse_docs(lines, defs, filename)
    return defs


def main():
    if len(sys.argv) == 1:
        print 'Usage:', sys.argv[0], '<python file to get docstrings from>'
        return
    print json.dumps(parse_py_file(sys.argv[1]), indent=2)


if __name__ == '__main__':
    main()
