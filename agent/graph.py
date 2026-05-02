"""
LangGraph Agent 工作流
state → judge_node (LLM判断+决定是否调用MCP) → alert_node (执行MCP工具)
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
# LLM 初始化 (MiniMax)
# ======================
llm = ChatOpenAI(
    model="minimax-m2.7",
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.chat/v1",
    temperature=0.1,
    timeout=30
)

# ======================
# LangGraph State 定义
# ======================
class AgentState(TypedDict):
    current_app: str
    today_usage_seconds: int
    emotion: str
    is_entertainment: bool
    alert: bool
    msg: str
    need_alert: bool
    mcp_tool_called: bool  # MCP工具是否被调用

# ======================
# 提醒阈值配置
# ======================
USAGE_THRESHOLD_SECONDS = 240  # 4分钟

# ======================
# MCP 客户端
# ======================
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "..", "server", "mcp_server_run.py")

async def call_mcp_tool(name: str, arguments: dict) -> bool:
    """调用 MCP 工具（每次新建连接）"""
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
            print(f"✅ MCP {name} 调用成功")
            return True
        finally:
            await session.__aexit__(None, None, None)
            await stdio_transport.__aexit__(None, None, None)
    except Exception as e:
        print(f"❌ MCP {name} 调用失败: {e}")
        return False

# ======================
# LangGraph Nodes
# ======================
async def judge_node(state: AgentState) -> AgentState:
    """
    judge_node: LLM 判断是否需要提醒，并决定是否调用 MCP 工具
    """
    print(f"\n{'='*50}")
    print(f"🔍 Judge Node: LLM 分析用户状态")
    print(f"{'='*50}")

    current_app = state.get("current_app", "未知")
    duration = state.get("today_usage_seconds", 0)
    emotion = state.get("emotion", "neutral")
    is_ent = state.get("is_entertainment", False)

    # LLM 判断
    prompt = f"""你是用户健康使用助手。用户当前状态：
