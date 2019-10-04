.. pyjunix documentation master file, created by
   sphinx-quickstart on Fri Oct  4 00:46:34 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyjunix's documentation!
===================================

``pyjunix`` is an attempt at implementing `Eric Fischer's junix <https://github.com/ericfischer/junix>`_.

The functionality implemented so far includes:

* ``pyjkeys``
* ``pyjarray``
* ``pyjunarray``
* ``pyjls``

Installation
------------

1. Checkout the repository
2. Create a ``virtualenv`` with Python 3
3. Install the requirements with ``pip install -r requirments3.txt``
4. Try with ``python pyjls.py`` and so on.


Notes on junix
--------------

* A major question is how to handle mix content passing through these scripts. Mix content is a combination of JSON and
  raw strings, possibly delineated by newlines.
    * The main issue here being that newline delineated strings are basically an implicit JSON array but a newline 
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
      

      
      

  

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
