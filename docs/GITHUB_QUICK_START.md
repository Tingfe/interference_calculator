# GitHub Project Board 快速设置指南

> **注意**: 本文档是 `docs/GITHUB_SETUP_GUIDE.md` 的精简版，提供快速操作步骤。详细信息请参考完整指南。

## 快速开始（5分钟）

### 1️⃣ 安装GitHub CLI（如果未安装）

```bash
# macOS
brew install gh

# Linux
sudo apt install gh

# Windows
winget install GitHub.cli

# 认证
gh auth login
```

### 2️⃣ 创建里程碑

**方法A: 网页界面**
- 访问: https://github.com/Tingfe/interference_calculator/milestones
- 点击 "New milestone"
- 创建5个里程碑（见下表）

| 标题 | 截止日期 |
|------|---------|
| Phase 1: Core Performance Optimization | 2026-07-01 |
| Phase 2: Architecture Refactoring | 2026-08-05 |
| Phase 3: Quality Assurance Enhancement | 2026-08-26 |
| Phase 4: Documentation & UX | 2026-09-23 |
| Phase 5: Modernization | 2026-10-07 |

**方法B: GitHub CLI（一键）**
```bash
cd /path/to/interference_calculator
python scripts/create_milestones.py  # 脚本待创建
```

### 3️⃣ 创建Issue标签

访问: https://github.com/Tingfe/interference_calculator/labels

创建以下标签：
- `P0` (红色 #d73a4a)
- `P1` (黄色 #fbca04)
- `P2` (蓝色 #0075ca)
- `enhancement` (浅蓝 #a2eeef)
- `performance` (紫色 #5319e7)
- `refactoring` (橙色 #fb8532)
- `testing` (青色 #006b75)
- `documentation` (蓝色 #0075ca)
- `i18n` (米色 #fef2c0)
- `devops` (黑色 #000000)

### 4️⃣ 批量创建Issue

```bash
cd /path/to/interference_calculator
python scripts/create_issues.py
```

脚本会自动：
- ✅ 创建12个优化任务Issue
- ✅ 关联正确的标签
- ✅ 关联对应的里程碑
- ✅ 输出所有Issue的URL

### 5️⃣ 创建Project Board

1. 访问: https://github.com/orgs/Tingfe/projects
2. 点击 **"New project"**
3. 选择 **"Board"** 模板
4. 填写：
   - Name: `Optimization Roadmap 2026`
   - Description: `Track the 5-phase optimization plan for interference_calculator (v2.6.0)`
5. 点击 **"Create project"**

### 6️⃣ 配置看板列

添加4列：
- 📋 **Backlog** (待办)
- 🔍 **In Review** (审查中)
- 🚧 **In Progress** (进行中)
- ✅ **Done** (已完成)

### 7️⃣ 添加Issue到看板

**手动方式**:
1. 打开任意Issue
2. 右侧边栏找到 "Projects"
3. 点击 "Add to project"
4. 选择 "Optimization Roadmap 2026"

**批量方式** (需要知道项目编号):
```bash
# 获取项目ID（替换PROJECT_NUMBER为实际编号）
PROJECT_ID=$(gh api graphql -f query='
  query {
    organization(login: "Tingfe") {
      projectV2(number: PROJECT_NUMBER) {
        id
      }
    }
  }
' --jq '.data.organization.projectV2.id')

# 批量添加所有P0/P1/P2标签的Issue
gh issue list --label "P0,P1,P2" --state open --json number --jq '.[].number' | \
while read ISSUE_NUM; do
  ISSUE_NODE_ID=$(gh api repos/Tingfe/interference_calculator/issues/$ISSUE_NUM --jq '.node_id')
  gh api graphql -f query='
    mutation($project: ID!, $issue: ID!) {
      addProjectV2ItemById(input: {projectId: $project, contentId: $issue}) {
        item { id }
      }
    }
  ' -f project=$PROJECT_ID -f issue=$ISSUE_NODE_ID
done
```

### 8️⃣ 配置自动化规则

在项目页面点击右上角 **"..."** → **"Settings"** → **"Workflows"**

添加以下规则：

| 触发条件 | 动作 |
|---------|------|
| Item added to project | Move to 📋 Backlog |
| Pull request opened | Move to 🔍 In Review |
| Pull request merged | Move to ✅ Done |
| Item closed | Move to ✅ Done |

### 9️⃣ 更新README

已自动更新！查看更改：
```bash
git diff README.rst
```

提交更改：
```bash
git add README.rst docs/GITHUB_SETUP_GUIDE.md scripts/create_issues.py
git commit -m "docs: Add GitHub Project Board setup guide and issue creation script"
git push
```

---

## 验证清单

完成上述步骤后，检查以下内容：

- [ ] 5个里程碑已创建且截止日期正确
- [ ] 10个Issue标签已创建
- [ ] 12个Issue已创建并关联正确的标签和里程碑
- [ ] Project Board已创建名为 "Optimization Roadmap 2026"
- [ ] 看板包含4列：Backlog, In Review, In Progress, Done
- [ ] 所有12个Issue已添加到看板
- [ ] 自动化规则已配置
- [ ] README已更新并包含Project Board链接
- [ ] 更改已推送到GitHub

---

## 常见问题

### Q: GitHub CLI认证失败怎么办？
```bash
gh auth logout
gh auth login
# 重新按照提示认证
```

### Q: 如何查看项目编号？
访问项目页面，URL中的数字即为项目编号：
```
https://github.com/orgs/Tingfe/projects/1
                                        ↑ 这里是编号
```

### Q: Issue没有正确关联里程碑？
手动编辑Issue，在右侧边栏选择正确的里程碑。

### Q: 自动化规则不生效？
- 确认PR确实关联了Issue（在PR描述中使用 `Fixes #123`）
- 刷新项目页面查看更新

---

## 下一步

✅ 设置完成后，团队可以开始Phase 1工作！

1. 分配Issue给团队成员
2. 将正在处理的Issue移动到 "In Progress"
3. 提交PR时关联对应Issue
4. PR合并后Issue自动移动到 "Done"

**祝优化计划顺利！** 🚀

---

**详细文档**: 请参阅 `docs/GITHUB_SETUP_GUIDE.md`  
**脚本位置**: `scripts/create_issues.py`  
**路线图**: `docs/OPTIMIZATION_ROADMAP.md`
