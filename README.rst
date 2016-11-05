|Build Status| |Coverage Status|

ps_alchemy
==========

`ps_alchemy` is extension for `pyramid_sacrud
<https://github.com/sacrud/pyramid_sacrud/>`_ which provides SQLAlchemy
models.

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

For more docs see http://ps-alchemy.rtfd.org

Support and Development
=======================

To report bugs, use the `issue tracker
<https://github.com/sacrud/ps_alchemy/issues>`_

We welcome any contribution: suggestions, ideas, commits with new futures,
bug fixes, refactoring, docs, tests, translations etc

If you have question, contact me sacrud@uralbash.ru or IRC channel #sacrud

License
=======

The project is licensed under the MIT license.

.. |Build Status| image:: https://travis-ci.org/sacrud/ps_alchemy.svg?branch=master
   :target: https://travis-ci.org/sacrud/ps_alchemy
.. |Coverage Status| image:: https://coveralls.io/repos/sacrud/ps_alchemy/badge.png?branch=master
   :target: https://coveralls.io/r/sacrud/ps_alchemy?branch=master
