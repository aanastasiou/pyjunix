"""
PyJGrep retrieves items from JSON data structures.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import os
import sys
import json
import jsonpath2
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser


class PyJGrep(BasePyJUnixFunction):
    """
    Performs grep by applying the XPath equivalent to a JSON document.
    
    It accepts a jsonpath query string and zero or more command line parameters. In this case, it evaluates the 
    query string on each content item passed as a command line parameter and returns its result in an array.
    
    When operating over ``stdin``, it assumes a single properly formatted document at its input.
    
    By definition, PyJGrep should return lists as its result is produced by iterative application of the query string 
    over its command line parameters (for example). However, if the result of a query is a single item list, the content
    of that item is returned rather than the list. This saves additional ``pyjunix`` script invocation later on, to 
    isolate those single items.
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjgrep", description="Performs grep over JSON documents using jsonpath.")
        ret_parser.add_argument("jsonpath_pattern", help="The jsonpath query string. (See https://github.com/json-path/JsonPath).")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more JSON objects to run the query over.")
        
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
        
        result = []
        # TODO: HIGH, This should be tested at the validate args level and raise exception if it should fail.
        jsonpath_exp = jsonpath2.Path.parse_str(self.script_args.jsonpath_pattern)
        
        for a_var in self.script_args.cli_vars:
            query_results = list(map(lambda x:x.current_value, jsonpath_exp.match(a_var)))
            if len(query_results) == 1:
                result.append(query_results[0])
            else:
                result.append(query_results)
                
        if len(result) == 1:
            return json.dumps(result[0])
        else:
            return json.dumps(result)
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        # print(self.script_args.jsonpath_pattern)
        # TODO: HIGH, This should be tested at the validate args level and raise exception if it should fail.
        jsonpath_exp = jsonpath2.Path.parse_str(self.script_args.jsonpath_pattern)
        
        json_data = json.load(sys.stdin)
        query_result = list(map(lambda x:x.current_value, jsonpath_exp.match(json_data)))
        if len(query_result) == 1:
            query_result = query_result[0]
            
        return json.dumps(query_result)
        
