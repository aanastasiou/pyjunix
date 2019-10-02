import sys
from pyjunix import PyJls

if __name__ == "__main__":
    result = PyJls(sys.argv)()
    sys.stdout.write(result)
    
