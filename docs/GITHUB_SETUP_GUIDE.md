# GitHub Project Board 设置指南

本指南帮助您为 interference_calculator 项目创建优化路线图的 GitHub Project Board，用于跟踪12个优化任务的进度。

## 目录

1. [前置条件](#前置条件)
2. [第一步：创建里程碑 (Milestones)](#第一步创建里程碑-milestones)
3. [第二步：创建Issue标签](#第二步创建issue标签)
4. [第三步：批量创建Issue](#第三步批量创建issue)
5. [第四步：创建Project Board](#第四步创建project-board)
6. [第五步：配置自动化规则](#第五步配置自动化规则)
7. [第六步：更新README](#第六步更新readme)
8. [故障排除](#故障排除)

---

## 前置条件

### 必需工具

1. **GitHub账号**: 拥有项目的写入权限
2. **GitHub CLI (gh)**: 可选，用于批量创建Issue
   ```bash
   # macOS
   brew install gh
   
   # Linux
   sudo apt install gh
   
   # Windows
   winget install GitHub.cli
   ```

3. **认证GitHub CLI**:
   ```bash
   gh auth login
   # 选择 GitHub.com
   # 选择 HTTPS
   # 按照提示完成浏览器认证
   ```

### 权限要求

- 必须是仓库的 **Owner** 或具有 **Admin** 权限
- 能够创建 Milestones、Issues 和 Projects

---

## 第一步：创建里程碑 (Milestones)

### 方法A：通过GitHub网页界面（推荐）

1. **进入里程碑页面**
   - 访问: `https://github.com/Tingfe/interference_calculator/milestones`
   - 点击 **"New milestone"** 按钮

2. **创建5个里程碑**

   | # | 标题 | 截止日期 | 描述 |
   |---|------|---------|------|
   | M1 | Phase 1: Core Performance Optimization | 2026-07-01 | 计算引擎性能提升 + 内存优化 |
   | M2 | Phase 2: Architecture Refactoring | 2026-08-05 | UI模块化 + 配置持久化 + 插件系统 |
   | M3 | Phase 3: Quality Assurance Enhancement | 2026-08-26 | 测试覆盖率提升 + 日志监控系统 |
   | M4 | Phase 4: Documentation & UX | 2026-09-23 | API文档 + 用户指南 + 国际化 |
   | M5 | Phase 5: Modernization | 2026-10-07 | 依赖管理现代化 + CI/CD优化 |

3. **详细步骤（以M1为例）**
   
   a. 点击 "New milestone"
   
   b. 填写表单：
   ```
   Title: Phase 1: Core Performance Optimization
   Due date: July 1, 2026
   Description: 
   ## 第一阶段：核心性能优化
   
   - 计算引擎性能提升（预过滤剪枝 + 并行计算）
   - 内存优化（生成器模式 + 流式处理）
   - 目标：maxsize=4场景速度提升10-100倍，内存降低50-70%
   
   详见：docs/OPTIMIZATION_ROADMAP.md
   ```
   
   c. 点击 **"Create milestone"**
   
   d. 重复以上步骤创建M2-M5

### 方法B：使用GitHub CLI（快速）

```bash
# M1: Phase 1
gh api repos/Tingfe/interference_calculator/milestones \
  --method POST \
  --field title="Phase 1: Core Performance Optimization" \
  --field due_on="2026-07-01T00:00:00Z" \
  --field description="计算引擎性能提升 + 内存优化。详见 docs/OPTIMIZATION_ROADMAP.md"

# M2: Phase 2
gh api repos/Tingfe/interference_calculator/milestones \
  --method POST \
  --field title="Phase 2: Architecture Refactoring" \
  --field due_on="2026-08-05T00:00:00Z" \
  --field description="UI模块化 + 配置持久化 + 插件系统。详见 docs/OPTIMIZATION_ROADMAP.md"

# M3: Phase 3
gh api repos/Tingfe/interference_calculator/milestones \
  --method POST \
  --field title="Phase 3: Quality Assurance Enhancement" \
  --field due_on="2026-08-26T00:00:00Z" \
  --field description="测试覆盖率提升 + 日志监控系统。详见 docs/OPTIMIZATION_ROADMAP.md"

# M4: Phase 4
gh api repos/Tingfe/interference_calculator/milestones \
  --method POST \
  --field title="Phase 4: Documentation & UX" \
  --field due_on="2026-09-23T00:00:00Z" \
  --field description="API文档 + 用户指南 + 国际化。详见 docs/OPTIMIZATION_ROADMAP.md"

# M5: Phase 5
gh api repos/Tingfe/interference_calculator/milestones \
  --method POST \
  --field title="Phase 5: Modernization" \
  --field due_on="2026-10-07T00:00:00Z" \
  --field description="依赖管理现代化 + CI/CD优化。详见 docs/OPTIMIZATION_ROADMAP.md"
```

### 验证里程碑创建成功

访问 `https://github.com/Tingfe/interference_calculator/milestones` 确认5个里程碑已显示。

---

## 第二步：创建Issue标签

### 建议的标签体系

| 标签名称 | 颜色 | 用途 |
|---------|------|------|
| `P0` | 🔴 #d73a4a | 最高优先级（性能优化） |
| `P1` | 🟡 #fbca04 | 中优先级（架构重构） |
| `P2` | 🔵 #0075ca | 低优先级（文档/现代化） |
| `enhancement` | 🟢 #a2eeef | 功能增强 |
| `performance` | 🟣 #5319e7 | 性能相关 |
| `refactoring` | 🟠 #fb8532 | 代码重构 |
| `testing` | 🔵 #006b75 | 测试相关 |
| `documentation` | 🟢 #0075ca | 文档相关 |
| `i18n` | 🟡 #fef2c0 | 国际化 |
| `devops` | ⚫ #000000 | CI/CD和构建 |

### 创建标签（网页界面）

1. 访问: `https://github.com/Tingfe/interference_calculator/labels`
2. 点击 **"New label"**
3. 依次创建上述10个标签

### 创建标签（GitHub CLI）

```bash
# P0/P1/P2 优先级标签
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="P0" -f color="d73a4a" -f description="最高优先级"
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="P1" -f color="fbca04" -f description="中优先级"
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="P2" -f color="0075ca" -f description="低优先级"

# 功能分类标签
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="enhancement" -f color="a2eeef" -f description="功能增强"
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="performance" -f color="5319e7" -f description="性能优化"
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="refactoring" -f color="fb8532" -f description="代码重构"
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="testing" -f color="006b75" -f description="测试相关"
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="documentation" -f color="0075ca" -f description="文档完善"
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="i18n" -f color="fef2c0" -f description="国际化支持"
gh api repos/Tingfe/interference_calculator/labels --method POST -f name="devops" -f color="000000" -f description="CI/CD和构建"
```

---

## 第三步：批量创建Issue

### 方法A：使用提供的Python脚本（推荐）

我们提供了 `scripts/create_issues.py` 脚本，可以一次性创建所有12个Issue。

**使用步骤**:

1. **确保已安装GitHub CLI并认证**:
   ```bash
   gh auth status
   ```

2. **运行脚本**:
   ```bash
   cd /path/to/interference_calculator
   python scripts/create_issues.py
   ```

3. **脚本会自动**:
   - 获取里程碑ID
   - 创建12个Issue
   - 关联正确的标签和里程碑
   - 输出每个Issue的URL

### 方法B：手动创建（适合少量Issue）

如果不想使用脚本，可以手动创建每个Issue：

1. 访问: `https://github.com/Tingfe/interference_calculator/issues/new`

2. **示例：创建第一个Issue**

   **标题**: `[P0] Performance: Optimize interference() calculation engine with pruning and parallelization`
   
   **标签**: 勾选 `P0`, `performance`, `enhancement`
   
   **里程碑**: 选择 `Phase 1: Core Performance Optimization`
   
   **内容**: （复制下面的模板）

3. **Issue模板清单**

以下是12个Issue的详细信息，请按需创建：

#### Phase 1 - M1 Milestone

**Issue 1**: 计算引擎优化
- **标题**: `[P0] Performance: Optimize interference() calculation engine with pruning and parallelization`
- **标签**: `P0`, `performance`, `enhancement`
- **里程碑**: `Phase 1: Core Performance Optimization`
- **详情**: 见下方完整模板

**Issue 2**: 内存优化
- **标题**: `[P0] Memory: Reduce memory footprint with generator patterns and streaming processing`
- **标签**: `P0`, `performance`, `enhancement`
- **里程碑**: `Phase 1: Core Performance Optimization`

#### Phase 2 - M2 Milestone

**Issue 3**: UI模块化
- **标题**: `[P1] Architecture: Modularize ui.py into separate components (MVVM pattern)`
- **标签**: `P1`, `refactoring`, `enhancement`
- **里程碑**: `Phase 2: Architecture Refactoring`

**Issue 4**: 配置持久化
- **标题**: `[P1] Feature: Add configuration persistence system with JSON backend`
- **标签**: `P1`, `enhancement`
- **里程碑**: `Phase 2: Architecture Refactoring`

**Issue 5**: 插件系统
- **标题**: `[P1] Architecture: Implement plugin system for extensibility (species templates, formation factors)`
- **标签**: `P1`, `refactoring`, `enhancement`
- **里程碑**: `Phase 2: Architecture Refactoring`

#### Phase 3 - M3 Milestone

**Issue 6**: 测试覆盖率
- **标题**: `[P1] Testing: Increase test coverage with screenshot comparison and performance benchmarks`
- **标签**: `P1`, `testing`, `enhancement`
- **里程碑**: `Phase 3: Quality Assurance Enhancement`

**Issue 7**: 日志监控
- **标题**: `[P1] DevOps: Add logging and monitoring system with error tracking`
- **标签**: `P1`, `devops`, `enhancement`
- **里程碑**: `Phase 3: Quality Assurance Enhancement`

#### Phase 4 - M4 Milestone

**Issue 8**: API文档
- **标题**: `[P2] Docs: Generate API documentation with Sphinx and type annotations`
- **标签**: `P2`, `documentation`, `enhancement`
- **里程碑**: `Phase 4: Documentation & UX`

**Issue 9**: 用户指南
- **标题**: `[P2] Docs: Enhance user manual with tutorials, videos, and FAQ`
- **标签**: `P2`, `documentation`, `enhancement`
- **里程碑**: `Phase 4: Documentation & UX`

**Issue 10**: 国际化
- **标题**: `[P2] i18n: Extend internationalization support (Japanese, German)`
- **标签**: `P2`, `i18n`, `enhancement`
- **里程碑**: `Phase 4: Documentation & UX`

#### Phase 5 - M5 Milestone

**Issue 11**: 依赖管理
- **标题**: `[P2] Build: Modernize dependency management with Poetry`
- **标签**: `P2`, `devops`, `enhancement`
- **里程碑**: `Phase 5: Modernization`

**Issue 12**: CI/CD优化
- **标题**: `[P2] CI/CD: Optimize continuous integration pipeline with automated quality checks`
- **标签**: `P2`, `devops`, `enhancement`
- **里程碑**: `Phase 5: Modernization`

---

## 第四步：创建Project Board

### 步骤1：创建新项目

1. **访问Projects页面**
   - URL: `https://github.com/orgs/Tingfe/projects`
   - 或者从仓库页面点击顶部导航栏的 **"Projects"** → **"New project"**

2. **点击 "New project"**

3. **选择模板**
   - 选择 **"Board"** 类型
   - 或者选择 **"Blank"** 从头开始

4. **填写项目信息**
   ```
   Project name: Optimization Roadmap 2026
   Description: Track the 5-phase optimization plan for interference_calculator (v2.6.0)
   Visibility: Public (or Private if preferred)
   ```

5. **点击 "Create project"**

### 步骤2：配置看板列

创建以下4列：

1. **📋 Backlog**
   - 描述: 待办任务池
   - 颜色: 默认

2. **🔍 In Review**
   - 描述: PR审查阶段
   - 颜色: 黄色 (#fbca04)

3. **🚧 In Progress**
   - 描述: 正在进行中
   - 颜色: 蓝色 (#0075ca)

4. **✅ Done**
   - 描述: 已完成
   - 颜色: 绿色 (#008000)

**操作方法**:
- 点击看板右上角的 **"..."** → **"Settings"**
- 在 **"Views"** 部分，确保有一个 **"Board"** 视图
- 点击 **"Add column"** 添加上述4列

### 步骤3：添加自定义字段

为了更好追踪任务，添加以下字段：

1. **Priority** (Single select)
   - 选项: P0, P1, P2
   - 颜色: P0红色, P1黄色, P2蓝色

2. **Phase** (Single select)
   - 选项: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5

3. **Estimated Effort** (Text)
   - 格式: "X weeks" 或 "X days"

4. **Progress** (Number)
   - 范围: 0-100
   - 用于显示完成百分比

**操作方法**:
- 点击右上角 **"..."** → **"Settings"** → **"Fields"**
- 点击 **"Add field"** 逐个添加

### 步骤4：将Issue添加到看板

**方法A：手动添加**

1. 打开任意一个Issue
2. 在右侧边栏找到 **"Projects"** 部分
3. 点击 **"Add to project"**
4. 选择 "Optimization Roadmap 2026"
5. 初始状态自动设为 "Backlog"

**方法B：批量添加（推荐）**

使用GitHub CLI批量添加所有12个Issue到看板：

```bash
# 首先获取Project ID
PROJECT_ID=$(gh api graphql -f query='
  query {
    organization(login: "Tingfe") {
      projectV2(number: PROJECT_NUMBER) {
        id
      }
    }
  }
' --jq '.data.organization.projectV2.id')

# 获取所有相关Issue的ID
ISSUE_IDS=$(gh issue list --label "P0,P1,P2" --state open --json number --jq '.[].number')

# 逐个添加到项目
for ISSUE_NUM in $ISSUE_IDS; do
  gh api graphql -f query='
    mutation($project: ID!, $issue: ID!) {
      addProjectV2ItemById(input: {projectId: $project, contentId: $issue}) {
        item {
          id
        }
      }
    }
  ' -f project=$PROJECT_ID -f issue=$(gh api repos/Tingfe/interference_calculator/issues/$ISSUE_NUM --jq '.node_id')
done
```

**注意**: 需要将 `PROJECT_NUMBER` 替换为实际的项目编号（可在项目URL中看到）。

---

## 第五步：配置自动化规则

### 自动化工作流设置

GitHub Projects支持自动化规则，可以在特定事件发生时自动移动卡片。

**配置步骤**:

1. 打开项目页面
2. 点击右上角 **"..."** → **"Settings"** → **"Workflows"**
3. 点击 **"Add workflow"**

#### 规则1: Issue添加到项目时

```yaml
Name: Auto-move to Backlog
Trigger: When an item is added to this project
Action: Set status to "📋 Backlog"
```

#### 规则2: PR打开时

```yaml
Name: Move to Review on PR
Trigger: When a pull request is opened
Action: Set status to "🔍 In Review"
Condition: Item is linked to a PR
```

#### 规则3: PR合并时

```yaml
Name: Move to Done on Merge
Trigger: When a pull request is merged
Action: Set status to "✅ Done"
Condition: Item is linked to a PR
```

#### 规则4: Issue关闭时

```yaml
Name: Auto-complete on Close
Trigger: When an item is closed
Action: Set status to "✅ Done"
```

### 视图配置

创建多个视图以便不同场景使用：

#### 视图1: Table View（表格视图）

- **用途**: 查看所有任务的详细信息
- **显示字段**:
  - Title
  - Assignee
  - Status
  - Milestone
  - Priority (自定义字段)
  - Phase (自定义字段)
  - Labels

**配置方法**:
1. 点击左上角视图切换器
2. 选择 **"Table"**
3. 点击 **"..."** → **"Edit view"**
4. 添加上述字段

#### 视图2: Roadmap View（路线图视图）

- **用途**: 按时间线查看里程碑进度
- **分组依据**: Milestone
- **时间轴**: 按Due date

**配置方法**:
1. 点击 **"New view"**
2. 选择 **"Roadmap"**
3. 设置 **"Group by"** = Milestone
4. 启用 **"Timeline"** 并按Due date排序

#### 视图3: Board View（看板视图）

- **用途**: 日常任务管理
- **分组依据**: Status
- **排序**: 按Priority降序

**配置方法**:
1. 点击 **"New view"**
2. 选择 **"Board"**
3. 设置 **"Group by"** = Status
4. 添加排序规则：Priority (DESC)

---

## 第六步：更新README

在项目根目录的 `README.rst` 中添加Project Board链接和开发状态徽章。

### 添加内容位置

在 "Project Metadata" 章节后添加新章节：

```rst
Development Status
------------------

.. image:: https://img.shields.io/badge/Project_Board-Optimization_Roadmap-blue
   :target: https://github.com/Tingfe/interference_calculator/projects/PROJECT_NUMBER
   :alt: Project Board

.. image:: https://img.shields.io/github/issues-pr/Tingfe/interference_calculator
   :target: https://github.com/Tingfe/interference_calculator/pulls
   :alt: Pull Requests

.. image:: https://img.shields.io/github/contributors/Tingfe/interference_calculator
   :target: https://github.com/Tingfe/interference_calculator/graphs/contributors
   :alt: Contributors

当前开发重点：**Optimization Roadmap 2026** (v2.6.0)

查看项目进展: `Project Board <https://github.com/Tingfe/interference_calculator/projects/PROJECT_NUMBER>`_

贡献指南
--------

欢迎贡献！请参考：

- `优化路线图 <docs/OPTIMIZATION_ROADMAP.md>`_: 了解未来开发计划
- `Project Board <https://github.com/Tingfe/interference_calculator/projects/PROJECT_NUMBER>`_: 查看正在进行的任务
- `分支模型 <docs/BRANCHING.md>`_: 了解如何提交代码
- `发布指南 <docs/RELEASE.md>`_: 了解版本发布流程

**如何开始贡献**:

1. 浏览 `Project Board <https://github.com/Tingfe/interference_calculator/projects/PROJECT_NUMBER>`_ 寻找 ``good first issue`` 标签的任务
2. Fork 仓库并创建特性分支
3. 提交PR并关联相关Issue
4. 等待代码审查和合并
```

### 替换说明

- 将 `PROJECT_NUMBER` 替换为实际的项目编号（例如：`1`, `2`, `3`等）
- 项目编号可在项目URL中找到：`https://github.com/orgs/Tingfe/projects/PROJECT_NUMBER`

---

## 故障排除

### 问题1: GitHub CLI认证失败

**症状**: `gh auth status` 显示未认证

**解决**:
```bash
gh auth logout
gh auth login
# 重新按照提示认证
```

### 问题2: 权限不足无法创建Milestone

**症状**: API返回403错误

**解决**:
- 确认您是仓库的Owner或具有Admin权限
- 联系仓库管理员授予权限

### 问题3: Project Board未显示

**症状**: 创建项目后找不到

**解决**:
- 检查是否在正确的Organization下创建
- 访问 `https://github.com/orgs/Tingfe/projects` 查看所有项目
- 确认项目可见性设置（Public/Private）

### 问题4: Issue未正确关联里程碑

**症状**: Issue创建后里程碑为空

**解决**:
- 确认里程碑名称完全匹配（包括大小写和空格）
- 手动编辑Issue，在右侧边栏选择正确的里程碑

### 问题5: 自动化规则不生效

**症状**: PR合并后卡片未移动到Done

**解决**:
- 检查Workflow是否正确配置
- 确认PR确实关联了Issue（在PR描述中使用 `Fixes #123`）
- 刷新项目页面查看更新

---

## 附录：完整Issue模板

以下是12个Issue的完整模板，可直接复制使用：

### Issue 1: 计算引擎优化

```markdown
## Background
The current `interference()` function in main.py uses brute-force combination enumeration, which causes exponential explosion when maxsize ≥ 4. For 10 elements with ~50 isotopes, maxsize=5 generates ~300 million combinations.

## Objective
Implement performance optimizations to achieve 10-100x speedup while maintaining API compatibility.

## Implementation Plan

### 1. Pre-filtering Pruning
- Add mass range validation before generating combinations
- Skip combinations that cannot fall within target m/z ± tolerance
- Implement early termination for low-probability branches

### 2. Parallel Computing
- Use multiprocessing.Pool for independent combination batches
- Add configurable worker count (default: CPU cores)
- Ensure thread-safe result aggregation

### 3. Optional GPU Acceleration
- Create CuPy-based backend interface
- Fallback to CPU if GPU unavailable
- Benchmark comparison report

## Acceptance Criteria
- [ ] Speed improvement: 10-100x faster for maxsize=4-5 scenarios
- [ ] Memory usage: No significant increase (< 20%)
- [ ] API compatibility: All existing tests pass without modification
- [ ] Backward compatibility: Default behavior unchanged
- [ ] Documentation: Update docstring with performance notes

## Estimated Effort
- Development: 2 weeks
- Testing: 3 days
- Documentation: 2 days

## Related Files
- interference_calculator/main.py (interference function)
- tests/test_core.py (add performance benchmarks)

## References
- Optimization Roadmap: docs/OPTIMIZATION_ROADMAP.md
- Deep Analysis Report: Research output from agent 8157f5d8
```

### Issue 2: 内存优化

```markdown
## Background
Current implementation stores all isotope combinations in memory before filtering, causing GB-level memory usage for maxsize=5 with 50 elements.

## Objective
Reduce peak memory usage by 50-70% using generator patterns and streaming processing.

## Implementation Plan

### 1. Generator Pattern
- Replace list comprehensions with generators in combination generation
- Implement lazy evaluation for mass calculations
- Stream results instead of building complete DataFrame at once

### 2. Streaming DataFrame Construction
- Process results in chunks (e.g., 10,000 rows per chunk)
- Use pd.concat() only at the end
- Avoid intermediate list storage

### 3. Data Type Optimization
- Use float32 instead of float64 where precision allows
- Use int8 for charge states
- Optimize categorical columns

## Acceptance Criteria
- [ ] Peak memory reduced by ≥50% (verified with memory_profiler)
- [ ] Calculation results identical to original (numerical error <1e-6)
- [ ] No MemoryError for maxsize=5, 50 elements scenario
- [ ] Performance impact <10% slowdown (acceptable trade-off)

## Estimated Effort
- Development: 1 week
- Testing: 2 days

## Related Files
- interference_calculator/main.py
- interference_calculator/inorganic.py

## References
- docs/OPTIMIZATION_ROADMAP.md Section 1.2
```

*(由于篇幅限制，此处仅展示前2个Issue的完整模板。其余10个Issue的模板已包含在 `scripts/create_issues.py` 脚本中)*

---

## 下一步行动

完成上述设置后：

1. ✅ 验证所有5个里程碑已创建
2. ✅ 验证所有12个Issue已创建并关联正确标签和里程碑
3. ✅ 验证Project Board已创建并包含所有Issue
4. ✅ 验证自动化规则正常工作
5. ✅ 更新README并推送更改
6. ✅ 通知团队成员开始Phase 1工作

**祝优化计划顺利实施！** 🚀

---

**文档版本**: 1.0  
**最后更新**: 2026-06-08  
**维护者**: Tingfe  
**反馈**: 如有问题请在GitHub Issue中提出
