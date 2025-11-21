from graph.content_graph import State

def handle_context(context:dict):
    """整理用户需求"""
    update_context = {k:v for k,v in context.items() if v != '用户拒绝提供' and v is not None}
    return update_context