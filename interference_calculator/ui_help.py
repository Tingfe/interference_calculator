# -*- coding: utf-8 -*-
""" Help and tooltip text for ui.py """
from html import escape
import sys

atoms_input_tooltip = '''
<html><head/><body>
<p><b>Elements to include in the interference search.</b></p>
<p>Use sample, matrix, plasma, and common background elements separated by spaces.
All stable isotopes for each element are included automatically.</p>
</body></html>
'''

element_set_input_tooltip = '''
<html><head/><body>
<p><b>Add common element sets.</b></p>
<p>Adds only the missing elements from common plasma, background, matrix, or
imported GDMS element sets. Existing imported/sample elements are kept. The
all-elements set is tuned for inorganic MS screening and excludes short-lived
radioactive elements.</p>
</body></html>
'''

mode_input_tooltip = '''
<html><head/><body>
<p><b>Instrument preset.</b></p>
<p>GDMS, ICP-MS, and SIMS set practical defaults for ion charge, risk model,
mass window, and resolving power. General scan keeps the older enumeration path.</p>
</body></html>
'''

charge_preset_input_tooltip = '''
<html><head/><body>
<p><b>Ion charge preset.</b></p>
<p>Selects charge states and sign for generated candidate ions.</p>
</body></html>
'''

mz_input_tooltip = '''
<html><head/><body>
<p><b>Target mass-to-charge ratio.</b></p>
<p>Give a mass-to-charge (m/z) value to filter the results. Only molecules
inside the selected window width and up to max size atoms will be shown.</p>
<p>If empty, all possible combinations of all isotopes of the selected
atoms will be displayed. <i>This may be a very long list!</i></p>
</body></html>
'''

mzrange_input_tooltip = '''
<html><head/><body>
<p><b>Target mass-to-charge window width.</b></p>
<p>Give the full instrument window width. For example, 2000 ppm is calculated
as ±1000 ppm around the target peak. When an imported GDMS target has valid
Mass points, the Auto switch estimates the full ppm window from the real Mass
range.</p>
</body></html>
'''

window_unit_input_tooltip = '''
<html><head/><body>
<p><b>Window unit.</b></p>
<p>m/z uses an absolute mass-to-charge full window. ppm uses the full ppm
window width. Switching units also converts the current window value when a
valid target is available.</p>
</body></html>
'''

maxsize_input_tooltip = '''
<html><head/><body>
<p><b>Maximum molecule size.</b></p>
<p>Give the maximum number of atoms in a molecule. The number of
possible combinations of <i>n</i> atoms in a molecule grows exponentially
with <i>n</i>, so keep this number low to avoid obscenely large lists.</p>
</body></html>
'''

instrument_mrp_input_tooltip = '''
<html><head/><body>
<p><b>Instrument mass-resolving power.</b></p>
<p>Used to mark whether each candidate peak is resolvable from the target.
It does not change which candidate peaks are calculated. Set to off to
calculate required MRP only. When an imported GDMS target has valid FWHM,
the Auto switch estimates MRP as observed m/z divided by FWHM.</p>
</body></html>
'''

interference_button_tooltip = '''
<html><head/><body>
<p>(enter)</p>
</body></html>
'''

if sys.platform == 'darwin':
    _modifier = '&#8984;'
else:
    _modifier = 'ctrl'

standard_ratio_button_tooltip = '''
<html><head/><body>
<p>({}-enter)</p>
</body></html>
'''.format(_modifier)

help_button_tooltip = '''
<html><head/><body>
<p>Help ({}-H)</p>
</body></html>
'''.format(_modifier)

spectrum_button_tooltip = '''
<html><head/><body>
<p>Show the interference spectrum ({}-D). Unresolved peaks are highlighted
using the instrument MRP setting. With a target peak, the x-axis is centered
on the target. Hover a peak for details, click a peak to select its table row,
optionally enable imported GDMS Mass/Values profiles as an experimental overlay,
optionally match observed profile centers to theoretical isotope m/z with guide
lines and shift labels, and export the current spectrum from the spectrum
toolbar.</p>
</body></html>
'''.format(_modifier)

