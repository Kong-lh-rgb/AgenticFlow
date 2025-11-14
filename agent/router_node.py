from graph.content_graph import State
from pydantic import BaseModel,Field
from typing import Literal
from llm.llm_provider import easy_llm
from langchain.agents import create_agent,AgentState
from langchain.agents.structured_output import ToolStrategy
from langchain.agents.middleware import dynamic_prompt, ModelRequest

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
        f"""你是一个意图识别助手，负责分析用户的输入{question}并识别其意图。
        如果用户的输入涉及到任务的规划、或需要制定计划，输出 'planner_node'
        如果用户的输入是一个具体的问题，期望得到直接的答案，输出 'qa_node'
        示例：
        用户: 帮我制定一个学习计划
        意图: planner_node
        用户: 地球到月球的距离是多少？
        意图: qa_node
        输出结果，不要多余文字
        请仅返回意图，不要添加任何额外的信息。"""
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
    res = agent.invoke({
        "input": question,
        "question": question
    })
    intent_result = res['structured_response'].intent
    state["next_node"] = intent_result
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