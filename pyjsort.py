#!/usr/bin/env python3
import sys
from pyjunix import PyJSort

if __name__ == "__main__":
    result = PyJSort(sys.argv)()
    sys.stdout.write(result)
    
