"""每日报告主脚本：采集 → DeepSeek 摘要 → 渲染(MD/DOCX/PDF) → 钉钉推送。

环境变量（均可在 GitHub Actions Secrets 中配置，缺省时优雅降级）：
  GH_TOKEN            GitHub Token（Actions 内置 GITHUB_TOKEN，提高 API 限流）
  DEEPSEEK_API_KEY    DeepSeek API Key（缺省时降级为项目自带英文描述）
  DINGTALK_WEBHOOK    钉钉机器人 Webhook URL（缺省时跳过推送）
  DINGTALK_SECRET     钉钉机器人加签密钥（可选）
  REPO / BRANCH       仓库信息，用于生成报告下载链接（默认 Prosperity-code/Attempt main）

用法：python scripts/generate_report.py
输出：daily-reports/YYYY-MM-DD/report.{md,docx,pdf}
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import llm
import notify
import render
import sources

REPO = os.environ.get("REPO", "Prosperity-code/Attempt")
BRANCH = os.environ.get("BRANCH", "main")


def main() -> None:
    today = sources.beijing_today()
    yesterday = sources.beijing_yesterday()
    date_str = today.isoformat()

    gh_token = os.environ.get("GH_TOKEN", "").strip()
    webhook = os.environ.get("DINGTALK_WEBHOOK", "").strip()
    ding_secret = os.environ.get("DINGTALK_SECRET", "").strip()
    llm_configured = bool(os.environ.get("DEEPSEEK_API_KEY", "").strip())

    # 1. GitHub 热榜（面向新手深度介绍，取前 5 名）
    print(f"[1/5] 采集 GitHub 热榜 TOP5（{date_str}）...")
    projects = sources.github_trending(token=gh_token, limit=5)
    if not projects:
        raise SystemExit("GitHub 热榜采集失败：未获取到任何项目，终止运行")
    for p in projects:
        print(f"       - {p['name']} ⭐{p['stars']} ({p['language']})")

    # 2. AI 动态
    print(f"[2/5] 聚合 AI 动态（{yesterday.isoformat()}）...")
    news = sources.ai_news()
    print(f"       共 {len(news)} 条：{', '.join(sorted(set(it['source'] for it in news)))}")

    # 3. DeepSeek 摘要
    print("[3/5] 生成中文摘要（DeepSeek）...")
    used_llm = False
    if llm_configured:
        project_sums = llm.summarize_projects(projects)
        news_sums = llm.summarize_news(news)
        if project_sums is not None and news_sums is not None:
            for i, p in enumerate(projects):
                s = project_sums[i] if i < len(project_sums) else {}
                p["introduction"] = s.get("introduction") or p.get("description") or "（暂无简介）"
                p["usage"] = s.get("usage", "")
                p["fields"] = s.get("fields", "")
                p["help"] = s.get("help", "")
            for it in news:
                it["summary"] = news_sums.get(it["url"], "")
            used_llm = True
            print("       DeepSeek 摘要完成")
        else:
            print("       LLM 调用失败，降级为原文描述")
    else:
        print("       未配置 DEEPSEEK_API_KEY，使用项目自带描述")
    if not used_llm:
        for p in projects:
            p["introduction"] = p.get("description") or "（暂无简介）"
            p["usage"] = ""
            p["fields"] = ""
            p["help"] = ""
        for it in news:
            it["summary"] = ""

    # 4. 渲染
    out_dir = Path("daily-reports") / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[4/5] 渲染报告 → {out_dir}")
    md_text = render.render_markdown(today, projects, news, used_llm)
    (out_dir / "report.md").write_text(md_text, encoding="utf-8")
    render.render_docx(today, projects, news, used_llm, out_dir / "report.docx")
    render.render_pdf(today, projects, news, used_llm, out_dir / "report.pdf")
    print(f"       report.md {len(md_text)} 字符；report.docx / report.pdf 已生成")

    # 5. 钉钉推送
    print("[5/5] 推送钉钉 ...")
    if webhook:
        page = f"https://github.com/{REPO}/tree/{BRANCH}/daily-reports/{date_str}"
        raw_docx = f"https://github.com/{REPO}/raw/{BRANCH}/daily-reports/{date_str}/report.docx"
        raw_pdf = f"https://github.com/{REPO}/raw/{BRANCH}/daily-reports/{date_str}/report.pdf"
        footer = (
            "\n\n---\n"
            f"📁 [查看完整报告]({page})\n"
            f"📄 [下载 Word 版]({raw_docx}) ｜ [下载 PDF 版]({raw_pdf})"
        )
        n = notify.send_markdown(webhook, f"每日报告 {date_str}", md_text + footer, secret=ding_secret)
        print(f"       已发送 {n} 条消息")
    else:
        print("       未配置 DINGTALK_WEBHOOK，跳过推送")

    print("完成 ✓")


if __name__ == "__main__":
    main()
