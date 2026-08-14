"""钉钉群机器人推送（自定义机器人 Webhook）。

支持钉钉自定义机器人的两种常见安全设置：
- 加签（secret）：自动计算 timestamp + sign 并附加到 URL；
- 自定义关键词：报告正文包含 "每日报告" 字样，可用作关键词。
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import time

import requests

# 钉钉 markdown 消息上限 20000 字符，留安全余量后按此切分
MAX_CHARS = 15000


def _sign(secret: str, timestamp: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    digest = hmac.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _split_text(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """超长文本按行切分，尽量在换行处断开。"""
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        if current and len(current) + len(line) + 1 > max_chars:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks


def send_markdown(webhook: str, title: str, text: str, secret: str = "") -> int:
    """发送 markdown 消息；超长自动拆成多条依次发送。返回发送条数。"""
    chunks = _split_text(text)
    for i, chunk in enumerate(chunks):
        payload = {"msgtype": "markdown", "markdown": {"title": title, "text": chunk}}
        url = webhook
        if secret:
            ts = str(round(time.time() * 1000))
            sep = "&" if "?" in webhook else "?"
            url = f"{webhook}{sep}timestamp={ts}&sign={_sign(secret, ts)}"
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        body = resp.json()
        if body.get("errcode") != 0:
            raise RuntimeError(f"钉钉推送失败: {body}")
        if i < len(chunks) - 1:
            time.sleep(1.5)  # 钉钉限流：每机器人每分钟最多 20 条
    return len(chunks)
