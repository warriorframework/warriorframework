import os
import os.path 
import re, glob, json, docstrings
#gpysrcdir = pathname(cfg['pythonsrcdir'])
gpysrcdir = ""

def mkactiondirs(driverpath, srcdir):  # changed
    '''Given a directory name `drivername`, return its action python file name.'''
    # FrameworkDirectory/ used to be the prefix in the directory name.
    gpysrcdir = srcdir

    actions_dirpath_list = []
    actions_package_list = get_action_dirlist(driverpath)
    if len(actions_package_list) == 0:
        print "the driver {0} does not import any actions package or import format is wrong".format(os.path.basename(driverpath))

    elif len(actions_package_list) > 0:
        for package in actions_package_list:
            try:
                package = package.replace(' ', '')
                pkg = re.sub('[\n\t' '\\\]', '', package)
                if pkg == 'Actions':
                    actions_dirpath = gpysrcdir + os.sep + 'Actions'
                elif pkg.startswith('Actions.'):
                    path = pkg.replace('.', os.sep)
                    actions_dirpath = gpysrcdir + os.sep + path
                else:
                    path = pkg.replace('.', os.sep)
                    actions_dirpath = gpysrcdir + os.sep + 'Actions' + os.sep + path
                if os.path.isdir(actions_dirpath):
                    actions_dirpath_list.append(actions_dirpath)
                else:
                    print "the actions package {0} does not exist or the location is not compatible with warrior framework:".format(
                        actions_dirpath)
            except Exception, e:
                print str(e)
    return actions_dirpath_list


def get_action_dirlist(driverpath):  # changed
    """ Get the list of action directories """
    actions_package_list = []
    try:
        if os.path.isfile(driverpath):
            with open(driverpath, 'r') as fobj:
                lines = fobj.readlines()
            lines_as_string = ''.join(lines)
            search_string = re.compile('package_list.*=.*\]',
                                       re.DOTALL | re.MULTILINE)
            match = re.search(search_string, lines_as_string)

            if match:
                match_string = match.group()
                actions_package_list = match_string.split('[')[1].split(']')[
                    0].split(',')
            return actions_package_list
        else:
            print "file {0} does not exist".format(driverpath)
            return actions_package_list
    except Exception, e:
        print str(e)
    return actions_package_list


def mkactionpyfiles(dirlist):  # changed
    '''Find .py files in given directory.'''
    final_py_list = []
    try:
        for dir in dirlist:
            pyfile_list = glob.glob(dir + os.sep + '*.py')
            for pyfile in pyfile_list:
                nameonly = os.path.basename(pyfile)
                if nameonly.startswith("__init__"):
                    pyfile_list.remove(pyfile)
            final_py_list.extend(pyfile_list)
        return final_py_list
    except Exception, e:
        print str(e)
        return final_py_list


def fetch_comments(sa):
    '''From the tuple array, made of (drivername, array_of_filenames),
    build the comments data structure.'''
    res = {}
    for a in sa:
        comments = []
        for f in a[1]:
            comments.append(docstrings.parse_py_file(f))
        res[a[0]] = comments
    return res


def py_file_details(gpysrcdir):
    pyfiles_list = glob.glob(
        gpysrcdir + os.sep + 'ProductDrivers' + os.sep + '*.py')
    pyfiles = []
    for fl in pyfiles_list:
        if os.path.isfile(fl):
            if os.path.basename(fl) != '__init__.py':
                pyfiles.append(fl)

    driver_nameonly = map(lambda f: os.path.basename(f), pyfiles)
    drivers = sorted([df[:df.find('.py')] for df in driver_nameonly])
    drivers_fpath = sorted([df for df in pyfiles])

    srcdirs = [ gpysrcdir for df in pyfiles ]
    actiondirs = map(mkactiondirs, drivers_fpath, srcdirs)

    actionpyfiles = map(mkactionpyfiles, actiondirs)
    drivercomments = fetch_comments(zip(drivers, actionpyfiles))
    return drivercomments
