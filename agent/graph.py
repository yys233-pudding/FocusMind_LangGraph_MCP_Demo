"""
LangGraph Agent Workflow
state -> judge_node (LLM decision) -> set_alert (update state)
"""
import asyncio
import json
import os
import time
import re
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import sys
from dotenv import load_dotenv

load_dotenv()

# ======================
# LLM Initialization (MiniMax)
# ======================
llm = ChatOpenAI(
    model="minimax-m2.7",
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.chat/v1",
    temperature=0.1,
    timeout=30
)

# ======================
# LangGraph State Definition
# ======================
class AgentState(TypedDict):
    current_app: str
    today_usage_seconds: int
    emotion: str
    is_entertainment: bool
    alert: bool
    msg: str
    need_alert: bool
    mcp_tool_called: bool

# ======================
# Alert Threshold Config
# ======================
USAGE_THRESHOLD_SECONDS = 240  # 4 minutes

# ======================
# MCP Client
# ======================
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "..", "server", "mcp_server_run.py")

async def call_mcp_tool(name: str, arguments: dict) -> bool:
    """Call MCP tool (new connection each time)"""
    try:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[MCP_SERVER_PATH]
        )

        stdio_transport = stdio_client(server_params)
        read, write = await stdio_transport.__aenter__()
        session = ClientSession(read, write)
        await session.initialize()

        try:
            await session.call_tool(
                name=name,
                arguments=arguments,
                tool_call_id=f"{name}-{time.time()}"
            )
            print(f"[OK] MCP {name} called successfully")
            return True
        finally:
            await session.__aexit__(None, None, None)
            await stdio_transport.__aexit__(None, None, None)
    except Exception as e:
        print(f"[FAIL] MCP {name} call failed: {e}")
        return False

