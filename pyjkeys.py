#!/usr/bin/env python3

import sys
from pyjunix import PyJKeys

if __name__ == "__main__":
    result = PyJKeys(sys.argv)()
    sys.stdout.write(result)
    
