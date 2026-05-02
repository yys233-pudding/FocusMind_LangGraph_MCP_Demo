from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import winsound
import time

app = FastAPI(title="MCP Data Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态，给前端展示
latest_status = {
    "app": "等待数据...",
    "duration": 0,
    "emotion": "检测中...",
    "is_entertainment": False,
    "agent_alert": False,
    "agent_msg": "",
    "last_alert_time": ""
}

# ASCII 表情矩阵
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
        " [ ≡   ≡ ] ",
        " [   ..  ] ",
        " [  ___  ] "
    ]
}

# Windows 提示音配置
ALERT_SOUNDS = {
    "happy": (784, 300),
    "sad": (262, 400),
    "warn": (880, 200),
    "tired": (392, 500),
    "default": (523, 300)
}

def play_alert_sound(emotion: str):
    """播放系统提示音"""
    try:
        freq, dur = ALERT_SOUNDS.get(emotion, ALERT_SOUNDS["default"])
        winsound.Beep(freq, dur)
        time.sleep(0.1)
        if emotion == "warn":
            winsound.Beep(freq + 200, 200)
    except:
        pass

def print_emotion_matrix(emotion: str, msg: str):
    """控制台打印表情矩阵"""
    matrix = EMOTION_MATRIX.get(emotion, EMOTION_MATRIX["neutral"])
    print("\n" + "="*30)
    for line in matrix:
        print(line.center(30))
    print(f"\n📢 提醒：{msg}")
    print("="*30 + "\n")

@app.post("/api/update")
async def update_status(req: Request):
    """兼容原有接口（可选保留）"""
    data = await req.json()
    global latest_status
    latest_status["app"] = data.get("app", latest_status["app"])
    latest_status["duration"] = data.get("duration", latest_status["duration"])
    latest_status["emotion"] = data.get("emotion", latest_status["emotion"])
    latest_status["is_entertainment"] = data.get("is_entertainment", latest_status["is_entertainment"])
    return {"status": "ok"}

@app.post("/api/set_agent_result")
async def set_agent_result(req: Request):
    """接收 MCP + LLM 的决策结果"""
    data = await req.json()
    global latest_status
    latest_status["agent_alert"] = data.get("alert", False)
    latest_status["agent_msg"] = data.get("msg", "")
    if data.get("alert"):
        latest_status["last_alert_time"] = time.strftime("%H:%M:%S")
        emo = data.get("emotion", "warn")
        # 打印表情 + 播放提示音
        print_emotion_matrix(emo, data.get("msg",""))
        play_alert_sound(emo)
    return {"status":"ok"}

@app.get("/api/data")
async def get_data():
    """向前端提供实时状态"""
    return latest_status

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)