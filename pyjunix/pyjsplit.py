"""
PyJSplit splits a JSON file containing lists of items, to one or more files.

:authors: Athanasios Anastasiou
:date: Oct 2019

"""

import sys
import json
import argparse
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser


class PyJSplit(BasePyJUnixFunction):
    """
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjsplit", description="Pastes two or more JSON documents")
        ret_parser.add_argument("json_file", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="File to split.")
        ret_parser.add_argument("prefix", default="x", help="File prefix")
        ret_parser.add_argument("--additional-suffix", dest="additional_suffix", help="Additional suffix")
        ret_parser.add_argument("-d", action="store_true", dest="use_numeric_suffix", help="Use numeric suffix")
        ret_parser.add_argument("-l", dest="num_items", default=1000, help="Number of items per generated file")
        ret_parser.add_argument("-a", "--suffix-length", type=int, default=2, help="Suffix length")
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        return json.dumps([1,2])
