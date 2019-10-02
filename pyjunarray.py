import sys
from pyjunix import PyJUnArray

if __name__ == "__main__":
    result = PyJUnArray(sys.argv)()
    sys.stdout.write(result)
    
