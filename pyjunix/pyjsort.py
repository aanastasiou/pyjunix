"""
PyJSort, sorts items in arrays according to a jsonpath key.

:authors: Athanasios Anastasiou
:date: September 2019

"""
import sys
import json
import jsonpath2
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser

class PyJSort(BasePyJUnixFunction):
    """
    Sorts items in its input. It naturally operates over lists of items.
    
    When called over command line arguments, it treats them as a list.
    When called over stdin, a valid JSON list must be passed as an argument.
    
    ::
    
        usage: pyjsort [-h] [-k KEY] [-r] [cli_vars [cli_vars ...]]

        Sorts items in its input.

        positional arguments:
          cli_vars           Zero or more JSON objects to sort. These are treated
                             implicitly as a list.

        optional arguments:
          -h, --help         show this help message and exit
          -k KEY, --key KEY  JSONPath to the key to be used for sorting items.
          -r, --reverse      Sort in reverse order.
    
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjsort", description="Sorts items in its input.")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more JSON objects to sort. These are treated implicitly as a list.")
        ret_parser.add_argument("-k", "--key", help="JSONPath to the key to be used for sorting items.")
        ret_parser.add_argument("-r", "--reverse", default=False, action="store_true", help="Sort in reverse order.")
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not len(self.script_args.cli_vars):
            return None

        if not self.script_args.key:
            index = [(u, u) for u in self.script_args.cli_vars]
        else:
            jsonpath_exp = jsonpath2.Path.parse_str(self.script_args.key)
            query_results = map(lambda x:x.current_value, jsonpath_exp.match(self.script_args.cli_vars))
            index=list(zip(query_results, self.script_args.cli_vars))
        
        return json.dumps(list(map(lambda x:x[1], sorted(index, key=lambda x:x[0], reverse = self.script_args.reverse))))

    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        # TODO: HIGH, This needs a try, catch to catch any JSON conversion errors.
        stdin_data = json.load(sys.stdin)
        if type(stdin_data) is not list:
            raise TypeError(f"pyjsort expects a list in its input, received {type(stdin_data)}")
        
        # TODO: HIGH, Reduce code duplication in the functionality of these scripts.
        if not self.script_args.key:
            index = [(u, u) for u in stdin_data]
        else:
            jsonpath_exp = jsonpath2.Path.parse_str(self.script_args.key)
            query_results = map(lambda x:x.current_value, jsonpath_exp.match(stdin_data))
            index=list(zip(query_results, stdin_data))
        
        return json.dumps(list(map(lambda x:x[1], sorted(index, key=lambda x:x[0], reverse = self.script_args.reverse))))
