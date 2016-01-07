Template redefinition
=====================

Just create template file in your project ``templates/ps_alchemy/crud/``
directory:

.. code::

    myapp/
    └── templates
        └── ps_alchemy/crud/
              └── create.jinja2  <-- custom template for ps_alchemy create page
              └── list.jinja2    <-- custom template for ps_alchemy list page

You can also change the template for just one model or your own for each model.

.. code-block:: python
    :linenos:
    :emphasize-lines: 8-9

    class Tree(Base):
        __tablename__ = 'tree'

        id = Column(Integer, primary_key=True)
        name = Column(Unicode)
        parent_id = Column(Integer, ForeignKey('tree.id'))

        sacrud_list_template = 'myapp:/templates/my_custom_list_with_jqtree.jinja2'
        sacrud_edit_template = 'myapp:/templates/my_custom_edit.mako'
