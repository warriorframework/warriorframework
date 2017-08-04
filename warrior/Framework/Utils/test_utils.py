

import unittest 
import signal
import sys, select


def wait_for_keystroke(n_seconds=None):
    n = int(n_seconds) 
    if n < 1: return -1
    i,o,e = select.select([sys.stdin],[],[],n) 
    if (i): 
        print "Input ", sys.stdin.readline().strip()
    else: 
        print "timed out"


class TestMethods(unittest.TestCase):
    def test_keystroke(self):
        wait_for_keystroke(4) 


if __name__ == '__main__':
    unittest.main() 