gdms_import_tooltip = '''
<html><head/><body>
<p><b>Import GDMS Excel profile data.</b></p>
<p>Reads isotope profile exports, extracts target peaks such as Fe{56}, and
fills the element list from the exported plasma/sample profiles. Profile m/z
is calculated from the imported mass/intensity points as a centroid, or apex
when a centroid is not available. The imported Mass/Values points are retained
and can be overlaid as real peak shapes in the spectrum view by enabling the
experimental profile toggle. In the spectrum toolbar, Match m/z can additionally
align each observed profile centroid/apex to its theoretical isotope m/z; this
turns on the profile overlay automatically, draws match guides, and does not
change the calculation.</p>
</body></html>
'''

manual_target_tooltip = '''
<html><head/><body>
<p><b>Manual target override.</b></p>
<p>After importing GDMS profiles, keep this off to choose targets from the
instrument-exported peak list. Enable it only when you need to calculate a
target that is not present in the imported file.</p>
</body></html>
'''

mz_warning = '''
<html><head/><body>
<p>If you do not specify a target, <b>ALL</b> combinations up to
<i>max size</i> will be calculated. This can take a long time.</p>
<p>Are you sure?</p>
<p></p>
</body></html>
'''

help_text = '''
<html><head/>
<body>
<div style="margin-left: 128px" align="center">
        <h1>Inorganic MS Interference Calculator</h1>
        <p><strong>version __VERSION__</strong></p>
        <p><strong>&copy; 2017, Zan Peeters</strong></p>
        <p><strong>Latest contributor: Tingfe</strong></p>
        <p><a href="https://github.com/Tingfe/interference_calculator">https://github.com/Tingfe/interference_calculator</a>
</div>

<br/>
<h2>Software overview</h2>
<p>This program calculates possible mass interferences around a target mass-to-charge
peak from the elements present in a sample, matrix, plasma, or background gas.</p>

<p>The original general scan enumerates isotope combinations up to the selected
maximum molecule size. The new inorganic mass-spectrometry workflow adds dedicated
instrument presets for GDMS, ICP-MS, and SIMS, with practical defaults for ion
charge, mass window, risk model, and resolving power.</p>

<p>In inorganic mode, candidates are generated from common inorganic MS interference
templates rather than only by unrestricted enumeration. The screening prioritizes
atomic ions, doubly charged atomic ions, oxides, hydrides, hydroxides, nitrides,
carbides, sulfides, halides, plasma adducts, background molecules, and small matrix
clusters. This makes the result set more focused for GDMS peak-interference review.</p>

<p>The element set menu appends missing elements from common plasma, background,
matrix, imported GDMS, and all-elements inorganic MS presets without clearing the
current selection. The all-elements preset focuses on commonly measurable
inorganic MS elements, keeps Th/U, and excludes short-lived or unusual
radioactive elements.</p>

<p>GDMS Excel profile exports can be imported directly. The software reads
exported isotope profiles such as Fe{56}, fills the element list from the file,
and lets users select a target peak from the imported profile list before
running the interference calculation. The displayed profile m/z is calculated
from the imported mass/intensity data as a peak centroid, or from the apex when
the centroid cannot be calculated. The spectrum view can also overlay the real
Mass/Values peak profiles from the imported file. The selected target profile
centroid/apex is aligned to the theoretical target center before plotting, so
real profile shapes and theoretical interference candidates share the same
target-centered axis. This overlay is experimental and off by default. The
spectrum toolbar also provides a display-only Match m/z switch that aligns each
observed profile center to the corresponding theoretical isotope m/z for visual
comparison. It turns on profile overlays automatically and draws guide lines
with shift labels.</p>

<p>The GDMS target window defaults to 2000 ppm and is entered as a full window
width. For example, a 2000 ppm window means the software searches 1000 ppm lower
and 1000 ppm higher than the calibrated target peak. When imported Mass points
are available, the optional Auto switch estimates this full ppm window from the
real profile range.</p>

<p>Instrument MRP is used after candidate generation to estimate whether each
candidate can be resolved from the target. It does not remove candidates from the
calculation; unresolved peaks are highlighted in the table and spectrum.</p>

<p>The spectrum display is target-centered when a target peak is present. In ppm
mode, the x-axis is shown as &Delta;ppm so the calibrated target peak is at zero
and nearby interference peaks can be compared directly.</p>

<p>Relative risk is a qualitative screening score based on isotope probability and
method-specific formation factors. It is intended for prioritizing candidate
interferences, not for quantitative abundance correction.</p>

<h2>Data sources</h2>
<p>The atomic data used in this program is taken from the International Union for
Physical and Applied Chemistry (IUPAC), Commission on Isotopic Abundances and Atomic
Weights (CIAAW).</p>

<ul>
<li>Atomic masses
    <p><a href=http://ciaaw.org/atomic-masses.htm>http://ciaaw.org/atomic-masses.htm</a></p>
    <p>AME2020 atomic masses, <i>Chinese Physics C</i>, <b>2021</b>, 45, 030002 and 030003.</p>

<li>Isotopic abundances
    <p><a href=https://ciaaw.org/isotopic-abundances.htm>https://ciaaw.org/isotopic-abundances.htm</a></p>
     <p>CIAAW Isotopic Compositions of the Elements 2024. Interval bounds are retained in the packaged isotope database.</p>

<li>Electron mass
    <p><a href=http://physics.nist.gov/cgi-bin/cuu/Value?me>http://physics.nist.gov/cgi-bin/cuu/Value?me</a></p>
    <p>CODATA recommended values of the fundamental physical constants: 2022.</p>
</ul>
<br/>
</body></html>
'''

