<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App Usage Monitor - LangGraph + MCP Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #fafafa;
            color: #333;
            line-height: 1.6;
        }
        .lang-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 8px;
            z-index: 100;
        }
        .lang-toggle button {
            padding: 6px 16px;
            border: 1px solid #ccc;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        .lang-toggle button:hover {
            background: #f0f0f0;
        }
        .lang-toggle button.active {
            background: #4a90d9;
            color: white;
            border-color: #4a90d9;
        }
        h1 {
            font-size: 28px;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        h2 {
            font-size: 20px;
            margin: 30px 0 15px;
            color: #34495e;
            border-bottom: 2px solid #4a90d9;
            padding-bottom: 5px;
        }
        h3 {
            font-size: 16px;
            margin: 20px 0 10px;
            color: #555;
        }
        p {
            margin: 10px 0;
        }
        .subtitle {
            color: #666;
            font-size: 16px;
            margin-bottom: 30px;
        }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            border: 1px solid #ddd;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 14px;
        }
        ul {
            margin: 10px 0;
            padding-left: 25px;
        }
        li {
            margin: 5px 0;
        }
        .lang-content {
            display: none;
        }
        .lang-content.active {
            display: block;
        }
        .section {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 15px 0;
        }
        .item {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
        }
        .item h4 {
            margin: 0 0 8px;
            color: #4a90d9;
        }
        .item p {
            margin: 0;
            font-size: 14px;
            color: #666;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            text-align: left;
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f4f4f4;
            font-weight: 600;
        }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 12px;
            margin-right: 5px;
        }
        .badge-green {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .badge-blue {
            background: #e3f2fd;
            color: #1565c0;
        }
        .badge-orange {
            background: #fff3e0;
            color: #ef6c00;
        }
        .note {
            background: #fff8e1;
            border-left: 4px solid #ffc107;
            padding: 12px 15px;
            border-radius: 0 8px 8px 0;
            margin: 15px 0;
        }
        footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 14px;
        }
    </style>
</head>
<body>

<div class="lang-toggle">
    <button class="active" onclick="switchLang('en')">English</button>
    <button onclick="switchLang('zh')">中文</button>
</div>

<!-- English Content -->
<div class="lang-content active" id="en">
    <h1>App Usage Monitor</h1>
    <p class="subtitle">LangGraph + MCP Demo</p>

    <div class="section">
        <h2>Project Overview</h2>
        <p>An intelligent app usage monitoring system built with LangGraph and Model Context Protocol (MCP), combining emotion recognition and app usage tracking to provide healthy digital life recommendations.</p>
    </div>

    <div class="section">
        <h2>Project Structure</h2>
        <pre>
LangGraph_MCP_demo/
├── main.py                    # Main data collection loop
├── agent/
│   └── graph.py               # LangGraph workflow (judge -> set_alert)
├── collector/
│   └── monitor.py             # RealTimeMonitor - emotion & usage tracking
├── server/
│   ├── mcp_server_run.py      # MCP Server (stdio interface)
│   └── web_server.py          # FastAPI server + web frontend
├── data/
│   ├── current_state.json     # Shared state file
│   └── usage_stats.db        # SQLite usage database
└── README.md</pre>
    </div>

    <div class="section">
        <h2>Architecture</h2>
        <pre>
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
    └── call_mcp_alert_tool() → mcp_server_run.py (stdio)</pre>
    </div>

    <div class="section">
        <h2>Alert Rules</h2>
        <ul>
            <li><strong>Entertainment app + happy emotion</strong> → alert</li>
            <li><strong>Usage duration > 4 minutes</strong> → alert</li>
            <li><strong>tired/sad/angry emotion</strong> → alert</li>
        </ul>
    </div>

    <div class="section">
        <h2>Quick Start</h2>
        <p><strong>Terminal 1 - Web Server (frontend)</strong>:</p>
        <pre>python server/web_server.py
