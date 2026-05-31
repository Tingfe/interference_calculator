.. image:: interference_calculator/icon.svg
   :width: 96px
   :height: 96px
   :align: right
   :alt: 干扰计算器图标

.. _chinese-section:

============================================================
无机质谱峰干扰计算器 / Inorganic MS Interference Calculator 2.4
============================================================

`English <english-section_>`_ | **中文**

**无机质谱峰干扰计算器** 是一款用于质谱峰干扰筛查的科学桌面工具。当前 ``main`` 分支是面向 GDMS、ICP-MS 和 SIMS 的无机材料专用工具；``maintenance/original`` 是已经现代化维护过的通用扫描分支，保留原作者通用元素 / 同位素组合扫描和同位素比功能，同时继续使用更新后的数据、依赖和打包流程。

该应用整合了双语 PyQt 界面、以 GDMS 优先的默认设置、基于模板的无机干扰生成、CIAAW 2024 / AME2020 同位素数据、以 ``ppm`` 表示的完整窗口宽度、以目标峰为中心的交互式谱图，以及紧凑高效的干扰结果表格。

.. image:: docs/images/main_zh.png
   :align: center
   :alt: 中文界面截图

2.4 版更新内容
--------------

2.x 是一次重大迭代，2.4 版在 2.1 的无机质谱主线基础上完成了 GDMS Excel
谱图导入、目标峰选择、发布打包和启动体验的里程碑升级：

* 现代化科学工具 GUI：更清晰的控制面板、结果概览标签、空状态提示、更紧凑的表格布局，并支持中英文界面切换。
* GDMS、ICP-MS 和 SIMS 预设：提供电荷态、目标窗口、风险模型和仪器质量分辨力（MRP）的实用默认值；导入目标峰存在有效 ``FWHM`` 时，可按 ``observed m/z / FWHM`` 自动估算 MRP。
* GDMS Excel 谱图导入：自动读取导出文件中的 ``Fe{56}`` 这类同位素谱图，填充元素列表，并提供实测目标峰选择；导入的 ``Mass`` / ``Values`` 点可通过默认关闭的实验开关在谱图中叠加为真实峰形，也可按理论同位素 ``m/z`` 进行可选显示对齐。
* 常用无机元素集：包含适用于无机质谱筛查的全元素集。
* GDMS 默认目标窗口为 ``2000 ppm``（全窗口宽度），等同于目标峰校准后 ``±1000 ppm`` 的范围；导入目标峰有有效 ``Mass`` 点列时，可按真实数据范围自动估算完整 ppm 窗口。
* 新的无机质谱算法：基于干扰模板生成原子离子、双电荷离子、氧化物、氢化物、氢氧化物、氮化物、碳化物、硫化物、卤化物、等离子体加合物、背景分子及小型基质团簇的干扰。
* ``相对风险`` 排序：基于同位素概率和特定方法的形成因子进行评估，用于筛查排序而非定量校正。
* 目标峰中心交互式谱图：存在目标峰时显示 ``Δppm`` 分布，支持可选的导入 GDMS 真实峰形叠加（测试功能，默认关闭）、实测峰到理论 ``m/z`` 的显示匹配、峰悬停详情、点击联动表格、仪器 MRP 未分辨区显示和 PNG 导出。
* 同位素数据库更新：基于 CIAAW 2024 同位素丰度和 AME2020 原子质量生成，包含不确定度和丰度范围元数据。
* Python 3 现代化改造，并为核心分子解析、干扰搜索、无机筛查、双语覆盖和数据模式编写了单元测试。

项目信息
--------

当前版本：``2.4.2``

原作者：Zan Peeters

当前维护者及最新贡献者：Tingfe

仓库地址：https://github.com/Tingfe/interference_calculator

安装
----

**方式一：免安装版（推荐，无需 Python）**

从 `GitHub Releases <https://github.com/Tingfe/interference_calculator/releases>`_
下载对应平台的免安装版本，直接运行：

- **Windows**：下载 ``InterferenceCalculator-Windows-*.zip``，解压后双击
  ``InterferenceCalculator.exe``。Windows 采用目录版打包，避免单文件 ``.exe``
  每次启动前解压运行时导致长时间无响应。
