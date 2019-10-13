#!/usr/bin/env python3
import sys
from pyjunix import PyJArray, PyJUnArray, PyJLs, PyJKeys, PyJGrep, PyJPrtPrn

script_dir = {"pyjarray": PyJArray, 
              "pyjunarray": PyJUnArray,
              "pyjls": PyJLs,
              "pyjkeys": PyJKeys,
              "pyjgrep": PyJGrep,
              "pyjprtprn": PyJPrtPrn} 


if __name__ == "__main__":
    # Complain if pyjbox doesn't know what to do.
    if len(sys.argv)<2:
        print(f"pyjbox is used to launch pyjunix scripts.\n\tUsage: pyjbox <script> [script parameters]\n\tScripts "
              f"supported in this version:\n\t\t{', '.join(script_dir.keys())}\n")
        sys.exit(-2)
        
    if "pyjbox" in sys.argv[0]:
        script_to_run = sys.argv[1]
        script_params = sys.argv[1:]
    else:
        script_to_run = sys.argv[0]
        script_params = sys.argv
        
    script_to_run = script_to_run.lower().replace("./","").replace(".py","")
    result = script_dir[script_to_run](script_params)()
    sys.stdout.write(result)
    
