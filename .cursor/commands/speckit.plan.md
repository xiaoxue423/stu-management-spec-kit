---
description: 执行实施规划工作流, 使用计划模板生成设计工件.
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前, 你**必须**考虑用户输入(如果不为空).

## 大纲

0. 从仓库根目录运行以下脚本，标记当前阶段开启。脚本执行结果不影响流程
   脚本参数：根据用户输入的ones任务解析出 ONES_TASK_ID，例如 https://ones.sankuai.com/ones/product/47458/workItem/task/detail/123，则ONES_TASK_ID=123
```bash
bash .specify/scripts/bash/notify-sdd-status.sh \
  --taskId {ONES_TASK_ID} \
  --stage 'plan' \
  --status 'start' \
  --repo {当前仓库绝对路径} \
  --branch {当前分支名}
```

1. **设置**: 从仓库根目录运行 `.specify/scripts/bash/setup-plan.sh --json` 并解析 JSON 获取 FEATURE_SPEC、SPECS_DIR、BRANCH、DESIGN. 对于参数中的单引号如 "I'm Groot", 使用转义语法: 例如 'I'\''m Groot'(或尽可能使用双引号: "I'm Groot").

2. **加载上下文**: 读取 FEATURE_SPEC 和 `.specify/memory/constitution.md`. 加载 DESIGN 模板(已复制).

3. **执行计划工作流**: 按照 DESIGN 模板中的结构:
   - 填充技术背景(将未知项标记为"NEEDS CLARIFICATION")
   - 从章程文档填充章程检查部分
   - 评估关卡(如果违规无正当理由则报错)
   - 阶段 0: 生成 FEATURE_DIR/temp/research.md(解决所有 NEEDS CLARIFICATION)
   - 阶段 1：生成 FEATURE_DIR/temp/data-model.md、FEATURE_DIR/temp/contracts/、FEATURE_DIR/temp/quickstart.md
   - 阶段 1: 结合 FEATURE_DIR/temp/ 目录下已生成文件，按照 DESIGN 模板结构，构建完整的 DESIGN
   - 阶段 1: 通过运行代理脚本更新代理上下文
   - 阶段 1: 从仓库根目录运行 `{SCRIPT_DIR}/clear-temp-files.sh --json`，删除 FEATURE_DIR/temp/ 路径下所有md文件内容
   - 设计后重新评估章程检查

4. **停止并报告**: 命令在阶段 2 规划后结束. 报告分支、DESIGN 路径和生成的工件.

## 阶段

### 阶段 0: 大纲与研究

1. **从上述技术上下文中提取未知项**: 
   - 每个 NEEDS CLARIFICATION → 研究任务
   - 每个依赖项 → 最佳实践任务
   - 每个集成 → 模式任务

2. **生成和分发研究代理**: 
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **在 `FEATURE_DIR/temp/research.md` 中整合发现**, 使用格式: 
   - Decision: [选择了什么]
   - Rationale: [为什么选择]
   - Alternatives considered: [还评估了什么]

**输出**: research.md, 所有 NEEDS CLARIFICATION 已解决

### 阶段 1: 设计与协议

**前提条件**: `FEATURE_DIR/temp/research.md` 完成

1. **从功能规范中提取实体** → `FEATURE_DIR/temp/data-model.md`:
    - 实体名称、字段、关系
    - 来自需求的验证规则
    - 状态转换(如适用)

2. **从功能需求生成 API 协议**: → `FEATURE_DIR/temp/contracts/`
    - 每个用户操作 → 端点
    - 使用标准 REST/GraphQL 模式
    - 将 OpenAPI/GraphQL 模式输出到 `FEATURE_DIR/temp/contracts/`

3. **方案设计 生成**: → `FEATURE_DIR/design.md`
   - 参考 功能规范、实体、API 协议 中的内容
   - 按照 DESIGN 模板结构，构建完整的 DESIGN

4. **代理上下文更新**: 
   - 运行 `.specify/scripts/bash/update-agent-context.sh cursor-agent`
   - 这些脚本检测正在使用哪个 AI 代理
   - 更新相应的代理特定上下文文件
   - 仅添加当前计划中的新技术
   - 保留标记之间的手动添加内容

5. **临时文件删除**
   - 从仓库根目录运行 `{SCRIPT_DIR}/clear-temp-files.sh --json`
   - 解析 JSON 输出验证删除结果
   - 确认 `success` 字段为 `true`
   - 检查 `deleted_files` 数组包含预期的文件（research.md、data-model.md、quickstart.md、contracts/下的文件等）
   - 如果删除失败或未找到文件，报告警告但不阻止流程

6. 在完成所有步骤并报告完成情况后, 从仓库根目录运行以下脚本标记阶段结束。脚本执行结果不影响流程:
   脚本参数：根据用户输入的ones任务解析出 ONES_TASK_ID，例如 https://ones.sankuai.com/ones/product/47458/workItem/task/detail/123，则ONES_TASK_ID=123
```bash
bash .specify/scripts/bash/notify-sdd-status.sh \
  --taskId {ONES_TASK_ID} \
  --stage 'plan' \
  --status 'finished' \
  --repo {当前仓库绝对路径} \
  --branch {当前分支名}
```

**输出**: design.md、代理特定文件

## 关键规则

- 使用绝对路径
- 关卡失败或未解决的澄清事项时报错
