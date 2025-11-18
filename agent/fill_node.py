# from langchain_core.messages import HumanMessage
#
# from graph.content_graph import State
# from llm.llm_provider import easy_llm
#
# def fill_user_info_node(state:State):
#     user_info = state.get("user_info", [])
#     user_reply = state.get("user_reply", "")
#     fields = "\n".join([f"- {u['field']}" for u in user_info])
#
#     prompt = f"""
#     你是一个信息抽取助手。
#
#     以下是需要填写的字段：
#     {fields}
#
#     用户的补充回答是：
#     {user_reply}
#
#     请从用户的回答中提取字段对应的值，以 JSON 格式返回，缺失的字段不要填。
#     格式如下：
#     {{
#       "字段1": "值",
#       "字段2": "值"
#     }}
#     """
#
#     result = easy_llm.invoke([HumanMessage(content=prompt)])
#
#     # 解析 result 成 dict（你模型应该返回 JSON）
#     import json
#     extracted = json.loads(result.content)
#
#     for ui in user_info:
#         field = ui["field"]
#         if field in extracted:
#             ui["answer"] = extracted[field]
#
#     state["user_info"] = user_info
#     return state
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_classic.chains.question_answering.map_reduce_prompt import messages
from langchain_core.messages import HumanMessage,AIMessage
from pydantic import BaseModel
from langchain.agents import create_agent
from graph.content_graph import State
from llm.llm_provider import smart_llm
from typing import Optional, Literal
from langgraph.types import interrupt


class FillOutput(BaseModel):
    mode: Literal["filled", "ask_back", "refuse"]
    value: Optional[str] = None
    reply: Optional[str] = None



# @dynamic_prompt
# def fill_prompt(request: ModelRequest):
#     missing = request.state.get("missing")
#     user_reply = request.state.get("user_reply")
#
#     field = missing["field"]
#
#     return f"""
#         你是一个信息抽取助手。
#
#         任务: 从用户的补充回答中提取字段 "{field}" 的值。
#
#         【用户补充回答】
#         "{user_reply}"
#
#         【规则】
#         1. 直接提取用户回答中的核心内容作为字段值
#         2. 只有在以下情况返回 null:
#            - 用户明确拒绝 (如: "不想说"、"不知道")
#            - 回答完全无意义 (如: "啊啊啊"、"嗯嗯")
#         3. 即使回答简短或模糊,也尽量提取有效内容，尽量不要输出null
#
#         【输出格式】
#         严格输出 JSON:
#         {{
#            "value": "抽取的信息"
#         }}
#
#         不要输出其他内容。
#
#         请输出 JSON:
#         """
@dynamic_prompt
def fill_prompt(request: ModelRequest):
    state = request.state
    missing = state.get("missing")
    user_reply = state.get("user_reply")
    field = missing["field"]

    return f"""
        你是一个信息抽取和对话助手。
        
        当前缺失字段是："{field}"
        
        用户刚刚的回复是：
        "{user_reply}"
        
        【你的任务】
        判断用户的回复属于以下哪种情况:
        
        **情况 1: 用户在正面回答问题**
        示例:
        - 问:"报告的主题是什么?" → 答:"人工智能" ✅
        - 问:"字数要求?" → 答:"1000字左右" ✅
        - 问:"风格?" → 答:"正式一点" ✅
        
        如果是这种,输出:
        ```json
        {{
           "mode": "filled",
           "value": "<抽取的信息>",
           "reply": null
        }}

        你的任务有三种可能：
        
        1. 如果用户已经给出了这个字段的有效值，比如：
           - 问的是受众，用户说 "大学生"
           - 问的是长度，用户说 "1000 字左右"
           → 则 mode = "filled"，value 里放提取到的值，reply 不可以为null，要回复用户。
        
        2. 如果用户是在反问、质疑、想要你解释，比如：
           - "为什么要告诉你这个？"
           - "这个问题有什么用？"
           - "你先说说这个有什么影响？"
           → 如果是这种，输出
           {{
          "mode": "ask_back",
           "value": null,
           "reply": "<用 1-2 句话解释为什么需要这个信息,然后再次礼貌地重复提问>"
            }} 
        
        3. 如果用户明确拒绝提供这个信息，比如：
           - "不想说"
           - "这个我不方便告诉你"
              - "随便吧"
              -"无所谓"
           → 则 输出
            {{
           "mode": "refuse",
           "value": "用户拒绝提供",
           "reply": "<用 1-2 句话表示理解>"
            }}

            【核心判断标准】
            反问 = 用户在质疑你为什么要问这个问题 → ask_back
            拒绝 = 用户表示不愿意/不知道如何回答 → refuse
            其他 = 用户在尝试回答(即使简短/模糊) → filled
            【输出要求】
            不要输出任何解释文字，不要加多余内容。
            """

