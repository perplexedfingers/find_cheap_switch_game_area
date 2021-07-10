Tell which area has the most Switch games in lowest price.

Credit to
=========

`eShop Checker <http://eshop-checker.xyz>`_


Requirement
===========

Python >= 3.2

or

Julia >= 1.6.1


Usage
=====

* Connected online

* ``python3 find.py``

or

* ``julia --project=. julia.jl``


Performance?
============

Python
------

.. code-block:: python

    >>> import find
    >>> import timeit
    >>> data, rate = find.download_data()
    >>> timeit.timeit('find.compute(data, rate)', globals=globals(), number=10)
    0.9814049470000441
    >>> timeit.timeit('find.compute(data, rate)', globals=globals(), number=100)
    9.869106056000021
    >>> timeit.timeit('find.compute(data, rate)', globals=globals(), number=1000)
    96.02839189499997


Julia
-----

``julia --project=.``

.. code-block:: julia

    julia> include("Find.jl")
    julia> @time (for i = 1:100; compute(data, rate); end)
    9.665869 seconds (30.91 M allocations: 1.230 GiB, 2.22% gc time)
    julia> @time (for i = 1:1000; compute(data, rate); end)
    90.634181 seconds (309.14 M allocations: 12.297 GiB, 1.43% gc time)


Reference
=========

- https://www.nationsonline.org/oneworld/country_code_list.htm
- https://www.iban.com/currency-codes
