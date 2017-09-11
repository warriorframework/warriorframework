import os
import os.path 
import re
#gpysrcdir = pathname(cfg['pythonsrcdir'])
gpysrcdir = "/home/khusain/warriorframework/warrior/"

def mkactiondirs(driverpath):  # changed
    '''Given a directory name `drivername`, return its action python file name.'''
    # FrameworkDirectory/ used to be the prefix in the directory name.
    actions_dirpath_list = []
    actions_package_list = get_action_dirlist(driverpath)
    if len(actions_package_list) == 0:
        print "the driver {0} does not import any actions package or import format is wrong".format(os.path.basename(driverpath))
    # print "action package list in mkactions dir", actions_package_list
    # print type(actions_package_list)

    elif len(actions_package_list) > 0:
        for package in actions_package_list:
            try:
                print package
                package = package.replace(' ', '')
                pkg = re.sub('[\n\t' '\\\]', '', package)
                print pkg
                print package
                if pkg == 'Actions':
                    actions_dirpath = gpysrcdir + os.sep + 'Actions'
                elif pkg.startswith('Actions.'):
                    path = pkg.replace('.', os.sep)
                    actions_dirpath = gpysrcdir + os.sep + path
                else:
                    path = pkg.replace('.', os.sep)
                    actions_dirpath = gpysrcdir + os.sep + 'Actions' + os.sep + path
                    print actions_dirpath
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
            '''
            fobj = open(driverpath, 'r')
            lines = fobj.readlines()
            '''
            lines = []
            with open(driverpath, 'r') as fobj:
                lines = fobj.readlines()
            lines_as_string = ''.join(lines)
            search_string = re.compile('package_list.*=.*\]',
                                       re.DOTALL | re.MULTILINE)
            match = re.search(search_string, lines_as_string)

            if match:
                match_string = match.group()
                # print match_string
                actions_package_list = match_string.split('[')[1].split(']')[
                    0].split(',')
                print "\n action package list: ", actions_package_list
                # for line in lines:
                # if re.search(search, line):
                # print "package_list found"
                # print line
                # actions_package_list = line.split('[')[1].split(']')[0].split(',')
                # print "\n action package list: ", actions_package_list
            return actions_package_list
        else:
            print "file {0} does not exist".format(driverpath)
            return actions_package_list
    except Exception, e:
        print str(e)
    return actions_package_list


def mkactionpyfiles(dirlist):  # changed
    '''Find .py files in given directory.'''
    # print "dirlist for action py file s=>>>>>>>>>>>>>>", dirlist
    final_py_list = []
    try:
        for dir in dirlist:
            pyfile_list = glob.glob(dir + os.sep + '*.py')
            # print "pyfile list ---->", pyfile_list
            for pyfile in pyfile_list:
                nameonly = os.path.basename(pyfile)
                if nameonly.startswith("__init__"):
                    pyfile_list.remove(pyfile)
            final_py_list.extend(pyfile_list)
        return final_py_list
    except Exception, e:
        print str(e)
        return final_py_list


def fetchpath(keyname):
    config = readconfig()
    # print 'fetchpath, config:', config
    return pathname(config['cfg'][keyname])


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


def py_file_details():  # changed
    print gpysrcdir
    cfg = readconfig()
    print cfg
    # gpysrcdir = fetchpath('pythonsrcdir')
    # gpysrcdir = pathname(cfg['pythonsrcdir'])
    gpysrcdir = cfg['pythonsrcdir']
    print ">>> source directory:", gpysrcdir

    pyfiles_list = glob.glob(
        gpysrcdir + os.sep + 'ProductDrivers' + os.sep + '*.py')
    pyfiles = []
    for fl in pyfiles_list:
        print fl
        if os.path.isfile(fl):
            print "is a file:", fl
            if os.path.basename(fl) != '__init__.py':
                print "not init hence accepting"
                pyfiles.append(fl)
        else:
            print "not a file", fl

    driver_nameonly = map(lambda f: os.path.basename(f), pyfiles)
    drivers = sorted([df[:df.find('.py')] for df in driver_nameonly])
    drivers_fpath = sorted([df for df in pyfiles])
    # print 'drivers', json.dumps(drivers)
    # print 'drivers_fpath', json.dumps(drivers_fpath)
    print "\n*****pyfiles : \n\n", pyfiles
    print "\n***** drivers nameonly: \n\n", driver_nameonly
    print "\n***** drivers: \n\n", drivers
    print "\n***** drivers fullpath: \n\n", drivers_fpath

    # actiondirs = []
    # for path in drivers_fpath:
    #     for directory in mkactiondirs(path):
    #         actiondirs.append(directory)
    actiondirs = map(mkactiondirs, drivers_fpath)
    print "\n\n drivers: \n\n", json.dumps(drivers_fpath, indent=2)
    print '\n\nactiondirs: \n\n', json.dumps(actiondirs, indent=2)

    actionpyfiles = map(mkactionpyfiles, actiondirs)
    drivercomments = fetch_comments(zip(drivers, actionpyfiles))
    # print 'driver:docs\n', json.dumps(drivercomments, indent=2)
    return drivercomments