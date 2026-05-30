.. image:: interference_calculator/icon.svg
   :width: 96px
   :height: 96px
   :align: right
   :alt: 干扰计算器图标

================================
干扰计算器 / Interference Calculator 2.0
================================

**干扰计算器** 是一款用于质谱峰干扰筛查的科学桌面工具。2.0 版将原本通用分子干扰计算器升级为面向 GDMS、ICP-MS 和 SIMS 的现代化无机质谱分析工作流。

该应用整合了双语 PyQt 界面、以 GDMS 优先的默认设置、基于模板的无机干扰生成、CIAAW 2024 / AME2020 同位素数据、ppm 或绝对 m/z 窗口、以目标峰为中心的光谱视图，以及紧凑高效的干扰结果表格。

.. image:: docs/images/main_zh.png
   :align: center
   :alt: 中文界面截图

2.0 版更新内容
--------------

2.0 版是一次重大迭代：

* 现代化科学工具 GUI：更清晰的控制面板、结果概览标签、空状态提示、更紧凑的表格布局，并支持中英文界面切换。
* GDMS、ICP-MS 和 SIMS 预设：提供电荷态、目标窗口、风险模型和仪器质量分辨力（MRP）的实用默认值。
* 常用无机元素集：包含适用于无机质谱筛查的全元素集。
* GDMS 默认目标窗口为 ``2000 ppm``（全窗口宽度），等同于目标峰校准后 ``±1000 ppm`` 的范围。
* 新的无机质谱算法：基于干扰模板生成原子离子、双电荷离子、氧化物、氢化物、氢氧化物、氮化物、碳化物、硫化物、卤化物、等离子体加合物、背景分子及小型基质团簇的干扰。
* ``相对风险`` 排序：基于同位素概率和特定方法的形成因子进行评估，用于筛查排序而非定量校正。
* 目标峰中心光谱视图：存在目标峰时显示 ``Δppm`` 或 ``Δm/z`` 分布。
* 同位素数据库更新：基于 CIAAW 2024 同位素丰度和 AME2020 原子质量生成，包含不确定度和丰度范围元数据。
* Python 3 现代化改造，并为核心分子解析、干扰搜索、无机筛查和数据模式编写了单元测试。

项目信息
--------

当前版本：``2.0.0``

原作者：Zan Peeters

当前维护者及最新贡献者：Tingfe

仓库地址：https://github.com/Tingfe/interference_calculator

安装
----

需要 Python 3.9 或更高版本。

.. code-block:: bash

   python3 -m venv .venv
   . .venv/bin/activate
   pip install -e .

若从 PyPI 安装：

.. code-block:: bash

   pip install interference_calculator

启动界面
--------

从源码目录启动：

.. code-block:: bash

   python interference_calculator/ui.py

安装后使用控制台入口：

.. code-block:: bash

   interference_calculator

GDMS 快速工作流
---------------

1. 选择 ``GDMS`` 模式。
2. 输入目标峰，如 ``75As`` 或 ``56Fe``。
3. 保持默认 ``2000 ppm`` 全窗口，或切换为绝对 ``m/z`` 窗口。
4. 输入样品、基质、等离子体及背景元素，例如 ``Ar Cl As O H``，或添加全元素无机预设进行广泛筛查。
5. 根据需要设置离子模型和仪器 MRP。
6. 点击 **计算**。
7. 查阅候选峰、``Δppm``、所需 MRP、相对风险及每个峰是否可分辨。
8. 打开光谱视图查看以目标峰为中心的峰分布。

.. image:: docs/images/spectrum_zh.png
   :align: center
   :alt: 目标峰中心光谱截图

用户手册
--------

图文用户手册请见：

`docs/USER_MANUAL.md <docs/USER_MANUAL.md>`_

核心概念
--------

窗口宽度
~~~~~~~~

界面使用全窗口宽度，这与常见的仪器设置一致。例如 ``2000 ppm`` 表示计算范围为低于目标峰 ``1000 ppm`` 至高于目标峰 ``1000 ppm``。存在有效目标峰时，``ppm`` 与 ``m/z`` 之间可互相转换。

