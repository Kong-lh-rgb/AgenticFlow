# run_graph.py
from langgraph.types import Command, Interrupt
from main import app

# def interactive():
#     config = {"configurable": {"thread_id": "1"}}
#
#     question = input("用户：")
#     state = app.invoke({"question": question}, config)
#
#     while True:
#         # 检查是否是 interrupt
#         if "__interrupt__" in state:
#             interrupt_info: Interrupt = state["__interrupt__"][0]
#             print("\n🤖 机器人：")
#             print(interrupt_info.value)
#
#             user_reply = input("\n用户补充： ")
#
#             # 恢复执行
#             state = app.invoke(
#                 Command(resume=user_reply),
#                 config
#             )
#         else:
#             print("\n🎉 图执行完成：")
#             print(state)
#             break


def interactive():
    config = {"configurable": {"thread_id": "1"}}

    question = input("用户：")
    state = app.invoke({"question": question}, config=config)

    while True:
        # 如果图中有 interrupt
        if "__interrupt__" in state:
            interrupt_info = state["__interrupt__"][0]
            print("\n 助手：")
            print(interrupt_info.value)

            user_reply = input("\n用户： ")

            # 恢复执行
            state = app.invoke(
                Command(resume=user_reply),
                config=config
            )
        else:
            print("\n图执行完成：")
            print(state)
            break


if __name__ == "__main__":
    while True:
        interactive()

