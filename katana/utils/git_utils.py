import subprocess


def check_url_is_a_valid_repo(url):
    print "Verifying if {0} is a valid git repository.".format(url)
    if subprocess.call(["git", "ls-remote", url]) != 0:
        print "-- An Error Occurred -- {0} is not a valid git repository.".format(url)
        return False
    print "{0} is available".format(url)
    return True


def get_repository_name(url):
    li_temp_1 = url.rsplit('/', 1)
    return li_temp_1[1][:-4] if \
        li_temp_1[1].endswith(".git") else li_temp_1[1]