# Open http://127.0.0.1:8001</pre>

        <p><strong>Terminal 2 - Agent (LangGraph)</strong>:</p>
        <pre>python main.py</pre>
    </div>

    <div class="section">
        <h2>Requirements</h2>
        <ul>
            <li>Python 3.9+</li>
            <li>Windows OS (window listening, beep alerts)</li>
            <li>Webcam (emotion recognition)</li>
            <li>MiniMax API key in <code>.env</code></li>
        </ul>

        <h3>Install Dependencies</h3>
        <pre>pip install -r requirements.txt</pre>

        <h3>Environment Variables</h3>
        <p>Create <code>.env</code>:</p>
        <pre>MINIMAX_API_KEY=your_api_key_here</pre>
    </div>

    <div class="section">
        <h2>Components</h2>

        <div class="grid">
            <div class="item">
                <h4>1. RealTimeMonitor</h4>
                <p><code>collector/monitor.py</code></p>
                <p>Window listener tracks foreground switches. Emotion capture via DeepFace settles every 5s. Usage stats persisted to SQLite with entertainment grouping.</p>
            </div>
            <div class="item">
                <h4>2. LangGraph Agent</h4>
                <p><code>agent/graph.py</code></p>
                <p><strong>judge_node</strong>: LLM decides alert. <strong>set_alert_node</strong>: Updates state after recovery check. Direct HTTP push to frontend + MCP stdio for console.</p>
            </div>
            <div class="item">
                <h4>3. MCP Server</h4>
                <p><code>server/mcp_server_run.py</code></p>
                <p>Provides tools: get_user_usage_state, judge_rest_alert, send_alert_to_frontend. Uses stdio interface.</p>
            </div>
            <div class="item">
                <h4>4. Web Server</h4>
                <p><code>server/web_server.py</code></p>
                <p>FastAPI on port 8001. Serves frontend with real-time emotion matrix display and LLM-generated messages.</p>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>API Endpoints</h2>
        <table>
            <tr><th>Endpoint</th><th>Method</th><th>Description</th></tr>
            <tr><td><code>/</code></td><td>GET</td><td>Frontend dashboard</td></tr>
            <tr><td><code>/api/update</code></td><td>POST</td><td>Receive main.py data</td></tr>
            <tr><td><code>/api/set_agent_result</code></td><td>POST</td><td>Receive agent/MCP alert data</td></tr>
            <tr><td><code>/api/data</code></td><td>GET</td><td>Combined state for polling</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Tech Stack</h2>
        <span class="badge badge-blue">LangGraph</span>
        <span class="badge badge-blue">FastAPI</span>
        <span class="badge badge-green">DeepFace</span>
        <span class="badge badge-green">OpenCV</span>
        <span class="badge badge-orange">MCP</span>
        <span class="badge badge-orange">MiniMax LLM</span>
        <span class="badge badge-blue">pywin32</span>
        <span class="badge badge-green">SQLite</span>
    </div>

    <div class="section">
        <h2>Privacy</h2>
        <div class="note">
            All emotion and usage data is processed locally only. Camera data is never uploaded to the cloud. Usage stats stored locally in SQLite.
        </div>
    </div>

    <footer>MIT License</footer>
</div>

<!-- Chinese Content -->
<div class="lang-content" id="zh">
    <h1>应用使用监控系统</h1>
    <p class="subtitle">LangGraph + MCP Demo</p>

    <div class="section">
        <h2>项目简介</h2>
        <p>基于 LangGraph 和 Model Context Protocol (MCP) 的智能应用使用监控系统，结合表情识别和应用使用追踪，为用户提供健康的数字生活建议。</p>
    </div>

    <div class="section">
        <h2>项目结构</h2>
        <pre>
LangGraph_MCP_demo/
├── main.py                    # 主程序入口
├── agent/
│   └── graph.py               # LangGraph 工作流 (judge -> set_alert)
├── collector/
│   └── monitor.py             # RealTimeMonitor - 表情与应用监控
├── server/
│   ├── mcp_server_run.py     # MCP Server (stdio 接口)
│   └── web_server.py         # FastAPI 服务器 + 网页前端
├── data/
│   ├── current_state.json    # 共享状态文件
│   └── usage_stats.db        # SQLite 使用数据库
└── README.md</pre>
    </div>

    <div class="section">
        <h2>架构图</h2>
        <pre>
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
    └── call_mcp_alert_tool() → mcp_server_run.py (stdio)</pre>
    </div>

    <div class="section">
        <h2>提醒规则</h2>
        <ul>
            <li><strong>娱乐应用 + 快乐表情</strong> → 触发提醒</li>
            <li><strong>使用时长超过 4 分钟</strong> → 触发提醒</li>
            <li><strong>tired/sad/angry 表情</strong> → 触发提醒</li>
        </ul>
    </div>

    <div class="section">
        <h2>快速开始</h2>
        <p><strong>终端 1 - Web 服务器（前端）</strong>：</p>
        <pre>python server/web_server.py
