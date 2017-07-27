import os, sys, subprocess

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filelist = open(sys.argv[1]).readlines()
        filelist = [x.strip() for x in filelist]
        print filelist