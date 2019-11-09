"""
PyJKeys returns the keys of a JSON object.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser
            
class PyJKeys(BasePyJUnixFunction):
    """
    Returns the keys of a JSON mapping. 
    
    Anything other than a JSON mapping as input to ``PyJKeys`` is an error condition.
    
    ::
    
        usage: pyjkeys [-h] [cli_vars [cli_vars ...]]

        Returns the keys of a hash

        positional arguments:
          cli_vars    JSON Objects to extract the keys from

        optional arguments:
          -h, --help  show this help message and exit

    """
    
    def on_get_parser(self):
        # TODO: HIGH, This can be abstracted more to PyJUnixFunctions that are supposed to operate over zero or more 
        #       "input" parameters.
        ret_parser = PyJCommandLineArgumentParser(prog="pyjkeys", description="Returns the keys of a hash")
        ret_parser.add_argument("cli_vars", nargs="*", help="JSON Objects to extract the keys from")
        return ret_parser
        
    def on_validate_args(self, *args, **kwargs):
        for an_arg in self.script_args.cli_vars:
            if type(an_arg) is not dict:
                raise TypeError(f"pyjkeys expects map, received {type(an_arg)}")
        return True
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        
        if not self.script_args.cli_vars:
            return None
            
        result = []
        for an_item in self.script_args.cli_vars:
            result.append(list(an_item.keys()))
        return json.dumps(result)
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        # Validate stdin here
        stdin_data = json.load(sys.stdin)
        if not type(stdin_data) is dict:
            raise TypeError(f"pyjkeys expects map, received {type(stdin_data)} through stdin.")
        return json.dumps(stdin_data.keys())
        
