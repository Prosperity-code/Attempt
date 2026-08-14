"""数据采集：GitHub 热榜 + AI 新闻聚合。

设计原则：任何单个数据源的失败都不应中断整个流程，
因此所有网络请求均捕获异常并返回空列表，由调用方决定如何降级。
"""
from __future__ import annotations

import datetime as dt
import re
from urllib.parse import quote

import feedparser
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; daily-report-bot/1.0)"}
REDDIT_HEADERS = {"User-Agent": "linux:daily-report:v1.0 (by /u/daily_report_bot)"}

# 中文 RSS 源：(URL, 显示名称)
# 说明：机器之心曾提供 RSS，现已失效（302 到 web 应用），故未收录
RSS_SOURCES = [
    ("https://www.qbitai.com/feed", "量子位"),
    ("https://www.aiera.com.cn/feed", "新智元"),
    ("https://www.infoq.cn/feed", "InfoQ 中文"),
]


# ---------- 时间工具 ----------

def beijing_today() -> dt.date:
    """北京时间（UTC+8）今天的日期。"""
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=8)).date()


def beijing_yesterday() -> dt.date:
    return beijing_today() - dt.timedelta(days=1)


def _utc_yesterday() -> dt.date:
    return dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)


def _day_range(day: dt.date) -> tuple[int, int]:
    """返回某天的 [起始, 结束) Unix 时间戳（UTC）。"""
    start = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp())
    return start, start + 86400


def _get(url: str, *, headers=None, params=None, timeout: int = 25) -> requests.Response:
    h = dict(HEADERS)
    if headers:
        h.update(headers)
    resp = requests.get(url, headers=h, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp


# ---------- GitHub 热榜 ----------

def github_trending(token: str | None = None, days: int = 7, limit: int = 10) -> list[dict]:
    """GitHub Search API：近 days 天创建、Stars 降序取前 limit 名。

    这是官方 API 对 "trending" 的常用近似：新创建 + 涨星快。
    返回的每一项包含 name/url/description/stars/forks/language/topics，
    以及留给后续填充的 introduction/usage 字段。
    """
    since = (beijing_today() - dt.timedelta(days=days)).isoformat()
    params = {
        "q": f"created:>{since}",
        "sort": "stars",
        "order": "desc",
        "per_page": str(limit),
    }
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = _get("https://api.github.com/search/repositories", headers=headers, params=params).json()
    items = []
    for it in data.get("items", []):
        items.append({
            "name": it.get("full_name", ""),
            "url": it.get("html_url", ""),
            "description": (it.get("description") or "").strip(),
            "stars": it.get("stargazers_count", 0),
            "forks": it.get("forks_count", 0),
            "language": it.get("language") or "未知",
            "topics": it.get("topics", [])[:6],
            "introduction": "",
            "usage": "",
        })
    return items


# ---------- AI 动态 ----------

def hn_stories(day: dt.date, limit: int = 5) -> list[dict]:
    """Hacker News（Algolia API）当日 AI / LLM 相关高赞故事。"""
    start, end = _day_range(day)
    out: list[dict] = []
    seen: set[str] = set()
    for query in ("AI", "LLM"):
        try:
            data = _get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": query,
                    "tags": "story",
                    # 只按标题匹配，避免命中正文含 AI 字样但与 AI 无关的故事
                    "restrictSearchableAttributes": "title",
                    "numericFilters": f"created_at_i>{start},created_at_i<{end}",
                    "hitsPerPage": "40",
                },
            ).json()
        except requests.RequestException:
            continue
        for hit in data.get("hits", []):
            oid = hit.get("objectID")
            title = (hit.get("title") or "").strip()
            if not oid or oid in seen or not title:
                continue
            seen.add(oid)
            out.append({
                "title": title,
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={oid}",
                "points": hit.get("points") or 0,
                "source": "Hacker News",
                "summary": "",
            })
    out.sort(key=lambda x: x["points"], reverse=True)
    return out[:limit]


