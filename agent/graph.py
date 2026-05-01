import json
import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()

class AgentState(TypedDict):
    data: dict
    decision: dict

llm = ChatOpenAI(
    model="minimax-m2.7",
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.chat/v1",
    temperature=0.1
)

async def judge_node(state: AgentState):
    data = state["data"]
    
    # 获取当前使用时长，用于兜底逻辑判断
    current_duration = data.get("today_usage_seconds", 0) 

    # 1. 修改 Prompt 指令，让 AI 知道现在的规则是 30 秒
    prompt = f"""
你是健康助手。根据用户信息判断是否提醒。

用户数据：
{json.dumps(data, ensure_ascii=False, indent=2)}

规则：
1. 娱乐应用 + 开心表情 → 提醒
2. 任何应用使用超过 30 秒 → 提醒  <-- [已修改：从5分钟缩短至30秒]
3. 其他情况不提醒

请只返回JSON，不要加任何其他文字，例子：
{{"alert":false,"msg":""}}
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # 超强清洗！解决 JSON 报错
        content = content.replace("```json", "").replace("```", "").strip()
        content = content.split("{")[-1]
        content = content.split("}")[0]
        content = "{" + content + "}"

        state["decision"] = json.loads(content)
    except Exception as e:
        print(f"AI调用失败: {e}")
        
        # 2. 修改“本地兜底规则”，确保 AI 挂掉时逻辑依然是 30 秒[cite: 5]
        is_happy = data.get("emotion") == "happy"
        
        # 直接通过数值判断是否超过 30 秒[cite: 5]
        too_long = current_duration > 30 
        
        # 只要开心或者超过30秒就提醒 (用于测试)
        alert = is_happy or too_long
        state["decision"] = {"alert": alert, "msg": f"你已经使用了 {current_duration} 秒，该休息一下啦！"}

    return state

async def alert_node(state: AgentState):
    decision = state.get("decision", {})
    if decision.get("alert"):
        msg = decision.get("msg", "休息一下吧！")
        try:
            async with sse_client("http://localhost:8000/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    await session.call_tool("trigger_alert", {"message": msg})
            print(f"✅ 提醒成功: {msg}")
        except Exception as e:
            print(f"⚠️ 提醒发送失败: {e}")
    return state

workflow = StateGraph(AgentState)
workflow.add_node("judge", judge_node)
workflow.add_node("alert", alert_node)
workflow.set_entry_point("judge")
workflow.add_edge("judge", "alert")
workflow.add_edge("alert", END)

agent_app = workflow.compile()