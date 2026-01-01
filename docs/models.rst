======
Models
======

.. toctree::
    :titlesonly:


Example models
**************

.. code:: python

   from init import db
   from shopyo.api.models import PkModel

   class MyModel(PkModel):
       __tablename__ = 'mymodel'
       name = db.Column(db.String(100))

🔩 Migrations
-------------

.. note::

   You can run

   .. code:: bash

       shopyo <command>

   or

   .. code:: bash

       python manage.py <command>

In case of change to models, do

.. code-block:: bash

   python manage.py db migrate
   python manage.py db upgrade
