#接受用户的补充信息输入，生成完整的查询信息
from graph.content_graph import State
from llm.llm_provider import easy_llm
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from pydantic import BaseModel

class AddField(BaseModel):
    field:str
    value:str

class UserIdentifyOutput(BaseModel):
    adding: list[AddField]

@dynamic_prompt
def prompt(request:ModelRequest):
    need_add = request.state.get("user_info")
    # user_reply = request.state.get("input")
    user_reply = request.state["messages"][-1].content
    # return (
    #     f"""你接受用户的输入以及需要补充的信息列表：{need_add}。
    #     请根据用户的输入{input}，提取出每个需要补充的信息对应的值，
    #     并且按照JSON格式输出adding列表，包含每个字段名和对应的值。
    #     请严格输出如下 JSON 结构：
    #     {{
    #       "adding": [
    #         {{"field": "...", "value": "..."}},
    #         ...
    #       ]
    #     }}
    #     不要输出任何解释，不要输出额外文字。
    #     """
    # )
    return (
        f"""你需要根据用户补充的回答，为缺失的信息字段找到对应的值。

            需要填充的字段如下:
            {need_add}

            用户的回答是:
            "{user_reply}"

            请从用户的回答中提取每个字段的值，并严格按照下面的JSON格式输出。'field' 必须与上面列出的字段名完全一致。
            {{
              "adding": [
                {{"field": "length", "value": "1500字"}},
                {{"field": "audience", "value": "学生"}}
              ]
            }}
            不要输出任何解释或额外文字。
            """
    )


agent = create_agent(
    model = easy_llm,
    tools = [],
    middleware=[prompt],
    state_schema=State,
    response_format=UserIdentifyOutput
)

def user_identify_node(state:State):
    # # input = state["messages"][-1].content
    # res = agent.invoke({
    #     # "input": input
    # })
    # # adding_list = res['structured_response'].adding
    # # state["need_info"] = [item.model_dump() for item in adding_list]
    # # return state
    # extracted_values = {item.field: item.value for item in res['structured_response'].adding}
    #
    # # 获取 planner 创建的原始 user_info 列表
    # current_user_info = state.get("user_info", [])
    #
    # # 遍历列表，将提取到的值填充回去
    # for item in current_user_info:
    #     # 如果当前项的 'field' 在提取出的值中，并且它还没有 'value'
    #     if item.get("field") in extracted_values and "value" not in item:
    #         item["value"] = extracted_values[item.get("field")]
    #
    # # 将更新后的列表（现在包含 value）写回 state
    # state["user_info"] = current_user_info
    # state["next_node"] = "planner"
    # return state
    pass