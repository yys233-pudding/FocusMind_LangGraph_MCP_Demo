# App Usage Monitor

[English](#english) | [中文](#中文)

---

# English

## Overview

An intelligent app usage monitoring system built with **LangGraph** and **Model Context Protocol (MCP)**, combining emotion recognition and app usage tracking to provide healthy digital life recommendations.

## Project Structure

```
LangGraph_MCP_demo/
├── main.py                    # Main data collection loop
├── agent/
│   └── graph.py               # LangGraph workflow (judge -> set_alert)
├── collector/
│   └── monitor.py             # RealTimeMonitor - emotion & usage tracking
├── server/
│   ├── mcp_server_run.py     # MCP Server (stdio interface)
│   └── web_server.py          # FastAPI server + web frontend
├── data/
│   ├── current_state.json    # Shared state file
│   └── usage_stats.db        # SQLite usage database
└── README.md
```

## Architecture

```
main.py (collector)
    │
    ├── writes current_state.json
    ├── pushes to /api/update
    │
    ▼
web_server.py (port 8001)
    │
    └── /api/data → frontend polling
          │
agent/graph.py (LangGraph Agent)
    │
    ├── reads current_state.json
    ├── LLM decision (MiniMax)
    │
    ├── push_alert_to_webserver() → /api/set_agent_result
    └── call_mcp_alert_tool() → mcp_server_run.py (stdio)
```

## Alert Rules

| # | Rule | Trigger |
|---|------|---------|
| 1 | Entertainment app + happy emotion | Alert |
| 2 | Usage duration > 4 minutes | Alert |
| 3 | tired/sad/angry emotion | Alert |

## Quick Start

**Terminal 1 - Web Server (frontend):**

```bash
python server/web_server.py
# Open http://127.0.0.1:8001
```

**Terminal 2 - Agent:**

```bash
python main.py
```

## Requirements

- Python 3.9+
- Windows OS (window listening, beep alerts)
- Webcam (emotion recognition)
- MiniMax API key in `.env`

**Install:** `pip install -r requirements.txt`

## Components

### 1. RealTimeMonitor (`collector/monitor.py`)

Window listener tracks foreground switches. Emotion capture via DeepFace settles every 5s. Usage stats persisted to SQLite with entertainment grouping.

### 2. LangGraph Agent (`agent/graph.py`)

- **judge_node**: LLM decides alert
- **set_alert_node**: Updates state after recovery check
- Direct HTTP push to frontend + MCP stdio for console output

### 3. MCP Server (`server/mcp_server_run.py`)

Tools: `get_user_usage_state`, `judge_rest_alert`, `send_alert_to_frontend`. Uses stdio interface.

### 4. Web Server (`server/web_server.py`)

FastAPI on port 8001. Serves frontend with real-time emotion matrix display and LLM-generated messages.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Frontend dashboard |
| `/api/update` | POST | Receive main.py data |
| `/api/set_agent_result` | POST | Receive agent/MCP alert data |
| `/api/data` | GET | Combined state for polling |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Agent | LangGraph |
| Web | FastAPI |
| Emotion | DeepFace |
| Video | OpenCV |
| Protocol | MCP |
| LLM | MiniMax |
| Windows | pywin32 |
| Database | SQLite |

## Privacy

All emotion and usage data is processed **locally only**. Camera data is never uploaded to the cloud.

---

# 中文

## 项目简介

基于 **LangGraph** 和 **Model Context Protocol (MCP)** 的智能应用使用监控系统，结合表情识别和应用使用追踪，为用户提供健康的数字生活建议。

## 项目结构

```
LangGraph_MCP_demo/
├── main.py                    # 主程序入口
├── agent/
│   └── graph.py              # LangGraph 工作流 (judge -> set_alert)
├── collector/
│   └── monitor.py            # RealTimeMonitor - 表情与应用监控
├── server/
│   ├── mcp_server_run.py     # MCP Server (stdio 接口)
│   └── web_server.py         # FastAPI 服务器 + 网页前端
├── data/
│   ├── current_state.json   # 共享状态文件
│   └── usage_stats.db       # SQLite 使用数据库
└── README.md
```

## 架构流程

```
main.py (数据采集)
    │
    ├── 写入 current_state.json
    ├── 推送至 /api/update
    │
    ▼
web_server.py (端口 8001)
    │
    └── /api/data → 前端轮询
          │
agent/graph.py (LangGraph Agent)
    │
    ├── 读取 current_state.json
    ├── LLM 决策 (MiniMax)
    │
    ├── push_alert_to_webserver() → /api/set_agent_result
    └── call_mcp_alert_tool() → mcp_server_run.py (stdio)
```

## 提醒规则

| # | 规则 | 触发条件 |
|---|------|----------|
| 1 | 娱乐应用 + 快乐表情 | 触发提醒 |
| 2 | 使用时长超过 4 分钟 | 触发提醒 |
| 3 | tired/sad/angry 表情 | 触发提醒 |

## 快速启动

**终端 1 - 启动 Web 服务（前端）：**

```bash
python server/web_server.py
# 打开浏览器访问 http://127.0.0.1:8001
```

**终端 2 - 启动采集 & Agent：**

```bash
python main.py
```

## 系统要求

- Python 3.9+
- Windows 系统（窗口监听、提示音）
- 摄像头（表情识别）
- `.env` 配置 MiniMax API Key

**安装依赖：** `pip install -r requirements.txt`

## 核心组件

### 1. RealTimeMonitor (`collector/monitor.py`)

窗口监听器追踪前台应用切换。DeepFace 表情识别每 5 秒结算一次。使用数据存入 SQLite 并按娱乐应用分组。

### 2. LangGraph Agent (`agent/graph.py`)

- **judge_node**：LLM 判断是否提醒
- **set_alert_node**：恢复检查后更新状态
- 直接 HTTP 推送到前端 + MCP stdio 控制台输出

### 3. MCP Server (`server/mcp_server_run.py`)

工具：`get_user_usage_state`、`judge_rest_alert`、`send_alert_to_frontend`。使用 stdio 接口。

### 4. Web 服务器 (`server/web_server.py`)

FastAPI 端口 8001。提供仪表盘、实时表情矩阵、AI 提醒展示。

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 仪表盘首页 |
| `/api/update` | POST | 接收采集数据 |
| `/api/set_agent_result` | POST | 接收 Agent 提醒 |
| `/api/data` | GET | 前端获取完整状态 |

## 技术栈

| 组件 | 技术 |
|------|------|
| Agent | LangGraph |
| Web | FastAPI |
| 表情 | DeepFace |
| 视频 | OpenCV |
| 协议 | MCP |
| LLM | MiniMax |
| Windows | pywin32 |
| 数据库 | SQLite |

## 隐私说明

所有数据**仅在本地处理**，摄像头数据不会上传到任何云端。

---

[Back to Top](#app-usage-monitor) | [返回顶部](#app-usage-monitor)

MIT License
