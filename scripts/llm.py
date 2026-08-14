"""DeepSeek 中文摘要模块（OpenAI 兼容接口）。

未配置 DEEPSEEK_API_KEY 或调用失败时，返回 None，由主脚本降级为原文。
"""
from __future__ import annotations

import json
import os

try:
    from openai import OpenAI
except ImportError:  # 本地未安装 openai 包时，不影响其余功能
    OpenAI = None

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"


def _client() -> OpenAI | None:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key or OpenAI is None:
        return None
    return OpenAI(api_key=key, base_url=BASE_URL)


def _chat_json(client: OpenAI, system: str, user: str, max_tokens: int = 3000) -> dict | None:
    """调用 DeepSeek，要求返回 JSON 对象；失败返回 None。"""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content or ""
        data = json.loads(content)
        return data if isinstance(data, dict) else None
    except Exception as e:
        print(f"      [llm] 调用失败：{e}")
        return None


def summarize_projects(projects: list[dict]) -> list[dict] | None:
    """为 GitHub 项目批量生成中文简介 + 用途介绍。

    返回与输入顺序一致的 [{introduction, usage}, ...]；失败返回 None。
    """
    client = _client()
    if client is None:
        return None
    payload = [
        {
            "name": p["name"],
            "description": (p.get("description") or "")[:400],
            "language": p.get("language", ""),
        }
        for p in projects
    ]
    system = (
        "你是一名资深技术编辑。下面是一批 GitHub 开源项目（近 7 天新创建的热门项目）。"
        "请为每个项目写两段中文内容：\n"
        "1) introduction：2~3 句中文简介，概括项目是什么、解决什么问题；\n"
        "2) usage：1~2 句中文用途介绍，说明开发者可以用它来做什么、典型使用场景。\n"
        '以 JSON 对象返回，格式：{"projects": [{"name": "项目全名", "introduction": "...", "usage": "..."}]}，'
        "顺序与输入一致，只返回 JSON，不要输出任何多余文字。"
    )
    data = _chat_json(client, system, json.dumps(payload, ensure_ascii=False), max_tokens=3000)
    if not data:
        return None
    arr = data.get("projects")
    return arr if isinstance(arr, list) else None


def summarize_news(items: list[dict]) -> dict[str, str] | None:
    """为新闻批量生成中文摘要，返回 {url: 摘要}；失败返回 None。"""
    client = _client()
    if client is None:
        return None
    if not items:
        return {}
    payload = [{"title": it["title"], "source": it["source"]} for it in items]
    system = (
        "你是一名 AI 领域新闻编辑。下面是从 Hacker News、Reddit、arXiv、中文科技媒体"
        "聚合的昨日 AI 动态标题列表。请为每条写 1~2 句中文摘要：这条新闻讲了什么、为什么值得关注。\n"
        '以 JSON 对象返回：{"summaries": ["摘要1", "摘要2", ...]}，顺序与输入一致，只返回 JSON。'
    )
    data = _chat_json(client, system, json.dumps(payload, ensure_ascii=False), max_tokens=4000)
    if not data:
        return None
    sums = data.get("summaries")
    if not isinstance(sums, list):
        return None
    return {it["url"]: str(s) for it, s in zip(items, sums)}
