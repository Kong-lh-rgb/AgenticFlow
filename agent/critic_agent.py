# 对报告进行审查，提出修改意见，并决定是否需要重新撰写
from graph.content_graph import State
def review_node(state:State):
    """审查结点"""
    print("进入审查节点")
    topic = state["topic"]
    draft = state["draft"]
    #传给大模型提出修改意见,如果大模型觉得没有问题，把is_final设为True,否在设为False
    review_notes = ["修改意见1","修改意见2"]
    return {"review_notes":review_notes}