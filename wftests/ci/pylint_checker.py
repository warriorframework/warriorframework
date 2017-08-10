"""
Get a list of file and run pylint on each of the files
on pull request source branch and target branch
"""
import sys
import subprocess
from pprint import pprint
# from pylint import epylint as lint

def process_file_list(input_file, rc_file):
    """
        Generate a list of files that need to be pylint
    """
    filelist = open(input_file).readlines()
    filelist = [x.strip() for x in filelist]

    pylintrc = open(rc_file).readlines()
    ignore = [x for x in pylintrc if x.startswith("ignore=")]
    if ignore:
        ignore = ignore[0][7:].replace('\n', '').split(',')

    result = [x for x in filelist if all([y not in x for y in ignore])]
    print "The following files will be tested with Pylint:\n", "\n".join(result), "\n"
    return result

def pylint(file_list):
    file_score = {}
    for fi in file_list:
        print "linting", fi
        try:
            output = subprocess.check_output('pylint --rcfile=.pylintrc {}'.format(fi), shell=True)
        except subprocess.CalledProcessError as e:
            output = e.output

        score = output.split('\n')
        score = [x.replace("Your code has been rated at ", "") for x in score if x.startswith("Your code has been")]
        if score:
            # code has been rated
            file_score[fi] = [score[0], output]
        else:
            print fi, "doesn't get a Pylint score on this branch"
    return file_score

def report(file_score, branch_file_score):
    print "\n\n\n!---------- Detail score for this pull request ----------!\n\n\n"
    for k, v in branch_file_score.items():
        # print k, "\n", v[1]
        pass

    print "\n\n\n!---------- Summary score for this pull request ----------!\n\n\n"
    for k, v in branch_file_score.items():
        print k, v[0]

def main():
    """
        main function to process logic
    """
    if len(sys.argv) > 4:
        file_score = {}
        file_list = process_file_list(sys.argv[1], sys.argv[2])

        print "target branch:", sys.argv[3], "\nsource branch:", sys.argv[4]
        subprocess.check_output("git checkout {}".format(sys.argv[3]), shell=True)
        print "\nRunning pylint on", sys.argv[3]
        file_score = pylint(file_list)

        subprocess.check_output("git checkout {}".format(sys.argv[4]), shell=True)
        print "\nRunning pylint on", sys.argv[4]
        branch_file_score = pylint(file_list)

        report(file_score, branch_file_score)
    else:
        print "Missing arguments, require filenames, pylintrc_file, target_branch, source_branch"

if __name__ == "__main__":
    main()
