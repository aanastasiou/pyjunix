"""
PyJPrtPrn applies Pretty Print over JSON in compact form.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
from .core import BasePyJUnixFunction, PyJUnixException, PyJCommandLineArgumentParser

class PyJPrtPrn(BasePyJUnixFunction):
    """
    Renders JSON content in a more human readable form (Pretty Print).
    
    While ``PyJPrtPrn`` does not break the JSON format in any way, it is best if it is called last in a pipe sequence.
    This will reduce the load of parsing extra whitespace characters. But also, if ``PyJPrtPrn`` is called "mid-script"
    it will disrupt the functionality of ``PyJArray, PyJUnArray`` that expect JSON items in "compact form". Use with 
    caution.
    
    ::
    
        usage: pyprtprn [-h] [cli_vars [cli_vars ...]]

        Renders JSON content in a more human readable form.

        positional arguments:
          cli_vars    Zero or more JSON objects to pretty print.

        optional arguments:
          -h, --help  show this help message and exit

    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyprtprn", description="Renders JSON content in a more human readable form.")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more JSON objects to pretty print.")
        
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        return self.script_args.cli_vars
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        stdin_data = json.load(sys.stdin)
        return stdin_data
        
    def on_after_exec(self, exec_result, *args, **kwargs):
        return json.dumps(exec_result, indent=4, sort_keys=True)
