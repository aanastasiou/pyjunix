.. pyjunix documentation master file, created by
   sphinx-quickstart on Fri Oct  4 00:46:34 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyjunix's documentation!
===================================

``pyjunix`` is an attempt at implementing `Eric Fischer's junix <https://github.com/ericfischer/junix>`_.

For the functionality that has been implemented so far, please see :ref:`current_imp_status` 

Installation
------------

1. Checkout the repository
2. Create a ``virtualenv`` with Python 3
3. Install the requirements with ``pip install -r requirments3.txt``
4. Try with ``python pyjls.py`` and so on.

Invocation
----------

All functionality of ``PyJUnix`` is accessible through the script ``pyjbox.py``. This accepts the name of the script 
to run followed by its parameters. For example, to run ``PyJLs``:

::

    > ./pyjbox.py pyjls
    
Alternatively, it is possible to add symbolic links to ``pyjbox.py`` and it will then decide which script to launch.
This is a straight inspiration from the way `Busybox <https://busybox.net/>`_ works. For example, to call ``pyjls``, 
"automatically":

::

    > ln -s pyjbox.py pyjls
    > ./pyjls
    
In this example, linking ``pyjls`` to ``pyjbox.py`` allows it to decide automatically that it needs to run ``pyjls``.




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
