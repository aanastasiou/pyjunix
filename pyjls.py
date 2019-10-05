#!/usr/bin/env python3
import sys
from pyjunix import PyJLs

if __name__ == "__main__":
    result = PyJLs(sys.argv)()
    sys.stdout.write(result)
    
