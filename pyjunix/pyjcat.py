"""

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
import argparse
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser


class PyJCat(BasePyJUnixFunction):
    """
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjjoin", description="Joins two JSON documents on specific "
                                                  "fields.")
        ret_parser.add_argument("files", nargs="+", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="Files.")
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        json_data = [json.load(fd) for fd in self.script_args.files]
        to_ret = json_data[0]
        for jd in json_data[1:]:
            to_ret.extend(jd)
            
        return json.dumps(to_ret)
