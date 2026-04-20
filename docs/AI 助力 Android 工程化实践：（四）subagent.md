> ## 文档索引
> 完整文档索引见：https://code.claude.com/docs/llms.txt
> 在进一步查阅之前，可以先用这个文件了解所有可用页面。

# 创建自定义 subagents

> 在 Claude Code 中创建并使用专门化的 AI subagents，以支持特定任务工作流并改进上下文管理。

Subagents 是专门处理特定类型任务的 AI 助手。当某个旁支任务会让主对话被搜索结果、日志或你之后不会再引用的文件内容淹没时，就适合使用 subagent：它会在自己的上下文里完成这部分工作，只把总结结果返回给你。当你反复以相同指令启动同一类 worker 时，就应该定义一个自定义 subagent。

每个 subagent 都运行在独立的上下文窗口中，拥有自定义 system prompt、特定的工具访问权限和独立的权限设置。当 Claude 遇到与某个 subagent 描述相匹配的任务时，就会把任务委派给它；subagent 会独立完成工作并返回结果。如果你想直观看到它在节省上下文方面的效果，可以参考 [上下文窗口可视化](/en/context-window)，其中展示了一个 subagent 在独立窗口中完成调研任务的会话过程。

<Note>
  如果你需要多个 agent 并行工作并彼此通信，请改用 [agent teams](/en/agent-teams)。Subagents 工作在单个会话内；agent teams 则跨多个独立会话进行协作。
</Note>

Subagents 可以帮助你：

* **保留上下文**，把探索和实现过程从主对话中隔离出去
* **施加约束**，限制某个 subagent 可使用的工具
* **复用配置**，通过用户级 subagents 在多个项目间共享设置
* **专门化行为**，用聚焦的 system prompt 服务特定领域
* **控制成本**，把任务路由到更快、更便宜的模型，例如 Haiku

Claude 会根据每个 subagent 的 description 来判断何时进行委派。因此在创建 subagent 时，要写出清晰的描述，让 Claude 知道应该在什么情况下使用它。

