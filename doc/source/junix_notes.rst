Notes on PyJUnix
================

At the moment, these notes are not in any particular order and are collected progressively as I am gradually 
working over the functionality of each script. 

``join`` should become more specific
------------------------------------

The original intent of ``join`` is to join ``CSV`` type of files. In those files, data is assumed to be formatted 
in rows and columns with a possible header on the first line of either file.

However, if either of the files is ``JSON`` then items can be organised as:

1. Lists of lists
2. Lists of primitives
3. Lists of objects

In each of these cases, there are three problems that have to be addressed:

1. How to locate and form the index
2. How to perform the matching
3. How to combine the matched items

And ideally, it should also be possible to join any of the above combinations (e.g. list of lists to a list of objects)

The current implementation operates over files/``stdin`` that are formated as list of lists. However the rest of the 
options are very attractive for ``PyJUnix`` as well. Here is a preliminary list of options / choices:

1. List of lists (current)
    1. Locate index by its zero-based index
    2. Match by forming an index Map of zero-base indexed column value --> list of items sharing the same value
    3. Combine the two by list extension, making sure to remove the index from the matched item.
    
2. List of primitives (with a single column)
    1. The index is the item index. For example, for an input of ``[42, 2, 1]``, the index is assumed to be
       ``[[0,42], [1,2], [2,1]]``.
    2. The matching is performed as per the *List of lists* section
    3. The combination is performed as per the *List of lists* section
        * Inputs ``[0,1,55]`` and ``[3,3,3]`` would produce ``[[0,3],[1,3],[55,3]]``, **but** inputs 
          ``[[0, 22], [0, 54],[1, 89]]`` and ``[42, 44, 38]`` would produce ``[[0, 22, 42], [0, 54, 42], [1, 89, 44]]``
          
3. List of objects
    1. The index can be named
    2. The matching is performed in exactly the same way (in code) as the first case
    3. The combination is perfomed by excluding the index attribute and ``update`` ing the temporary dictionaries.
    

Joining different data types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Combinations of the above cases are not straightforward to resolve, especially when it comes to **combining** data 
types. For example, having matched ``dict`` to ``list``, how should the combination be performed? By copy or
combination?


Further notes
^^^^^^^^^^^^^

1. Could it be possible to *pull* the index via ``jsonpath`` (?)
2. Could it be possible to allow the user to specify the format by letting them specify an inline lambda function as
   ``lambda x,y:`` where ``x,y`` are the matched items from files 1 and 2 (?)



``grep`` is XPath
-----------------

* Grep is easy if you treat it as `XPath <https://en.wikipedia.org/wiki/XPath>`_. 
  That is, just as ``grep`` applies regexp as a "query language" over "string documents", so is XPath a query language 
  for XML documents.

* Fortunately, there is a `jsonpath <https://github.com/JSON-path/JsonPath>`_ and even more fortunately, there is 
  `jsonpath2 <https://github.com/pacifica/python-jsonpath2>`_ for Python.


``ls`` output is nested lists
-----------------------------

* If ``ls`` is not formatted as a set of nested lists, it is very difficult to query it with ``PyJGrep`` later on.
  Every mapping would be an object.
  
* With nested lists, the ``jsonpath`` expression of grep can be considerably simplified.


Need for a schema validator
---------------------------

* A script that validates JSON according to some JSON schema document and can be used in ``test``
* This is relatively easy by using an existing jsonschema module
* Its output could be a minimal well formed JSON document


Data volume and streaming
-------------------------

* For huge JSON files, ``JSON.load()`` might not be a good idea, both for speed and memory size reasons.
* Alternatively, it would be possible to use something like `ijson <https://pypi.org/project/ijson/>`_ with 
  minimal changes to the current `PyJUnix` design.
* In that case, the validator would have to operate on a "per item" basis (expecting that each item would be smaller 
  than the whole document. Also, the ``grep`` would have to operate in the same way.

* But just as it happens with applying XPath over XML with tools such as 
  `xsltproc <http://xmlsoft.org/XSLT/xsltproc.html>`_ for example, you can still do it but it would be better if 
  the files were broken down into smaller, more manageable size files. (Consider for example a 1.5GB KML file. It is 
  doable, but very difficult to work with.
  
* This again brings about the question of what is the sort of "target" or ideal job size for ``pyjunix``. At the moment
  it would be possible to work over jobs that competely exhaust the memory.
