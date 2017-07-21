import os
import sys

if __name__ == "__main__":

    args = sys.argv[1:]
    directory = os.path.dirname(sys.argv[0])

    command = "python"
    port = 5000
    runserver = "runserver"
    filepath = "manage.py"

    if directory is not "":
        filepath = directory + os.sep + filepath

    for i in range(0, len(args)):
        if args[i] == "-p":
            if i+1 >= len(args):
                print "No port number given. Exiting."
                sys.exit()
            else:
                port = args[i+1]
            break

    os.system("{0} {1} {2} {3}".format(command, filepath, runserver, port))