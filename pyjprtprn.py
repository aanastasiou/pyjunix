#!/usr/bin/env python3

import sys
from pyjunix import PyJPrtPrn

if __name__ == "__main__":
    result = PyJPrtPrn(sys.argv)()
    sys.stdout.write(result)
    
