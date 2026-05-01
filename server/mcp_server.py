from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI(title="MCP Data Server")

# 必须添加 CORS，否则前端 8001 无法访问 8000 的接口[cite: 2, 3]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_status = {
    "app": "等待数据...",
    "duration": 0,
    "emotion": "检测中...",
    "last_alert": ""
}

@app.post("/api/update")
async def update_status(req: Request):
    data = await req.json()
    global latest_status
    latest_status["app"] = data.get("app", latest_status["app"])
    latest_status["duration"] = data.get("duration", latest_status["duration"])
    latest_status["emotion"] = data.get("emotion", latest_status["emotion"])
    return {"status": "ok"}

@app.get("/api/data")
async def get_data():
    return latest_status

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)