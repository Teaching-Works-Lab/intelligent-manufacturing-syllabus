# 智能制造工程课程大纲 Skill

一个面向日常教学工作的可查询 Skill，内置智能制造工程 2025 版培养方案结构化数据，可用于检索课程基础字段、课程—指标点支撑关系和课程—培养目标派生追踪。

它属于 [Teaching Works Lab 课程教学 Skill 体系](https://github.com/Teaching-Works-Lab)，由 `training-program-skill-factory` 生成，可作为 `course-teaching-workflows` 编制课程基座和课程大纲时的可选培养方案依据。

## 适合做什么

- 按课程名称或课程代码查询学分、学时、学期、考核方式和开课单位；
- 查询课程对毕业要求指标点的官方直接支撑关系；
- 沿“指标点 → 毕业要求 → 培养目标”查看派生追踪路径；
- 为课程大纲准备来源中已经提供的基础字段；
- 检查结构、关系端点、课时汇总和建议性警告。

来源未提供课程目标、周次内容、教材或考核细则时，结果会保持 `待编制`，不会根据课程名称补写。

## 给 AI 的入口

执行课程查询或大纲准备前先读取 [SKILL.md](SKILL.md)，并遵守以下边界：

- 官方课程—指标点关系与系统派生的课程—培养目标路径必须分开呈现；
- `extracted` 和 `needs_review` 关系不能作为已核实关系使用；
- 数据只适用于智能制造工程 2025 版，其他专业或版本转交 [training-program-skill-factory](https://github.com/Teaching-Works-Lab/training-program-skill-factory)；
- 结构校验、支撑关系数量和派生路径不能表述为培养质量或学习成效。

## 快速开始

```powershell
git clone https://github.com/Teaching-Works-Lab/intelligent-manufacturing-syllabus.git
cd intelligent-manufacturing-syllabus

# 校验捆绑数据
py -3.12 scripts/curriculum.py validate data/program.json

# 查询课程关系
py -3.12 scripts/curriculum.py query data/program.json `
  --course "工程建模与科学计算可视化基础（Python）" `
  --format markdown

# 准备课程大纲基础字段
py -3.12 scripts/curriculum.py syllabus data/program.json `
  --course "25JD31403"
```

如果作为 Codex Skill 安装，将整个仓库克隆或复制到 `$CODEX_HOME/skills/intelligent-manufacturing-syllabus`；未设置 `CODEX_HOME` 时通常使用 `~/.codex/skills/`。

也可以通过组织 Marketplace 选择安装：

```text
codex plugin marketplace add Teaching-Works-Lab/.github
codex plugin add intelligent-manufacturing-syllabus@teaching-works-lab
```

安装后可显式使用 `$intelligent-manufacturing-syllabus`。该专业数据 Skill 按需安装，不会随工厂或课程工作流自动安装。

## 数据内容

公开数据包含：

- 4 个培养目标；
- 12 个毕业要求；
- 30 个指标点；
- 100 个课程行和 23 个课程组；
- 714 条保留 provenance 的关系记录。

学校、学院和私有源文件身份已经匿名化。专业名称与代码、培养目标、毕业要求、指标点、课程/课程组字段、汇总值和关系数据不属于匿名化允许项。具体边界见 [ANONYMIZATION.md](ANONYMIZATION.md)。

## 主要文件

```text
SKILL.md                    AI 执行入口与回答边界
data/program.json           可查询的结构化主数据
data/course-catalog.md      人类可读课程目录
data/validation-report.md   错误与建议性警告
data/manifest.public.json   公开版本、计数和数据摘要
generated-from.json         工厂提交与模板摘要
scripts/curriculum.py       独立查询与校验 CLI
```

## 数据状态与限制

- 当前结构校验为 0 个错误、108 个建议性警告；警告不是课程质量结论。
- 官方声明实践教学学分为 77.39，类别行机械合计为 76.89；0.50 的来源内部差异被保留，未擅自修正。
- 专业选修备选课程全部作为可查询实体保存，因此“全部开设行机械求和”与学生选定修读口径不同。
- 原 PDF 不在公开仓库中；捆绑校验不会重新读取或替代原 PDF 视觉审核。

## 验证

项目在 Python 3.12 环境完成验证；结构校验使用 `jsonschema`，测试使用 `pytest`。

```powershell
py -3.12 -m pytest -q
py -3.12 scripts/curriculum.py validate data/program.json
```

私有主数据与公开数据可通过 `scripts/verify_public_equivalence.py` 对比。该工具只允许学校身份和私有源文件信息发生变化，课程或关系字段变化会被列为越界差异。