def reddit_machinelearning(day: dt.date, limit: int = 4) -> list[dict]:
    """Reddit r/MachineLearning 当日帖子（排除 [P]/[D]/[R] 等标签）。"""
    start, end = _day_range(day)
    out: list[dict] = []
    try:
        data = _get("https://www.reddit.com/r/MachineLearning/new.json", headers=REDDIT_HEADERS).json()
    except requests.RequestException:
        return out
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        created = d.get("created_utc", 0)
        if not start <= created < end:
            continue
        title = (d.get("title") or "").strip()
        if not title or any(tag in title.lower() for tag in ("[p]", "[d]", "[r]", "[research]")):
            continue
        out.append({
            "title": title,
            "url": "https://www.reddit.com" + d.get("permalink", ""),
            "points": d.get("score", 0),
            "source": "Reddit r/MachineLearning",
            "summary": "",
        })
    out.sort(key=lambda x: x["points"], reverse=True)
    return out[:limit]


def arxiv_csai(day: dt.date, limit: int = 3) -> list[dict]:
    """arXiv cs.AI 当日新提交论文。"""
    day_str = day.strftime("%Y%m%d")
    params = {
        "search_query": "cat:cs.AI",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": "40",
    }
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    out: list[dict] = []
    try:
        feed = feedparser.parse(f"http://export.arxiv.org/api/query?{query}")
    except Exception:
        return out
    for entry in feed.entries:
        pub = (getattr(entry, "published", "") or "")[:10].replace("-", "")
        if pub != day_str:
            continue
        out.append({
            "title": re.sub(r"\s+", " ", (entry.get("title") or "")).strip(),
            "url": entry.get("link", ""),
            "points": 0,
            "source": "arXiv cs.AI",
            "summary": "",
        })
        if len(out) >= limit:
            break
    return out


_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def _rss_items(url: str, source: str, day: dt.date, limit: int) -> list[dict]:
    """抓取中文科技媒体 RSS 当日文章。

    用 requests 会话（浏览器 UA、自动处理重定向与 Cookie）先取回 XML，
    再交给 feedparser 解析，兼容带反爬 Cookie 校验的站点。
    """
    out: list[dict] = []
    try:
        resp = _get(url, headers={"User-Agent": _BROWSER_UA}, timeout=25)
        # 个别站点声明 UTF-8 但内容含无效字节（如新智元），严格解码失败时替换坏字节，
        # 避免 feedparser 回退解码导致中文标题乱码
        raw = resp.content
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
        feed = feedparser.parse(text)
    except Exception:
        return out
    for entry in feed.entries:
        parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if not parsed:
            continue
        pub_date = dt.datetime(*parsed[:6], tzinfo=dt.timezone.utc).date()
        if pub_date != day:
            continue
        out.append({
            "title": re.sub(r"\s+", " ", (entry.get("title") or "")).strip(),
            "url": entry.get("link", ""),
            "points": 0,
            "source": source,
            "summary": "",
        })
        if len(out) >= limit:
            break
    return out


NEWS_TARGET = 6  # 每日精选 AI 动态条数（约 5 条左右）


def ai_news() -> list[dict]:
    """聚合全部新闻源，返回昨日精选 AI 动态（约 6 条，来源均衡）。

    组成：Hacker News 2 条 + Reddit 1 条 + arXiv 1 条 + 中文源 2 条。
    任一来源失败时自动由其他来源补足。
    """
    day = _utc_yesterday()
    items: list[dict] = []
    items += hn_stories(day, limit=2)
    items += reddit_machinelearning(day, limit=1)
    items += arxiv_csai(day, limit=1)

    # 中文源按"源轮换"取 2 条，避免被单一来源刷屏
    cn_lists = [_rss_items(url, name, day, limit=2) for url, name in RSS_SOURCES]
    cn_pool: list[dict] = []
    for i in range(2):
        for lst in cn_lists:
            if i < len(lst):
                cn_pool.append(lst[i])
    items += cn_pool[:2]
    return items


# 供 generate_report.py 输出来源清单
RSS_NAMES = [name for _, name in RSS_SOURCES]
