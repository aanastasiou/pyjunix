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
    Merges two or more JSON files into one.
    
    This operation expects JSON files to contain lists of lists or lists of objects.
    
    If the files contain lists of lists, parallel merging occurs list element by list element. That is, the first list 
    element of the output is the concatenation of each file's first element (and so on).
    If the files contain lists of objects, parallel merging is equivalent to a merge of each line's dictionaries.
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjpaste", description="Pastes two or more JSON documents")
        ret_parser.add_argument("files", nargs="+", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="Files to paste.")
        # ret_parser.add_argument("-s", action="store_true", dest="paste_serial", 
        #                         default=False, help="Paste serial instead of parallel")
        return ret_parser
        
    def _perform_merge(self, row_data):
        """
        Performs merging of a data "row", depending on the row's data type
        
        :param row_data: A list with the elements to be merged
        :type row_data: list
        :returns: Merged row object (e.g. list or dictionary)
        :rtype: list<list>, list<dict>
        :raises TypeError: If ``row_data`` is not a list of lists or list of objects.
        """
        merged_row = row_data[0]
        for an_item in row_data[1:]:
            if type(merged_row) is list and type(an_item) is list:
                merged_row.extend(an_item)
            elif type(merged_row) is dict and type(an_item) is dict:
                merged_row.update(an_item)
            else:
                raise TypeError(f"pyjpaste expects list of lists or list of objects as content,"
                                f"received {row_data}")
        return merged_row
        
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
                    row_data.append(a_file[1][k])
                except IndexError:
                    files_done.add(a_file[0])
            done = len(files_done) == len_json_file_data
            if not done:
                to_ret.append(self._perform_merge(row_data))
                k+=1
        
        return json.dumps(to_ret)
