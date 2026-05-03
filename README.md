<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App Usage Monitor | 应用使用监控系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Microsoft YaHei";
            max-width: 960px;
            margin: 0 auto;
            padding: 40px 24px;
            background: #fff;
            color: #24292e;
            line-height: 1.7;
        }
        .top-bar {
            position: sticky;
            top: 0;
            background: #fff;
            padding: 12px 0;
            border-bottom: 1px solid #e1e4e8;
            margin-bottom: 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }
        .top-bar h1 {
            font-size: 18px;
            font-weight: 600;
            color: #24292e;
        }
        .lang-switch {
            display: flex;
            gap: 4px;
            background: #f6f8fa;
            padding: 4px;
            border-radius: 6px;
        }
        .lang-switch button {
            padding: 6px 14px;
            border: none;
            background: transparent;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            color: #444;
            transition: all 0.15s;
        }
        .lang-switch button:hover {
            color: #24292e;
        }
        .lang-switch button.active {
            background: #fff;
            color: #24292e;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .section {
            margin: 36px 0;
        }
        .section-title {
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e1e4e8;
            color: #24292e;
        }
        .section-title-zh {
            margin-left: 12px;
            font-size: 16px;
            font-weight: 400;
            color: #666;
        }
        p {
            margin: 12px 0;
            color: #24292e;
        }
        .desc {
            color: #586069;
            font-size: 15px;
        }
        pre {
            background: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
            margin: 16px 0;
            border: 1px solid #e1e4e8;
        }
        code {
            background: #f6f8fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
            color: #24292e;
        }
        ul {
            margin: 12px 0;
            padding-left: 24px;
        }
        li {
            margin: 6px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
        }
        th, td {
            text-align: left;
            padding: 10px 14px;
            border: 1px solid #e1e4e8;
        }
        th {
            background: #f6f8fa;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background: #fafafa;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin: 16px 0;
        }
        .card {
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 16px;
            background: #fafafa;
        }
        .card h4 {
            margin: 0 0 8px;
            font-size: 14px;
            color: #0366d6;
        }
        .card .file {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }
        .card p {
            margin: 0;
            font-size: 13px;
            color: #586069;
        }
        .badge-group {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 12px 0;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-blue { background: #ddf4ff; color: #0969da; }
        .badge-green { background: #dafbe1; color: #1a7f37; }
        .badge-orange { background: #fff3cd; color: #9a6700; }
        .badge-purple { background: #fbefff; color: #8250df; }
        .note {
            background: #fff8c5;
            border-left: 4px solid #fcc419;
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin: 16px 0;
            font-size: 14px;
        }
        .divider {
            height: 1px;
            background: #e1e4e8;
            margin: 32px 0;
        }
        .content-en, .content-zh {
            display: none;
        }
        .content-en.active, .content-zh.active {
            display: block;
        }
        footer {
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid #e1e4e8;
            text-align: center;
            color: #666;
            font-size: 13px;
        }
        @media (max-width: 640px) {
            .grid-2 { grid-template-columns: 1fr; }
            .top-bar { flex-direction: column; gap: 12px; align-items: flex-start; }
        }
    </style>
</head>
<body>

<div class="top-bar">
    <h1>App Usage Monitor</h1>
    <div class="lang-switch">
        <button class="active" id="btn-en" onclick="setLang('en')">EN</button>
        <button id="btn-zh" onclick="setLang('zh')">中文</button>
    </div>
</div>

<!-- English -->
<div class="content-en active" id="content-en">
    <div class="section">
        <h2 class="section-title">Overview</h2>
        <p>An intelligent app usage monitoring system built with LangGraph and Model Context Protocol (MCP), combining emotion recognition and app usage tracking to provide healthy digital life recommendations.</p>
    </div>

    <div class="section">
        <h2 class="section-title">Project Structure</h2>
        <pre>LangGraph_MCP_demo/
├── main.py                 # Main data collection loop
├── agent/
│   └── graph.py            # LangGraph workflow (judge -> set_alert)
├── collector/
│   └── monitor.py          # RealTimeMonitor - emotion & usage tracking
├── server/
│   ├── mcp_server_run.py   # MCP Server (stdio interface)
│   └── web_server.py       # FastAPI server + web frontend
├── data/
│   ├── current_state.json  # Shared state file
│   └── usage_stats.db     # SQLite usage database
└── README.md</pre>
    </div>

    <div class="section">
        <h2 class="section-title">Architecture</h2>
        <pre>main.py (collector)
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
        <h2 class="section-title">Alert Rules</h2>
        <table>
            <tr><th>#</th><th>Rule</th><th>Trigger</th></tr>
            <tr><td>1</td><td>Entertainment app + happy emotion</td><td>Alert</td></tr>
            <tr><td>2</td><td>Usage duration > 4 minutes</td><td>Alert</td></tr>
            <tr><td>3</td><td>tired/sad/angry emotion</td><td>Alert</td></tr>
        </table>
    </div>

    <div class="section">
        <h2 class="section-title">Quick Start</h2>
        <p><strong>Terminal 1 - Web Server (frontend):</strong></p>
        <pre>python server/web_server.py
# Open http://127.0.0.1:8001</pre>
        <p><strong>Terminal 2 - Agent:</strong></p>
        <pre>python main.py</pre>
    </div>

    <div class="section">
        <h2 class="section-title">Requirements</h2>
        <ul>
            <li>Python 3.9+</li>
            <li>Windows OS (window listening, beep alerts)</li>
            <li>Webcam (emotion recognition)</li>
            <li>MiniMax API key in <code>.env</code></li>
        </ul>
        <p class="desc">Install: <code>pip install -r requirements.txt</code></p>
    </div>

    <div class="section">
        <h2 class="section-title">Components</h2>
        <div class="grid-2">
            <div class="card">
                <h4>1. RealTimeMonitor</h4>
                <div class="file">collector/monitor.py</div>
                <p>Window listener tracks foreground switches. Emotion capture via DeepFace settles every 5s. Usage stats persisted to SQLite.</p>
            </div>
            <div class="card">
                <h4>2. LangGraph Agent</h4>
                <div class="file">agent/graph.py</div>
                <p><strong>judge_node</strong>: LLM decides alert. <strong>set_alert_node</strong>: Updates state after recovery check. HTTP push + MCP stdio.</p>
            </div>
            <div class="card">
                <h4>3. MCP Server</h4>
                <div class="file">server/mcp_server_run.py</div>
                <p>Tools: get_user_usage_state, judge_rest_alert, send_alert_to_frontend. Uses stdio interface.</p>
            </div>
            <div class="card">
                <h4>4. Web Server</h4>
                <div class="file">server/web_server.py</div>
                <p>FastAPI on port 8001. Serves frontend with real-time emotion matrix display and LLM-generated messages.</p>
            </div>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">API Endpoints</h2>
        <table>
            <tr><th>Endpoint</th><th>Method</th><th>Description</th></tr>
            <tr><td><code>/</code></td><td>GET</td><td>Frontend dashboard</td></tr>
            <tr><td><code>/api/update</code></td><td>POST</td><td>Receive main.py data</td></tr>
            <tr><td><code>/api/set_agent_result</code></td><td>POST</td><td>Receive agent/MCP alert data</td></tr>
            <tr><td><code>/api/data</code></td><td>GET</td><td>Combined state for polling</td></tr>
        </table>
    </div>

    <div class="section">
        <h2 class="section-title">Tech Stack</h2>
        <div class="badge-group">
            <span class="badge badge-blue">LangGraph</span>
            <span class="badge badge-blue">FastAPI</span>
            <span class="badge badge-green">DeepFace</span>
            <span class="badge badge-green">OpenCV</span>
            <span class="badge badge-orange">MCP</span>
            <span class="badge badge-orange">MiniMax LLM</span>
            <span class="badge badge-purple">pywin32</span>
            <span class="badge badge-green">SQLite</span>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">Privacy</h2>
        <div class="note">All emotion and usage data is processed locally only. Camera data is never uploaded to the cloud.</div>
    </div>

    <footer>MIT License</footer>
</div>

<!-- Chinese -->
<div class="content-zh" id="content-zh">
    <div class="section">
        <h2 class="section-title">项目简介</h2>
        <p>基于 LangGraph 和 Model Context Protocol (MCP) 的智能应用使用监控系统，结合表情识别和应用使用追踪，为用户提供健康的数字生活建议。</p>
    </div>

    <div class="section">
        <h2 class="section-title">项目结构</h2>
        <pre>LangGraph_MCP_demo/
├── main.py                 # 主程序入口
├── agent/
│   └── graph.py            # LangGraph 工作流 (judge -> set_alert)
├── collector/
│   └── monitor.py          # RealTimeMonitor - 表情与应用监控
├── server/
│   ├── mcp_server_run.py   # MCP Server (stdio 接口)
│   └── web_server.py       # FastAPI 服务器 + 网页前端
├── data/
│   ├── current_state.json  # 共享状态文件
│   └── usage_stats.db     # SQLite 使用数据库
└── README.md</pre>
    </div>

    <div class="section">
        <h2 class="section-title">架构图</h2>
        <pre>main.py (数据采集)
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
        <h2 class="section-title">提醒规则</h2>
        <table>
            <tr><th>#</th><th>规则</th><th>触发条件</th></tr>
            <tr><td>1</td><td>娱乐应用 + 快乐表情</td><td>触发提醒</td></tr>
            <tr><td>2</td><td>使用时长超过 4 分钟</td><td>触发提醒</td></tr>
            <tr><td>3</td><td>tired/sad/angry 表情</td><td>触发提醒</td></tr>
        </table>
    </div>

    <div class="section">
        <h2 class="section-title">快速开始</h2>
        <p><strong>终端 1 - Web 服务器（前端）:</strong></p>
        <pre>python server/web_server.py
# 打开 http://127.0.0.1:8001</pre>
        <p><strong>终端 2 - Agent:</strong></p>
        <pre>python main.py</pre>
    </div>

    <div class="section">
        <h2 class="section-title">系统要求</h2>
        <ul>
            <li>Python 3.9+</li>
            <li>Windows 系统（窗口监听、提示音）</li>
            <li>摄像头（表情识别）</li>
            <li>.env 中配置 MiniMax API Key</li>
        </ul>
        <p class="desc">安装: <code>pip install -r requirements.txt</code></p>
    </div>

    <div class="section">
        <h2 class="section-title">核心组件</h2>
        <div class="grid-2">
            <div class="card">
                <h4>1. RealTimeMonitor</h4>
                <div class="file">collector/monitor.py</div>
                <p>窗口监听器追踪前台切换。表情捕捉通过 DeepFace 每 5 秒结算一次。使用数据持久化到 SQLite。</p>
            </div>
            <div class="card">
                <h4>2. LangGraph Agent</h4>
                <div class="file">agent/graph.py</div>
                <p><strong>judge_node</strong>: LLM 决策是否提醒。<strong>set_alert_node</strong>: 恢复检查后更新状态。HTTP 推送 + MCP stdio。</p>
            </div>
            <div class="card">
                <h4>3. MCP Server</h4>
                <div class="file">server/mcp_server_run.py</div>
                <p>工具: get_user_usage_state, judge_rest_alert, send_alert_to_frontend。使用 stdio 接口。</p>
            </div>
            <div class="card">
                <h4>4. Web 服务器</h4>
                <div class="file">server/web_server.py</div>
                <p>FastAPI 运行在 8001 端口。前端实时显示表情矩阵和 LLM 生成的提醒消息。</p>
            </div>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">API 接口</h2>
        <table>
            <tr><th>端点</th><th>方法</th><th>说明</th></tr>
            <tr><td><code>/</code></td><td>GET</td><td>前端仪表盘</td></tr>
            <tr><td><code>/api/update</code></td><td>POST</td><td>接收 main.py 数据</td></tr>
            <tr><td><code>/api/set_agent_result</code></td><td>POST</td><td>接收 Agent/MCP 提醒数据</td></tr>
            <tr><td><code>/api/data</code></td><td>GET</td><td>组合状态用于轮询</td></tr>
        </table>
    </div>

    <div class="section">
        <h2 class="section-title">技术栈</h2>
        <div class="badge-group">
            <span class="badge badge-blue">LangGraph</span>
            <span class="badge badge-blue">FastAPI</span>
            <span class="badge badge-green">DeepFace</span>
            <span class="badge badge-green">OpenCV</span>
            <span class="badge badge-orange">MCP</span>
            <span class="badge badge-orange">MiniMax LLM</span>
            <span class="badge badge-purple">pywin32</span>
            <span class="badge badge-green">SQLite</span>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">隐私说明</h2>
        <div class="note">所有数据仅在本地处理。摄像头数据不会上传到云端。</div>
    </div>

    <footer>MIT License</footer>
</div>

<script>
function setLang(lang) {
    document.getElementById('content-en').classList.toggle('active', lang === 'en');
    document.getElementById('content-zh').classList.toggle('active', lang === 'zh');
    document.getElementById('btn-en').classList.toggle('active', lang === 'en');
    document.getElementById('btn-zh').classList.toggle('active', lang === 'zh');
    document.documentElement.lang = lang;
}
</script>

</body>
</html>