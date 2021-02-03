Welcome to CANOpen Monitor's documentation!
===========================================

.. warning::
    This is still a work in progress.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Node Ranges to Types Map
------------------------

+----------------+--------+---------+
|Type            |Range In|Range Out|
+----------------+--------+---------+
|NMT node control|0       |         |
+----------------+--------+---------+
|SYNC            |0x080   |         |
+----------------+--------+---------+
|Emergency       |0x80    |0x100    |
+----------------+--------+---------+
|Time Stamp      |100     |         |
+----------------+--------+---------+
|PDO1 tx         |0x180   |0x200    |
+----------------+--------+---------+
|PDO1 rx         |0x200   |0x280    |
+----------------+--------+---------+
|PDO2 tx         |0x280   |0x300    |
+----------------+--------+---------+
|PDO2 rx         |0x300   |0x380    |
+----------------+--------+---------+
|PDO3 tx         |0x380   |0x400    |
+----------------+--------+---------+
|PDO3 rx         |0x400   |0x480    |
+----------------+--------+---------+
|PDO4 tx         |0x480   |0x500    |
+----------------+--------+---------+
|PDO4 rx         |0x500   |0x580    |
+----------------+--------+---------+
|SDO tx          |0x580   |0x600    |
+----------------+--------+---------+
|SDO rx          |0x600   |0x680    |
+----------------+--------+---------+
|Heartbeats      |0x700   |0x7FF    |
+----------------+--------+---------+

Glossary
--------

.. toctree::
    :maxdepth: 2

    glossary

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _OreSat Website: https://www.oresat.org/
.. _OreSat GitHub: https://github.com/oresat
