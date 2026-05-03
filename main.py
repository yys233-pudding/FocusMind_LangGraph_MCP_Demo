import asyncio
import json
import os
import requests
from collector.monitor import RealTimeMonitor

monitor = RealTimeMonitor()

async def main():
    print("[OK] Data collection Agent started. Keep window active and face the camera.")

    os.makedirs("data", exist_ok=True)

    while True:
        try:
            state = monitor.get_fused_state()

            app = state["current_app"]
            duration = state["today_usage_seconds"]
            emotion = state["emotion"]
            is_entertainment = state["is_entertainment"]

            # 1. Save to file for MCP Server
            state_for_mcp = {
                "current_app": app,
                "today_usage_seconds": duration,
                "emotion": emotion,
                "is_entertainment": is_entertainment,
                "timestamp": state["timestamp"]
            }
            with open("data/current_state.json", "w") as f:
                json.dump(state_for_mcp, f, ensure_ascii=False)

            # 2. Push to web_server (port 8001)
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
                print(f"DEBUG: {app} | {duration}s | {emotion} | entertainment: {is_entertainment}")
            except Exception as e:
                print(f"[FAIL] Push failed (check if server/web_server.py is running): {e}")

        except Exception as e:
            print(f"[ERROR] Loop exception: {e}")

        await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        monitor.stop()