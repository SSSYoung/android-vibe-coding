# AI 助力 Android 工程化实践：（三）自建 MCP Server：让大模型接入内部知识库

*—— 让 AI 不再“凭感觉回答”，而是基于你的内部文档给出可落地的结论与代码*

---

## 1. 背景

大模型懂公网知识，但看不见你的内部接口文档、私有 SDK、团队规范；你一旦问“内部问题”，它就可能开始“猜”，甚至编造接口/字段。

典型风险：

- 编造不存在的接口、参数、返回结构，联调直接翻车
- 把公网最佳实践当成内部规范，导致返工与规范失守

本文要做的事很简单：自建一个 MCP Server，把本地/内网内部文档“接入”到大模型，让回答基于检索到的文档片段而不是凭空发挥。

---

## 2. 具体实践：自建 MCP Server 接入内部知识库

> 这一章用 `demo/mcp-server/server.py` 这个最小例子，演示如何把本地/内网文档接入到大模型，让模型回答前先“查内部资料”。

<img src="../assets/mcp_local_kb_flow.svg" alt="整体链路示意图（IDE/大模型 -> MCP Client -> MCP Server -> 内部文档目录）" width="800">

### 2.1 准备运行环境

这个 Demo 用 Python 实现，核心依赖：

- `mcp`：MCP Server 框架（FastMCP）
- `pypdf`（或 `PyPDF2`）：解析 PDF 文本

安装示例（按你的环境调整）：

```bash
pip install mcp pypdf
```

<!-- TODO: 插图：依赖安装/环境准备截图 -->

### 2.2 编写 MCP Server（核心代码）

MCP Server 的目标很简单：提供一个工具 `search_internal_docs(query)`，把内部文档里最相关的片段返回给大模型作为上下文。

**1）定义 MCP 服务与文档目录**

`demo/mcp-server/server.py`：

```python
from pathlib import Path
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AndroidTeamKnowledge")

BASE_DIR = Path(os.environ.get("KNOWLEDGE_BASE_DIR", Path(__file__).resolve().parent.parent))
DOC_DIR = Path(os.environ.get("KNOWLEDGE_PDF_DIR", BASE_DIR / "internal_docs"))
```

**2）PDF/TXT 读取（兼容 pypdf / PyPDF2）**

```python
def _extract_text(pdf_path: Path) -> str:
    try:
        import pypdf as pdf_lib
    except Exception:
        import PyPDF2 as pdf_lib

    reader = pdf_lib.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)
```

**3）对外暴露检索工具：`search_internal_docs`**

```python
@mcp.tool()
def search_internal_docs(query: str) -> str:
    if not _DOCS:
        _build_index()
    tokens = _tokenize(query)
    if not tokens:
        return "No query tokens found."

    ranked = sorted(
        ((name, chunk, _score(tokens, chunk)) for name, chunk in _DOCS),
        key=lambda item: item[2],
        reverse=True,
    )
    top_hits = [item for item in ranked if item[2] > 0][:3]
    if not top_hits:
        return "No relevant passages found."

    lines = []
    for name, chunk, score in top_hits:
        lines.append(f"[{name}] score={score}")
        lines.append(chunk)
        lines.append("")
    return "\n".join(lines).strip()
```

> 你不需要一开始就上“向量库 + RAG 全家桶”。先把“内部文档可检索、可被大模型引用”跑通，收益立竿见影。

<!-- TODO: 插图：server.py 核心代码截图（可只截工具函数和返回结果格式） -->

### 2.3 在 Cursor 中接入 MCP Server

在 Cursor 的 `mcp.json` 添加一个本地 MCP Server 配置（示例）。下面是我在本项目里的实际配置（Windows + venv + 绝对路径）：

```json
{
  "mcpServers": {
    "androidTeamKnowledge": {
      "args": [
        "D:\\CodeStation\\github\\android-vibe-coding\\demo\\mcp-server\\server.py"
      ],
      "command": "D:\\CodeStation\\github\\android-vibe-coding\\demo\\venv\\Scripts\\python.exe",
      "disabled": false,
      "env": {
        "KNOWLEDGE_PDF_DIR": "D:\\CodeStation\\github\\android-vibe-coding\\demo\\internal_docs"
      }
    }
  }
}
```

> `androidTeamKnowledge` 这个名字可以自定义，但后面调用工具时要用同一个 server 名称。

本地单独启动（用于排查环境问题）：

```bash
python demo/mcp-server/server.py
```

<!-- TODO: 插图：Cursor mcp.json 配置截图 -->

### 2.4 快速验证（推荐两条问题）

你可以直接在对话里让模型调用工具（示例文案）：

1）验证埋点规范：

> 请调用 `androidTeamKnowledge` 的 `search_internal_docs`，查询“埋点 eventName 命名规则 与 必填字段”，并基于返回片段总结规范。

2）验证接口文档：

> 请调用 `androidTeamKnowledge` 的 `search_internal_docs`，查询“用户模块 登录/获取用户信息 接口”，并基于返回片段给出请求示例（不要编造未出现的字段）。

<!-- TODO: 插图：工具返回片段 + 模型基于片段作答的效果截图 -->

## 3. 实战演示（待补充）

## 4. 边界与演进（待补充）

## 5. 总结（待补充）