- **macOS**：下载 ``InterferenceCalculator-macOS-*.dmg``，打开后将应用拖入 ``Applications`` 文件夹，首次打开需在「安全性与隐私」中允许。

**方式二：通过 PyPI 安装（需要 Python 3.9+）**

.. code-block:: bash

   pip install interference_calculator

GDMS Excel 导入和 Excel 导出所需的 ``openpyxl`` 已包含在默认依赖中。

也可从 `GitHub Releases <https://github.com/Tingfe/interference_calculator/releases>`_
下载 wheel 包手动安装：

.. code-block:: bash

   pip install interference_calculator-*.whl

**方式三：从源码安装（开发者）**

.. code-block:: bash

   git clone https://github.com/Tingfe/interference_calculator.git
   cd interference_calculator
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -e .

启动界面
--------

- **免安装版**：Windows 解压 ``.zip`` 后双击 ``InterferenceCalculator.exe``；
  macOS 打开 ``.dmg`` 后点击应用。
- **PyPI 安装版**：在终端中运行 ``interference_calculator`` 即可启动图形界面。
- **源码运行**：在项目根目录运行 ``python -m interference_calculator.ui``；直接运行
  ``python interference_calculator/ui.py`` 也受支持。

GDMS 快速工作流
---------------

1. 选择 ``GDMS`` 模式。
2. 如有 GDMS 导出的 Excel 谱图文件，点击 **导入**，软件会自动提取文件中的元素和可选目标峰。
3. 导入后优先从目标峰列表选择；只有目标不在导入文件中时，勾选 **手动目标** 再选择 ``75As``、``56Fe`` 等目标。
4. 保持默认 ``2000 ppm`` 全窗口；导入目标峰有有效 ``Mass`` 点列时，可勾选扫描窗口旁边的 ``自动``。
5. 导入文件后，``添加组合`` 会出现 ``导入元素`` 预设；组合选择只会追加当前缺失的元素，因此可在保留导入样品元素的同时补充 Ar 背景、轻元素背景、卤素 / 硫或基体元素。
6. 如未导入文件，点击元素区的 **添加** 按钮选择样品、基质、等离子体及背景元素，例如 ``Ar Cl As O H``，或添加全元素无机预设进行广泛筛查。
7. 根据需要设置离子模型和仪器 MRP；导入目标峰有有效 ``FWHM`` 时，可勾选 MRP 旁边的 ``自动``。
8. 点击 **计算**。
9. 查阅候选峰、``Δppm``、所需 MRP、相对风险及每个峰是否可分辨。
10. 打开谱图视图查看以目标峰为中心的峰分布；已导入 GDMS Excel 时，可在谱图工具栏手动打开 ``实测峰（测试）`` 叠加真实 ``Mass`` / ``Values`` 峰形，必要时再打开 ``匹配 m/z`` 将每条实测峰中心对齐到理论同位素 ``m/z``。``匹配 m/z`` 会自动打开实测峰叠加，并显示对齐参考线和偏移量标签；悬停峰可看详情，点击峰可定位表格行。

导入目标峰时，``谱图质心`` / ``谱图峰顶`` 是软件从 Excel 的 ``Mass`` / ``Values``
点计算得到的峰形摘要；``Δm/z``、``Δppm``、MRP 和谱图中心始终相对理论目标
``m/z`` 计算。真实谱图曲线默认会先用所选目标峰的谱图质心 / 峰顶做零点对齐，再绘制到同一个目标居中横轴上，避免把理论候选峰和原始 observed 目标位置混用。谱图工具栏中的 ``匹配 m/z`` 是显示选项，会把每条实测峰的质心 / 峰顶分别对齐到对应同位素的理论 ``m/z``，并用参考线和偏移标签显示对齐量，不改变干扰计算结果。

.. image:: docs/images/spectrum_zh.png
   :align: center
   :alt: 目标峰中心光谱截图

用户手册
--------

图文用户手册请见：

`docs/USER_MANUAL.md <docs/USER_MANUAL.md>`_

维护与发布文档：

- `分支模型 / Branching model <docs/BRANCHING.md>`_
- `发布指南 / Release guide <docs/RELEASE.md>`_