fill_agent = create_agent(
    model=smart_llm,
    tools=[],
    middleware=[fill_prompt],
    state_schema=State,
    response_format=FillOutput
)


# def fill_node(state: State):
#     missing = state["missing"]
#     field = missing["field"]
#     user_reply = state["user_reply"]
#     print(user_reply)
#     print(state)
#     if not user_reply:
#         return state
#     # 调用 fill agent
#     result = fill_agent.invoke(state)
#     value = result["structured_response"].value
#     print(value)
#     # 如果模型返回有效值 → 填入 context
#     context = state.get("context", {})
#     if value:
#         context[field] = value
#         print("如果有效填充结果后", state)
#     else:
#         print(f"⚠️ fill_agent 返回 value=None，跳过填充字段 {field}")
#
#
#
#     # 下一步交给 validator 去判断是否继续询问
#     return {
#         "context":context,
#         "user_reply": None,
#         "next_node": "validator_node"
#     }

def fill_node(state: State):
    missing = state.get("missing") or {}
    field = missing.get("field")
    user_reply = state.get("user_reply")
    update_messages = state.get("messages")
    if not user_reply:
        state["next_node"] = "validator_node"
        return state

    # 1. 让模型判断当前属于哪种情况
    print("11",state)
    result = fill_agent.invoke(state)
    out: FillOutput = result["structured_response"]
    i = state.get("i", 1)

    print(f"第{i}次 fill_node 执行")
    i = i + 1
    state["i"] = i
    print(f"   判断: {out.mode}")
    print(f"   填入: {out.value}")
    print(f"   回复: {out.reply}\n")
    # 2. 三种分支逻辑

    # 2.1 用户给了有效值 → 填 context，继续 validator
    if out.mode == "filled" and out.value:
        context = state.get("context", {}) or {}
        context[field] = out.value
        bot_response = out.reply
        print(bot_response)
        update_messages.append(AIMessage(bot_response))
        state["context"] = context
        update_messages.append(HumanMessage(user_reply))
        state["messages"] = update_messages
        state["user_reply"] = None
        state["next_node"] = "validator_node"
        return state

        # 2) 用户在反问，需要解释 + 再次等待用户回答
    if out.mode == "ask_back" and out.reply:
        # new_reply = interrupt({
        #     "instruction": "用户有疑问，请向用户解释，并再次让用户回答该问题：",
        #     "content": out.reply
        # })
        bot_response = out.reply
        update_messages.append(HumanMessage(user_reply))
        update_messages.append(AIMessage(bot_response))
        print("12", state)
        new_reply = interrupt(bot_response)
        update_messages.append(HumanMessage(new_reply))
        print("13",state)
        state["user_reply"] = new_reply
        state["messages"] = update_messages
        print("14", state)
        # 不修改 next_node，让图重新回到 fill_node，根据新的 user_reply 再跑一轮
        state["next_node"] = "fill_node"
        return state

    # 2.3 用户拒绝提供信息 → 视策略处理
    if out.mode == "refuse":
        context = state.get("context", {}) or {}
        context[field] = "用户拒绝提供"
        state["context"] = context

        info = out.reply
        print(info)
        update_messages.append(HumanMessage(user_reply))
        update_messages.append(AIMessage(info))

        state["messages"] = update_messages
        state["user_reply"] = None
        state["missing"] = None
        state["next_node"] = "validator_node"
        return state


    return state