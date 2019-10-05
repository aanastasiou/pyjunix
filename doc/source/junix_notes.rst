Notes on junix
==============

Pure JSON Or Mixed Content?
---------------------------

* A major question is how to handle mix content passing through these scripts. Mix content is a combination of JSON and
  raw strings, possibly delineated by newlines.
    * Newline delineated strings are basically an implicit JSON array but a newline 
      delineated JSON object is not a JSON object. If the input was something like:
      ::
      
          {"Stavro":4,
           "Mula":2}
          "Beta"
          
      Then a tool like ``pyjarray`` (for example) would have to infer that it is dealing with mixed content in its 
      ``stdin`` and produce the output ``[ {"Stavro":4, "Mula":2}, "Beta" ]``, rather than ``[ "{"Stavro":4,", 
      ""Mula":2", ""Beta"" ]`` that it produces now.
      
    * This in turn means employing a mixed content JSON parser 
        * This could be done with ``pyparsing`` (for example) but it would be extremely slow for huge documents.
        * It might be possible to put something together just by looking for specific literal characters that imply 
          specific JSON types (``{}, [], "", something numeric``).
          
    * If ``junix`` respects JSON throughout, then the tools are supposed to communicate via well formatted JSON.
        * ``pyjkeys`` for example, returns a JSON array of a map's keys, rather than newline delineated strings.
        * At the same time, this reduces somewhat the functionality (and purpose) of ``jarray``.
        
    * Maybe there can be mixed content scripts? Or a universally agreed switch that predisposes the scripts that the 
      input is actually mixed content (?)
      
      
grep is XPath
-------------

* Grep is easy if you treat it as `XPath <https://en.wikipedia.org/wiki/XPath>`_. 
  That is, ``grep`` applies regexp as a "query language" over "string documents" and XPath is a query language for 
  XML documents.

* Fortunately, there is a `jsonpath <https://github.com/JSON-path/JsonPath>`_ and even more fortunately, there is 
  `jsonpath2 <https://github.com/pacifica/python-jsonpath2>`_ for Python.


ls output is nested lists
-------------------------

* If ``ls`` is not formatted as a set of nested lists, it is very difficult to query it with ``PyJGrep`` later on.
  Every mapping would be an object.
  
* With nested lists, the ``jsonpath`` expression will be evaluated for each list item.


Need for a schema validator
---------------------------

* A script that validates JSON according to some JSON schema document and can be used in ``test``
* This is relatively easy by using an existing jsonschema module
* Its output could be a minimal well formed JSON document


Data volume and streaming
-------------------------

* For huge JSON files, `JSON.load()` might not be a good idea, both for speed and memory size reasons.
* Alternatively, it would be possible to use something like `ijson <https://pypi.org/project/ijson/>`_ with 
  minimal changes to the current `PyJUnix` design.
* In that case, the validator would have to operate on a "per item" basis (expecting that each item would be smaller 
  than the whole document. Also, the ``grep`` would have to operate in the same way.

* But just as it happens with applying XPath over XML with tools such as 
  `xsltproc <http://xmlsoft.org/XSLT/xsltproc.html>`_ for example, you can still do it but it would be better if 
  the files were broken down into smaller, more manageable size files. (Consider for example a 1.5GB KML file. It is 
  doable, but very difficult to work with.
  
* This again brings about the question of what is the sort of "target" or ideal job size for ``pyjunix``. At the moment
  it would be possible to work over jobs that competely exhaust the memory (?).
