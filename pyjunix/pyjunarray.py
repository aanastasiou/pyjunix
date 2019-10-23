"""
PyJUnArray unpacks items from an array.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser

class PyJUnArray(BasePyJUnixFunction):
    """
    Unpacks a JSON object from a list to a newline delineated list of items.
    
    Anything other than a list as input to ``PyJUnArray`` is an error condition.
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjunarray", description="Unpacks JSON objects from an array.")
        ret_parser.add_argument("cli_vars", nargs="*", help="List of arrays to unpack to a JSON array.")
        return ret_parser
        
    def on_validate_args(self, *args, **kwargs):
        for some_array in self.script_args.cli_vars:
            if type(some_array) is not list:
                raise TypeError(f"pyjunarray expects list, received {type(some_array)}.")
        return True
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
            
        result = []
        for an_arg in self.script_args.cli_vars:
            result.extend(an_arg)
            
        return json.dumps(result)

    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        json_list_in_stdin = json.load(sys.stdin)
        if not type(json_list_in_stdin) is list:
            raise TypeError(f"pyjunarray expects list in stdin, received {type(json_list_in_stdin)}")
        return "\n".join([json.dumps(u) for u in json_list_in_stdin])
        
