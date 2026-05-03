
import asyncio
import json
import os
import time
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 创建 MCP Server 实例
server = Server("usage-monitor-server")

# 存储最新状态（从 main.py 的推送获取）
latest_state = {
    "current_app": "未知",
    "today_usage_seconds": 0,
    "emotion": "neutral",
    "is_entertainment": False,
    "timestamp": ""
}

# 提醒阈值配置
USAGE_THRESHOLD_SECONDS = 300  # 5分钟

# 娱乐应用关键词
ENTERTAINMENT_APPS = [
    "哔哩哔哩", "bilibili", "Steam", "微信", "QQ",
    "爱奇艺", "腾讯视频", "优酷", "YouTube", "Netflix", "Spotify"
]

# 表情矩阵
EMOTION_MATRIX = {
    "happy": [" [ ^   ^ ] ", " [   v   ] ", " [  ___  ] "],
    "sad": [" [ _   _ ] ", " [   .   ] ", " [  ---  ] "],
    "neutral": [" [ -   - ] ", " [   .   ] ", " [  ---  ] "],
    "warn": [" [ !   ! ] ", " [   ^   ] ", " [  ~~~  ] "],
    "tired": [" [ ≡   ≡ ] ", " [   ..  ] ", " [  ___  ] "],
    "angry": [" [ >   < ] ", " [   ##  ] ", " [  ===  ] "]
}

def is_entertainment(app_name: str) -> bool:
    app_lower = app_name.lower()
    for keyword in ENTERTAINMENT_APPS:
        if keyword.lower() in app_lower:
            return True
    return False

def judge_alert(state: dict) -> dict:
    """判断是否需要提醒"""
    current_app = state.get("current_app", "未知")
    duration = state.get("today_usage_seconds", 0)
    emotion = state.get("emotion", "neutral")
    is_ent = state.get("is_entertainment", False)

    alert = False
    msg = ""

    # 条件1: 娱乐应用 + happy表情
    if is_ent and emotion == "happy":
        alert = True
        msg = f"检测到您在 {current_app} 过度兴奋，请注意休息！"
    # 条件2: 使用时长超过5分钟
    elif duration > USAGE_THRESHOLD_SECONDS:
        alert = True
        msg = f"{current_app} 已连续使用 {duration // 60}分{duration % 60}秒，超过5分钟了，休息一下吧！"
    # 条件3: tired 表情
    elif emotion == "tired":
        alert = True
        msg = f"您看起来有些疲惫，{current_app} 已使用 {duration} 秒，该休息了！"

    return {
        "alert": alert,
        "msg": msg,
        "emotion": emotion if alert else "happy"
    }

@server.list_tools()
async def list_tools():
    """列出所有可用工具"""
    return [
        Tool(
            name="get_user_usage_state",
            description="获取用户当前使用状态",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="judge_rest_alert",
            description="根据状态判断是否需要提醒",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_app": {"type": "string", "description": "当前应用名称"},
                    "duration": {"type": "integer", "description": "使用时长(秒)"},
                    "emotion": {"type": "string", "description": "当前表情"},
                    "is_entertainment": {"type": "boolean", "description": "是否为娱乐应用"}
                },
                "required": ["current_app", "duration", "emotion", "is_entertainment"]
            }
        ),
        Tool(
            name="send_alert_to_frontend",
            description="发送提醒到前端显示",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_msg": {"type": "string", "description": "LLM生成的提醒文案"},
                    "agent_emotion": {"type": "string", "description": "用户当前表情类型"},
                    "current_app": {"type": "string", "description": "当前应用"}
                },
                "required": ["agent_msg", "agent_emotion", "current_app"]
            }
        )
    ]

async def push_alert_to_web_server(result: dict):
    """推送提醒结果到 web_server"""
    import aiohttp
    import sys
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                "http://localhost:8001/api/set_agent_result",
                json={
                    "alert": result["alert"],
                    "msg": result["msg"],
                    "emotion": result.get("emotion", "happy")
                },
                timeout=aiohttp.ClientTimeout(total=3)
            )
            # 写入 stderr 日志（不污染 stdout）
            sys.stderr.write(f"MCP推送成功: {resp.status}\n")
            sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"MCP推送失败: {e}\n")
        sys.stderr.flush()

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """处理工具调用"""
    global latest_state

    if name == "get_user_usage_state":
        # 从文件读取最新状态（由 main.py 更新）
        try:
            with open("data/current_state.json", "r") as f:
                latest_state = json.load(f)
        except:
            pass

        return [TextContent(
            type="text",
            text=json.dumps(latest_state, ensure_ascii=False)
        )]

    elif name == "judge_rest_alert":
        # 使用传入的参数进行判断
        state = {
            "current_app": arguments.get("current_app", "未知"),
            "today_usage_seconds": arguments.get("duration", 0),
            "emotion": arguments.get("emotion", "neutral"),
            "is_entertainment": arguments.get("is_entertainment", False)
        }

        result = judge_alert(state)

        # 如果需要提醒，推送到 web_server
        if result["alert"]:
            await push_alert_to_web_server(result)

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "send_alert_to_frontend":
        agent_msg = arguments.get("agent_msg", "休息一下吧！")
        agent_emotion = arguments.get("agent_emotion", "happy")

        # 从文件读取最新的用户使用数据（由 main.py 更新）
        try:
            with open("data/current_state.json", "r") as f:
                user_state = json.load(f)
        except:
            user_state = {}

        # 推送到前端（包含用户数据和LLM生成的数据）
        result = {
            "alert": True,
            "agent_msg": agent_msg,
            "alert_emotion": agent_emotion,
            "user_emotion": user_state.get("emotion", "neutral"),
            "current_app": user_state.get("current_app", ""),
            "today_usage_seconds": user_state.get("today_usage_seconds", 0),
            "is_entertainment": user_state.get("is_entertainment", False)
        }
        await push_alert_to_web_server(result)

        # 获取表情矩阵
        emotion_matrix = EMOTION_MATRIX.get(agent_emotion, EMOTION_MATRIX["happy"])

        # 返回结果（包含表情矩阵）
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "agent_msg": agent_msg,
                "agent_emotion": agent_emotion,
                "matrix": emotion_matrix,
                "printed": True
            }, ensure_ascii=False)
        )]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """启动 MCP Server"""
    # 初始化状态文件
    os.makedirs("data", exist_ok=True)
    with open("data/current_state.json", "w") as f:
        json.dump(latest_state, f, ensure_ascii=False)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())