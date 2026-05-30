.. image:: interference_calculator/icon.svg
    :width: 96px
    :height: 96px
    :align: right
    :alt: Interference calculator icon

*******************************
Interference Calculator 2.0
*******************************

Interference Calculator is a scientific desktop tool for mass-spectrometry peak
interference screening. Version 2.0 turns the original general molecular
interference calculator into a modern inorganic mass-spectrometry workflow for
GDMS, ICP-MS, and SIMS.

The application now combines a bilingual PyQt GUI, GDMS-first defaults,
template-based inorganic interference generation, CIAAW 2024 / AME2020 isotope
data, ppm or absolute m/z windows, target-centered spectra, and a compact
data-dense results table.

.. image:: docs/images/main_zh.png
    :align: center
    :alt: Chinese UI screenshot

What Changed In 2.0
-------------------

Version 2.0 is a major project iteration:

* Modern scientific-tool GUI with a clearer control panel, result summary chips,
  empty state, improved table density, and bilingual language switching.
* GDMS, ICP-MS, and SIMS presets with practical defaults for charge state,
  target window, risk model, and instrument mass resolving power.
* Common inorganic element sets, including an all-elements set tuned for
  inorganic MS screening.
* GDMS default target window is ``2000 ppm`` as a full window width, equivalent
  to ``±1000 ppm`` around the calibrated target peak.
* New inorganic mass-spectrometry algorithm using interference templates for
  atomic ions, doubly charged ions, oxides, hydrides, hydroxides, nitrides,
  carbides, sulfides, halides, plasma adducts, background molecules, and small
  matrix clusters.
* ``relative risk`` ranking based on isotope probability and method-specific
  formation factors. It is a screening score, not a quantitative correction.
* Target-centered spectrum display using ``Δppm`` or ``Δm/z`` when a target peak
  is present.
* Updated isotope database generated from CIAAW 2024 isotopic compositions and
  AME2020 atomic masses, including uncertainty and abundance interval metadata.
* Python 3 modernization and focused unit tests for core molecule parsing,
  interference search, inorganic screening, and data schema.

Project Metadata
----------------

Current version: ``2.0.0``

Original author: Zan Peeters

Current maintainer and latest contributor: Tingfe

Repository: https://github.com/Tingfe/interference_calculator

Installation
------------

Use Python 3.9 or newer.

.. code-block:: bash

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -e .

If installing from PyPI after a release:

.. code-block:: bash

    pip install interference_calculator

Running The GUI
---------------

From the source checkout:

.. code-block:: bash

    python interference_calculator/ui.py

After installation, the console entry point is:

.. code-block:: bash

    interference_calculator

Quick GDMS Workflow
-------------------

1. Select ``GDMS`` mode.
2. Enter a target peak such as ``75As`` or ``56Fe``.
3. Keep the default ``2000 ppm`` full window or switch to absolute ``m/z``.
4. Enter sample, matrix, plasma, and background elements, for example
   ``Ar Cl As O H``, or add the all-elements inorganic preset for a broad screen.
5. Set ion model and instrument MRP if needed.
6. Click ``Calculate``.
7. Review candidate peaks, ``Δppm``, required MRP, relative risk, and whether
   each candidate is resolvable.
8. Open the spectrum view to inspect a target-centered peak display.

.. image:: docs/images/spectrum_zh.png
    :align: center
    :alt: Target-centered spectrum screenshot

User Manual
-----------

The illustrated user manual is available here:

`docs/USER_MANUAL.md <docs/USER_MANUAL.md>`_

Core Concepts
-------------

Window Width
~~~~~~~~~~~~

The GUI uses full window width because this matches common instrument settings.
For example, ``2000 ppm`` means the calculation searches ``1000 ppm`` below and
``1000 ppm`` above the target peak. When a valid target peak exists, switching
between ``ppm`` and ``m/z`` converts the displayed value.

Instrument MRP
~~~~~~~~~~~~~~

Instrument MRP does not change candidate generation. It is applied after mass
calculation to mark whether a candidate peak is resolvable from the target.
Candidates that require higher resolving power than the instrument setting are
highlighted as unresolved.

Relative Risk
~~~~~~~~~~~~~

``relative risk`` is a qualitative prioritization score:

.. code-block:: text

    relative risk = isotope probability × formation factor

It helps sort likely interferences for review. It should not be used as a
quantitative abundance correction without method-specific calibration.

Data Sources
------------

Atomic masses are based on AME2020, published in ``Chinese Physics C`` 45,
030002 and 030003. Isotopic compositions are based on CIAAW 2024. Electron mass
uses CODATA 2022.

The packaged isotope table stores representative abundances as well as interval
bounds where CIAAW reports normal-material abundance ranges.

Python API
----------

Inorganic screening:

.. code-block:: python

    import interference_calculator as ic

    data = ic.inorganic_interference(
        ['Ar', 'Cl', 'As', 'O', 'H'],
        '75As',
        targetrange=0.074921,   # half-window in m/z
        charge=[1, 2],
        maxsize=3,
        risk_preset='gdms',
    )

General molecular enumeration is still available:

.. code-block:: python

    import interference_calculator as ic

    data = ic.interference(
        ['Ca', 'O', 'H', 'Si'],
        'Fe',
        targetrange=0.3,
        maxsize=4,
        charge=[1],
        chargesign='+',
    )

Isotope ratio table:

.. code-block:: python

    ratios = ic.standard_ratio(['Ca', 'O'])

Development
-----------

Run the test suite:

.. code-block:: bash

    python -m unittest discover -s tests -v

Update the isotope database:

.. code-block:: bash

    python interference_calculator/update_periodic_table.py

License
-------

BSD 3-Clause Clear. See ``LICENSE.rst``.
