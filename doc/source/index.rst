.. pyjunix documentation master file, created by
   sphinx-quickstart on Fri Oct  4 00:46:34 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyjunix's documentation!
===================================

``pyjunix`` started as an attempt at implementing `Eric Fischer's junix <https://github.com/ericfischer/junix>`_ idea, 
around September 2019.

The tag line of ``junix`` was *"Unix as if JSON mattered"* and it seemed to suggest using JSON as the serialisation format
for inter-process communication but also a set of programs for processing JSON following the 
`Unix Philosophy <https://en.wikipedia.org/wiki/Unix_philosophy>`_:

* Write programs that do one thing and do it well.
* Write programs to work together.
* Write programs to handle text streams, because that is a universal interface.

``PyJUnix`` offers a basic object oriented framework to parse arguments and data from the command line and pass them 
over to the programs that implement each functionality separately. It also offers the set of programs for processing 
JSON that translate their Unix functionality over text files to functionality over JSON objects. Wherever it is 
possible, the scripts are almost identical, even down to the individual parameter names they expect.

The currently implemented functionality is divided into two broad categories of scripts:

* Pure JSON Data Generators
    * These include ``PyJLs, PyJPs, PyJLast`` to get a list of files, a list of processes and a list of users logged in 
      to the system respetively.

* JSON Data Processors
  This is further subdivided into two categories because of JSON's repertoir of different data types:
  
    * JSON Specific processors
        * These implement operations that are specific to JSON
            * ``PyJArray, PyJUnArray`` to pack and unpack raw lines of text into arrays
            * ``PyJKeys`` to unpick just the keys from maps
            
    * Unix text processing programs "translated" over JSON
        * In this case, a modification of principle *"Write programs to handle text streams, because that is a universal
          interface"* is proposed, where the word "text" is exchanged for the word "JSON". This change is mostly 
          straightforward because "text", in unix, implies two more data types, those of "list" (lines of text separated
          by a newline character) and "array" (comma separated lines of text that split a line in "fields" and these 
          lines also separated by newlines).
        * Where "text" implies "list, list-of-lists", JSON also adds 
          `Maps <https://en.wikipedia.org/wiki/Associative_array>`_. The implication here is that in addition to a
          "field selector" (e.g. "Sort this array by the **third** column", JSON documents can also specify "paths" to 
          select a particular field. 
        * Wherever this is required, ``PyJUnix`` makes use of `jsonpath <https://github.com/pacifica/python-jsonpath2>`_
          which is basically `XPath <https://en.wikipedia.org/wiki/XPath>`_ expressions over JSON data structures.
    * At the moment, scripts in this category include ``PyJCat, PyJDiff, PyJGrep, PyJJoin, PyJPaste, PyJSort, PyJSplit, 
      PyJUniq``

 
For more information on the functionality that has been implemented so far, please see :ref:`current_imp_status` 

Installation
------------

1. Checkout the repository
2. Create a ``virtualenv`` with Python 3
3. Install the requirements with ``pip install -r requirments3.txt``
4. Try with ``python pyjls.py`` and so on.

Launching scripts
-----------------

All functionality of ``PyJUnix`` is accessible through the script ``pyjbox.py``. This accepts the name of the script 
to run followed by its parameters. For example, to run ``PyJLs``:

::

    > ./pyjbox.py pyjls
    
In this way, it is possible to add symbolic links to ``pyjbox.py`` and it will then decide which script to launch. For
example:

::

    > ln -s ./pyjbox.py pyjls
    
Now ``pyjls`` can be called as if it was a standalone ``pyjls`` script. Obviously here, ``pyjbox.py`` and the symbolic 
links to it can "live" in different locations on a file system. This is a straight inspiration from the way 
`Busybox <https://busybox.net/>`_ works. 


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   junix_notes
   pyjunix_api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
