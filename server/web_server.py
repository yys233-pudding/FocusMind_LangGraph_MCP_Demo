from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import winsound
import time

app = FastAPI(title="AI Entertainment Time Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_status = {
    "app": "Waiting for data...",
    "duration": 0,
    "emotion": "Detecting...",
    "is_entertainment": False,
    "agent_alert": False,
    "agent_msg": "",
    "alert_emotion": "neutral",
    "user_emotion": "neutral",
    "last_alert_time": ""
}

EMOTION_MATRIX = {
    "happy": [
        " [ ^   ^ ] ",
        " [   v   ] ",
        " [  ___  ] "
    ],
    "sad": [
        " [ _   _ ] ",
        " [   .   ] ",
        " [  ---  ] "
    ],
    "neutral": [
        " [ -   - ] ",
        " [   .   ] ",
        " [  ---  ] "
    ],
    "warn": [
        " [ !   ! ] ",
        " [   ^   ] ",
        " [  ~~~  ] "
    ],
    "tired": [
        " [ =   = ] ",
        " [   ..  ] ",
        " [  ___  ] "
    ]
}

def play_alert_sound(emotion: str):
    try:
        frequencies = {"happy": 784, "sad": 262, "warn": 880, "tired": 392, "default": 523}
        freq = frequencies.get(emotion, frequencies["default"])
        winsound.Beep(freq, 300)
    except:
        pass

def print_emotion_matrix(emotion: str, msg: str):
    matrix = EMOTION_MATRIX.get(emotion, EMOTION_MATRIX["neutral"])
    print("\n" + "="*30)
    for line in matrix:
        print(line.center(30))
    print(f"\n[ALERT] {msg}")
    print("="*30 + "\n")

@app.post("/api/update")
async def update_status(req: Request):
    data = await req.json()
    global latest_status
    latest_status["app"] = data.get("app", latest_status["app"])
    latest_status["duration"] = data.get("duration", latest_status["duration"])
    latest_status["emotion"] = data.get("emotion", latest_status["emotion"])
    latest_status["is_entertainment"] = data.get("is_entertainment", latest_status["is_entertainment"])
    return {"status": "ok"}

@app.post("/api/set_agent_result")
async def set_agent_result(req: Request):
    try:
        data = await req.json()
    except:
        return {"status": "error", "msg": "Invalid JSON"}
    global latest_status

    latest_status["agent_alert"] = data.get("alert", False)
    latest_status["agent_msg"] = data.get("agent_msg", "")
    latest_status["alert_emotion"] = data.get("alert_emotion", "happy")

    if "current_app" in data:
        latest_status["app"] = data.get("current_app", latest_status["app"])
    if "today_usage_seconds" in data:
        latest_status["duration"] = data.get("today_usage_seconds", latest_status["duration"])
    if "user_emotion" in data:
        latest_status["user_emotion"] = data.get("user_emotion", latest_status["user_emotion"])
    if "is_entertainment" in data:
        latest_status["is_entertainment"] = data.get("is_entertainment", latest_status["is_entertainment"])

    if data.get("alert"):
        latest_status["last_alert_time"] = time.strftime("%H:%M:%S")

    return {"status":"ok"}

@app.get("/api/data")
async def get_data():
    return latest_status

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Study Assistant</title>
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
    <div class="card">
        <h2>Real-time Status</h2>
        <div class="grid">
            <div class="item">
                <span class="label">Current App:</span>
                <span id="app">-</span>
            </div>
            <div class="item">
                <span class="label">Duration:</span>
                <span id="duration">0</span> s
            </div>
            <div class="item">
                <span class="label">User Emotion:</span>
                <span id="emotion">-</span>
            </div>
            <div class="item">
                <span class="label">Entertainment:</span>
                <span id="is_ent" class="normal">No</span>
            </div>
            <div class="item">
                <span class="label">AI Status:</span>
                <span id="agent_status" class="normal">Normal</span>
            </div>
            <div class="item">
                <span class="label">Last Alert:</span>
                <span id="last_alert">-</span>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>AI Emotion</h2>
        <div id="faceArea" class="face-box">
 [ ^   ^ ]
 [   v   ]
 [  ___  ]
        </div>
    </div>

    <div class="card">
        <h2>AI Reminder</h2>
        <div id="chatArea" class="chat-box">
Keep studying, stay focused!
        </div>
    </div>
</div>

<script>
const DEFAULT_FACE = ` [ ^   ^ ]
 [   v   ]
 [  ___  ]`;
const DEFAULT_TEXT = "Keep studying, stay focused!";

const FACE_MAP = {
    warn: ` [ !   ! ]
 [   ^   ]
 [  ~~~  ]`,
    happy: ` [ ^   ^ ]
 [   v   ]
 [  ___  ]`,
    tired: ` [ =   = ]
 [   ..  ]
 [  ___  ]`,
    sad: ` [ _   _ ]
 [   .   ]
 [  ---  ]`
};

async function update() {
    try {
        const res = await fetch("http://127.0.0.1:8001/api/data");
        const data = await res.json();

        document.getElementById("app").innerText = data.app || "Unknown";
        document.getElementById("duration").innerText = data.duration || 0;
        document.getElementById("emotion").innerText = data.emotion || "Unknown";
        document.getElementById("last_alert").innerText = data.last_alert_time || "-";

        const is_ent = document.getElementById("is_ent");
        is_ent.innerText = data.is_entertainment ? "Yes" : "No";
        is_ent.className = data.is_entertainment ? "warn" : "normal";

        const status = document.getElementById("agent_status");
        const face = document.getElementById("faceArea");
        const chat = document.getElementById("chatArea");

        if (data.agent_alert) {
            status.innerText = "Alerting";
            status.className = "warn";
            face.className = "face-box face-alert";
            chat.className = "chat-box chat-alert";
            const alertEmotion = data.alert_emotion || data.emotion || "warn";
            face.innerText = FACE_MAP[alertEmotion] || FACE_MAP.warn;
            chat.innerText = data.agent_msg || "Take a break!";
        } else {
            status.innerText = "Normal";
            status.className = "normal";
            face.className = "face-box";
            chat.className = "chat-box";
            face.innerText = DEFAULT_FACE;
            chat.innerText = DEFAULT_TEXT;
        }

    } catch (e) {
        console.log("Waiting for backend connection...");
    }
}

setInterval(update, 1000);
</script>

</body>
</html>
"""

if __name__ == "__main__":
    print("Web frontend started: http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)