Claude Code 内置了若干 subagents，例如 **Explore**、**Plan** 和 **general-purpose**。你也可以创建自定义 subagents 来处理特定任务。本文会介绍[内置 subagents](#built-in-subagents)、[如何创建自己的 subagent](#quickstart-create-your-first-subagent)、[完整配置选项](#configure-subagents)、[使用模式](#work-with-subagents)以及[示例 subagents](#example-subagents)。

## 内置 subagents

Claude Code 自带一些内置 subagents，Claude 会在合适的时候自动调用。它们都会继承父会话的权限，但附带额外的工具限制。

<Tabs>
  <Tab title="Explore">
    一个快速、只读的 agent，专门优化用于搜索和分析代码库。

    * **模型**：Haiku（速度快、延迟低）
    * **工具**：只读工具（禁止使用 Write 和 Edit 工具）
    * **用途**：发现文件、代码搜索、代码库探索

    当 Claude 需要在不做修改的前提下搜索或理解代码库时，就会委派给 Explore。这样可以把探索过程产生的结果留在独立上下文中，不污染你的主对话。

    在调用 Explore 时，Claude 会指定一个详尽程度：**quick** 用于定向查询，**medium** 用于平衡式探索，**very thorough** 用于全面分析。
  </Tab>

  <Tab title="Plan">
    一个在 [plan mode](/en/common-workflows#use-plan-mode-for-safe-code-analysis) 中使用的研究型 agent，会在给出计划前先收集上下文。

    * **模型**：继承主对话
    * **工具**：只读工具（禁止使用 Write 和 Edit 工具）
    * **用途**：为规划阶段做代码库调研

    当你处于 plan mode，而 Claude 又需要先理解你的代码库时，它会把调研工作委派给 Plan subagent。这样既能避免无限嵌套（subagent 不能再启动其他 subagents），又能获得必要的上下文。
  </Tab>

  <Tab title="General-purpose">
    一个能力全面的 agent，适合既需要探索又需要执行的复杂多步骤任务。

    * **模型**：继承主对话
    * **工具**：全部工具
    * **用途**：复杂调研、多步骤操作、代码修改

    当任务既需要探索又需要修改，或者需要复杂推理来解释结果，又或者包含多个相互依赖的步骤时，Claude 会委派给 general-purpose。
  </Tab>

  <Tab title="Other">
    Claude Code 还包含一些面向特定任务的辅助 agent。它们通常会被自动调用，因此你一般不需要直接使用。

    | Agent             | Model  | Claude 会在何时使用 |
    | :---------------- | :----- | :------------------ |
    | statusline-setup  | Sonnet | 当你运行 `/statusline` 来配置状态栏时 |
    | Claude Code Guide | Haiku  | 当你询问 Claude Code 功能相关问题时 |
  </Tab>
</Tabs>

除了这些内置 subagents 之外，你还可以创建自己的 subagent，并为其配置自定义 prompt、工具限制、permission mode、hooks 和 skills。下面会介绍如何开始以及如何进一步定制。

## 快速开始：创建你的第一个 subagent

Subagents 以带 YAML frontmatter 的 Markdown 文件形式定义。你可以[手动创建](#write-subagent-files)，也可以使用 `/agents` 命令。

下面这个示例会演示如何通过 `/agents` 命令创建一个用户级 subagent。该 subagent 用于审查代码，并为代码库提出改进建议。

<Steps>
  <Step title="打开 subagents 界面">
    在 Claude Code 中运行：

    ```text theme={null}
    /agents
    ```
  </Step>

  <Step title="选择存放位置">
    切换到 **Library** 标签页，选择 **Create new agent**，然后选择 **Personal**。这样会把 subagent 保存到 `~/.claude/agents/`，使其在你所有项目中都可用。
  </Step>

  <Step title="让 Claude 生成">
    选择 **Generate with Claude**。出现提示后，描述这个 subagent：

    ```text theme={null}
    A code improvement agent that scans files and suggests improvements
    for readability, performance, and best practices. It should explain
    each issue, show the current code, and provide an improved version.
    ```

    Claude 会为你生成 identifier、description 和 system prompt。
  </Step>

  <Step title="选择工具">
    如果你想要的是一个只读审查者，就把除 **Read-only tools** 之外的选项全部取消勾选。如果保留所有工具，subagent 会继承主对话可用的全部工具。
  </Step>

  <Step title="选择模型">
    选择 subagent 使用的模型。这个示例中，选择 **Sonnet**，它在分析代码模式时兼顾能力与速度。
  </Step>

  <Step title="选择颜色">
    为 subagent 选择一个背景色。这样你可以在 UI 中更容易识别当前正在运行的是哪个 subagent。
  </Step>

  <Step title="配置 memory">
    选择 **User scope**，为 subagent 启用位于 `~/.claude/agent-memory/` 的[持久 memory 目录](#enable-persistent-memory)。subagent 可以借此在多次对话中持续积累洞见，例如代码库模式和反复出现的问题。如果你不希望它保留学习结果，就选择 **None**。
  </Step>

  <Step title="保存并试用">
    检查配置摘要。按 `s` 或 `Enter` 保存，或按 `e` 保存并在编辑器中打开文件。保存后 subagent 会立刻可用。可以这样试试：

    ```text theme={null}
    Use the code-improver agent to suggest improvements in this project
    ```

    Claude 会把任务委派给你新建的 subagent，它会扫描代码库并返回改进建议。
  </Step>
</Steps>

现在，你已经拥有一个可以在本机任意项目中使用的 subagent，用来分析代码库并给出改进建议。

你也可以手动以 Markdown 文件形式创建 subagents，通过 CLI 参数定义它们，或通过插件分发它们。下面会介绍全部配置选项。

## 配置 subagents

### 使用 /agents 命令

`/agents` 命令会打开一个带标签页的管理界面。**Running** 标签页会显示当前正在运行的 subagents，并允许你打开或停止它们。**Library** 标签页则可以让你：

* 查看所有可用 subagents（内置、用户级、项目级和插件提供的）
* 通过向导或 Claude 生成创建新的 subagents
* 编辑已有 subagent 的配置和工具访问权限
* 删除自定义 subagents
* 在存在重名定义时，查看当前实际生效的是哪一个

这是创建和管理 subagents 的推荐方式。如果你更偏向手动创建或自动化管理，也可以直接添加 subagent 文件。

如果你想在命令行中列出所有已配置的 subagents，而不启动交互式会话，可以运行 `claude agents`。它会按来源分组显示 agents，并标明哪些定义被更高优先级的版本覆盖了。

### 选择 subagent 的作用域

Subagents 是带 YAML frontmatter 的 Markdown 文件。你可以根据作用域把它们存放在不同位置。如果多个 subagent 使用了同一个名称，则优先级更高的位置会生效。

| Location                     | Scope                  | Priority    | 创建方式 |
| :--------------------------- | :--------------------- | :---------- | :------- |
| Managed settings             | 组织范围               | 1（最高）   | 通过 [managed settings](/en/settings) 部署 |
| `--agents` CLI flag          | 当前会话               | 2           | 启动 Claude Code 时传入 JSON |
| `.claude/agents/`            | 当前项目               | 3           | 交互式或手动创建 |
| `~/.claude/agents/`          | 你的所有项目           | 4           | 交互式或手动创建 |
| Plugin's `agents/` directory | 插件启用的作用范围内   | 5（最低）   | 通过 [plugins](/en/plugins) 安装 |

**项目级 subagents**（`.claude/agents/`）非常适合与特定代码库绑定的 subagents。建议将它们提交到版本控制，让团队成员能够协作使用和改进。

项目级 subagents 会从当前工作目录开始向上查找。通过 `--add-dir` 添加的目录[只授予文件访问权限](/en/permissions#additional-directories-grant-file-access-not-configuration)，不会被扫描用于发现 subagents。若要在多个项目之间共享 subagents，请使用 `~/.claude/agents/` 或 [plugin](/en/plugins)。

**用户级 subagents**（`~/.claude/agents/`）是你个人可在所有项目中使用的 subagents。

**通过 CLI 定义的 subagents** 在启动 Claude Code 时以 JSON 形式传入。它们只存在于当前会话中，不会保存到磁盘，因此很适合快速测试或自动化脚本。你可以在一次 `--agents` 调用中定义多个 subagents：

```bash theme={null}
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors, identify root causes, and provide fixes."
  }
}'
```

`--agents` 参数接收的 JSON，支持与文件式 subagents 相同的 [frontmatter](#supported-frontmatter-fields) 字段：`description`、`prompt`、`tools`、`disallowedTools`、`model`、`permissionMode`、`mcpServers`、`hooks`、`maxTurns`、`skills`、`initialPrompt`、`memory`、`effort`、`background`、`isolation` 和 `color`。其中 `prompt` 用来指定 system prompt，等价于文件式 subagent 中的 Markdown 正文。

**Managed subagents** 由组织管理员部署。将 Markdown 文件放到[managed settings 目录](/en/settings#settings-files)中的 `.claude/agents/` 下，frontmatter 格式与项目级和用户级 subagents 相同。对于同名定义，managed 版本优先于项目级和用户级版本。

**插件提供的 subagents** 来自你安装的 [plugins](/en/plugins)。它们会和你的自定义 subagents 一起显示在 `/agents` 中。有关如何创建插件 subagents，请参见 [plugin components reference](/en/plugins-reference#agents)。

<Note>
  出于安全原因，插件提供的 subagents 不支持 `hooks`、`mcpServers` 或 `permissionMode` 这几个 frontmatter 字段。加载插件中的 agent 时，这些字段会被忽略。如果你确实需要这些能力，请把 agent 文件复制到 `.claude/agents/` 或 `~/.claude/agents/`。你也可以在 `settings.json` 或 `settings.local.json` 中的 [`permissions.allow`](/en/settings#permission-settings) 里添加规则，但这些规则作用于整个会话，而不只是某个插件 subagent。
</Note>

来自以上任一作用域的 subagent 定义，也都可供 [agent teams](/en/agent-teams#use-subagent-definitions-for-teammates) 使用：当你启动一个 teammate 时，可以引用某种 subagent 类型，该 teammate 会使用它的 `tools` 和 `model`，并把该定义的正文附加到 teammate 的 system prompt 里作为额外指令。关于这种路径下哪些 frontmatter 字段会生效，请参见 [agent teams](/en/agent-teams#use-subagent-definitions-for-teammates)。

### 编写 subagent 文件

Subagent 文件使用 YAML frontmatter 进行配置，后面跟着写在 Markdown 中的 system prompt：

<Note>
  Subagents 会在会话启动时加载。如果你是通过手动添加文件的方式创建 subagent，需要重启会话，或使用 `/agents` 立即加载它。
</Note>

```markdown theme={null}
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

Frontmatter 用于定义 subagent 的元数据和配置。正文会成为指导 subagent 行为的 system prompt。Subagent 只会收到这段 system prompt（以及诸如工作目录之类的基础环境信息），而不会收到完整的 Claude Code system prompt。

Subagent 默认从主对话当前的工作目录启动。在 subagent 内部，`cd` 命令不会在 Bash 或 PowerShell 工具调用之间持续生效，也不会影响主对话的工作目录。如果你希望给 subagent 一个隔离的仓库副本，则应设置 [`isolation: worktree`](#supported-frontmatter-fields)。

#### 支持的 frontmatter 字段

下列字段都可以用于 YAML frontmatter。只有 `name` 和 `description` 是必填项。

| Field | Required | Description |
| :---- | :------- | :---------- |
| `name` | Yes | 由小写字母和连字符组成的唯一标识符 |
| `description` | Yes | Claude 应在什么情况下把任务委派给这个 subagent |
| `tools` | No | 该 subagent 可使用的[工具](#available-tools)。省略时继承所有工具 |
| `disallowedTools` | No | 要禁止的工具，会从继承或指定的工具列表中移除 |
| `model` | No | 使用的[模型](#choose-a-model)：`sonnet`、`opus`、`haiku`、完整模型 ID（如 `claude-opus-4-7`），或 `inherit`。默认值为 `inherit` |
| `permissionMode` | No | [permission mode](#permission-modes)：`default`、`acceptEdits`、`auto`、`dontAsk`、`bypassPermissions` 或 `plan` |
| `maxTurns` | No | subagent 停止前允许的最大 agentic turn 数 |
| `skills` | No | 启动时加载到 subagent 上下文中的 [Skills](/en/skills)。会直接注入完整 skill 内容，而不仅仅是让它可被调用。Subagents 不会继承父对话中的 skills |
| `mcpServers` | No | 该 subagent 可用的 [MCP servers](/en/mcp)。每个条目可以是引用已配置 server 的名称（例如 `"slack"`），也可以是一个以内联形式定义的 server，其中 key 为 server 名称，value 为完整的 [MCP server config](/en/mcp#installing-mcp-servers) |
| `hooks` | No | 作用域限定在该 subagent 内的[生命周期 hooks](#define-hooks-for-subagents) |
| `memory` | No | [持久 memory 作用域](#enable-persistent-memory)：`user`、`project` 或 `local`。可实现跨会话学习 |
| `background` | No | 设为 `true` 时，该 subagent 始终以[后台任务](#run-subagents-in-foreground-or-background)方式运行。默认值：`false` |
| `effort` | No | 该 subagent 处于活动状态时的 effort level。会覆盖会话级 effort。默认继承会话配置。可选项：`low`、`medium`、`high`、`xhigh`、`max`；实际可用级别取决于模型 |
| `isolation` | No | 设为 `worktree` 时，会让 subagent 在临时 [git worktree](/en/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees) 中运行，从而获得仓库的隔离副本。如果 subagent 没有产生变更，该 worktree 会自动清理 |
| `color` | No | subagent 在任务列表和 transcript 中显示的颜色。可选值为 `red`、`blue`、`green`、`yellow`、`purple`、`orange`、`pink` 或 `cyan` |
| `initialPrompt` | No | 当这个 agent 作为主会话 agent 运行时（通过 `--agent` 或 `agent` 设置），会自动作为第一条用户消息提交。会处理其中的 [Commands](/en/cli-reference#slash-commands) 和 [skills](/en/skills)。如果用户另外提供 prompt，它会被追加在前面 |

### 选择模型

`model` 字段用于控制 subagent 使用哪个 [AI model](/en/models)：

* **模型别名**：使用可用别名之一：`sonnet`、`opus` 或 `haiku`
* **完整模型 ID**：使用完整模型 ID，例如 `claude-opus-4-7` 或 `claude-sonnet-4-6`。支持与 `--model` 参数相同的取值
* **inherit**：使用与主对话相同的模型
* **省略**：如果未指定，默认值为 `inherit`（即使用主对话模型）

当 Claude 调用某个 subagent 时，也可以在那一次调用里传入 `model` 参数。Claude Code 会按以下顺序解析 subagent 应使用的模型：

1. 若已设置，则优先使用环境变量 [`CLAUDE_CODE_SUBAGENT_MODEL`](/en/env-vars)
2. 单次调用上传入的 `model` 参数
3. subagent 定义里的 `model` frontmatter
4. 主对话使用的模型

### 控制 subagent 的能力

你可以通过工具访问、permission modes 和条件规则来控制 subagent 能做什么。

#### 可用工具

Subagents 可以使用 Claude Code 的任意[内部工具](/en/tools-reference)。默认情况下，subagent 会继承主对话中的全部工具，包括 MCP 工具。若要限制工具，可使用 `tools` 字段（allowlist）或 `disallowedTools` 字段（denylist）。下面这个例子使用 `tools`，只允许 Read、Grep、Glob 和 Bash，因此 subagent 不能编辑文件、写入文件，也不能使用任何 MCP 工具：

```markdown theme={null}
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
---
```

下面这个例子则使用 `disallowedTools`，继承主对话的所有工具，但排除 Write 和 Edit。这样 subagent 仍然保留 Bash、MCP 工具以及其他所有工具：

```markdown theme={null}
---
name: no-writes
description: Inherits every tool except file writes
disallowedTools: Write, Edit
---
```

如果两个字段都设置了，Claude Code 会先应用 `disallowedTools`，再基于剩余工具解析 `tools`。如果某个工具同时出现在两者中，它会被移除。

#### 限制可启动的 subagent 类型

当某个 agent 通过 `claude --agent` 作为主线程运行时，它可以使用 Agent 工具启动 subagents。若要限制它能启动哪些 subagent 类型，可以在 `tools` 字段中使用 `Agent(agent_type)` 语法。

在 2.1.63 版本中，Task 工具被重命名为 Agent。现有配置和 agent 定义中的 `Task(...)` 仍然作为别名继续生效。

```markdown theme={null}
---
name: coordinator
description: Coordinates work across specialized agents
tools: Agent(worker, researcher), Read, Bash
---
```

这是一种 allowlist：只允许启动 `worker` 和 `researcher` 两种 subagent。如果该 agent 试图启动任何其他类型，请求会失败，而且它在 prompt 中只能看到被允许的类型。若你想在允许其他所有 agent 的同时屏蔽特定 agent，请改用 `permissions.deny`。如果你希望允许启动任意 subagent 而不做限制，可以直接使用不带括号的 `Agent`：

```markdown theme={null}
tools: Agent, Read, Bash
```

如果 `tools` 列表中完全没有 `Agent`，则该 agent 不能启动任何 subagents。这个限制只适用于通过 `claude --agent` 作为主线程运行的 agent。Subagents 本身不能再启动其他 subagents，因此在 subagent 定义中使用 `Agent(agent_type)` 不会产生任何效果。

#### 将 MCP servers 限定在某个 subagent 内

使用 `mcpServers` 字段，可以为某个 subagent 提供主对话中不可用的 [MCP](/en/mcp) servers。以内联方式定义的 server 会在 subagent 启动时连接，在结束时断开。字符串引用则会共享父会话已有的连接。列表中的每一项都可以是一个内联 server 定义，或一个引用当前会话已配置 MCP server 的字符串：

```yaml theme={null}
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  # Inline definition: scoped to this subagent only
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  # Reference by name: reuses an already-configured server
  - github
---

Use the Playwright tools to navigate, screenshot, and interact with pages.
```

内联定义使用与 `.mcp.json` 中 server 条目相同的 schema（`stdio`、`http`、`sse`、`ws`），并以 server 名作为 key。如果你希望某个 MCP server 完全不出现在主对话中，以免它的工具描述在那里占用上下文，就应把它以内联方式定义在这里，而不是放到 `.mcp.json` 中。这样工具只会提供给 subagent，而不会提供给父对话。

#### permission modes

`permissionMode` 字段用于控制 subagent 如何处理权限提示。Subagent 会继承主对话的权限上下文，也可以覆盖模式；但如果父模式按下文规则具有更高优先级，则仍以父模式为准。

| Mode | Behavior |
| :--- | :------- |
| `default` | 标准权限检查，并在需要时弹出提示 |
| `acceptEdits` | 自动接受针对工作目录或 `additionalDirectories` 路径中的文件编辑和常见文件系统命令 |
| `auto` | [Auto mode](/en/permissions#auto-mode)：后台分类器会审查命令和对受保护目录的写入 |
| `dontAsk` | 自动拒绝权限提示（但被显式允许的工具仍可使用） |
| `bypassPermissions` | 跳过权限提示 |
| `plan` | Plan mode（只读探索） |

使用 `bypassPermissions` 时要格外谨慎。它会跳过权限提示，允许 subagent 在不经批准的情况下执行操作。不过，对 `.git`、`.claude`、`.vscode`、`.idea` 和 `.husky` 目录的写入仍然会要求确认，唯独 `.claude/commands`、`.claude/agents` 和 `.claude/skills` 例外。详见 [permission modes](/en/permissions#permission-modes)。

如果父会话使用的是 `bypassPermissions` 或 `acceptEdits`，那么它的优先级更高，无法被覆盖。如果父会话使用的是 [auto mode](/en/permissions#auto-mode)，subagent 也会继承 auto mode，此时 frontmatter 中的任何 `permissionMode` 都会被忽略：分类器会按照与父会话相同的阻止和允许规则来评估 subagent 的工具调用。

#### 预加载 skills 到 subagents 中

使用 `skills` 字段，可以在 subagent 启动时把 skill 内容直接注入其上下文。这样一来，subagent 无需在执行过程中自行发现并加载 skills，也能立即具备某一领域的知识。

```markdown theme={null}
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

每个 skill 的完整内容都会被注入到 subagent 上下文中，而不只是让它在执行时可供调用。Subagents 不会继承父对话中的 skills；必须显式列出。

这与 [在 subagent 中运行 skill](/en/skills#run-a-skill-in-a-subagent) 正好相反。对于 subagent 中的 `skills`，是由 subagent 控制 system prompt 并加载 skill 内容；而 skill 中的 `context: fork`，则是把 skill 内容注入到你指定的 agent 中。两者底层使用的是同一套机制。

#### 启用持久 memory

`memory` 字段会为 subagent 提供一个跨多次对话持续存在的目录。Subagent 可以用它逐步积累知识，例如代码库模式、调试经验以及架构决策。

```markdown theme={null}
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

可以根据 memory 应该作用到多大范围来选择作用域：

| Scope | Location | Use when |
| :---- | :------- | :------- |
| `user` | `~/.claude/agent-memory/<name-of-agent>/` | 该 subagent 应在所有项目中都记住学习结果 |
| `project` | `.claude/agent-memory/<name-of-agent>/` | 该 subagent 的知识是项目专属的，并且适合通过版本控制共享 |
| `local` | `.claude/agent-memory-local/<name-of-agent>/` | 该 subagent 的知识是项目专属的，但不应提交到版本控制 |

启用 memory 后：

* subagent 的 system prompt 中会加入关于如何读取和写入 memory 目录的说明
* subagent 的 system prompt 还会包含该 memory 目录下 `MEMORY.md` 的前 200 行或前 25KB 内容（二者取先达到的一个），并在超出限制时提示其整理 `MEMORY.md`
* 会自动启用 Read、Write 和 Edit 工具，以便 subagent 管理自己的 memory 文件

##### 持久 memory 使用建议

* `project` 是推荐的默认作用域。它可以让 subagent 的知识通过版本控制进行共享。如果该 subagent 的知识适用于所有项目，则用 `user`；如果这些知识不应该提交到版本控制，则用 `local`
* 在开始任务前，让 subagent 先查阅自己的 memory，例如：“Review this PR, and check your memory for patterns you’ve seen before.”
* 在任务完成后，让 subagent 更新自己的 memory，例如：“Now that you’re done, save what you learned to your memory.” 长期下来，这会积累出一个知识库，让 subagent 越来越高效
* 也可以把 memory 相关要求直接写进 subagent 的 Markdown 文件，让它主动维护自己的知识库：

```text theme={null}
Update your agent memory as you discover codepaths, patterns, library
locations, and key architectural decisions. This builds up institutional
knowledge across conversations. Write concise notes about what you found
and where.
```

#### 使用 hooks 实现条件规则

如果你希望更动态地控制工具使用，可以利用 `PreToolUse` hooks 在操作真正执行前做校验。当你需要允许某个工具的部分操作、同时拦截另一些操作时，这种方式尤其有用。下面这个例子创建了一个只允许执行只读数据库查询的 subagent。`PreToolUse` hook 会在每次 Bash 命令执行之前，先运行 `command` 中指定的脚本：

```yaml theme={null}
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

Claude Code 会通过 stdin 将 [hook 输入](/en/hooks#pretooluse-input) 以 JSON 形式传递给 hook 命令。校验脚本会读取这段 JSON，提取 Bash 命令，并通过 [以 code 2 退出](/en/hooks#exit-code-2-behavior-per-event) 来阻止写操作：

```bash theme={null}
#!/bin/bash
# ./scripts/validate-readonly-query.sh

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Block SQL write operations (case-insensitive)
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b' > /dev/null; then
  echo "Blocked: Only SELECT queries are allowed" >&2
  exit 2
fi

exit 0
```

完整输入 schema 参见 [Hook input](/en/hooks#pretooluse-input)，退出码如何影响行为请参见 [exit codes](/en/hooks#exit-code-output)。

#### 禁用特定 subagents

你可以在 [settings](/en/settings) 的 `deny` 数组中加入特定 subagent，从而阻止 Claude 使用它们。格式为 `Agent(subagent-name)`，其中 `subagent-name` 必须与该 subagent 的 `name` 字段一致。

```json theme={null}
{
  "permissions": {
    "deny": ["Agent(Explore)", "Agent(my-custom-agent)"]
  }
}
```

这对内置 subagents 和自定义 subagents 都有效。你也可以使用 `--disallowedTools` CLI 参数：

```bash theme={null}
claude --disallowedTools "Agent(Explore)"
```

更多关于权限规则的说明，请参见 [Permissions documentation](/en/permissions#tool-specific-permission-rules)。

### 为 subagents 定义 hooks

Subagents 可以定义在自身生命周期内运行的 [hooks](/en/hooks)。配置方式有两种：

1. **在 subagent 的 frontmatter 中定义**：这些 hooks 只会在该 subagent 运行期间生效
2. **在 `settings.json` 中定义**：这些 hooks 作用于主会话，会在 subagent 启动或停止时触发

#### 在 subagent frontmatter 中定义 hooks

你可以直接在 subagent 的 Markdown 文件中定义 hooks。这些 hooks 只会在对应 subagent 处于活动状态时运行，并在其结束后自动清理。

<Note>
  Frontmatter 中定义的 hooks，会在该 agent 通过 Agent 工具或 @ 提及方式作为 subagent 启动时触发；如果它是通过 [`--agent`](#invoke-subagents-explicitly) 或 `agent` 设置作为主会话运行，则不会触发。若要配置会话级 hooks，请改在 [`settings.json`](/en/hooks) 中设置。
</Note>

支持全部 [hook events](/en/hooks#hook-events)。在 subagent 场景下最常见的是：

| Event | Matcher input | When it fires |
| :---- | :------------ | :------------ |
| `PreToolUse` | Tool name | subagent 使用工具之前 |
| `PostToolUse` | Tool name | subagent 使用工具之后 |
| `Stop` | (none) | subagent 完成时触发（运行时会转换为 `SubagentStop`） |

下面这个例子会用 `PreToolUse` hook 校验 Bash 命令，并在文件被修改后通过 `PostToolUse` 运行 linter：

```yaml theme={null}
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

Frontmatter 中的 `Stop` hooks 会自动转换为 `SubagentStop` 事件。

#### 面向 subagent 事件的项目级 hooks

你也可以在 `settings.json` 中配置 hooks，让它们响应主会话里的 subagent 生命周期事件。

| Event | Matcher input | When it fires |
| :---- | :------------ | :------------ |
| `SubagentStart` | Agent type name | 当某个 subagent 开始执行时 |
| `SubagentStop` | Agent type name | 当某个 subagent 执行完成时 |

这两个事件都支持 matcher，可按名称精确匹配特定 agent 类型。下面这个例子会在 `db-agent` subagent 启动时运行 setup 脚本，并在任意 subagent 停止时运行 cleanup 脚本：

```json theme={null}
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db-connection.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          { "type": "command", "command": "./scripts/cleanup-db-connection.sh" }
        ]
      }
    ]
  }
}
```

完整 hook 配置格式见 [Hooks](/en/hooks)。

## 使用 subagents

### 理解自动委派

Claude 会根据你的请求描述、subagent 配置中的 `description` 字段以及当前上下文，自动决定是否把任务委派给某个 subagent。若想鼓励 Claude 主动委派，可以在 subagent 的 description 中加入类似 “use proactively” 的措辞。

### 显式调用 subagents

如果自动委派还不够，你也可以主动要求使用某个 subagent。从“一次性建议”到“整个会话默认使用”，通常有三种方式：

* **自然语言**：在 prompt 中点名 subagent，由 Claude 决定是否委派
* **@-mention**：保证该 subagent 会在某个任务中运行
* **整个会话范围**：通过 `--agent` 参数或 `agent` 设置，让整个会话都使用该 subagent 的 system prompt、工具限制和模型

对于自然语言方式，不需要特殊语法。你只要在提示中点名 subagent，Claude 通常就会进行委派：

```text theme={null}
Use the test-runner subagent to fix failing tests
Have the code-reviewer subagent look at my recent changes
```

**使用 @ 提及 subagent。** 输入 `@`，然后像 @ 文件那样在补全列表中选择 subagent。这样可以确保执行的是你指定的 subagent，而不是把决定权交给 Claude：

```text theme={null}
@"code-reviewer (agent)" look at the auth changes
```

你的整条消息仍然会先发送给 Claude，由 Claude 根据你的意图来撰写 subagent 的任务 prompt。@-mention 决定的是 Claude 调用哪个 subagent，而不是该 subagent 接收到什么 prompt。

由已启用 [plugin](/en/plugins) 提供的 subagents，会在补全中显示为 `<plugin-name>:<agent-name>`。当前会话中正在运行的、带名称的后台 subagents 也会显示在补全列表中，并附带当前状态。

你也可以不通过选择器，直接手动输入 mention：本地 subagent 使用 `@agent-<name>`，插件 subagent 使用 `@agent-<plugin-name>:<agent-name>`。

**让整个会话作为某个 subagent 运行。** 使用 [`--agent <name>`](/en/cli-reference) 启动会话后，主线程本身会采用该 subagent 的 system prompt、工具限制和模型：

```bash theme={null}
claude --agent code-reviewer
```

这个 subagent 的 system prompt 会完全替换默认的 Claude Code system prompt，效果与 [`--system-prompt`](/en/cli-reference) 类似。`CLAUDE.md` 文件和项目 memory 仍会通过正常的消息流加载。启动头部会显示 agent 名称为 `@<name>`，以便你确认它已生效。

这对内置和自定义 subagents 都有效，并且当你恢复会话时，该选择也会被保留。

如果要使用插件提供的 subagent，请传入带作用域的名称：`claude --agent <plugin-name>:<agent-name>`。

若要把它设为项目内每次会话的默认 agent，可以在 `.claude/settings.json` 中配置 `agent`：

```json theme={null}
{
  "agent": "code-reviewer"
}
```

如果 CLI 参数和配置同时存在，CLI 参数优先。

### 在前台或后台运行 subagents

Subagents 可以在前台（阻塞式）或后台（并发式）运行：

* **前台 subagents** 会阻塞主对话，直到执行完成。权限提示和澄清问题（如 [`AskUserQuestion`](/en/tools-reference)）会直接转发给你
* **后台 subagents** 会在你继续工作的同时并发运行。启动前，Claude Code 会先为 subagent 需要的工具权限向你发出请求，确保它提前获得所需批准。启动后，subagent 会继承这些权限，并自动拒绝所有未经预批准的操作。如果后台 subagent 需要提出澄清问题，该工具调用会失败，但 subagent 会继续运行

如果后台 subagent 因缺少权限而失败，你可以用同样的任务重新启动一个前台 subagent，以便通过交互式提示重试。

Claude 会根据任务性质决定是前台还是后台运行 subagents。你也可以：

* 直接告诉 Claude “run this in the background”
* 按 **Ctrl+B** 将正在运行的任务切换到后台

如果要彻底禁用后台任务功能，请把环境变量 `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` 设为 `1`。详见 [Environment variables](/en/env-vars)。

### 常见模式

#### 隔离高输出量操作

Subagent 最有效的用法之一，就是把会产生大量输出的操作隔离出去。运行测试、抓取文档或处理日志文件，都会消耗大量上下文。把这些工作委派给 subagent 后，冗长输出会留在它自己的上下文里，返回主对话的只有你真正需要的总结。

```text theme={null}
Use a subagent to run the test suite and report only the failing tests with their error messages
```

#### 并行研究

如果是相互独立的调查任务，可以同时启动多个 subagents 并行工作：

```text theme={null}
Research the authentication, database, and API modules in parallel using separate subagents
```

每个 subagent 会独立探索自己的区域，然后 Claude 再把结果整合起来。它最适合那些研究路径彼此独立、不互相依赖的场景。

<Warning>
  当 subagents 完成任务后，它们的结果会返回到你的主对话中。如果你同时运行很多 subagents，而且每个都返回详细结果，主对话依然可能消耗大量上下文。
</Warning>

对于需要长期并行、或超出单个上下文窗口容量的任务，建议使用 [agent teams](/en/agent-teams)，这样每个 worker 都拥有独立上下文。

#### 串联 subagents

对于多步骤工作流，可以让 Claude 按顺序调用多个 subagents。每个 subagent 完成自己的任务后把结果返回给 Claude，再由 Claude 把相关上下文交给下一个 subagent。

```text theme={null}
Use the code-reviewer subagent to find performance issues, then use the optimizer subagent to fix them
```

### 在 subagents 和主对话之间做选择

以下情况更适合使用**主对话**：

* 任务需要频繁来回沟通或反复迭代打磨
* 多个阶段共享大量上下文（规划 → 实现 → 测试）
* 你要做的是快速、定向的小改动
* 你很在意延迟。Subagent 每次都是全新启动，可能需要时间自行收集上下文

以下情况更适合使用**subagents**：

* 任务会产生大量你不希望留在主上下文中的输出
* 你希望强制施加特定的工具限制或权限规则
* 工作本身相对自包含，最终只需要返回一个总结

如果你的目标是获得可复用的 prompts 或工作流，并且希望它们运行在主对话上下文中而不是隔离的 subagent 上下文里，那么应优先考虑 [Skills](/en/skills)。

如果只是想快速问一个与你当前对话内容有关的问题，可以用 [`/btw`](/en/interactive-mode#side-questions-with-btw) 而不是 subagent。它能看到你的全部上下文，但没有工具访问权限，而且回答不会写入历史记录。

<Note>
  Subagents 不能再启动其他 subagents。如果你的工作流需要嵌套委派，请改用 [Skills](/en/skills) 或在主对话中[串联多个 subagents](#chain-subagents)。
</Note>

### 管理 subagent 上下文

#### 恢复 subagents

每次调用 subagent，都会创建一个拥有全新上下文的新实例。若你想继续某个已有 subagent 的工作，而不是从头开始，可以让 Claude 恢复它。

恢复后的 subagent 会保留完整的对话历史，包括之前的所有工具调用、执行结果和推理过程。也就是说，它会从上次停止的位置继续，而不是重新开始。

当某个 subagent 完成任务后，Claude 会拿到它的 agent ID。Claude 会使用 `SendMessage` 工具，并把该 agent 的 ID 作为 `to` 字段来恢复它。`SendMessage` 工具只有在通过 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 启用了 [agent teams](/en/agent-teams) 时才可用。

要恢复一个 subagent，可以直接要求 Claude 继续之前的工作：

```text theme={null}
Use the code-reviewer subagent to review the authentication module
[Agent completes]

Continue that code review and now analyze the authorization logic
[Claude resumes the subagent with full context from previous conversation]
```

如果一个已停止的 subagent 收到 `SendMessage`，它会在后台自动恢复，无需新的 `Agent` 调用。

如果你想显式引用某个 subagent，也可以让 Claude 告诉你它的 agent ID；或者直接到 `~/.claude/projects/{project}/{sessionId}/subagents/` 下查看 transcript 文件。每份 transcript 都存成 `agent-{agentId}.jsonl`。

Subagent 的 transcript 与主对话彼此独立：

* **主对话压缩**：主对话发生 compact 时，不会影响 subagent transcript；它们保存在独立文件中
* **会话持久性**：subagent transcript 会在其所属 session 内持续存在。只要恢复同一个 session，即使重启 Claude Code 后，你依然可以[恢复某个 subagent](#resume-subagents)
* **自动清理**：transcript 会根据 `cleanupPeriodDays` 设置自动清理（默认 30 天）

#### 自动压缩

Subagents 支持与主对话相同逻辑的自动压缩。默认情况下，会在大约 95% 容量时触发自动压缩。若要更早触发，可以把 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 设置为更低的百分比（例如 `50`）。详见 [environment variables](/en/env-vars)。

压缩事件会记录在 subagent transcript 文件中：

```json theme={null}
{
  "type": "system",
  "subtype": "compact_boundary",
  "compactMetadata": {
    "trigger": "auto",
    "preTokens": 167189
  }
}
```

`preTokens` 表示压缩发生前已使用的 token 数量。

## 示例 subagents

这些示例展示了构建 subagents 的有效模式。你可以把它们作为起点，或者让 Claude 基于它们生成更适合你的版本。

<Tip>
  **最佳实践：**

  * **设计聚焦型 subagents：** 每个 subagent 都应该只在一个特定任务上表现出色
  * **写清楚 description：** Claude 会依据 description 决定是否委派
  * **限制工具访问：** 出于安全和专注性的考虑，只授予必要权限
  * **提交到版本控制：** 让项目级 subagents 能够被团队共享
</Tip>

### Code reviewer

一个只读的 subagent，只负责审查代码而不做修改。这个例子展示了如何设计一个聚焦型 subagent：工具访问受限（没有 Edit 和 Write），并且 prompt 详细规定了应关注什么、以及输出应如何组织。

```markdown theme={null}
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### Debugger

一个既能分析问题也能修复问题的 subagent。与 code reviewer 不同，这个例子包含了 Edit，因为修 bug 必然要修改代码。它的 prompt 给出了从定位到验证的清晰流程。

```markdown theme={null}
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### Data scientist

一个面向数据分析工作的领域专用 subagent。这个示例展示了如何为典型编码任务之外的专门工作流创建 subagents。它显式设置了 `model: sonnet`，以获得更强的分析能力。

```markdown theme={null}
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Key practices:
- Write optimized SQL queries with proper filters
- Use appropriate aggregations and joins
- Include comments explaining complex logic
- Format results for readability
- Provide data-driven recommendations

For each analysis:
- Explain the query approach
- Document any assumptions
- Highlight key findings
- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

### Database query validator

一个允许使用 Bash，但会校验命令、只允许只读 SQL 查询的 subagent。这个例子展示了当 `tools` 字段的粒度还不够细时，如何用 `PreToolUse` hooks 做条件校验。

```markdown theme={null}
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.

When asked to analyze data:
1. Identify which tables contain the relevant data
2. Write efficient SELECT queries with appropriate filters
3. Present results clearly with context

You cannot modify data. If asked to INSERT, UPDATE, DELETE, or modify schema, explain that you only have read access.
```

Claude Code 会通过 stdin 将 [hook input](/en/hooks#pretooluse-input) 以 JSON 形式传给 hook 命令。校验脚本会读取这段 JSON，提取待执行命令，并拿它与 SQL 写操作列表进行比对。如果检测到写操作，脚本会通过 [以 code 2 退出](/en/hooks#exit-code-2-behavior-per-event) 来阻止执行，并通过 stderr 把错误信息返回给 Claude。

你可以把校验脚本放在项目中的任意位置，但路径必须和 hook 配置中的 `command` 字段一致：

```bash theme={null}
#!/bin/bash
# Blocks SQL write operations, allows SELECT queries

# Read JSON input from stdin
INPUT=$(cat)

# Extract the command field from tool_input using jq
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block write operations (case-insensitive)
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE)\b' > /dev/null; then
  echo "Blocked: Write operations not allowed. Use SELECT queries only." >&2
  exit 2
fi

exit 0
```

把脚本设为可执行：

```bash theme={null}
chmod +x ./scripts/validate-readonly-query.sh
```

该 hook 会通过 stdin 接收 JSON，其中 Bash 命令位于 `tool_input.command`。退出码 2 会阻止操作执行，并把错误信息回传给 Claude。关于退出码的更多说明见 [Hooks](/en/hooks#exit-code-output)，完整输入 schema 见 [Hook input](/en/hooks#pretooluse-input)。

## 下一步

现在你已经理解了 subagents，可以继续看看这些相关功能：

* [通过 plugins 分发 subagents](/en/plugins)，以便在团队或多个项目之间共享
* [以编程方式运行 Claude Code](/en/headless)，结合 Agent SDK 用于 CI/CD 和自动化
* [使用 MCP servers](/en/mcp)，为 subagents 提供外部工具和数据访问能力
