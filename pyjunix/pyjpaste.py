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
        json_file_data = [json.load(fd) for fd in self.script_args.files]
        len_json_file_data = len(json_file_data)
        done = False
        k = 0
        files_done=set()
        to_ret = []
        
        while not done:
            row_data = []
            for a_file in enumerate(json_file_data):
                try:
                    row_data.extend(a_file[1][k])
                except IndexError:
                    files_done.add(a_file[0])
            to_ret.append(row_data)
            k+=1
            done = len(files_done) == len_json_file_data
        
        return json.dumps(to_ret)
