"""
PyJUniq returns unique items from a list of items.

:authors: Athanasios Anastasiou
:date: November 2019

"""

import sys
import json
from .core import BasePyJUnixFunction, PyJUnixException, PyJCommandLineArgumentParser
import deepdiff
import collections

import pdb

class PyJUniq(BasePyJUnixFunction):
    """
    Returns unique items from a list of items.
    
    This script deviates from the typical function of the ``uniq`` unix script in that it does not expect its input to 
    be sorted. This is because it indexes each item by its hash. The rest of the switches correspond to those of
    unix' ``uniq``.
    
    It expects its input formatted as a list and it can operate either via a list of arguments or a list JSON object 
    loaded from ``stdin``.
    
    **Optional Parameters:**
    
      * ``-c`` Returns a map<value><int> of unique values at its input pointing to the count of occurence.
      * ``-d`` Returns only duplicate items (one for each occurence)
      * ``-u`` Returns only unique items
      
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjuniq", description="Returns unique items from a list of JSON" 
                                                  " objects.")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more JSON objects to apply uniq on.")
        ret_parser.add_argument("-c", "--count", action="store_true", help="Prefix items by number of occurences "
                                "(returns object)")
        ret_parser.add_argument("-d", "--repeated", action="store_true", help="Only return duplicate items, "
                                "one for each occurence")
        ret_parser.add_argument("-u", "--unique", action="store_true", help="Only return unique items")
        return ret_parser
        
    @staticmethod
    def _uniq_over_list(a_list, repeated, unique, count):
        """
        Implements the ``uniq`` functionality over a JSON list.
        """
        # Create a dictionary that is indexed by hash and maintains attributes "value" and "count".
        hash_lookup = {}
        for an_item in a_list:
            item_hash = deepdiff.deephash.DeepHash(an_item)[an_item]
            if item_hash not in hash_lookup: 
                hash_lookup[item_hash] = {"value":an_item, "count":1}
            else:
                hash_lookup[item_hash]["count"]+=1
                
        # Functionality such as "only duplicates", "count" and others are offered here as queries over the 
        # index that was created earlier.
        if repeated:
            ret_items = dict(filter(lambda x:x[1]["count"]>1, hash_lookup.items()))
        elif unique:
            ret_items = dict(filter(lambda x:x[1]["count"]==1, hash_lookup.items()))
        else:
            ret_items = dict([(u, hash_lookup[u]) for u in set(hash_lookup.keys())])
            
        if count:
            ret_items = dict(map(lambda x:(x[1]["value"], x[1]["count"]), ret_items.items()))
            return json.dumps(ret_items)
            
        # Finally, return the resulting object of results.
        return json.dumps(list(map(lambda x:x[1]["value"] ,ret_items.items())))
        
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
        
        return self._uniq_over_list(self.script_args.cli_vars, self.script_args.repeated, self.script_args.unique, 
                                    self.script_args.count)
                                    
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        stdin_data = json.load(sys.stdin)
        if not type(stdin_data) is list:
            raise TypeError(f"PyJUnique expected list over stdin, received {type(stdin.data)}")
            
        return self._uniq_over_list(stdin_data, self.script_args.repeated, self.script_args.unique, 
                                    self.script_args.count)
                                    
