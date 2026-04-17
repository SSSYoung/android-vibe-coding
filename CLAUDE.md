# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Vibe Coding x Android 工程化实践仓库，聚焦 AI 在 Android 开发中的应用：MCP 上下文接入、Cursor 规则、A2UI 声明式 UI 协议等工程化落地实践。

## 目录结构

```
android-vibe-coding/
├── a2ui_sample/
│   ├── stock_lookup/           # Python A2UI Agent 服务端（股票查询示例）
│   │   ├── __main__.py        # 入口，启动 uvicorn 服务（端口 10004）
│   │   ├── agent.py            # StockAgent 实现
│   │   ├── agent_executor.py   # A2A AgentExecutor 请求处理器
│   │   ├── shared_a2ui/        # 共享基类
│   │   │   ├── agent_base.py   # SchemaValidatedA2uiAgent 基类
│   │   │   └── executor_base.py # SimpleA2uiAgentExecutor 基类
│   │   └── pyproject.toml      # Python 依赖（uv, hatch）
│   └── client/GenUIDemo/       # Flutter Android 客户端（渲染 A2UI）
│
├── demo/
│   ├── embedding/              # Embedding 服务
│   ├── internal_docs/          # 内部文档示例
│   ├── mcp-server/             # MCP Server 实现
│   └── main.py                # 简单演示入口
│
├── docs/                      # 中文技术文档
└── assets/                    # 图片和图表
```

## 核心技术

### A2UI（Agent-to-UI）协议
声明式 UI 协议，AI Agent 返回结构化 UI 定义。Agent 输出格式为：文本 + `---a2ui_JSON---` 分隔符 + JSON 数组，客户端解析后渲染为原生 UI。

### Google ADK
用于 Agent 执行。`SchemaValidatedA2uiAgent` 基类支持流式响应和 JSON Schema 校验。

### A2A（Agent-to-Agent）协议
通过 `a2a-sdk` 实现。stock_lookup 服务在 `http://localhost:10004` 暴露 A2A 端点，支持流式响应和 A2UI 扩展。

## 运行方式

### 启动股票查询 Agent

```bash
cd a2ui_sample/stock_lookup
uv sync
uv run python -m agent
# 服务启动于 http://localhost:10004
```

环境变量（参考 `.env.example`）：
- `LITELLM_MODEL`：使用的模型（默认 `gemini/gemini-2.5-flash`）
- `GEMINI_API_KEY` 或 `GOOGLE_GENAI_USE_VERTEXAI`：Gemini 模型认证
- `ZAI_API_KEY`：智谱 AI 模型认证

### 启动 Flutter 客户端

```bash
cd a2ui_sample/client/GenUIDemo
flutter pub get
flutter run
```

## A2UI 架构

协议交互流程：
1. 客户端发送查询到 A2A 服务器
2. Agent 使用 Google ADK + LLM 处理查询
3. Agent 返回 文本 + `---a2ui_JSON---` + JSON 数组（A2UI 消息）
4. 客户端解析 A2UI JSON 并渲染 UI

`SimpleA2uiAgentExecutor`（executor_base.py）负责解析和分割文本/JSON 响应。

## 构建命令

```bash
# Python 包
cd a2ui_sample/stock_lookup
uv sync                      # 安装依赖
uv run python -m agent       # 直接运行
uv build                     # 构建 wheel

# Flutter 应用
cd a2ui_sample/client/GenUIDemo
flutter pub get
flutter build apk --debug
```

## 文档

`docs/` 目录下有中文技术文章：
- Figma Context MCP + Cursor 高效 UI 工程化
- Cursor Rules 团队级开发规范
- 自建 MCP Server 接入内部知识库
- A2UI 协议规范与架构
