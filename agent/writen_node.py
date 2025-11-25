from llm.llm_provider import easy_llm
from graph.content_graph import State
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.agents import create_agent

llm = easy_llm


def format_evidence(research_findings):
    sections = []
    for block in research_findings:
        query = block.get("query", "未知问题")
        evidence_list = block.get("evidence", [])
        ev_text = "\n".join([f"- {e}" for e in evidence_list])
        sections.append(f"【问题】{query}\n【事实证据】\n{ev_text}")
    return "\n\n".join(sections)


def format_context(context: dict):
    if not context:
        return "（无上下文信息）"
    return "\n".join([f"【{k}】{v}" for k, v in context.items()])


@dynamic_prompt
def build_writer_prompt(request: ModelRequest):
    context_text = format_context(request.state.get("context", {}))
    evidence_text = format_evidence(request.state.get("research_findings", []))
    question = request.state.get("question", "未知主题")

    return f"""
你是一名专业的研究与报告撰写专家。

请基于用户提问、补充信息（Context）以及研究证据（Research Findings），撰写一篇完整、有结构、基于事实的报告。

====================
用户提问（question）
====================
{question}

====================
用户补充的对于写报告的要求（Context）
====================
{context_text}

====================
研究证据（Research Findings）
====================
{evidence_text}

====================
写作要求
====================
- 主体内容需按 Research Findings 中的 “问题 → 证据” 的顺序组织
- 报告结构必须至少包含：引言、主体、小结
- 主体部分要根据每个 query 写成独立小节
- 所有观点必须基于 evidence，不得凭空杜撰
- 表述风格需参考 context 中可能存在的内容（如 Audience、Style、Goal 等）
- 如果 context 中出现长度、风格、受众等描述，需自动遵循

只输出最终报告正文，不要输出任何解释或多余内容。
"""


agent = create_agent(
    model=llm,
    tools=[],
    middleware=[build_writer_prompt],
    state_schema=State,
)


def _extract_text(res) -> str:
    # create_agent 常见返回：dict(output=..., messages=...)
    if isinstance(res, dict):
        out = res.get("output")
        if isinstance(out, str) and out.strip():
            return out.strip()
        msgs = res.get("messages")
        if isinstance(msgs, list):
            for m in reversed(msgs):
                if hasattr(m, "content") and isinstance(m.content, str) and m.content.strip():
                    return m.content.strip()
        return str(res)

    # 少数情况返回 AIMessage
    if hasattr(res, "content") and isinstance(res.content, str):
        return res.content.strip()

    return str(res).strip()


def writen_node(state: State):
    # 只喂写作需要的字段，避免 state 越传越大、输出夹带 state
    agent_state = {
        "input": "生成报告",
        "messages": state.get("messages") or [],
        "question": state.get("question"),
        "context": state.get("context") or {},
        "research_findings": state.get("research_findings") or [],
    }

    res = agent.invoke(agent_state)

    text = _extract_text(res)

    state["final_report"] = text
    state["next_node"] = "review_node"
    # 如果你希望把 agent 的 messages 也同步回主 state（可选）
    if isinstance(res, dict) and isinstance(res.get("messages"), list):
        state["messages"] = res["messages"]

    return state
