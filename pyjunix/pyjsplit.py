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
    Splits a JSON file that contains a ``list<any>`` to one or more files whose ``list<any>`` contain a least number of 
    items.
    
    * **Mandatory parameters:**
      
      * ``json_file``: The file to split
    
    * **Optional parameters:**
    
      * ``--prefix``: The filename prefix to use, default to ``x``
      * ``--additional-suffix``: Any additional suffix to add after the file "part number". Defaults to an empty string.
      * ``-d``: Use numeric suffix (rather than "alphabetic")
      * ``-l``: (Least) Number of items per split file
      * ``--suffix-length``: The maximum length of the enumerated suffix. Defaults to 2.
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjsplit", description="Splits a JSON document.")
        ret_parser.add_argument("json_file", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="File to split.")
        ret_parser.add_argument("--prefix", dest="prefix", default="x", help="File prefix")
        ret_parser.add_argument("--additional-suffix", dest="additional_suffix",default="", help="Additional suffix")
        ret_parser.add_argument("-d", action="store_true", dest="use_numeric_suffix", help="Use numeric suffix")
        ret_parser.add_argument("-l", dest="num_items", default=1000, help="Number of items per generated file")
        ret_parser.add_argument("-a", "--suffix-length", dest="suffix_length",type=int, default=2, help="Suffix length")
        return ret_parser

    @staticmethod
    def _get_b26_num(rem, N): 
        """
        Recursively determine the base 26 string representation of number ``rem``.
        """
        if N>0:
            pexp = 26**N
            remainder = (rem % pexp) 
            return chr(97 + (rem // pexp)) + PyJSplit._get_b26_num(remainder, N-1) 
        else: 
            return chr(97 + rem) 

    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        # Load the data file
        json_data = json.load(self.script_args.json_file)
        # Basic validation here to throw an error if the file is not a list<any>
        if type(json_data) is not list:
            raise TypeError(f"PyJSplit expects list in {self.script_args.json_file.name}, received {type(json_data)}")
        
        # In the following block, a function that determines the file name is built up.
        if self.script_args.use_numeric_suffix:
            # Numeric suffix
            counter_rep = lambda x:f"{x:0{self.script_args.suffix_length}d}"
        else:
            # Alphabetic suffix
            counter_rep = lambda x:self._get_b26_num(x, self.script_args.suffix_length-1)
        part_file_name = lambda x:f"{self.script_args.prefix}{counter_rep(x)}{self.script_args.additional_suffix}"
        
        # A pretty basic "splitter"
        current_file_contents = []
        current_file_contents_n = 0
        current_file_idx = 0
        for a_row in json_data:
            if current_file_contents_n<self.script_args.num_items:
                current_file_contents.append(a_row)
                current_file_contents_n+=1
            else:
                with open(part_file_name(current_file_idx), "wt") as fd:
                    json.dump(current_file_contents, fd)
                current_file_idx += 1
                current_file_contents = [a_row]
                current_file_contents_n = 1
        # Write the last batch to the disk
        with open(part_file_name(current_file_idx), "wt") as fd:
                    json.dump(current_file_contents, fd)
        return json.dumps({})
