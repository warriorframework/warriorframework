import os, sys, subprocess
import StringIO
from pylint import epylint as lint

if __name__ == "__main__":
    if len(sys.argv) > 4:
        file_score = {}
        filelist = open(sys.argv[1]).readlines()
        filelist = [x.strip() for x in filelist]

        pylintrc = open(sys.argv[2]).readlines()
        ignore = [x for x in pylintrc if x.startswith("ignore=")]
        if ignore:
            ignore = ignore[0][7:].replace('\n', '').split(',')
            print "Ignoring", ', '.join(ignore)
        print sys.argv[3], sys.argv[4]
        subprocess.call("git checkout {}".format(sys.argv[3]), shell=True)
        for fi in filelist:
            if fi.endswith(".py") and all([x not in fi for x in ignore]):
                print "Pylint is running on:", fi
                # lint.py_run('{} --rcfile=../../.pylintrc'.format(fi))
                try:
                    output = subprocess.check_output('pylint --rcfile=.pylintrc {}'.format(fi), shell=True)
                except subprocess.CalledProcessError as e:
                    output = e.output
                # print output
                output = output.split('\n')
                output = [x for x in output if x.startswith("Your code has been")]
                if output:
                    # print output[0]
                    file_score[fi] = [output[0]]
        print file_score
        subprocess.call("git checkout {}".format(sys.argv[4]), shell=True)
        for fi in filelist:
            if fi.endswith(".py") and all([x not in fi for x in ignore]):
                print "Pylint is running on:", fi
                # lint.py_run('{} --rcfile=../../.pylintrc'.format(fi))
                try:
                    output = subprocess.check_output('pylint --rcfile=.pylintrc {}'.format(fi), shell=True)
                except subprocess.CalledProcessError as e:
                    output = e.output
                # print output
                output = output.split('\n')
                output = [x for x in output if x.startswith("Your code has been")]
                if output:
                    # print output[0]
                    if fi in file_score:
                        file_score[fi].append(output[0])
                    else:
                        file_score[fi] = [output[0]]
        print file_score