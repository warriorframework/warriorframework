"""
Get a list of file and run pylint on each of the files
on pull request source branch and target branch
"""
import sys
import subprocess
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
    if result:
        print "The following files will be tested with Pylint:\n", "\n".join(result), "\n"
    else:
        print "No file requires pylint check, exiting"
        exit(0)
    return result

def pylint(file_list):
    """
        Pylint files from file list
    """
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

def report(branch_file_score):
    """
        print out pylint result for each file
    """
    print "\n\n\n!---------- Detail score for branch {} ----------!\n".format(sys.argv[4])
    for k, v in branch_file_score.items():
        print k, "\n", v[1]

    print "\n\n\n!---------- Summary score for branch {} ----------!\n".format(sys.argv[4])
    for k, v in branch_file_score.items():
        print k, v[0]

def judge(branch_file_score):
    """
        Check the score and difference for each file
    """
    status = True
    for k, v in branch_file_score.items():
        # print k, v[0]
        score = v[0].split("/")[0]
        if float(score) < 5:
            status = False
            print k, "failed with a score lower than 5"

        if "previous" in v[0]:
            improvement = float(v[0].split(",")[1][:-1])
            if improvement < -0.1:
                status = False
                print k, "failed with a decreasing score"

        if float(score) >= 5 and "previous" in v[0] and improvement >= -0.1:
            print k, "pass"
    return status

def custom_rules(file_list):
    """
        Invoke custom rules checker on each file
    """
    status = True
    for fi in file_list:
        try:
            output = subprocess.check_output('python wftests/ci/custom_rules.py {}'.format(fi), shell=True)
        except subprocess.CalledProcessError as e:
            output = e.output
            status = False

        print output
    return status

def main():
    """
        main function to process logic
    """
    if len(sys.argv) > 4:
        file_list = process_file_list(sys.argv[1], sys.argv[2])

        print "target branch:", sys.argv[3], "\nsource branch:", sys.argv[4]
        subprocess.check_output("git checkout {}".format(sys.argv[3]), shell=True)
        print "Running pylint on", sys.argv[3]
        pylint(file_list)

        print "\n"
        subprocess.check_output("git checkout {}".format(sys.argv[4]), shell=True)
        print "\nRunning pylint on", sys.argv[4]
        branch_file_score = pylint(file_list)

        report(branch_file_score)

        print "\n\n\n!---------- Judging score for branch {} ----------!\n".format(sys.argv[4])
        status = judge(branch_file_score)

        print "\n\n\n!---------- Custom Rules Checker for branch {} ----------!\n".format(sys.argv[4])
        status &= custom_rules(file_list)
        if status:
            exit(0)
        else:
            exit(1)
    else:
        print "Missing arguments, require filenames, pylintrc_file, target_branch, source_branch"

if __name__ == "__main__":
    main()