仪器 MRP
~~~~~~~~

仪器 MRP 不影响候选峰生成。它在质量计算后应用以标记候选峰是否可从目标峰中分辨出来。需要比仪器设置更高分辨力的候选峰会被标记为未分辨。

相对风险
~~~~~~~~

``相对风险`` 是定性优先级评分：

.. code-block:: text

   相对风险 = 同位素概率 × 形成因子

用于对可能的干扰进行排序审查，不应在缺乏特定方法校准的情况下用作定量丰度校正。

数据来源
--------

原子质量基于 AME2020（发表于 *Chinese Physics C* 45, 030002 和 030003）。同位素丰度基于 CIAAW 2024。电子质量使用 CODATA 2022。

内置同位素表存储代表性丰度值以及 CIAAW 报告正常材料丰度范围的区间边界。

Python API
----------

无机筛查：

.. code-block:: python

   import interference_calculator as ic

   data = ic.inorganic_interference(
       ['Ar', 'Cl', 'As', 'O', 'H'],
       '75As',
       targetrange=0.074921,   # 半窗口，单位 m/z
       charge=[1, 2],
       maxsize=3,
       risk_preset='gdms',
   )

通用分子枚举仍可使用：

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

同位素比率表：

.. code-block:: python

   ratios = ic.standard_ratio(['Ca', 'O'])

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

================================
Interference Calculator 2.0
================================

Interference Calculator is a scientific desktop tool for mass-spectrometry peak
interference screening. Version 2.0 turns the original general molecular
interference calculator into a modern inorganic mass-spectrometry workflow for
GDMS, ICP-MS, and SIMS.

The application combines a bilingual PyQt GUI, GDMS-first defaults,
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
* Target-centered spectrum display using ``Δppm`` or ``Δm/z`` when a target
  peak is present.
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

If installing from PyPI:

.. code-block:: bash

   pip install interference_calculator

Running the GUI
---------------

From the source checkout:

.. code-block:: bash

   python interference_calculator/ui.py

After installation:

.. code-block:: bash

   interference_calculator

Quick GDMS workflow
-------------------

1. Select ``GDMS`` mode.
2. Enter a target peak such as ``75As`` or ``56Fe``.
3. Keep the default ``2000 ppm`` full window or switch to absolute ``m/z``.
4. Enter sample, matrix, plasma, and background elements, for example
   ``Ar Cl As O H``, or add the all-elements preset for a broad screen.
5. Set ion model and instrument MRP if needed.
6. Click **Calculate**.
7. Review candidate peaks, ``Δppm``, required MRP, relative risk, and whether
   each candidate is resolvable.
8. Open the spectrum view to inspect the target-centered peak display.

.. image:: docs/images/spectrum_zh.png
   :align: center
   :alt: Target-centered spectrum screenshot

User manual
-----------

The illustrated user manual:

`docs/USER_MANUAL.md <docs/USER_MANUAL.md>`_

Core concepts
-------------

Window width
~~~~~~~~~~~~

The GUI uses full window width to match common instrument settings. For
example, ``2000 ppm`` means the calculation searches ``1000 ppm`` below and
``1000 ppm`` above the target peak. When a valid target peak exists, switching
between ``ppm`` and ``m/z`` converts the displayed value automatically.

Instrument MRP
~~~~~~~~~~~~~~

Instrument MRP does not change candidate generation. It is applied after mass
calculation to mark whether a candidate peak is resolvable from the target.
Candidates that require higher resolving power than the instrument setting are
highlighted as unresolved.

Relative risk
~~~~~~~~~~~~~

``relative risk`` is a qualitative screening score:

.. code-block:: text

   relative risk = isotope probability × formation factor

It helps rank interferences for review. It should not be used as a quantitative
abundance correction without method-specific calibration.

Data sources
------------

Atomic masses are based on AME2020, published in *Chinese Physics C* 45,
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
