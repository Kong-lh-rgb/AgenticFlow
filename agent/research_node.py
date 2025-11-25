from __future__ import annotations

import os
import re
from typing import Any, Dict, List

from dotenv import load_dotenv
from tavily import TavilyClient

from llm.llm_provider import easy_llm
from graph.content_graph import State  # 你如果 State 就是 dict，也能用


llm = easy_llm


def clean_text(text: Any) -> str:
    """清理文本内容，自动处理 None / 非字符串类型"""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)                 # md 图片
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)              # md 链接
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)   # md 标题
    text = re.sub(r"<.*?>", "", text)                            # html 标签
    text = re.sub(r"\n\s*\n", "\n", text)                        # 多余空行
    return text.strip()


def summarize_to_facts(text: str) -> List[str]:
    """把一堆原文浓缩成 3~5 条事实；返回 list[str] 方便后面 writer 拼证据"""
    prompt = f"""
请从下列材料中提取关键事实，要求：
- 只写事实，不要观点/推测
- 去重
- 3~5 条
- 用中文
- 每条一行输出（不要加前言后记）

材料：
{text}
""".strip()

    res = llm.invoke(prompt)
    content = res.content.strip() if hasattr(res, "content") else str(res).strip()

    # 把“1. ... / - ...”这种行规整成 facts list
    facts: List[str] = []
    for line in content.splitlines():
        s = line.strip()
        if not s:
            continue
        s = re.sub(r"^[-*\u2022]\s*", "", s)          # "- "
        s = re.sub(r"^\d+[.)、]\s*", "", s)            # "1. " / "1、"
        if s:
            facts.append(s)

    return facts[:8] if facts else ([content] if content else [])


def search_node(state: State) -> State:
    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("缺少环境变量 TAVILY_API_KEY（请检查 .env 或系统环境变量）")

    tavily_client = TavilyClient(api_key=api_key)

    # 兼容两种字段名：query（推荐）/ search_queries（你旧代码）
    queries = state.get("query") or state.get("search_queries") or []
    if not isinstance(queries, list):
        queries = []

    all_facts: List[Dict[str, Any]] = []

    for q in queries:
        if not isinstance(q, str) or not q.strip():
            continue

        q = q.strip()
        print(f"\n🔍 正在搜索：{q}")

        response = tavily_client.search(
            query=q,
            max_results=5,
            include_raw_content=True,
        )

        # 把多个网页 raw_content 合并，再总结一次（比每条都 summarize 省很多）
        docs: List[str] = []
        for item in response.get("results", []):
            raw = item.get("raw_content") or item.get("content") or ""
            cleaned = clean_text(raw)
            if len(cleaned) < 80:
                continue
            docs.append(cleaned[:6000])  # 截断，避免 prompt 爆炸

        combined = "\n\n---\n\n".join(docs[:5])
        evidence = summarize_to_facts(combined) if combined else []

        all_facts.append({"query": q, "evidence": evidence})

    state["research_findings"] = all_facts
    state["next_node"] = "writer_node"   # 关键：跑完 research 就去写报告
    return state