- 当前应用：{current_app}
- 使用时长：{duration}秒 ({duration//60}分{duration%60}秒)
- 用户情绪：{emotion}
- 是否娱乐应用：{'是' if is_ent else '否'}

规则：
1. 娱乐应用 + happy/warm表情 → 提醒
2. 时长超过 {USAGE_THRESHOLD_SECONDS} 秒 → 提醒
3. tired/sad/angry 表情 → 提醒

如果需要提醒，调用 MCP 工具 send_alert_to_frontend 发送提醒。
如果不需要提醒，返回普通回复。

请返回JSON格式（只有需要提醒时才调用工具）：
{{"need_alert": true/false, "alert": true/false, "msg": "提醒文案（不超过30字）"}}"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # 解析 JSON
        json_match = re.search(r'\{[^}]+\}', content)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(content)

        need_alert = result.get("need_alert", False)
        alert_msg = result.get("msg", "")  # LLM生成的提醒文案

        print(f"🤖 LLM 判断: need_alert={need_alert}, alert={result.get('alert')}")
        print(f"💬 LLM 建议: {alert_msg}")

        # 如果需要提醒，LLM 决定调用 MCP 工具
        if need_alert and alert_msg:
            print(f"📤 LLM 决定调用 MCP 工具 send_alert_to_frontend")
            try:
                # 传递完整的 LLM 生成数据
                mcp_success = await call_mcp_alert_tool(
                    agent_msg=alert_msg,      # LLM生成的提醒文案
                    agent_emotion=emotion,   # 用户当前表情
                    current_app=current_app
                )
                print(f"🔧 MCP 工具调用结果: {'成功' if mcp_success else '失败'}")
            except Exception as e:
                print(f"❌ MCP 调用异常: {e}")
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
        print(f"❌ LLM 调用失败: {e}")
        # LLM 失败时用规则兜底
        alert = is_ent and emotion == "happy" or duration > USAGE_THRESHOLD_SECONDS or emotion == "tired"
        alert_msg = "休息一下吧！" if alert else ""
        return {**state, "need_alert": alert, "alert": alert, "msg": alert_msg, "mcp_tool_called": False}

async def call_mcp_alert_tool(agent_msg: str, agent_emotion: str, current_app: str) -> bool:
    """通过 MCP stdio 调用 send_alert_to_frontend 工具"""
    print(f"📤 开始调用 MCP send_alert_to_frontend...")
    try:
        # 使用 asyncio.create_subprocess_exec 直接启动
        process = await asyncio.create_subprocess_exec(
            sys.executable, MCP_SERVER_PATH,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # MCP JSON-RPC 初始化请求
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

        # 发送工具调用请求
        tool_request = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "send_alert_to_frontend",
                "arguments": {
                    "agent_msg": agent_msg,           # LLM生成的提醒文案
                    "agent_emotion": agent_emotion,   # 用户当前表情
                    "current_app": current_app
                }
            }
        }) + "\n"

        print(f"📤 发送请求到 MCP...")
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=(init_request + tool_request).encode()),
            timeout=10.0
        )

        output = stdout.decode()
        print(f"📤 MCP 响应: {output[:200]}...")

        # 打印表情矩阵
        emotion_matrix = {
            "happy": [" [ ^   ^ ] ", " [   v   ] ", " [  ___  ] "],
            "sad": [" [ _   _ ] ", " [   .   ] ", " [  ---  ] "],
            "warn": [" [ !   ! ] ", " [   ^   ] ", " [  ~~~  ] "],
            "tired": [" [ ≡   ≡ ] ", " [   ..  ] ", " [  ___  ] "],
            "angry": [" [ >   < ] ", " [   ##  ] ", " [  ===  ] "]
        }
        matrix = emotion_matrix.get(agent_emotion, emotion_matrix["happy"])
        print("\n" + "="*30)
        for line in matrix:
            print(line.center(30))
        print(f"\n📢 {agent_msg}")
        print("="*30)

        return True
    except asyncio.TimeoutError:
        print(f"❌ MCP 调用超时（10秒）")
        return False
    except Exception as e:
        print(f"❌ MCP 工具调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def set_alert_state(state: AgentState) -> AgentState:
    """
    alert_node: 设置提醒状态（仅更新状态，不发送提醒）
    提醒已在 judge_node 中通过 MCP 发送
    """
    if not state.get("need_alert"):
        return state

    # 设置提醒状态用于恢复追踪
    agent_context.is_alerting = True
    agent_context.last_alert_app = state.get("entertainment_key", state.get("current_app", ""))
    agent_context.last_alert_time = time.time()

    return state

# ======================
# LangGraph 工作流
# ======================
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("judge", judge_node)
workflow.add_node("set_alert", set_alert_state)

# 设置入口点
workflow.set_entry_point("judge")

# judge 之后根据 need_alert 判断是否进入 set_alert
def should_alert(state: AgentState) -> str:
    return "set_alert" if state.get("need_alert") else END

workflow.add_conditional_edges("judge", should_alert)
workflow.add_edge("set_alert", END)

# 编译工作流
graph = workflow.compile()

# ======================
# 全局状态追踪（跨工作流调用）
# ======================
class AgentContext:
    def __init__(self):
        self.last_alert_app = ""        # 上次提醒的应用关键词
        self.last_alert_time = 0        # 上次提醒时间
        self.alert_cooldown = 60        # 提醒冷却时间（秒）
        self.is_alerting = False        # 当前是否在提醒状态
        self.alert_recovery_threshold = 30  # 恢复阈值：提醒后30秒或切换应用后自动恢复

    async def check_and_recover(self, state: dict, push_recovery: bool = True):
        """检查是否需要恢复提醒状态"""
        current_app = state.get("current_app", "")
        ent_key = state.get("entertainment_key", current_app)
        duration = state.get("today_usage_seconds", 0)
        emotion = state.get("emotion", "neutral")

        # 恢复条件：
        # 1. 应用切换了（ent_key 不同）
        # 2. 提醒状态超过恢复阈值
        # 3. 时长降到阈值以下且情绪正常
        should_recover = False

        if self.is_alerting:
            if ent_key != self.last_alert_app:
                print(f"🔄 应用切换 {self.last_alert_app} → {ent_key}，准备恢复")
                should_recover = True
            elif time.time() - self.last_alert_time > self.alert_recovery_threshold:
                # 超过恢复阈值，检查状态是否正常
                if duration < USAGE_THRESHOLD_SECONDS and emotion not in ["tired", "sad", "angry"]:
                    print(f"⏰ 超过恢复阈值 {self.alert_recovery_threshold}s，状态正常，准备恢复")
                    should_recover = True

            if should_recover and push_recovery:
                await self.push_recovery_to_frontend()

        return should_recover

    async def push_recovery_to_frontend(self):
        """推送恢复状态到前端"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    "http://localhost:8001/api/set_agent_result",
                    json={
                        "alert": False,
                        "msg": "好好休息，继续加油！",
                        "emotion": "happy"
                    },
                    timeout=aiohttp.ClientTimeout(total=3)
                )
                print(f"✅ 已推送恢复状态到前端")
        except Exception as e:
            print(f"⚠️ 推送恢复状态失败: {e}")
        self.is_alerting = False
        self.last_alert_time = 0  # 重置计时器

agent_context = AgentContext()

# ======================
# 主流程
# ======================
async def run_agent():
    """运行 Agent 工作流（循环决策）"""
    print("🚀 LangGraph Agent 已启动")
    print("=" * 50)
    print("工作流: state → judge_node → alert_node (MCP调用)")
    print("恢复规则: 应用切换 / 超过60秒 / 状态恢复正常")
    print("=" * 50)

    while True:
        try:
            # 从文件读取最新状态
            with open("data/current_state.json", "r") as f:
                state = json.load(f)

            print(f"\n[{time.strftime('%H:%M:%S')}] 📊 读取状态:")
            print(f"   app={state.get('current_app')}")
            print(f"   duration={state.get('today_usage_seconds')}s, emotion={state.get('emotion')}, is_ent={state.get('is_entertainment')}")

            # 检查是否需要恢复提醒状态
            await agent_context.check_and_recover(state)

            # 构建初始状态
            initial_state: AgentState = {
                "current_app": state.get("current_app", "未知"),
                "today_usage_seconds": state.get("today_usage_seconds", 0),
                "emotion": state.get("emotion", "neutral"),
                "is_entertainment": state.get("is_entertainment", False),
                "alert": False,
                "msg": "",
                "need_alert": False
            }

            # 检查冷却时间
            current_time = time.time()
            in_cooldown = (current_time - agent_context.last_alert_time) < agent_context.alert_cooldown

            if in_cooldown:
                print(f"⏳ 冷却中（{agent_context.alert_cooldown}s），距上次提醒 {current_time - agent_context.last_alert_time:.0f}s")

                # 即使冷却中，仍需更新 judge_node 判断（但不触发 alert_node）
                initial_state["need_alert"] = False  # 强制跳过 alert

            # 运行工作流
            final_state = await graph.ainvoke(initial_state)

            print(f"📤 工作流完成: need_alert={final_state.get('need_alert')}, alert={final_state.get('alert')}")

            await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ Agent 异常: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_agent())