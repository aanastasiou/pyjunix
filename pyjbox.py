#!/usr/bin/env python3
import sys
import argparse
from pyjunix import PyJArray, PyJUnArray, PyJLs, PyJKeys, PyJGrep, PyJPrtPrn

script_dir = {"pyjarray": PyJArray, 
              "pyjunarray": PyJUnArray,
              "pyjls": PyJLs,
              "pyjkeys": PyJKeys,
              "pyjgrep": PyJGrep,
              "pyjprtprn": PyJPrtPrn} 

if __name__ == "__main__":
    #pyjbox_parser = argparse.ArgumentParser(prog="pyjbox", description="Blah")
    #pyjbox_parser.add_argument("script", choices = list(script_dir.keys()), help="al")
    #pyjbox_parser.add_argument("other_args", nargs="*", help="jfh")
    
    #pyjbox_parser.parse_args(sys.argv[1:])
    
    if "pyjbox" in sys.argv[0]:
        script_to_run = sys.argv[1]
        script_to_run = script_to_run.replace("./","").replace(".py","")
        result = script_dir[script_to_run](sys.argv[1:])()
    else:
        script_to_run = sys.argv[0]
        script_to_run = script_to_run.replace("./","").replace(".py","")
        result = script_dir[script_to_run](sys.argv)()
    sys.stdout.write(result)
    
