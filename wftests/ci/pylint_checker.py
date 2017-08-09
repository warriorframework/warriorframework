import os, sys, subprocess
from pylint import epylint as lint

if __name__ == "__main__":
    if len(sys.argv) > 2:
        filelist = open(sys.argv[1]).readlines()
        filelist = [x.strip() for x in filelist]

        pylintrc = open(sys.argv[2]).readlines()
        ignore = [x for x in pylintrc if x.startswith("ignore=")]
        if ignore:
            ignore = ignore[0][7:].replace('\n', '').split(',')
            print ignore
        for fi in filelist:
            if fi.endswith(".py") and all([x not in fi for x in ignore]):
                print "this file is changed: ", fi
                lint.py_run('{} --rcfile=../../.pylintrc'.format(fi))
