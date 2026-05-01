import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Digital Health Dashboard")

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>实时健康监控</title>
    <style>
        body{font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#f0f2f5; padding:40px; color:#333}
        .container{max-width:800px; margin:0 auto; background:white; padding:30px; border-radius:15px; box-shadow:0 4px 12px rgba(0,0,0,0.1)}
        .grid{display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px; margin-top:20px}
        .card{background:#fafafa; padding:20px; border-radius:10px; border-top:5px solid #007bff; text-align:center}
        .label{font-size:14px; color:#666; margin-bottom:10px}
        .value{font-size:22px; font-weight:bold}
        .happy{color:#28a745} .sad{color:#dc3545} .neutral{color:#6c757d}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 实时状态监测</h1>
        <div class="grid">
            <div class="card"><div class="label">当前应用</div><div id="app" class="value">加载中...</div></div>
            <div class="card"><div class="label">使用时长</div><div id="dur" class="value">0 秒</div></div>
            <div class="card"><div class="label">心理表情</div><div id="emo" class="value">检测中...</div></div>
        </div>
    </div>
    <script>
        async function update() {
            try {
                const res = await fetch('http://localhost:8000/api/data');
                const d = await res.json();
                document.getElementById('app').innerText = d.app;
                document.getElementById('dur').innerText = d.duration + ' 秒';
                const e = document.getElementById('emo');
                e.innerText = d.emotion;
                e.className = 'value ' + (d.emotion === 'happy' ? 'happy' : (d.emotion === 'sad' ? 'sad' : 'neutral'));
            } catch(e) { console.error("连接失败", e); }
        }
        setInterval(update, 2000);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)