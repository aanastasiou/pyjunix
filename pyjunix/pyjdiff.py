"""

PyJDiff runs diff across two data structures initialised from JSON files and produces a 
dict representation of the differences it has found.

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
    Runs a diff equivalent over JSON data structures.
    
    ::
    
        usage: pyjdiff [-h] file_1 file_2

        Runs diff on two or more JSON documents

        positional arguments:
          file_1      First file to diff.
          file_2      Second file to diff.

        optional arguments:
          -h, --help  show this help message and exit

    
    PyjUnix' diff relies on `DeepDiff <https://github.com/seperman/deepdiff>`_ to assess differences between the JSON
    data structures. The output of DeepDiff is also a JSON data structure whose layout is explained in full detail 
    `here <https://deepdiff.readthedocs.io/en/latest/diff.html>`_.
    
    Very briefly and for the purposes of ``PyJDiff``: 
    
        * DeepDiff runs across two data structures (that here are initialised from JSON objects) and produces 
          a dictionary of "modifications". A "modification" can be ``type_changes``, ``values_changed``, 
          ``*_item_added, *_item_removed`` where ``*`` can be a wide range of types (iterables, ``dict``, ``set``, etc) and 
          a ``repetition_change``.
        * The actual modification is described via a small set of self-explanatory attributes such as ``old_value, 
          new_value``, ``old_type, new_type`` and others. In the case of deep nested data structures, the localisation 
          of attributes is provided via accessors expressed in Python (e.g. ``root[5]['some_attribute'][2]`` to imply
          a ``list<dict<str,list<int>>>`` data structure).
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
