import sys
from pyjunix import PyJKeys, PyJArray, PyJUnArray, PyJls

if __name__ == "__main__":
    result = PyJls(sys.argv)()
    sys.stdout.write(result)
    
