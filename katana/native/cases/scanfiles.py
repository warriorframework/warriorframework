#/usr/bin/env python

import glob

def fetch_action_file_names(basedir,name,num):
    '''Given a directory name, determine all of the Action python files.

    basedir = a path such '/home/vap/labs/fujitsu/raw/python' with or
                without a trailing / which is expected to contain
                the folder `FrameworkDirectory`.

    Returns:
        A map keys by a human readable action name that maps
        the action files associated with that name.
    '''
    if not basedir.endswith('/'):
        basedir = basedir + '/'
    if name=="action":    
        basedir = basedir + 'Actions'
        if num=='all':
            dirs = glob.glob(basedir + '/**/*actions.py')
        else:
            action_directory=basedir+'/'+num+'Actions'
            print 'action direcory %s'%action_directory
            dirs = glob.glob(action_directory+'/*actions.py')
        print '\n'
        for d in dirs: print d
    
        sa = {}
        for d in dirs:
            action = d.split('/')[-2].partition('Act')[0]
            da = sa.get(action, [])
            da.append(d)
            sa[action] = da
    elif name=='driver':
        
        basedir = basedir + 'ProductDrivers'
        print 'enterd driver %s'%basedir
        dirs = glob.glob(basedir + '/*driver.py')
        print '\n'
        for d in dirs: print d
    
        sa = {}
        for d in dirs:
            action = d.split('/')[-2].partition('Act')[0]
            da = sa.get(action, [])
            da.append(d)
            sa[action] = da

        

    for k, v in sa.iteritems():
        print k, v
    return sa
if __name__ == '__main__':
#    fetch_action_file_names('/home/vap/labs/fujitsu/raw/python')
     fetch_action_file_names('D:/meethu/fujitsu/fujitsu/app/raw/python')#D:\Meethu\fujitsu\fujitsu\play
