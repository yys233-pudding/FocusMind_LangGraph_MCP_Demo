# 应用使用监控系统 - LangGraph + MCP Demo

一个基于 LangGraph 和 Model Context Protocol (MCP) 的智能应用使用监控系统，结合表情识别和应用使用追踪，为用户提供健康的数字生活建议。

## 🎯 项目功能

### 核心功能
- **表情识别**：通过 DeepFace 库实时识别用户表情，智能统计表情变化
- **应用监控**：监听窗口切换事件，记录应用使用时长和历史数据
- **智能提醒**：基于表情和使用时长的双重条件触发提醒
- **数据持久化**：将应用使用数据保存到本地 JSON 文件
- **前端仪表板**：实时展示当前应用、表情和使用统计信息

### 提醒规则
1. **娱乐应用 + 快乐表情**：检测到在娱乐应用中过度兴奋时提醒
2. **使用时长超过5分钟**：连续使用单个应用超过5分钟时提醒
3. **多种表情矩阵**：不同场景下显示不同的表情 ASCII 艺术

## 📦 项目结构

```
LangGraph_MCP_demo/
├── main.py                 # 主程序入口
├── agent/
│   └── graph.py           # LangGraph Agent 工作流定义
├── collector/
│   └── monitor.py         # 表情和应用使用数据收集器
├── server/
│   ├── mcp_server.py      # MCP Server（提醒服务）
│   └── web_server.py      # Web 服务器和前端
├── app_usage.json         # 应用使用数据（自动生成）
└── README.md
```

## 🔧 依赖安装

### 系统要求
- Python 3.9+
- Windows OS（用于窗口监听和声音提醒）
- 摄像头（用于表情识别）

### 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install langgraph langchain langchain-community
pip install fastapi uvicorn
pip install deepface opencv-python
pip install pywin32
pip install python-dotenv
pip install mcp
pip install minimax-sdk
```

### 环境变量配置

创建 `.env` 文件并配置 MiniMax API：

```
MINIMAX_API_KEY=your_api_key_here
MINIMAX_GROUP_ID=your_group_id_here
```

## 🚀 使用方法

### 方式1：运行完整系统（推荐）

**终端1 - 启动 MCP 服务器**（提醒服务）：
```bash
python server/mcp_server.py
# 启动在 http://localhost:8000
```

**终端2 - 启动 Web 服务器**（前端仪表板）：
```bash
python server/web_server.py
# 启动在 http://localhost:8001
# 打开浏览器访问: http://localhost:8001
```

**终端3 - 启动 Agent**（核心监控程序）：
```bash
python main.py
# 每15秒检查一次用户状态并作出判断
```

打开浏览器访问 `http://localhost:8001` 查看实时仪表板。

### 方式2：仅运行 Agent（无前端）

```bash
python main.py
```

## 📊 核心组件说明

### 1. RealTimeMonitor（数据收集器）

**文件**：`collector/monitor.py`

**主要功能**：
- 表情采集：每秒识别一次，累积3个样本以上才输出（防止跳变）
- 窗口监听：监听应用切换，自动统计使用时长
- 数据融合：生成包含表情、应用、使用时长等的完整状态 JSON
- 数据持久化：保存每个应用的今日使用总时长

**关键参数**：
```python
MIN_EMOTION_SAMPLES = 3       # 最小表情样本数
USAGE_THRESHOLD_SECONDS = 300 # 5分钟提醒阈值
```

**融合状态 JSON 示例**：
```json
{
  "emotion": "happy",
  "app": "Bilibili",
  "time": "14:30:45",
  "current_usage_seconds": 320,
  "current_usage_formatted": "5分20秒",
  "today_total_seconds": 2400,
  "today_total_formatted": "40分",
  "is_entertainment": true,
  "usage_threshold_exceeded": true,
  "history_states": [...]
}
```

### 2. Agent 工作流（LangGraph）

**文件**：`agent/graph.py`

**工作流程**：
1. **judge_node**：判断是否需要触发提醒
   - 条件1：娱乐App + happy表情
   - 条件2：使用时长 > 5分钟

2. **alert_node**：通过 MCP 调用远程提醒服务

**触发提醒消息示例**：
```
[happy 表情矩阵]
别太开心了！Bilibili 已使用5分20秒，该休息一下了！

或

[tired 表情矩阵]
'Steam' 已连续使用5分20秒，超过5分钟限制
```

### 3. MCP 服务器（提醒服务）

**文件**：`server/mcp_server.py`

**功能**：
- 接收 Agent 的提醒请求
- 打印表情 ASCII 矩阵
- 发出系统声音提醒（Windows）

**支持的提醒类型**：
```
warn:  [ !   ! ]  快速双声调
       [   ^   ]  
       [  ---  ]  

tired: [ -   - ]  低音调提醒
       [   .   ]  
       [  ~~~  ]  

happy: [ ^   ^ ]  上升音调提醒
       [   v   ]  
       [  ___  ]  
```

### 4. Web 服务器 & 前端

**文件**：`server/web_server.py`

**API 接口**：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端仪表板页面 |
| `/api/status` | GET | 获取当前实时状态 |
| `/api/stats` | GET | 获取今日应用统计 |
| `/api/history` | GET | 获取历史状态 |

**前端特性**：
- 实时显示当前应用和表情
- 使用时长进度条（5分钟为满）
- 今日应用统计表
- 自动5秒刷新
- 响应式设计

## 📝 配置调整

### 修改表情样本阈值
在 `collector/monitor.py` 中修改：
```python
MIN_EMOTION_SAMPLES = 3  # 增加此值可降低误触发
```

### 修改提醒时长阈值
```python
USAGE_THRESHOLD_SECONDS = 300  # 改为 600 表示10分钟
```

### 添加/修改娱乐应用列表
```python
ENTERTAINMENT_APPS = ["Bilibili", "Steam", "Video", "Chrome", ...]
```

### 修改检查间隔
在 `main.py` 中修改：
```python
await asyncio.sleep(15)  # 改为其他秒数
```

## 🐛 常见问题

### 1. "No module named 'deepface'"
```bash
pip install deepface
```

### 2. "No cameras available"
- 检查摄像头是否被其他应用占用
- 在系统设置中给 Python 权限

### 3. MCP 连接错误
- 确保 MCP 服务器运行在 8000 端口
- 检查防火墙设置

### 4. 表情识别频繁失败
- 增加 `MIN_EMOTION_SAMPLES` 值
- 确保摄像头光线充足

## 📚 技术栈

- **LangGraph**：Agent 工作流编排
- **FastAPI**：Web 服务框架
- **DeepFace**：表情识别引擎
- **OpenCV**：视频采集处理
- **MCP (Model Context Protocol)**：远程服务通信
- **pywin32**：Windows 系统集成

## 📄 数据格式

### app_usage.json
```json
{
  "date": "2024-05-01",
  "apps": {
    "Bilibili": 2400,
    "Steam": 1800,
    "Chrome": 3600,
    "Desktop": 500
  }
}
```

## 🔐 隐私说明

- 所有表情和应用数据**仅在本地处理**
- 摄像头数据不上传到云端
- 应用使用数据本地存储在 `app_usage.json`

## 📧 许可证

MIT License