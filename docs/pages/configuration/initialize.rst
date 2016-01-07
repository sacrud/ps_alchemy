Initialize
==========

.. code-block:: python
    :linenos:

    from .models import (Model1, Model2, Model3,)

    # add SQLAlchemy backend
    config.include('ps_alchemy')

    # add pyramid_sacrud and project models
    settings = config.registry.settings
    settings['pyramid_sacrud.models'] = (
        ('Group1', [Model1, Model2]),
        ('Group2', [Model3])
    )

check it there http://localhost:6543/sacrud/
