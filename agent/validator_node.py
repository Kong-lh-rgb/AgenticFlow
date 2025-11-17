from pydantic import BaseModel
from typing import Optional
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.agents import create_agent
from graph.content_graph import State
from llm.llm_provider import easy_llm

class MissingField(BaseModel):
    field: str
    question: str

class ValidatorOutput(BaseModel):
    need_ask: bool
    missing: Optional[MissingField] = None


@dynamic_prompt
def validator_prompt(request: ModelRequest):
    task = request.state.get("task")
    context = request.state.get("context", {})

    return f"""
        你是一个智能 Validator。你的任务是判断：  
        当前 context（已经收集到的信息）是否足以完成用户的任务。
        
        -------------------------
        【用户任务 task】
        {task}
        
        【当前已知信息 context】
        {context}
        -------------------------
        【关键规则】
        ✅ **以下情况视为"字段已填充完毕",不要再次提问:**
        1. 字段有明确的有效值 (如 topic="ai", length="100字")
        2. 字段值是 "用户拒绝提供" → **这表示用户不想提供,必须跳过**
        3. 字段值是 null 或 None → **也表示已处理,不要再问**
        
        ❌ **只有字段完全不存在于 context 中,才算缺失**
        
        -------------------------

        【你的工作逻辑】
        1. 分析 task(如: 写报告、写总结、写文章)。
        2. 判断该任务最关键的参数是什么(如 topic, goal, audience, length, style 等)。
        
        **对于"写报告"这类任务,通常需要以下字段:**
        - topic (主题)
        - goal (目的)
        - audience (受众,如: 大学生、专业人士)
        - length (长度)
        - style (风格,如: 正式、通俗)
        - language (语言)
        - key points (要点)
        
        3. 检查 context 中哪些字段已经具备,哪些缺失:
           - 如果某字段 = "用户拒绝提供" → 跳过,不要再问
           - 如果某字段 = 有效值 → 已具备
           - 如果某字段不存在 → 缺失
        
        4. **只有当至少 4 个关键字段已具备(或被拒绝)时,才输出:**
           {{
             "need_ask": false,
             "missing": null
           }}
        
        5. 如果缺少关键信息,选择"最重要的那一个"(且不在 context 中的字段),输出:
           {{
              "need_ask": true,
              "missing": {{
                 "field": "<缺失字段名(英文)>",
                 "question": "<为该字段生成一个自然语言提问>"
              }}
           }}
        
        6. **绝对不要重复提问 context 中已经存在的字段** (即使值是 "用户拒绝提供")
        
        -------------------------
        【输出要求】
        - 严格输出 JSON
        - 不要输出多余文字
        
        请输出 JSON:
        """

validator_agent = create_agent(
    model=easy_llm,
    tools=[],
    middleware=[validator_prompt],
    state_schema=State,
    response_format=ValidatorOutput
)


def validator_node(state: State):
    task = state["task"]
    context = state.get("context", {})

    result = validator_agent.invoke(state)

    res: ValidatorOutput = result["structured_response"]

    if res.need_ask:
        # 更新 missing，供 ask_node 使用
        state["missing"] = res.missing.model_dump()
        state["need_ask"] = True
        state["next_node"] = "ask_node"
    else:
        # 信息足够 → 可以写报告
        state["need_ask"] = False
        state["next_node"] = "research_node"

    return state
