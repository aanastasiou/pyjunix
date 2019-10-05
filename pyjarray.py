#!/usr/bin/env python3

import sys
from pyjunix import PyJArray

if __name__ == "__main__":
    result = PyJArray(sys.argv)()
    sys.stdout.write(result)
    