help_text_zh = '''
<html><head/>
<body>
<div style="margin-left: 128px" align="center">
        <h1>无机质谱峰干扰计算器</h1>
        <p><strong>版本 __VERSION__</strong></p>
        <p><strong>&copy; 2017, Zan Peeters</strong></p>
        <p><strong>最新贡献者：Tingfe</strong></p>
        <p><a href="https://github.com/Tingfe/interference_calculator">https://github.com/Tingfe/interference_calculator</a>
</div>

<br/>
<h2>软件介绍</h2>
<p>本软件用于根据样品、基体、等离子体或背景气体中的元素，计算目标质荷比峰附近
可能出现的质谱峰干扰。</p>

<p>原有的通用扫描模式会在设定的最大原子数内枚举同位素组合。新增的无机质谱
专项流程内置 GDMS、ICP-MS 和 SIMS 预设，并为离子电荷、质量窗口、风险模型和
分辨能力提供更贴近仪器使用习惯的默认值。</p>

<p>在无机模式下，候选干扰峰来自常见无机质谱干扰模板，而不是单纯无限制枚举。
筛查对象包括原子离子、双电荷原子离子、氧化物、氢化物、氢氧化物、氮化物、
碳化物、硫化物、卤化物、等离子体加合物、背景分子以及小型基体团簇。这样更
适合 GDMS 峰干扰排查。</p>

<p>元素组合菜单会在保留当前选择的基础上，追加常见等离子体、背景、基体、导入
GDMS 元素以及无机质谱全元素预设中尚未选择的元素。全元素预设面向常见无机质谱
可测元素，保留 Th/U，并排除短寿命或非常规放射性元素。</p>

<p>软件可以直接导入 GDMS Excel 谱图导出文件，读取 Fe{56} 这类同位素谱图，
用文件中的谱图元素填充元素列表，并在计算前优先从导入谱图列表中选择目标峰。
界面显示的谱图 m/z 来自导入质量 / 强度点的质心计算；无法计算质心时使用峰顶位置。
谱图窗口还可以通过默认关闭的实验开关叠加显示导入文件中的真实 Mass / Values 峰形；
绘图前会将所选目标峰
的谱图质心 / 峰顶对齐到理论目标峰中心，因此真实峰形和理论干扰候选峰共用同一个
目标居中横轴。谱图工具栏还提供仅用于显示的匹配 m/z 开关，可将每条实测峰中心
对齐到对应同位素的理论 m/z，并显示参考线和偏移量标签，便于目视比较。</p>

<p>GDMS 的目标窗口默认使用 2000 ppm，并按完整窗口宽度输入。例如 2000 ppm 表示
软件会在校准后的目标峰两侧各搜索 1000 ppm。有导入 Mass 点时，可选的自动开关会
根据真实谱图范围估算完整 ppm 窗口。</p>

<p>Instrument MRP 在候选峰生成后用于判断候选峰是否可与目标峰分辨。它不会改变
候选峰的生成范围；未能分辨的峰会在表格和谱图中高亮显示。</p>

<p>存在目标峰时，谱图会以目标峰为中心显示。ppm 模式下，横轴显示为 &Delta;ppm，
因此校准后的目标峰位于零点，附近干扰峰可以直接对比。</p>

<p>Relative risk 是基于同位素概率和方法相关生成因子的定性筛查分数，适合用于
干扰候选峰排序，不应作为定量校正因子。</p>

<h2>数据来源</h2>
<p>本软件使用的原子质量与同位素丰度数据来自 IUPAC 下属 CIAAW，电子质量来自
CODATA 推荐值。</p>

<ul>
<li>原子质量
    <p><a href=http://ciaaw.org/atomic-masses.htm>http://ciaaw.org/atomic-masses.htm</a></p>
    <p>AME2020 atomic masses, <i>Chinese Physics C</i>, <b>2021</b>, 45, 030002 and 030003.</p>

<li>同位素丰度
    <p><a href=https://ciaaw.org/isotopic-abundances.htm>https://ciaaw.org/isotopic-abundances.htm</a></p>
     <p>CIAAW Isotopic Compositions of the Elements 2024。本软件保留了数据库中的丰度区间边界。</p>

<li>电子质量
    <p><a href=http://physics.nist.gov/cgi-bin/cuu/Value?me>http://physics.nist.gov/cgi-bin/cuu/Value?me</a></p>
    <p>CODATA recommended values of the fundamental physical constants: 2022.</p>
</ul>
<br/>
</body></html>
'''


