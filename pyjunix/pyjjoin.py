"""
PyJJoin joins two JSON files containing lists of lists data on a common attribute.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
import argparse
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser


class PyJJoin(BasePyJUnixFunction):
    """
    Joins two JSON files on a common attribute.
    
    At the moment, the contents of the files should resolve to lists of lists.
    
    **Mandatory parameters:**
    
        * f1, f2: These are filenames to the two files participating in the join. Either (but only one of them) 
          can be ``-``, which indicates ``stdin``.
          
    **Optional parameters:**
    
        * ``-a FILENUM`` include unpairable items from FILENUM where FILENUM is 1 or 2
        * ``-v FILENUM`` exactly like ``-a`` but suppress the joined items.
        * ``-1 NUM`` zero based index of the field to join on from the first JSON file
        * ``-2 NUM`` zero based index of the field to join on from the second JSON file
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjjoin", description="Joins two JSON documents on specific "
                                                  "fields.")
        ret_parser.add_argument("-a", dest="include_unpaired_items_from", type=int, default=-1, choices=[1,2], 
                                help="Include unpairable items from file 1 or 2")
        ret_parser.add_argument("-v", dest="suppress_joined_items", type=int, default=-1, choices=[1,2], 
                                help="Similar to -a but indicating which file's items to suppress")
        ret_parser.add_argument("-1", dest="file_1_key", type=int, default=0, 
                                help="jsonpath READ expression that determines the attribute to use as a key for the "
                                "first file")
        ret_parser.add_argument("-2", dest="file_2_key", type=int, default=0, 
                                help="jsonpath READ expression that determines the attribute to use as a key for the "
                                "second file")
        ret_parser.add_argument("f1", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="File name of the first file to join.")
        ret_parser.add_argument("f2", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="File name of the seocnd file to join.")
        return ret_parser
        
    def on_validate_args(self, *args, **kwargs):
        if self.script_args.f1.name=="<stdin>" and self.script_args.f2.name=="<stdin>":
            # TODO: MED, This should be turned to an exception (Possibly a generic PyJUnixError exception (?))
            print("\nPyJJoin Error: Both input files point to <stdin>\n")
            sys.exit(-2)
        return True
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        
        # TODO: MED, It would be great if the index was specified by jsonpath but this would complicate the output
        # file_1_key = jsonpath2.Path.parse_str(self.script_args.file_1_key)
        # file_2_key = jsonpath2.Path.parse_str(self.script_args.file_2_key)
        file_data_1 = json.load(self.script_args.f1)
        file_data_2 = json.load(self.script_args.f2)
        
        if type(file_data_1) is not list:
            raise TypeError(f"PyJJoin expected {self.script_args.f1.name} content to be a list, received "
                            f"{type(file_data_1)}")
             
        if type(file_data_2) is not list:
            raise TypeError(f"PyJJoin expected {self.script_args.f2.name} content to be a list, received "
                            f"{type(file_data_2)}")
            
        # TODO: MED, This should also work across lists of lists or lists of dict
        # Index the entries of both files according to the indicated field
        file_idx_1 = {}
        file_idx_2 = {}
        for an_item in file_data_1:
            try:
                file_idx_1[an_item[self.script_args.file_1_key]].append(an_item)
            except KeyError:
                file_idx_1[an_item[self.script_args.file_1_key]] = [an_item]
                
        for an_item in file_data_2:
            try:
                file_idx_2[an_item[self.script_args.file_2_key]].append(an_item)
            except KeyError:
                file_idx_2[an_item[self.script_args.file_2_key]] = [an_item]
                
        result = []
        
        if self.script_args.suppress_joined_items>0:
            # This is -v {1,2}. In this case, suppress the matched output and translate to the equivalent -a {1,2}
            self.script_args.include_unpaired_items_from = self.script_args.suppress_joined_items
        else:
            # Perform the join
            for a_key in file_idx_1:
                for an_item in file_idx_1[a_key]:
                    try:
                        for another_item in file_idx_2[a_key]:
                            result.append(an_item + list(map(lambda x:x[1], filter(lambda x:not x[0]==self.script_args.file_2_key,enumerate(another_item)))))
                    except KeyError:
                        # This key error indicates keys that were find in the first file but not in the second
                        pass
                    
        # Also include unpaired entries from one of the input files
        if self.script_args.include_unpaired_items_from>0:
            if self.script_args.include_unpaired_items_from==1:
                # Include unpaired entries from the first file
                # This is the difference of keys in the first file not in the second
                additional_item_indices = set(file_idx_1.keys()) - set(file_idx_2.keys())
                source_idx = file_idx_1
            else:
                # Include unpaired entries from the second file
                # This is the difference of keys in the second file not in the first.
                additional_item_indices = set(file_idx_2.keys()) - set(file_idx_1.keys())
                source_idx = file_idx_2
            for a_key in additional_item_indices:
                result.extend(source_idx[a_key])

        return json.dumps(result)
