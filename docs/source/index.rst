Hoss Client Library for Python
===============================================

A Python library for the Hoss hybrid cloud object store system. It lets you do most administrative things that you can do from the Hoss
UI in addition to interacting with datasets – create datasets, modify permissions, configure syncing, list, upload, and download files, etc.


Installation
------------

The latest stable version `is available on PyPI <https://pypi.python.org/pypi/hoss-client/>`_. Either add ``hoss-client`` to your ``requirements.txt`` file or install with pip::

    pip install -U hoss-client

Getting started
---------------

To authenticate with a server, you must set the environment variable ``HOSS_PAT`` to a valid Personal Access Token (PAT). You can only generate
PATs via the Hoss UI. To generate a PAT, log into a server, navigate to the "Tokens" page, and create a new token.

To interact with a server, first instantiate a server instance using the :py:func:`~hoss.connect` function.:

.. code-block:: python

  import hoss
  server = hoss.connect("https://hoss.mycompany.com")

Once you have a server connection, you can list available namespaces:

.. code-block:: python

  >>> server.list_namespaces()
  [<Namespace: default - Default namespace>]

  >>> ns = server.get_namespaces("default")

Create a dataset in a namespace:

.. code-block:: python

  >>> ds = ns.create_dataset("example-dataset", "A dataset for an example")

Write and read data to a dataset:

.. code-block:: python

  >>> file1 = ds / "my-file.txt"

  >>> file1.write_text("Hello, Hoss!")

  >>> print(file1.read_text())
  "Hello, Hoss!"

Iterate through files in a dataset:

.. code-block:: python

  >>> for f in (ds).glob("*"):
  ...   print(f)

  <DatasetRef: example-dataset/folder1/>
  <DatasetRef: example-dataset/foo0.txt>
  <DatasetRef: example-dataset/my-file.bin>
  <DatasetRef: example-dataset/my-file.txt>

  >>> for f in (ds).glob("**/foo*"):
  ...   print(f)

  <DatasetRef: example-dataset/folder1/foo1.txt>
  <DatasetRef: example-dataset/folder1/foo2.txt>
  <DatasetRef: example-dataset/folder1/foo3.txt>
  <DatasetRef: example-dataset/foo0.txt>


Search for objects via metadata tags:

.. code-block:: python

  >>> results = server_local.search_refs({'fizz': 'buzz'})
  >>> print(results)
  [<DatasetRef: example-dataset/file42.txt>]


  >>> results[0].metadata
  {'fizz': 'buzz', 'foo': 'bar'}

That's just a sample of what you can do. For more details, :doc:`review the rest of the documentation <servers>`.

For more detailed examples, check out
`the examples directory <https://github.com/gigantum/hoss-client/tree/main/examples>`_

Contribute
----------

- Issue Tracker: `https://github.com/gigantum/hoss-client/issues <https://github.com/gigantum/hoss-client/issues>`_
- Source Code: `https://github.com/gigantum/hoss-client <https://github.com/gigantum/hoss-client>`_

License
-------

The project is licensed under the `MIT license. <https://github.com/gigantum/hoss-client/blob/main/LICENSE>`_

.. toctree::
   :hidden:
   :maxdepth: 2

   servers
   namespaces
   datasets
   data
   groups
   cli
   hoss



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
