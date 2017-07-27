import os, sys, subprocess
from pylint import epylint as lint

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filelist = open(sys.argv[1]).readlines()
        filelist = [x.strip() for x in filelist]
        for fi in filelist:
            if fi.endswith(".py"):
                print "this file is changed: ", fi
                lint.py_run('fi --rcfile=.pylintrc')