核心概念
--------

窗口宽度
~~~~~~~~

界面使用全窗口宽度，这与常见的仪器设置一致。例如 ``2000 ppm`` 表示计算范围为低于目标峰 ``1000 ppm`` 至高于目标峰 ``1000 ppm``。GUI 使用 ``ppm`` 窗口；Python API 仍使用 ``m/z`` 半宽作为 ``targetrange``。导入 GDMS 目标峰包含有效 ``Mass`` 点列时，可启用扫描窗口旁边的 ``自动``；软件会按 ``(max Mass - min Mass) / observed m/z * 1e6`` 估算完整 ppm 窗口，没有有效 Mass 范围时该开关会禁用。

仪器 MRP
~~~~~~~~

仪器 MRP 不影响候选峰生成。它在质量计算后应用以标记候选峰是否可从目标峰中分辨出来。需要比仪器设置更高分辨力的候选峰会被标记为未分辨。导入 GDMS 目标峰包含有效 ``FWHM`` 时，可启用 ``自动`` MRP；软件会使用 ``observed m/z / FWHM`` 估算仪器分辨能力，没有有效 ``FWHM`` 时该开关会禁用。

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

分支策略：

- ``main``：无机材料 / 无机质谱专用主线，包含 GDMS、ICP-MS、SIMS 工作流，是默认发布分支。
- ``maintenance/original``：现代化通用扫描维护线，保留通用分子枚举和同位素比计算，继续使用新同位素数据库、现代依赖和打包流程，但不包含无机专项预设、模板或风险模型。

版本发布采用 GitHub Actions 自动化。更新 ``__version__`` 和中英文 ``CHANGELOG.md`` 后，推送 ``vX.Y.Z`` 标签会自动运行测试、构建源码包 / wheel、Windows ``.zip`` 目录版应用和 macOS ``.dmg``，并用当前版本的中英文 changelog 生成 GitHub Release。

未配置 Apple 签名 secrets 时，发布流程会生成未签名、未公证的 macOS DMG
（文件名包含 ``macOS-unsigned``）；配置完整 secrets 后会自动生成 Developer ID
签名并通过 Apple 公证的正式 DMG。详见
`docs/MACOS_SIGNING.md <docs/MACOS_SIGNING.md>`_。

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

=========================================
Inorganic MS Interference Calculator 2.4
=========================================

**English** | `中文 <chinese-section_>`_

Inorganic MS Interference Calculator is a scientific desktop tool for
mass-spectrometry peak interference screening. The current ``main`` branch is
the inorganic-materials edition for GDMS, ICP-MS, and SIMS;
``maintenance/original`` is the modernized general-scan maintenance line,
preserving the original element / isotope-combination scan and isotope-ratio
workflow while keeping refreshed data, dependencies, and packaging.

The application combines a bilingual PyQt GUI, GDMS-first defaults,
template-based inorganic interference generation, CIAAW 2024 / AME2020 isotope
data, full-width ``ppm`` target windows, an interactive target-centered
spectrum, and a compact data-dense results table.

.. image:: docs/images/main_en.png
   :align: center
   :alt: English UI screenshot

What Changed In 2.4
-------------------

Version 2.x is a major project iteration. Version 2.4 builds on the 2.1
inorganic-MS workflow with milestone upgrades for GDMS Excel profile import,
target selection, release packaging, and startup experience:

* Modern scientific-tool GUI with a clearer control panel, result summary chips,
  empty state, improved table density, and bilingual language switching.
* GDMS, ICP-MS, and SIMS presets with practical defaults for charge state,
  target window, risk model, and instrument mass resolving power. When an
  imported target has valid ``FWHM``, MRP can be estimated automatically as
  ``observed m/z / FWHM``.
* GDMS Excel profile import that reads exported isotope profiles such as
  ``Fe{56}``, fills the element list, and makes imported profile targets the
  primary selection path. Profile m/z is calculated from the imported
  mass/intensity points as a centroid, or from the apex when needed. Imported
  ``Mass`` / ``Values`` points can be overlaid as real peak shapes in the
  spectrum view through an experimental toggle that is off by default, with an
  optional display-only match to theoretical isotope ``m/z``.
