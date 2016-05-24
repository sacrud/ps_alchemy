Models
======

Fully support
`ColanderAlchemy <https://colanderalchemy.readthedocs.io/>`_ specification.

Columns
-------

read only
~~~~~~~~~

Redefine widget for column with ``readonly`` attribute.

.. code-block:: python
   :emphasize-lines: 5

    class Venue(Base):
        __tablename__ = 'venue'
        id = Column(Integer, primary_key=True,
                             info={'colanderalchemy': {
                                 'widget': deform.widget.TextAreaWidget(readonly=True)
                             }})

title
~~~~~

Change column title example:

.. code-block:: python
   :emphasize-lines: 6

    class Venue(Base):
        __tablename__ = 'venue'
        id = Column(Integer, primary_key=True,
                             info={'colanderalchemy': {
                                 'widget': deform.widget.TextAreaWidget(readonly=True),
                                 'title'='My id'
                             }})
