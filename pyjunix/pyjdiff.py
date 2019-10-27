"""

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
import argparse
import deepdiff
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser


class PyJDiff(BasePyJUnixFunction):
    """
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjdiff", description="Runs diff on two or more JSON documents")
        ret_parser.add_argument("file_1", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="First file to diff.")
        ret_parser.add_argument("file_2", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="Second file to diff.")
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        return json.dumps(deepdiff.DeepDiff(json.load(self.script_args.file_1), json.load(self.script_args.file_2), 
                          ignore_order=True))
