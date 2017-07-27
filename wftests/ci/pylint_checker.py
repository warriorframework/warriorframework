import os, sys, subprocess

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print open(sys.argv[1]).read()