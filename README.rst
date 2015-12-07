|Build Status| |Coverage Status| |PyPI|

ps_tree
=======

`ps_tree` is extension for `pyramid_sacrud
<https://github.com/ITCase/pyramid_sacrud/>`_ which displays a list of records
as tree. This works fine with models from `sqlalchemy_mptt
<https://github.com/ITCase/sqlalchemy_mptt/>`_.

.. image:: https://cdn.rawgit.com/ITCase/ps_tree/master/docs/source/_static/tree.png
   :alt: tree

Look how easy it is to use:

.. code-block:: python

   from pyramid_pages.models import BaseSacrudMpttPage

   Base = declarative_base()
   DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

   class PageTree(Base, BaseSacrudMpttPage):
       __tablename__ = 'pages'

       id = Column(Integer, primary_key=True)

.. code-block:: python

   config.include('ps_tree')
   config.registry.settings['ps_tree.models'] = (PageTree, )
   config.include('pyramid_sacrud', route_prefix='admin')
   config.registry.settings['pyramid_sacrud.models'] = ('', PageTree)

For more docs see http://ps-tree.rtfd.org

Support and Development
=======================

To report bugs, use the `issue tracker
<https://github.com/ITCase/ps_tree/issues>`_

We welcome any contribution: suggestions, ideas, commits with new futures,
bug fixes, refactoring, docs, tests, translations etc

If you have question, contact me sacrud@uralbash.ru or IRC channel #sacrud

License
=======

The project is licensed under the MIT license.

.. |Build Status| image:: https://travis-ci.org/ITCase/ps_tree.svg?branch=master
   :target: https://travis-ci.org/ITCase/ps_tree
.. |Coverage Status| image:: https://coveralls.io/repos/ITCase/ps_tree/badge.png?branch=master
   :target: https://coveralls.io/r/ITCase/ps_tree?branch=master
.. |PyPI| image:: http://img.shields.io/pypi/dm/ps_tree.svg
   :target: https://pypi.python.org/pypi/ps_tree/

