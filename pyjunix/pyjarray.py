"""
PyJArray packs items in JSON arrays.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser

class PyJArray(BasePyJUnixFunction):
    """
    Packs JSON objects in its input to a JSON array
    
    When operating over ``stdin``, it is assumed that the input is a newline delineated list of JSON items.
    
    ::
    
        usage: pyjarray [-h] [cli_vars [cli_vars ...]]

        Packs objects in its input to a JSON array

        positional arguments:
          cli_vars    Zero or more items to pack to an array.

        optional arguments:
          -h, --help  show this help message and exit

    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjarray", description="Packs objects in its input to a JSON array")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more items to pack to an array.")
        
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
        return json.dumps([an_arg for an_arg in self.script_args.cli_vars])
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        json_data = [json.loads(u) for u in map(lambda x:x.rstrip("\n"), sys.stdin.readlines())]
        return json.dumps(json_data)
        
