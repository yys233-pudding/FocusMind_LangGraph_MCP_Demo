from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="AI 娱乐时长监控助手")

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 学习助手</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: "Microsoft YaHei", sans-serif;
        }

        body {
            background: linear-gradient(135deg, #f0f4ff, #d9e2ff);
            padding: 30px 20px;
        }

        .container {
            max-width: 700px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }

        h2 {
            color: #2d3748;
            margin-bottom: 16px;
            font-size: 20px;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            font-size: 15px;
        }

        .item {
            padding: 8px 0;
        }

        .label {
            font-weight: bold;
            color: #4a5568;
            margin-right: 6px;
        }

        .warn {
            color: #e53e3e;
            font-weight: bold;
        }

        .normal {
            color: #38a169;
            font-weight: bold;
        }

        /* 表情矩阵框 */
        .face-box {
            width: 100%;
            min-height: 160px;
            background: #f7fafc;
            border-radius: 12px;
            padding: 20px;
            font-family: monospace;
            font-size: 16px;
            white-space: pre;
            border: 2px dashed #cbd5e0;
            text-align: center;
            line-height: 1.5;
        }

        /* 对话框 */
        .chat-box {
            width: 100%;
            min-height: 80px;
            background: #edf2f7;
            border-radius: 12px;
            padding: 16px;
            font-size: 16px;
            color: #2d3748;
            line-height: 1.6;
            white-space: pre-wrap;
        }

        .chat-alert {
            background: #fff5f5;
            color: #c53030;
            border: 1px solid #feb2b2;
        }

        .face-alert {
            border-color: #fc8181;
            background: #fff0f0;
        }
    </style>
</head>
<body>

<div class="container">
    <!-- 实时监控面板 -->
    <div class="card">
        <h2>🎯 实时使用状态</h2>
        <div class="grid">
            <div class="item">
                <span class="label">当前应用：</span>
                <span id="app">-</span>
            </div>
            <div class="item">
                <span class="label">已用时长：</span>
                <span id="duration">0</span> 秒
            </div>
            <div class="item">
                <span class="label">用户情绪：</span>
                <span id="emotion">-</span>
            </div>
            <div class="item">
                <span class="label">娱乐应用：</span>
                <span id="is_ent" class="normal">否</span>
            </div>
            <div class="item">
                <span class="label">AI 状态：</span>
                <span id="agent_status" class="normal">正常</span>
            </div>
            <div class="item">
                <span class="label">上次提醒：</span>
                <span id="last_alert">-</span>
            </div>
        </div>
    </div>

    <!-- 表情矩阵框 -->
    <div class="card">
        <h2>😊 AI 表情</h2>
        <div id="faceArea" class="face-box">
 [ ^   ^ ] 
 [   v   ] 
 [  ___  ]
        </div>
    </div>

    <!-- AI 对话框 -->
    <div class="card">
        <h2>💬 AI 提醒</h2>
        <div id="chatArea" class="chat-box">
好好学习，天天向上～
        </div>
    </div>
</div>

<script>
// 默认表情
const DEFAULT_FACE = ` [ ^   ^ ] 
 [   v   ] 
 [  ___  ]`;
const DEFAULT_TEXT = "好好学习，天天向上～";

// 表情矩阵库
const FACE_MAP = {
    warn: ` [ !   ! ] 
 [   ^   ] 
 [  ~~~  ]`,
    happy: ` [ ^   ^ ] 
 [   v   ] 
 [  ___  ]`,
    tired: ` [ ≡   ≡ ] 
 [   ..  ] 
 [  ___  ]`,
    sad: ` [ _   _ ] 
 [   .   ] 
 [  ---  ]`
};

// 每秒刷新数据
async function update() {
    try {
        const res = await fetch("http://127.0.0.1:8000/api/data");
        const data = await res.json();

        // 填充面板
        document.getElementById("app").innerText = data.app || "未知";
        document.getElementById("duration").innerText = data.duration || 0;
        document.getElementById("emotion").innerText = data.emotion || "未知";
        document.getElementById("last_alert").innerText = data.last_alert_time || "-";

        const is_ent = document.getElementById("is_ent");
        is_ent.innerText = data.is_entertainment ? "是" : "否";
        is_ent.className = data.is_entertainment ? "warn" : "normal";

        const status = document.getElementById("agent_status");
        const face = document.getElementById("faceArea");
        const chat = document.getElementById("chatArea");

        if (data.agent_alert) {
            status.innerText = "⚠️ 提醒中";
            status.className = "warn";
            face.className = "face-box face-alert";
            chat.className = "chat-box chat-alert";
            face.innerText = FACE_MAP.warn;
            chat.innerText = data.agent_msg || "休息一下吧！";
        } else {
            status.innerText = "✅ 正常";
            status.className = "normal";
            face.className = "face-box";
            chat.className = "chat-box";
            face.innerText = DEFAULT_FACE;
            chat.innerText = DEFAULT_TEXT;
        }

    } catch (e) {
        console.log("等待后端连接...");
    }
}

setInterval(update, 1000);
</script>

</body>
</html>
"""

if __name__ == "__main__":
    print("✅ 网页前端已启动：http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)