# 打开 http://127.0.0.1:8001</pre>

        <p><strong>终端 2 - Agent（LangGraph）</strong>：</p>
        <pre>python main.py</pre>
    </div>

    <div class="section">
        <h2>系统要求</h2>
        <ul>
            <li>Python 3.9+</li>
            <li>Windows 系统（窗口监听、提示音）</li>
            <li>摄像头（表情识别）</li>
            <li>.env 中配置 MiniMax API Key</li>
        </ul>

        <h3>安装依赖</h3>
        <pre>pip install -r requirements.txt</pre>

        <h3>环境变量</h3>
        <p>创建 <code>.env</code>：</p>
        <pre>MINIMAX_API_KEY=your_api_key_here</pre>
    </div>

    <div class="section">
        <h2>核心组件</h2>

        <div class="grid">
            <div class="item">
                <h4>1. RealTimeMonitor</h4>
                <p><code>collector/monitor.py</code></p>
                <p>窗口监听器追踪前台切换。表情捕捉通过 DeepFace 每 5 秒结算一次。使用数据通过娱乐分组持久化到 SQLite。</p>
            </div>
            <div class="item">
                <h4>2. LangGraph Agent</h4>
                <p><code>agent/graph.py</code></p>
                <p><strong>judge_node</strong>：LLM 决策是否提醒。<strong>set_alert_node</strong>：恢复检查后更新状态。直接 HTTP 推送到前端 + MCP stdio 控制台输出。</p>
            </div>
            <div class="item">
                <h4>3. MCP Server</h4>
                <p><code>server/mcp_server_run.py</code></p>
                <p>提供工具：get_user_usage_state、judge_rest_alert、send_alert_to_frontend。使用 stdio 接口。</p>
            </div>
            <div class="item">
                <h4>4. Web 服务器</h4>
                <p><code>server/web_server.py</code></p>
                <p>FastAPI 运行在 8001 端口。前端实时显示表情矩阵和 LLM 生成的提醒消息。</p>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>API 接口</h2>
        <table>
            <tr><th>端点</th><th>方法</th><th>说明</th></tr>
            <tr><td><code>/</code></td><td>GET</td><td>前端仪表盘</td></tr>
            <tr><td><code>/api/update</code></td><td>POST</td><td>接收 main.py 数据</td></tr>
            <tr><td><code>/api/set_agent_result</code></td><td>POST</td><td>接收 Agent/MCP 提醒数据</td></tr>
            <tr><td><code>/api/data</code></td><td>GET</td><td>组合状态用于轮询</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>技术栈</h2>
        <span class="badge badge-blue">LangGraph</span>
        <span class="badge badge-blue">FastAPI</span>
        <span class="badge badge-green">DeepFace</span>
        <span class="badge badge-green">OpenCV</span>
        <span class="badge badge-orange">MCP</span>
        <span class="badge badge-orange">MiniMax LLM</span>
        <span class="badge badge-blue">pywin32</span>
        <span class="badge badge-green">SQLite</span>
    </div>

    <div class="section">
        <h2>隐私说明</h2>
        <div class="note">
            所有表情和应用数据仅在本地处理。摄像头数据不会上传到云端。使用统计数据存储在本地 SQLite 数据库中。
        </div>
    </div>

    <footer>MIT License</footer>
</div>

<script>
function switchLang(lang) {
    document.querySelectorAll('.lang-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.lang-toggle button').forEach(btn => btn.classList.remove('active'));

    document.getElementById(lang).classList.add('active');
    document.querySelector(`.lang-toggle button[onclick="switchLang('${lang}')"]`).classList.add('active');

    document.documentElement.lang = lang;
}
</script>

</body>
</html>