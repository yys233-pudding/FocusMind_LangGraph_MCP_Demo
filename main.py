import asyncio
import json
import os
import requests
from collector.monitor import RealTimeMonitor

monitor = RealTimeMonitor()

async def main():
    print("✅ 数据采集 Agent 已启动。请保持窗口激活并面对摄像头。")

    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)

    while True:
        try:
            state = monitor.get_fused_state()

            # 修正：对应 monitor.py 中的 key
            app = state["current_app"]
            duration = state["today_usage_seconds"]
            emotion = state["emotion"]
            is_entertainment = state["is_entertainment"]

            # 1. 保存到文件供 MCP Server 读取
            state_for_mcp = {
                "current_app": app,
                "today_usage_seconds": duration,
                "emotion": emotion,
                "is_entertainment": is_entertainment,
                "timestamp": state["timestamp"]
            }
            with open("data/current_state.json", "w") as f:
                json.dump(state_for_mcp, f, ensure_ascii=False)

            # 2. 推送给 web_server (端口8001)
            try:
                requests.post(
                    "http://localhost:8001/api/update",
                    json={
                        "app": app,
                        "duration": duration,
                        "emotion": emotion,
                        "is_entertainment": is_entertainment
                    },
                    timeout=2
                )
                print(f"DEBUG: {app} | {duration}s | {emotion} | 娱乐应用: {is_entertainment}")
            except Exception as e:
                print(f"❌ 推送失败 (请检查 server/web_server.py 是否启动): {e}")

        except Exception as e:
            print(f"⚠️ 循环异常: {e}")

        await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        monitor.stop()