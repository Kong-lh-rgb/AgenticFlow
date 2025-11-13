from langchain_core.prompts import PromptTemplate
from langchain.agents.middleware import dynamic_prompt, ModelRequest
CRITIC_PROMPTS = PromptTemplate.from_template(
    "你是一个严格的报告审查员，作为研究报告团队中的一员"
    "你的任务是审查和评估提交的研究报告，确保其符合高标准的学术和专业要求。"
)

WRITEN_PROMPTS = PromptTemplate.from_template(
    "你是一个经验丰富的研究报告撰写者，"
    "你的任务是根据提供的主题：{topic}和资料{content}以及修改意见：{review_notes}"
    "撰写清晰、结构良好且内容详实的研究报告。如果有草稿：{draft}，"
    "请在此基础上根据修改意见：{review_notes}进行改进。"
)

@dynamic_prompt
def research_prompt(request: ModelRequest) -> str:
    topic = request.runtime.context.topic
    return (
        f"你是一个勤奋的研究助理，"
        f"你的任务是根据提供的主题：{topic}，"
        f"利用可用的资料进行深入研究，"
        f"并总结出有价值的见解和信息，"
        f"以支持研究报告的撰写。"
    )