_TOOLTIPS = {
    'en': {
        'atoms': atoms_input_tooltip,
        'element_set': element_set_input_tooltip,
        'mode': mode_input_tooltip,
        'charge_preset': charge_preset_input_tooltip,
        'mz': mz_input_tooltip,
        'mzrange': mzrange_input_tooltip,
        'window_unit': window_unit_input_tooltip,
        'maxsize': maxsize_input_tooltip,
        'instrument_mrp': instrument_mrp_input_tooltip,
        'interference_button': interference_button_tooltip,
        'standard_ratio_button': standard_ratio_button_tooltip,
        'help_button': help_button_tooltip,
        'spectrum_button': spectrum_button_tooltip,
        'gdms_import': gdms_import_tooltip,
        'manual_target': manual_target_tooltip,
    },
    'zh': {
        'atoms': '''
<html><head/><body>
<p><b>参与干扰搜索的元素。</b></p>
<p>输入样品、基体、等离子体和常见背景元素，元素之间用空格分隔。
软件会自动包含每个元素的稳定同位素。</p>
</body></html>
''',
        'element_set': '''
<html><head/><body>
<p><b>添加常用元素组合。</b></p>
<p>只追加常见等离子体、背景、基体或导入 GDMS 元素集合中尚未选择的元素，
保留当前已经导入或手动选择的样品元素。全元素组合面向无机质谱筛查，已排除
短寿命放射性元素。</p>
</body></html>
''',
        'mode': '''
<html><head/><body>
<p><b>仪器预设。</b></p>
<p>GDMS、ICP-MS 和 SIMS 会设置离子电荷、风险模型、质量窗口和分辨能力的实用默认值。
通用扫描保留原有枚举计算路径。</p>
</body></html>
''',
        'charge_preset': '''
<html><head/><body>
<p><b>离子电荷预设。</b></p>
<p>选择生成候选离子时使用的电荷态和电荷符号。</p>
</body></html>
''',
        'mz': '''
<html><head/><body>
<p><b>目标质荷比。</b></p>
<p>输入目标 m/z 后，结果只显示位于所选窗口内且不超过最大原子数的候选峰。</p>
<p>如果留空，将计算所选元素和同位素在最大原子数内的全部组合，结果可能很长。</p>
</body></html>
''',
        'mzrange': '''
<html><head/><body>
<p><b>目标质荷比窗口宽度。</b></p>
<p>输入完整的仪器窗口宽度。例如 2000 ppm 会按目标峰两侧各 1000 ppm 计算。导入
GDMS 目标峰有有效 Mass 点时，自动开关会根据真实 Mass 范围估算完整 ppm 窗口。</p>
</body></html>
''',
        'window_unit': '''
<html><head/><body>
<p><b>窗口单位。</b></p>
<p>m/z 表示绝对质荷比完整窗口；ppm 表示完整 ppm 窗口。
有有效目标峰时，切换单位会同步换算当前窗口数值。</p>
</body></html>
''',
        'maxsize': '''
<html><head/><body>
<p><b>最大分子大小。</b></p>
<p>设置候选分子中允许的最大原子数。原子数增加会导致组合数快速增长，因此建议保持较小值。</p>
</body></html>
''',
        'instrument_mrp': '''
<html><head/><body>
<p><b>仪器质量分辨能力。</b></p>
<p>用于标记候选峰是否能与目标峰分辨。它不改变候选峰生成范围。
设为关闭时，仅计算所需 MRP。导入 GDMS 目标峰有有效 FWHM 时，自动开关会按
observed m/z / FWHM 估算 MRP。</p>
</body></html>
''',
        'interference_button': '''
<html><head/><body>
<p>(enter)</p>
</body></html>
''',
        'standard_ratio_button': '''
<html><head/><body>
<p>({}-enter)</p>
</body></html>
'''.format(_modifier),
        'help_button': '''
<html><head/><body>
<p>帮助 ({}-H)</p>
</body></html>
'''.format(_modifier),
        'spectrum_button': '''
<html><head/><body>
<p>显示干扰谱图 ({}-D)。未分辨峰会根据仪器 MRP 高亮；存在目标峰时，横轴以目标峰为中心。
悬停峰可查看详情，点击峰可定位表格行；如已导入 GDMS 谱图，可手动开启实验性的真实
Mass / Values 峰形叠加，也可选择将实测峰中心匹配到理论同位素 m/z，并显示对齐
参考线和偏移量标签；也可在谱图工具栏导出当前谱图。</p>
</body></html>
'''.format(_modifier),
        'gdms_import': '''
<html><head/><body>
<p><b>导入 GDMS Excel 谱图数据。</b></p>
<p>读取导出的同位素谱图，自动提取 Fe{56} 这类目标峰，并用文件中的等离子体 /
样品谱图填充元素列表。谱图 m/z 由导入的质量 / 强度点计算质心；无法计算质心时
使用峰顶位置。导入的 Mass / Values 点会保留，并可通过谱图窗口的实验开关叠加为
真实峰形。谱图工具栏中的匹配 m/z 开关还可以将每条实测峰的质心 / 峰顶对齐到对应
同位素的理论 m/z；该功能会自动打开实测峰叠加并显示对齐标记，只影响显示，不改变
计算。</p>
</body></html>
''',
        'manual_target': '''
<html><head/><body>
<p><b>手动覆盖目标峰。</b></p>
<p>导入 GDMS 谱图后，默认从仪器导出的目标峰列表中选择。只有需要计算导入文件中
不存在的目标峰时，才启用手动目标。</p>
</body></html>
''',
    },
}


_MZ_WARNINGS = {
    'en': mz_warning,
    'zh': '''
<html><head/><body>
<p>如果不指定目标峰，软件会计算 <b>所有</b> 不超过最大原子数的组合。
这可能需要较长时间。</p>
<p>确定继续吗？</p>
<p></p>
</body></html>
''',
}


def tooltip_text(language, key):
    """Return localized tooltip HTML."""
    return _TOOLTIPS.get(language, _TOOLTIPS['en']).get(key, _TOOLTIPS['en'][key])


def help_text_for(language):
    """Return localized help HTML."""
    return help_text_zh if language == 'zh' else help_text


def render_help_text(language, version):
    """Return localized help HTML with the application version inserted."""
    return help_text_for(language).replace('__VERSION__', escape(str(version)))


def mz_warning_for(language):
    """Return localized no-target warning HTML."""
    return _MZ_WARNINGS.get(language, _MZ_WARNINGS['en'])
