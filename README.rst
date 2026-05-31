.. image:: interference_calculator/icon.svg
   :width: 96px
   :height: 96px
   :align: right
   :alt: 干扰计算器图标

.. _chinese-section:

====================================================
干扰计算器 2.0 维护版 / Interference Calculator 2.0
====================================================

`English <english-section_>`_ | **中文**

**本分支：``maintenance/original``**

这个分支不是旧代码冻结版，而是原作者通用计算器功能边界的现代化维护版。它保留
通用元素 / 同位素组合扫描和同位素比计算，移除无机质谱专项入口；过时的数据、
依赖和 Python 2 / PyQt4 时代的维护负担已经被更新。

无机材料 / GDMS、ICP-MS、SIMS 专用功能在 ``main`` 分支维护并发布。

分支定位
--------

``maintenance/original`` 保留：

* 通用分子 / 同位素组合枚举：``interference()``。
* 标准同位素比表：``standard_ratio()``。
* 现代 PyQt 图形界面、中英文切换、结果表格和谱图查看。
* CIAAW 2024 同位素丰度、AME2020 原子质量和 CODATA 2022 电子质量。
* Python 3.9+、PyQt5、QPainter 谱图、现代打包和测试流程。

``maintenance/original`` 不包含：

* GDMS、ICP-MS、SIMS 仪器预设。
* 无机质谱模板干扰算法。
* ``inorganic_interference()`` API。
* 方法相关的相对风险模型。

安装
----

**方式一：从源码安装（维护分支）**

.. code-block:: bash

   git clone https://github.com/Tingfe/interference_calculator.git
   cd interference_calculator
   git switch maintenance/original
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -e .

**方式二：通过 pip 安装发布版**

.. code-block:: bash

   pip install interference_calculator

注意：PyPI 或 GitHub Releases 的默认发布通常来自 ``main`` 分支。需要通用维护版时，
请确认所安装的版本来自 ``maintenance/original``。

启动界面
--------

.. code-block:: bash

   interference_calculator

通用扫描工作流
--------------

1. 在元素框中输入样品、基体或背景元素，例如 ``Ca O H Si``。
2. 可选：输入目标峰，例如 ``56Fe``、``40Ca16O`` 或 ``55.9349``。
3. 设置完整窗口宽度。通用扫描默认使用 ``m/z`` 窗口；如果输入了有效目标峰，也可以切换为 ``ppm``。
4. 选择离子电荷和最大原子数。
5. 点击 **计算**。
6. 查看候选峰、``m/z``、``Δm/z``、``Δppm``、所需 MRP、概率和可分辨标记。
7. 点击谱图按钮查看候选峰分布。

.. image:: docs/images/main_zh.png
   :align: center
   :alt: 中文界面截图

Python API
----------

通用干扰计算：

.. code-block:: python

   import interference_calculator as ic

   data = ic.interference(
       ['Ca', 'O', 'H', 'Si'],
       'Fe',
       targetrange=0.3,   # m/z 半窗口
       maxsize=4,
       charge=[1],
       chargesign='+',
   )

同位素比率表：

.. code-block:: python

   ratios = ic.standard_ratio(['Ca', 'O'])

数据来源
--------

原子质量基于 AME2020（*Chinese Physics C* 45, 030002 和 030003）。同位素丰度
基于 CIAAW 2024，内置表保留正常材料丰度区间边界。电子质量使用 CODATA 2022。

开发
----

运行测试：

.. code-block:: bash

   python -m unittest discover -s tests -v

更新同位素数据库：

.. code-block:: bash

   python interference_calculator/update_periodic_table.py

许可证
------

BSD 3-Clause Clear。详见 ``LICENSE.rst``。

----

.. _english-section:

====================================================
Interference Calculator 2.0 Maintenance Edition
====================================================

**English** | `中文 <chinese-section_>`_

**Branch: ``maintenance/original``**

This branch is not a frozen copy of the old code. It is the modern maintenance
line for the original calculator's product boundary. It keeps the general
element / isotope-combination scan and isotope-ratio workflow, while removing
the inorganic-MS specialist entry points. Outdated data, dependencies, and the
old Python 2 / PyQt4 maintenance burden have been updated.

Inorganic-materials workflows for GDMS, ICP-MS, and SIMS are developed and
released from the ``main`` branch.

Branch Scope
------------

``maintenance/original`` keeps:

* General molecular / isotope-combination enumeration: ``interference()``.
* Standard isotope-ratio tables: ``standard_ratio()``.
* Modern PyQt GUI with Chinese/English switching, result tables, and spectrum view.
* CIAAW 2024 isotopic compositions, AME2020 atomic masses, and CODATA 2022
  electron mass.
* Python 3.9+, PyQt5, QPainter spectrum rendering, modern packaging, and tests.

``maintenance/original`` does not include:

* GDMS, ICP-MS, or SIMS instrument presets.
* Inorganic-MS template interference generation.
* The ``inorganic_interference()`` API.
* Method-specific relative-risk models.

Installation
------------

**Option A - source install from this maintenance branch**

.. code-block:: bash

   git clone https://github.com/Tingfe/interference_calculator.git
   cd interference_calculator
   git switch maintenance/original
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -e .

**Option B - install a published package**

.. code-block:: bash

   pip install interference_calculator

Note: default PyPI or GitHub Releases builds normally come from ``main``. For
the general maintenance edition, verify that the package was built from
``maintenance/original``.

Run The GUI
-----------

.. code-block:: bash

   interference_calculator

General Scan Workflow
---------------------

1. Enter sample, matrix, or background elements, for example ``Ca O H Si``.
2. Optional: enter a target peak such as ``56Fe``, ``40Ca16O``, or ``55.9349``.
3. Set the full window width. General scan defaults to an absolute ``m/z``
   window; ``ppm`` is available when a valid target peak is present.
4. Select ion charge and maximum molecule size.
5. Click **Calculate**.
6. Review candidate peaks, ``m/z``, ``Δm/z``, ``Δppm``, required MRP,
   probability, and resolvability.
7. Open the spectrum view to inspect candidate peak distribution.

Python API
----------

General interference calculation:

.. code-block:: python

   import interference_calculator as ic

   data = ic.interference(
       ['Ca', 'O', 'H', 'Si'],
       'Fe',
       targetrange=0.3,   # half window in m/z
       maxsize=4,
       charge=[1],
       chargesign='+',
   )

Isotope ratio table:

.. code-block:: python

   ratios = ic.standard_ratio(['Ca', 'O'])

Data Sources
------------

Atomic masses are based on AME2020 (*Chinese Physics C* 45, 030002 and 030003).
Isotopic compositions are based on CIAAW 2024, including normal-material
abundance interval bounds where available. Electron mass uses CODATA 2022.

Development
-----------

Run tests:

.. code-block:: bash

   python -m unittest discover -s tests -v

Update isotope data:

.. code-block:: bash

   python interference_calculator/update_periodic_table.py

License
-------

BSD 3-Clause Clear. See ``LICENSE.rst``.
