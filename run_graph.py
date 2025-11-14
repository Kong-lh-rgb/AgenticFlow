# run_graph.py
from main import app


def run_test(user_input: str):
    """
    使用给定的用户输入运行图，并打印每一步的状态。
    """
    print(f"--- 开始测试 ---")
    print(f"用户输入: '{user_input}'")

    # 定义图的初始状态，只需要包含用户的提问
    initial_state = {"question": user_input}

    # 使用 stream() 方法可以观察图在每个节点执行后的状态变化
    final_state = None
    for event in app.stream(initial_state):
        for node_name, state_update in event.items():
            print(f"节点 '{node_name}' 执行完毕。")
            print(f"当前状态: {state_update}")
            print("-" * 30)
            # 保存最后一个非结束节点的状态
            if node_name != "__end__":
                final_state = state_update

    print("--- 测试结束 ---")
    if final_state:
        # 从最终状态中获取 router 节点的决策结果
        next_node = final_state.get('next_node')
        print(f"最终识别的意图（下一个节点）: '{next_node}'")
    else:
        print("未能获取最终状态。")


if __name__ == "__main__":
    # 测试用例1: 期望识别为 'planner_node'
    plan_question = input("输入：")
    run_test(plan_question)