* Imported GDMS element sets stay available in the element-set menu. Element
  presets append only missing elements, so users can keep imported sample
  elements while adding plasma, background, halogen/sulfur, or matrix sources.
* Common inorganic element sets, including an all-elements set tuned for
  inorganic MS screening.
* GDMS default target window is ``2000 ppm`` as a full window width, equivalent
  to ``±1000 ppm`` around the calibrated target peak. When an imported target
  has valid ``Mass`` points, the full ppm window can be estimated from the
  actual profile range.
* New inorganic mass-spectrometry algorithm using interference templates for
  atomic ions, doubly charged ions, oxides, hydrides, hydroxides, nitrides,
  carbides, sulfides, halides, plasma adducts, background molecules, and small
  matrix clusters.
* ``relative risk`` ranking based on isotope probability and method-specific
  formation factors. It is a screening score, not a quantitative correction.
* Interactive target-centered spectrum display using ``Δppm`` when a target
  peak is present, with optional imported GDMS real-profile overlays
  (experimental, off by default), observed-profile matching to theoretical
  ``m/z``, peak hover details, click-to-table selection, an instrument-MRP
  unresolved band, and PNG export.
* Updated isotope database generated from CIAAW 2024 isotopic compositions and
  AME2020 atomic masses, including uncertainty and abundance interval metadata.
* Python 3 modernization and focused unit tests for core molecule parsing,
  interference search, inorganic screening, bilingual coverage, and data schema.

Project Metadata
----------------

Current version: ``2.4.2``

Original author: Zan Peeters

Current maintainer and latest contributor: Tingfe

Repository: https://github.com/Tingfe/interference_calculator

Installation
------------

**Option A — Standalone app (recommended, no Python required)**

Download the platform-specific package from
`GitHub Releases <https://github.com/Tingfe/interference_calculator/releases>`_
and run directly:

- **Windows**: download ``InterferenceCalculator-Windows-*.zip``, extract it, and
  double-click ``InterferenceCalculator.exe``. Windows is distributed as an app
  directory to avoid the long no-feedback startup caused by one-file ``.exe``
  runtime extraction.
- **macOS**: download ``InterferenceCalculator-macOS-*.dmg``, open it, and drag
  the app to ``Applications``. On first launch you may need to allow the app in
  "Security & Privacy".

**Option B — pip install (requires Python 3.9+)**

.. code-block:: bash

   pip install interference_calculator

The ``openpyxl`` dependency required for GDMS Excel import and Excel export is
included by default.

You can also install a downloaded wheel manually:

.. code-block:: bash

   pip install interference_calculator-*.whl

**Option C — from source (developers)**

.. code-block:: bash

   git clone https://github.com/Tingfe/interference_calculator.git
   cd interference_calculator
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -e .

Running the GUI
---------------

- **Standalone app**: extract the downloaded Windows ``.zip`` and double-click
  ``InterferenceCalculator.exe``, or open the macOS ``.dmg`` and click the app
  icon.
- **pip install**: run ``interference_calculator`` from your terminal.
- **Source checkout**: run ``python -m interference_calculator.ui`` from the
  project root; ``python interference_calculator/ui.py`` is also supported.

Quick GDMS workflow
-------------------

1. Select ``GDMS`` mode.
2. If you have a GDMS Excel profile export, click **Import** so the
   software can extract elements and selectable target peaks from the file.
3. After import, select from the imported target list first. Enable **Manual
   target** only when the desired target is not present in the imported file.
4. Keep the default ``2000 ppm`` full window.
5. After import, the ``add set`` menu includes an ``imported GDMS elements``
   preset. Presets append only missing elements, so you can keep imported
   sample elements while adding Ar background, light background,
   halogen/sulfur, or matrix sources.
6. If no file was imported, use the element **Add** button to choose sample,
   matrix, plasma, and background elements, for example ``Ar Cl As O H``, or add
   the all-elements preset for a broad screen.
7. Set ion model and instrument MRP if needed. When the imported target has
   valid ``Mass`` points, enable ``Auto`` beside sweep. When it has
   valid ``FWHM``, enable ``Auto`` beside MRP.
