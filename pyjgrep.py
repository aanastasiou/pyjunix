#!/usr/bin/env python3

import sys
from pyjunix import PyJGrep

if __name__ == "__main__":
    result = PyJGrep(sys.argv)()
    sys.stdout.write(result)
    
