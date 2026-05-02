import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

# ======================
# LLM 初始化
# ======================
llm = ChatOpenAI(
    model="minimax-m2.7",
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.chat/v1",
    temperature=0.1,
    timeout=10
)

# ======================
# MCP 客户端调用逻辑
# ======================
async def call_mcp_tool(tool_name: str, arguments: dict = None) -> dict:
    """
    调用 MCP 注册的工具
    :param tool_name: 工具名
    :param arguments: 工具入参
    :return: 工具返回结果
    """
    async with ClientSession(sse_client("http://127.0.0.1:8765")) as session:
        # 调用工具
        result = await session.call_tool(
            tool_name=tool_name,
            arguments=arguments or {},
            tool_call_id=f"{tool_name}-{asyncio.get_event_loop().time()}"
        )

        # 解析结果
        if result.tool_result.status == "success":
            return json.loads(result.tool_result.content)
        else:
            raise Exception(f"MCP 工具调用失败：{result.tool_result.error.message}")

async def llm_decision_workflow():
    """LLM 驱动的完整决策流程：调用工具 → 分析结果 → 生成提醒"""
    while True:
        try:
            # 1. 调用 MCP 工具获取用户状态
            user_state = await call_mcp_tool("get_user_usage_state")
            print(f"\n📊 获取用户状态：{json.dumps(user_state, ensure_ascii=False)}")

            # 2. 调用 MCP 工具判断是否需要提醒（也可让 LLM 直接决策）
            judge_result = await call_mcp_tool(
                "judge_rest_alert",
                arguments={
                    "current_app": user_state["current_app"],
                    "duration": user_state["today_usage_seconds"],
                    "emotion": user_state["emotion"],
                    "is_entertainment": user_state["is_entertainment"]
                }
            )
            print(f"🤖 提醒判断结果：{json.dumps(judge_result, ensure_ascii=False)}")

            # 3. （可选）让 LLM 优化提醒文案
            if judge_result["alert"]:
                prompt = f"""
                你是用户体验优化助手，请根据以下信息优化休息提醒文案：
                - 当前应用：{user_state['current_app']}
                - 使用时长：{user_state['today_usage_seconds']}秒
                - 用户情绪：{user_state['emotion']}
                - 原始文案：{judge_result['msg']}
                
                要求：语气亲切，适配用户情绪，不超过50字。
                """
                llm_response = llm.invoke([HumanMessage(content=prompt)])
                optimized_msg = llm_response.content.strip()
                judge_result["msg"] = optimized_msg
                print(f"✨ LLM 优化后文案：{optimized_msg}")

            # 4. 推送提醒结果到前端服务器
            await push_alert_to_frontend(judge_result)

        except Exception as e:
            print(f"❌ 流程异常：{str(e)}")
        
        await asyncio.sleep(2)  # 每2秒执行一次

async def push_alert_to_frontend(decision: dict):
    """推送提醒结果到前端服务器（复用原有 mcp_server.py 的接口）"""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                "http://localhost:8000/api/set_agent_result",
                json={
                    "alert": decision["alert"],
                    "msg": decision["msg"],
                    "emotion": decision["emotion"]
                },
                timeout=aiohttp.ClientTimeout(total=3)
            )
    except Exception as e:
        print(f"❌ 推送前端失败：{str(e)}")

if __name__ == "__main__":
    asyncio.run(llm_decision_workflow())
    