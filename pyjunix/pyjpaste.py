"""
PyJPaste concatenates two or more JSON files containing lists of lists or lists of dictionaries data, either
"horizontally" or "vertically".

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
import argparse
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser


class PyJPaste(BasePyJUnixFunction):
    """
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjpaste", description="Pastes two or more JSON documents")
        ret_parser.add_argument("files", nargs="+", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="Files to paste.")
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        return json.dumps([1,2])
