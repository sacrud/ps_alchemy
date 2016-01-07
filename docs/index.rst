.. sacrud documentation master file, created by
   sphinx-quickstart on Fri Jun 27 15:28:02 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Overview
========

`ps_alchemy` is extension for `pyramid_sacrud
<https://github.com/sacrud/pyramid_sacrud/>`_ which provides SQLAlchemy models.

Look how easy it is to use:

.. code-block:: python

   Base = declarative_base()
   DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

   class PageTree(Base):
       __tablename__ = 'pages'

       id = Column(Integer, primary_key=True)

.. code-block:: python

   config.include('ps_alchemy')
   config.include('pyramid_sacrud', route_prefix='admin')
   config.registry.settings['pyramid_sacrud.models'] = ('webpages', [PageTree, ])

go to http://localhost:6543/sacrud/

Example can be found here https://github.com/sacrud/ps_alchemy/tree/master/example

Usage
=====

.. toctree::
  :maxdepth: 3

  pages/install.rst
  pages/configuration/index.rst
  pages/api.rst

Support and Development
=======================

To report bugs, use the `issue tracker
<https://github.com/sacrud/ps_alchemy/issues>`_.

We welcome any contribution: suggestions, ideas, commits with new futures,
bug fixes, refactoring, docs, tests, translations etc

If you have question, contact me sacrud@uralbash.ru or IRC channel #sacrud

License
=======

The project is licensed under the MIT license.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