# ======================
# LangGraph Nodes
# ======================
async def judge_node(state: AgentState) -> AgentState:
    """
    judge_node: LLM decides whether to send alert
    """
    print(f"\n{'='*50}")
    print(f"[JUDGE] Analyzing user state")
    print(f"{'='*50}")

    current_app = state.get("current_app", "Unknown")
    duration = state.get("today_usage_seconds", 0)
    emotion = state.get("emotion", "neutral")
    is_ent = state.get("is_entertainment", False)

    # LLM Decision
    prompt = f"""You are a user health assistant. Current user state:
- Current app: {current_app}
- Usage duration: {duration}s ({duration//60}m{duration%60}s)
- User emotion: {emotion}
- Entertainment app: {'Yes' if is_ent else 'No'}

Rules:
1. Entertainment app + happy/warm emotion -> alert
2. Duration > {USAGE_THRESHOLD_SECONDS} seconds -> alert
3. tired/sad/angry emotion -> alert

Return JSON only, no other text:
{{"need_alert": true/false, "alert": true/false, "msg": "alert message (max 30 chars)"}}"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # Parse JSON
        alert_msg = ""
        need_alert = False

        json_match = re.search(r'\{[^}]+\}', content)
        if json_match:
            try:
                result = json.loads(json_match.group())
                need_alert = result.get("need_alert", False)
                alert_msg = result.get("msg", "")
            except:
                pass

        print(f"[LLM] Decision: need_alert={need_alert}")
        if alert_msg:
            print(f"[LLM] Suggestion: {alert_msg}")

        # If alert needed, call MCP tool
        if need_alert and alert_msg:
            print(f"[AGENT] Calling MCP send_alert_to_frontend")
            try:
                # Push directly to frontend (reliable)
                await push_alert_to_webserver(alert_msg, emotion, current_app)

                # Also call MCP to get emotion matrix for console
                mcp_success = await call_mcp_alert_tool(
                    agent_msg=alert_msg,
                    agent_emotion=emotion,
                    current_app=current_app
                )
                print(f"[MCP] Tool result: {'Success' if mcp_success else 'Failed'}")
            except Exception as e:
                print(f"[ERROR] MCP call exception: {e}")
                import traceback
                traceback.print_exc()

        return {
            **state,
            "need_alert": need_alert,
            "alert": need_alert,
            "msg": alert_msg,
            "mcp_tool_called": need_alert
        }
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        # Fallback to rules
        alert = is_ent and emotion == "happy" or duration > USAGE_THRESHOLD_SECONDS or emotion == "tired"
        alert_msg = "Take a break!" if alert else ""
        return {**state, "need_alert": alert, "alert": alert, "msg": alert_msg, "mcp_tool_called": False}

async def push_alert_to_webserver(agent_msg: str, agent_emotion: str, current_app: str):
    """Push alert to frontend web_server directly"""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                "http://localhost:8001/api/set_agent_result",
                json={
                    "alert": True,
                    "agent_msg": agent_msg,
                    "alert_emotion": agent_emotion,
                    "user_emotion": agent_emotion,
                    "current_app": current_app
                },
                timeout=aiohttp.ClientTimeout(total=3)
            )
            print(f"[OK] Pushed to frontend: {agent_msg}")
    except Exception as e:
        print(f"[FAIL] Push to frontend failed: {e}")

async def call_mcp_alert_tool(agent_msg: str, agent_emotion: str, current_app: str) -> bool:
    """Call MCP send_alert_to_frontend via stdio"""
    print(f"[MCP] Starting call...")
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, MCP_SERVER_PATH,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # MCP JSON-RPC init request
        init_request = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {"name": "agent", "version": "1.0.0"}
            }
        }) + "\n"

        # Send tool call request
        tool_request = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "send_alert_to_frontend",
                "arguments": {
                    "agent_msg": agent_msg,
                    "agent_emotion": agent_emotion,
                    "current_app": current_app
                }
            }
        }) + "\n"

        print(f"[MCP] Sending request...")
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=(init_request + tool_request).encode()),
            timeout=10.0
        )

        output = stdout.decode()
        print(f"[MCP] Response: {output[:200]}...")

        # Print emotion matrix
        emotion_matrix = {
            "happy": [" [ ^   ^ ] ", " [   v   ] ", " [  ___  ] "],
            "sad": [" [ _   _ ] ", " [   .   ] ", " [  ---  ] "],
            "warn": [" [ !   ! ] ", " [   ^   ] ", " [  ~~~  ] "],
            "tired": [" [ =   = ] ", " [   ..  ] ", " [  ___  ] "],
            "angry": [" [ >   < ] ", " [   ##  ] ", " [  ===  ] "]
        }
        matrix = emotion_matrix.get(agent_emotion, emotion_matrix["happy"])
        print("\n" + "="*30)
        for line in matrix:
            print(line.center(30))
        print(f"\n[ALERT] {agent_msg}")
        print("="*30)

        return True
    except asyncio.TimeoutError:
        print(f"[FAIL] MCP call timeout (10s)")
        return False
    except Exception as e:
        print(f"[FAIL] MCP tool call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def set_alert_state(state: AgentState) -> AgentState:
    """
    set_alert_node: Set alert state (only updates state, does not send alert)
    Alert is already sent in judge_node
    """
    if not state.get("need_alert"):
        return state

    # Set alert state for recovery tracking
    agent_context.is_alerting = True
    agent_context.last_alert_app = state.get("entertainment_key", state.get("current_app", ""))
    agent_context.last_alert_time = time.time()

    return state

# ======================
# LangGraph Workflow
# ======================
workflow = StateGraph(AgentState)

workflow.add_node("judge", judge_node)
workflow.add_node("set_alert", set_alert_state)

workflow.set_entry_point("judge")

def should_alert(state: AgentState) -> str:
    return "set_alert" if state.get("need_alert") else END

workflow.add_conditional_edges("judge", should_alert)
workflow.add_edge("set_alert", END)

graph = workflow.compile()

# ======================
# Global State Tracking (cross-workflow)
# ======================
class AgentContext:
    def __init__(self):
        self.last_alert_app = ""
        self.last_alert_time = 0
        self.alert_cooldown = 60
        self.is_alerting = False
        self.alert_recovery_threshold = 30  # Auto-recover after 30s or app switch

    async def check_and_recover(self, state: dict, push_recovery: bool = True):
        """Check if recovery is needed"""
        current_app = state.get("current_app", "")
        ent_key = state.get("entertainment_key", current_app)
        duration = state.get("today_usage_seconds", 0)
        emotion = state.get("emotion", "neutral")

        should_recover = False

        if self.is_alerting:
            if ent_key != self.last_alert_app:
                print(f"[RECOVER] App switched {self.last_alert_app} -> {ent_key}")
                should_recover = True
            elif time.time() - self.last_alert_time > self.alert_recovery_threshold:
                if duration < USAGE_THRESHOLD_SECONDS and emotion not in ["tired", "sad", "angry"]:
                    print(f"[RECOVER] Threshold exceeded, state normal")
                    should_recover = True

            if should_recover and push_recovery:
                await self.push_recovery_to_frontend()

        return should_recover

    async def push_recovery_to_frontend(self):
        """Push recovery state to frontend"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    "http://localhost:8001/api/set_agent_result",
                    json={
                        "alert": False,
                        "agent_msg": "Keep it up, stay focused!",
                        "alert_emotion": "happy"
                    },
                    timeout=aiohttp.ClientTimeout(total=3)
                )
                print(f"[OK] Recovery state pushed")
        except Exception as e:
            print(f"[FAIL] Recovery push failed: {e}")
        self.is_alerting = False
        self.last_alert_time = 0

agent_context = AgentContext()

# ======================
# Main Loop
# ======================
async def run_agent():
    """Run Agent workflow (loop decision)"""
    print("LangGraph Agent Started")
    print("=" * 50)
    print("Workflow: state -> judge_node -> set_alert")
    print("Recovery: app switch / 60s timeout / state normal")
    print("=" * 50)

    while True:
        try:
            with open("data/current_state.json", "r") as f:
                state = json.load(f)

            print(f"\n[{time.strftime('%H:%M:%S')}] Reading state:")
            print(f"   app={state.get('current_app')}")
            print(f"   duration={state.get('today_usage_seconds')}s, emotion={state.get('emotion')}, is_ent={state.get('is_entertainment')}")

            await agent_context.check_and_recover(state)

            initial_state: AgentState = {
                "current_app": state.get("current_app", "Unknown"),
                "today_usage_seconds": state.get("today_usage_seconds", 0),
                "emotion": state.get("emotion", "neutral"),
                "is_entertainment": state.get("is_entertainment", False),
                "alert": False,
                "msg": "",
                "need_alert": False
            }

            current_time = time.time()
            in_cooldown = (current_time - agent_context.last_alert_time) < agent_context.alert_cooldown

            if in_cooldown:
                print(f"[WAIT] Cooldown ({agent_context.alert_cooldown}s), elapsed {current_time - agent_context.last_alert_time:.0f}s")
                initial_state["need_alert"] = False

            final_state = await graph.ainvoke(initial_state)

            print(f"[DONE] need_alert={final_state.get('need_alert')}, alert={final_state.get('alert')}")

            await asyncio.sleep(2)

        except Exception as e:
            print(f"[ERROR] Agent exception: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_agent())
