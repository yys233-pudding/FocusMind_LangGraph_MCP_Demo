import asyncio
import requests
from collector.monitor import RealTimeMonitor

monitor = RealTimeMonitor()

async def main():
    print("✅ 数据采集 Agent 已启动。请保持窗口激活并面对摄像头。")
    while True:
        try:
            state = monitor.get_fused_state()
            
            # 修正：对应 monitor.py 中的 key[cite: 4]
            app = state["current_app"]
            duration = state["today_usage_seconds"] 
            emotion = state["emotion"]
            is_entertainment = state["is_entertainment"]  # 新增：获取娱乐应用标识

            # 推送给中转服务器
            try:
                requests.post(
                    "http://localhost:8000/api/update",
                    json={
                        "app": app,
                        "duration": duration,
                        "emotion": emotion,
                        "is_entertainment": is_entertainment  # 新增：传递娱乐应用标识
                    },
                    timeout=2
                )
                print(f"DEBUG: {app} | {duration}s | {emotion} | 娱乐应用: {is_entertainment}")
            except Exception as e:
                print(f"❌ 推送失败 (请检查 server.py 是否启动): {e}")

        except Exception as e:
            print(f"⚠️ 循环异常: {e}")

        await asyncio.sleep(2) # 每2秒推送一次最新状态

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        monitor.stop()