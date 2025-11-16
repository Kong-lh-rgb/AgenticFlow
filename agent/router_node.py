from graph.content_graph import State
from pydantic import BaseModel,Field
from typing import Literal
from llm.llm_provider import easy_llm
from langchain.agents import create_agent,AgentState
from langchain.agents.structured_output import ToolStrategy
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.messages import HumanMessage, AIMessage

class output_schema(BaseModel):
    intent: Literal["planner_node","qa_node"] = Field(
        description="根据用户的输入识别出的意图"
    )

@dynamic_prompt
def prompt(request:ModelRequest):
    # question = request.runtime.context["question"]
    question = request.state.get("question")
    #增强意图识别的方法：强化提示词，few-shot学习，微调模型，结构化输出
    return (
        f"""
            你是一个意图识别助手，需要根据用户输入判断这是哪种类型的任务。
            
            【任务类型定义】
            1. planner_node：用户的输入表示需要“生成内容、写报告、写文章、写总结、生成方案、制定计划、撰写文档”等复杂任务，需要多步骤推理。
            2. qa_node：用户在询问一个具体事实、知识点、数据或者需要直接回答的问题。
            
            【分类逻辑】
            - 只要用户的输入包含 “帮我写… / 帮我生成… / 写一个… / 做一份报告… / 总结一下…” → 必须归为 planner_node
            - 用户问“是什么 / 为什么 / 多高 / 多远 / 怎么办 / 为什么会这样” → 属于 qa_node
            
            【用户输入】
            {question}
            
            请严格输出以下两者之一：
            "planner_node" 或 "qa_node"
            
            不要输出任何多余内容。
            """
    )

agent = create_agent(
    model = easy_llm,
    tools = [],
    middleware = [prompt],
    state_schema=State,
    response_format=output_schema
)

def router_node(state:State):
    """意图识别"""
    #state传过来一个字典
    question = state.get("question")
    # message = state.get("messages", [])
    res = agent.invoke({
        "input": question,
        "question": question
    })
    intent_result = res['structured_response'].intent
    state["next_node"] = intent_result
    # update_messages = message + [HumanMessage(content=question), AIMessage(content=intent_result)]
    # state["messages"] = update_messages
    messages = state.get("messages", [])
    messages.append(HumanMessage(content=question))
    messages.append(AIMessage(content=intent_result))
    state["messages"] = messages
    return state
#
# if __name__ == "__main__":
#     test_input1 = "帮我制定一个学习计划"
#     result1 = router_node(State(question=test_input1,topic="学习计划"))
#     print(result1)
#     print(result1["next_node"])
#     test_input2 = "地球到月球的距离是多少？"
#     result2 = router_node(State(question=test_input2))
#     print(f"测试输入2的识别结果: {result2}")