8. Click **Calculate**.
9. Review candidate peaks, ``Δppm``, required MRP, relative risk, and whether
   each candidate is resolvable.
10. Open the spectrum view to inspect the target-centered peak display; hover a
   peak for details and click a peak to select the corresponding result row. If
   a GDMS Excel file was imported, manually enable ``Profiles (test)`` in the
   spectrum toolbar to overlay real ``Mass`` / ``Values`` peak profiles; enable
   ``Match m/z`` when you want each observed profile center aligned to its
   theoretical isotope ``m/z``. ``Match m/z`` turns on the profile overlay
   automatically and draws match guide lines with shift labels.

For imported targets, ``profile centroid`` / ``profile apex`` is a peak-shape
summary calculated from the Excel ``Mass`` / ``Values`` points. ``Δm/z``,
``Δppm``, MRP, and the spectrum center always use the theoretical target
``m/z`` as the reference, so theoretical candidates are not mixed with a raw
observed target position. Real profile traces are zero-aligned by the selected
target profile centroid/apex before plotting on the same target-centered axis.
The spectrum toolbar's ``Match m/z`` option is display-only; it aligns each
observed profile centroid/apex to the corresponding theoretical isotope
``m/z`` and annotates the alignment shift without changing the interference
calculation.

.. image:: docs/images/spectrum_en.png
   :align: center
   :alt: Target-centered spectrum screenshot

User manual
-----------

The illustrated user manual:

`docs/USER_MANUAL.md <docs/USER_MANUAL.md>`_

Maintenance and release documents:

- `Branching model / 分支模型 <docs/BRANCHING.md>`_
- `Release guide / 发布指南 <docs/RELEASE.md>`_

Core concepts
-------------

Window width
~~~~~~~~~~~~

The GUI uses full window width to match common instrument settings. For
example, ``2000 ppm`` means the calculation searches ``1000 ppm`` below and
``1000 ppm`` above the target peak. The GUI uses ``ppm`` windows; the Python API
still uses ``m/z`` half-width as ``targetrange``.
When an imported GDMS target has valid ``Mass`` points, enable ``Auto`` beside
sweep to estimate the full ppm window as
``(max Mass - min Mass) / observed m/z * 1e6``. The switch is disabled when no
valid Mass range is available.

Instrument MRP
~~~~~~~~~~~~~~

Instrument MRP does not change candidate generation. It is applied after mass
calculation to mark whether a candidate peak is resolvable from the target.
Candidates that require higher resolving power than the instrument setting are
highlighted as unresolved.
When an imported GDMS target has valid ``FWHM``, enable ``Auto`` MRP to estimate
instrument resolving power as ``observed m/z / FWHM``. The switch is disabled
when no valid ``FWHM`` is available.

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

Branch model:

- ``main``: inorganic-materials / inorganic-MS specialist edition, including
  the GDMS, ICP-MS, and SIMS workflows. This is the default release branch.
- ``maintenance/original``: modern general-scan maintenance line, preserving
  general molecular enumeration and isotope-ratio calculation with the refreshed
  isotope database, modern dependencies, and packaging, but without
  inorganic-specific presets, templates, or risk models.

Releases are automated with GitHub Actions. After updating ``__version__`` and
the bilingual ``CHANGELOG.md``, pushing a ``vX.Y.Z`` tag runs tests, builds the
source package / wheel, Windows ``.zip`` app directory, and macOS ``.dmg``,
then creates a GitHub Release from the matching bilingual changelog section.

When Apple signing secrets are not configured, the workflow publishes an
unsigned, non-notarized macOS DMG with ``macOS-unsigned`` in the filename. With
complete secrets, it automatically publishes a Developer ID signed and
Apple-notarized DMG. See `docs/MACOS_SIGNING.md <docs/MACOS_SIGNING.md>`_ for
the required secrets and workflow configuration.

Run the test suite:

.. code-block:: bash

   python -m unittest discover -s tests -v

Update the isotope database:

.. code-block:: bash

   python interference_calculator/update_periodic_table.py

License
-------

BSD 3-Clause Clear. See ``LICENSE.rst``.
