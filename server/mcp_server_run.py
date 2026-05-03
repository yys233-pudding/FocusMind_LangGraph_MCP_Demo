import asyncio
import json
import os
import time
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("usage-monitor-server")

latest_state = {
    "current_app": "Unknown",
    "today_usage_seconds": 0,
    "emotion": "neutral",
    "is_entertainment": False,
    "timestamp": ""
}

USAGE_THRESHOLD_SECONDS = 300

ENTERTAINMENT_APPS = [
    "bilibili", "Steam", "WeChat", "QQ",
    "iQiyi", "Tencent Video", "Youku", "YouTube", "Netflix", "Spotify"
]

EMOTION_MATRIX = {
    "happy": [" [ ^   ^ ] ", " [   v   ] ", " [  ___  ] "],
    "sad": [" [ _   _ ] ", " [   .   ] ", " [  ---  ] "],
    "neutral": [" [ -   - ] ", " [   .   ] ", " [  ---  ] "],
    "warn": [" [ !   ! ] ", " [   ^   ] ", " [  ~~~  ] "],
    "tired": [" [ =   = ] ", " [   ..  ] ", " [  ___  ] "],
    "angry": [" [ >   < ] ", " [   ##  ] ", " [  ===  ] "]
}

def is_entertainment(app_name: str) -> bool:
    app_lower = app_name.lower()
    for keyword in ENTERTAINMENT_APPS:
        if keyword.lower() in app_lower:
            return True
    return False

def judge_alert(state: dict) -> dict:
    current_app = state.get("current_app", "Unknown")
    duration = state.get("today_usage_seconds", 0)
    emotion = state.get("emotion", "neutral")
    is_ent = state.get("is_entertainment", False)

    alert = False
    msg = ""

    if is_ent and emotion == "happy":
        alert = True
        msg = f"Over-excited on {current_app}, take a break!"
    elif duration > USAGE_THRESHOLD_SECONDS:
        alert = True
        msg = f"{current_app} used for {duration // 60}m{duration % 60}s, over 5 min - rest time!"
    elif emotion == "tired":
        alert = True
        msg = f"You look tired, {current_app} used for {duration}s, time for a break!"

    return {
        "alert": alert,
        "msg": msg,
        "emotion": emotion if alert else "happy"
    }

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_user_usage_state",
            description="Get user's current usage state",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="judge_rest_alert",
            description="Judge whether to alert based on state",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_app": {"type": "string", "description": "Current app name"},
                    "duration": {"type": "integer", "description": "Usage duration (seconds)"},
                    "emotion": {"type": "string", "description": "Current emotion"},
                    "is_entertainment": {"type": "boolean", "description": "Is entertainment app"}
                },
                "required": ["current_app", "duration", "emotion", "is_entertainment"]
            }
        ),
        Tool(
            name="send_alert_to_frontend",
            description="Send alert to frontend display",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_msg": {"type": "string", "description": "LLM-generated alert message"},
                    "agent_emotion": {"type": "string", "description": "User's current emotion type"},
                    "current_app": {"type": "string", "description": "Current app"}
                },
                "required": ["agent_msg", "agent_emotion", "current_app"]
            }
        )
    ]

async def push_alert_to_web_server(result: dict):
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
            sys.stderr.write(f"MCP push success: {resp.status}\n")
            sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"MCP push failed: {e}\n")
        sys.stderr.flush()

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    global latest_state

    if name == "get_user_usage_state":
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
        state = {
            "current_app": arguments.get("current_app", "Unknown"),
            "today_usage_seconds": arguments.get("duration", 0),
            "emotion": arguments.get("emotion", "neutral"),
            "is_entertainment": arguments.get("is_entertainment", False)
        }

        result = judge_alert(state)

        if result["alert"]:
            await push_alert_to_web_server(result)

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]

    elif name == "send_alert_to_frontend":
        agent_msg = arguments.get("agent_msg", "Take a break!")
        agent_emotion = arguments.get("agent_emotion", "happy")

        try:
            with open("data/current_state.json", "r") as f:
                user_state = json.load(f)
        except:
            user_state = {}

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

        emotion_matrix = EMOTION_MATRIX.get(agent_emotion, EMOTION_MATRIX["happy"])

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