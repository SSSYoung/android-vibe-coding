# A2UI 股票查询 Agent 示例

基于 [Google A2UI](https://github.com/google/A2UI) 的 `stock_lookup` 示例项目，提供独立的股票信息查询服务。

## ✨ 特性

- 🚀 **独立部署** - 无需依赖 A2UI 完整仓库结构
- 🔍 **智能查询** - 支持自然语言股票信息查询
- 📊 **实时数据** - 模拟 AAPL/TSLA/NVDA 等股票数据
- 🛠️ **快速启动** - 简单的配置和部署流程

## 📋 环境要求

| 要求 | 版本/说明 |
|------|-----------|
| Python | **3.13+** |
| 包管理器 | **UV** ([安装指南](https://docs.astral.sh/uv/)) |
| API 密钥 | **Gemini API Key** ([获取地址](https://aistudio.google.com/apikey)) |
| 依赖 | 本机 A2UI 仓库 (`../../A2UI/a2a_agents/python/a2ui_agent`) |

## 🚀 快速部署

### 步骤 1: 进入项目目录

```bash
cd a2ui_sample\agent
```

> 💡 **提示**: 如果你在 `android-vibe-coding` 根目录下，直接运行 `cd a2ui_sample`

### 步骤 2: 配置环境变量

#### Linux/macOS:
```bash
cp .env.example .env
```

#### Windows PowerShell:
```powershell
copy .env.example .env
```

### 步骤 3: 配置 API 密钥

编辑 `.env` 文件，添加以下配置：

```env
# Gemini API 配置
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
LITELLM_MODEL=gemini/gemini-2.5-flash
```

> � **获取 API 密钥**: 访问 [Google AI Studio](https://aistudio.google.com/apikey) 获取免费的 Gemini API 密钥

### 步骤 4: 安装依赖并启动服务

```bash
# 安装项目依赖
uv sync

# 启动服务
uv run . --host localhost --port 10004
```

服务启动成功后，访问 [http://localhost:10004](http://localhost:10004)

## 📖 使用方法

服务启动成功后，你可以通过以下方式使用：

### 方式 1: A2A 客户端查询
```bash
# 示例查询命令
"显示 AAPL 股票详情"
"查询特斯拉股票信息"
"获取 NVDA 股票价格"
```

### 方式 2: Web 界面
直接访问 [http://localhost:10004](http://localhost:10004) 使用 Web 界面

### 方式 3: API 调用
```bash
curl -X POST http://localhost:10004/query \
  -H "Content-Type: application/json" \
  -d '{"query": "显示 AAPL 股票详情"}'
```

## ⚙️ 配置说明

### 环境变量详解
| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `GEMINI_API_KEY` | Gemini API 密钥 | 必填 |
| `GOOGLE_GENAI_USE_VERTEXAI` | 是否使用 Vertex AI | `FALSE` |
| `LITELLM_MODEL` | 使用的模型 | `gemini/gemini-2.5-flash` |

### 支持的股票代码
- **AAPL** - 苹果公司
- **TSLA** - 特斯拉
- **NVDA** - 英伟达
- *更多股票数据可通过修改 `stock_data.json` 添加*

## 📁 项目结构

```
a2ui_sample/
├── agent/
│   ├── README.md          # 项目文档
│   ├── .env.example       # 环境变量模板
│   ├── stock_data.json    # 模拟股票数据
│   └── pyproject.toml     # 项目配置
└── ...
```

## ⚠️ 注意事项

- 📊 **数据源**: 使用本地 `stock_data.json` 模拟数据，非实时股票数据
- 📝 **调试**: LLM 原始输出会保存到 `llm_raw_response.txt` 文件
- 🌐 **网络**: 服务默认运行在 `localhost:10004`，仅限本地访问
- 🔗 **依赖**: 确保 `../../A2UI/a2a_agents/python/a2ui_agent` 路径存在

## 🔧 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| **API 密钥错误** | `.env` 文件中 `GEMINI_API_KEY` 无效或缺失 | 检查 API 密钥是否正确，访问 [Google AI Studio](https://aistudio.google.com/apikey) 重新获取 |
| **依赖找不到** | `a2ui-agent` 路径不正确 | 检查 `pyproject.toml` 中 `a2ui-agent` 的 path 配置 |
| **端口被占用** | 10004 端口已被其他程序使用 | 使用 `--port <新端口号>` 指定其他端口 |
| **依赖安装失败** | UV 版本不兼容或网络问题 | 运行 `uv sync --refresh` 重新安装依赖 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目遵循与 A2UI 相同的许可证。
