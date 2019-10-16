Notes on junix
==============

Dates & Timestamps
------------------

Throughout ``PyJUnix``, timestamps are converted to standard `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ 
formatted date strings. 

At the moment, these strings cannot be queried as dates. This capability will be added soon by marshaling the dates 
in an appropriate way so that they can still be queryable through ``jsonpath``.
 
grep is XPath
-------------

* Grep is easy if you treat it as `XPath <https://en.wikipedia.org/wiki/XPath>`_. 
  That is, just as ``grep`` applies regexp as a "query language" over "string documents", so is XPath a query language 
  for XML documents.

* Fortunately, there is a `jsonpath <https://github.com/JSON-path/JsonPath>`_ and even more fortunately, there is 
  `jsonpath2 <https://github.com/pacifica/python-jsonpath2>`_ for Python.


ls output is nested lists
-------------------------

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
