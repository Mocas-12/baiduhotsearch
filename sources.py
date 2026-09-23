# -*- coding: utf-8 -*-
"""数据源注册表与抓取器。

每个 fetcher 返回统一 schema 的 list[dict]：
    {"rank": 排名, "title": 标题, "url": 链接, "desc": 简介, "heat": 热度(float|None)}
fetcher 只接收一个普通 dict 参数 cfg（由 app.py 从 session_state 组装），不依赖 streamlit：
    cfg = {"proxy": str|None, "insecure": bool, "sixty_base": str|None,
           "weibo_cookie": str|None}
任何失败直接抛异常，由上层决定降级策略。
"""
import random
import re
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote

import requests

# 60s API 官方公共实例限流较严，内置官方 + 社区双实例容灾；用户可在侧边栏覆盖
SIXTY_BASES = ["https://60s.viki.moe", "https://60s-api.viki.moe"]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")


def build_session(cfg: dict) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "*/*"})
    if cfg.get("proxy"):
        s.proxies.update({"http": cfg["proxy"], "https": cfg["proxy"]})
    if cfg.get("insecure"):
        s.verify = False
    return s


# ---------------------------------------------------------------- 60s API（国内主力）

def _sixty_get(cfg: dict, endpoint: str, timeout: int = 12):
    bases = ([cfg["sixty_base"]] if cfg.get("sixty_base") else []) + SIXTY_BASES
    last_err = None
    # 应用并行抓多个源时会同时打到同一实例，错峰 + 429 退避，避免触发限流
    time.sleep(random.uniform(0.3, 1.5))
    for base in dict.fromkeys(bases):  # 去重且保持顺序
        for attempt in (1, 2):
            try:
                r = build_session(cfg).get(f"{base}/v2/{endpoint}", timeout=timeout)
                if r.status_code == 429 and attempt == 1:
                    time.sleep(2.2)
                    continue
                r.raise_for_status()
                d = r.json()
                if d.get("code") == 200 and d.get("data"):
                    return d["data"]
                last_err = RuntimeError(f"60s API 返回异常：{d.get('code')}")
                break
            except Exception as e:
                last_err = e
                if "429" in str(e) and attempt == 1:
                    time.sleep(2.2)
                    continue
                break
    raise RuntimeError(f"60s API 全部实例不可用：{last_err}")


def _norm_items(raw_items, heat_key="hot_value", url_keys=("link", "url")):
    items = []
    for i, it in enumerate(raw_items):
        url = ""
        for k in url_keys:
            if it.get(k):
                url = it[k]
                break
        items.append({
            "rank": i + 1,
            "title": str(it.get("title") or "").strip(),
            "url": url,
            "desc": str(it.get("detail") or it.get("word_explain") or "").strip(),
            "heat": _to_heat(it.get(heat_key)),
        })
    return [it for it in items if it["title"]]


def _to_heat(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _collect(raw_items, title_of, url_of=lambda it, t: "", desc_of=lambda it, t: "",
             heat_of=lambda it, t: None, rank_of=None):
    """各源 fetcher 公共循环：空 title 跳过 + rank 递增 + 统一 schema 组装。

    title_of(it) 提取并清洗标题，返回空值则跳过该条；其余字段提取函数收
    (原始条目, title) 两个参数（微博/抖音/B站等 URL 由 title 拼出）。
    rank_of 为 None 时按已收集条数递增（1 起）；否则 rank_of(序号, 原始条目)，
    序号 = len(items)+1。字段名、热度解析、排序、截断等差异全部留在调用侧。
    """
    items = []
    for it in raw_items:
        title = title_of(it)
        if not title:
            continue
        seq = len(items) + 1
        items.append({
            "rank": rank_of(seq, it) if rank_of else seq,
            "title": title,
            "url": url_of(it, title),
            "desc": desc_of(it, title),
            "heat": heat_of(it, title),
        })
    return items


def fetch_weibo(cfg):
    # 配置了微博 Cookie 时直连官方接口（云端也能用），否则走 60s API
    return _chain(_weibo_direct, lambda c: _norm_items(_sixty_get(c, "weibo")))(cfg)


def _weibo_direct(cfg):
    cookie = (cfg.get("weibo_cookie") or "").strip()
    if not cookie:
        raise RuntimeError("未配置微博 Cookie")
    s = build_session(cfg)
    s.headers.update({"Cookie": cookie, "Referer": "https://weibo.com/",
                      "Accept": "application/json, text/plain, */*"})
    r = s.get("https://weibo.com/ajax/side/hotSearch", timeout=10)
    r.raise_for_status()
    d = r.json()
    realtime = (d.get("data") or {}).get("realtime") or []
    if d.get("error") or not realtime:
        raise RuntimeError("微博接口返回异常（Cookie 可能已过期）")
    return _collect(
        realtime,
        title_of=lambda it: str(it.get("word") or "").strip(),
        url_of=lambda it, w: f"https://s.weibo.com/weibo?q={quote(w)}",
        heat_of=lambda it, w: _to_heat(it.get("num")),
    )


def fetch_douyin(cfg):
    # ttwid 可自动注册（字节跳动设备标识），无需登录，数据中心 IP 也可用
    return _chain(_douyin_direct, lambda c: _norm_items(_sixty_get(c, "douyin")))(cfg)


def _douyin_direct(cfg):
    s = build_session(cfg)
    r = s.post("https://ttwid.bytedance.com/ttwid/union/register/",
               json={"region": "cn", "aid": 1768, "needFid": False,
                     "service": "www.ixigua.com",
                     "migrate_info": {"ticket": "", "source": "node"},
                     "cbUrlProtocol": "https", "union": True},
               timeout=10)
    r.raise_for_status()
    if not s.cookies.get("ttwid"):
        raise RuntimeError("ttwid 注册失败")
    r2 = s.get("https://www.douyin.com/aweme/v1/web/hot/search/list/?source=6",
               headers={"Referer": "https://www.douyin.com/"}, timeout=10)
    r2.raise_for_status()
    wl = ((r2.json().get("data") or {}).get("word_list")) or []
    items = _collect(
        wl,
        title_of=lambda it: str(it.get("word") or "").strip(),
        url_of=lambda it, w: f"https://www.douyin.com/search/{quote(w)}",
        heat_of=lambda it, w: _to_heat(it.get("hot_value")),
        rank_of=lambda seq, it: int(it.get("position") or seq),
    )
    items.sort(key=lambda x: x["rank"])
    return items


def _chain(*fns):
    """多通道容灾：依次尝试，全部失败才抛最后一个异常。"""
    def run(cfg):
        last = None
        for fn in fns:
            try:
                items = fn(cfg)
                if items:
                    return items
            except Exception as e:
                last = e
        raise RuntimeError(f"所有通道失败（{last}）")
    return run


def _toutiao_direct(cfg):
    r = build_session(cfg).get("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
                               timeout=10)
    r.raise_for_status()
    return _collect(
        r.json().get("data") or [],
        title_of=lambda it: str(it.get("Title") or "").strip(),
        url_of=lambda it, t: it.get("Url") or "",
        heat_of=lambda it, t: _to_heat(it.get("HotValue")),
    )


def _bilibili_direct(cfg):
    r = build_session(cfg).get("https://app.bilibili.com/x/v2/search/trending/ranking",
                               timeout=10)
    r.raise_for_status()
    lst = ((r.json().get("data") or {}).get("list")) or []
    return _collect(
        lst,
        title_of=lambda it: str(it.get("keyword") or it.get("show_name") or "").strip(),
        url_of=lambda it, kw: f"https://search.bilibili.com/all?keyword={quote(kw)}",
        heat_of=lambda it, kw: _to_heat(it.get("hot_score")),
        rank_of=lambda seq, it: it.get("position") or seq,
    )


def fetch_toutiao(cfg):
    # 直连官方接口优先（数据中心 IP 也能访问），60s API 兜底
    return _chain(_toutiao_direct, lambda c: _norm_items(_sixty_get(c, "toutiao")))(cfg)


def fetch_bilibili(cfg):
    return _chain(_bilibili_direct, lambda c: _norm_items(_sixty_get(c, "bili")))(cfg)


def _parse_cn_heat(text):
    """解析中文热度文案：「2678 万」→ 2.678e7，「1.2亿」→ 1.2e8，纯数字原样；失败 None。"""
    t = str(text or "")
    m = re.search(r"([\d.]+)\s*亿", t)
    if m:
        return float(m.group(1)) * 1e8
    m = re.search(r"([\d.]+)\s*万", t)
    if m:
        return float(m.group(1)) * 1e4
    m = re.search(r"([\d.]+)", t)
    return float(m.group(1)) if m else None


def fetch_zhihu(cfg):
    # 知乎数值热度在 hot_value_desc 文案（如「2678 万」）里，detail 作为简介
    return _collect(
        _sixty_get(cfg, "zhihu"),
        title_of=lambda it: str(it.get("title") or "").strip(),
        url_of=lambda it, t: it.get("link") or "",
        desc_of=lambda it, t: str(it.get("detail") or "").strip(),
        heat_of=lambda it, t: _parse_cn_heat(it.get("hot_value_desc")),
    )


# ---------------------------------------------------------------- 百度（直连，保留原有逻辑）

def fetch_baidu(cfg):
    # 接口里 content=真实排名榜，topContent=平台置顶（不算榜一）。
    # 置顶条目挪到末尾并标注，否则榜一名次会被置顶新闻顶掉。
    s = build_session(cfg)
    s.headers.update({"Referer": "https://top.baidu.com/",
                      "Accept": "application/json, text/plain, */*"})
    r = s.get("https://top.baidu.com/api/board?platform=pc&tab=realtime", timeout=10)
    r.raise_for_status()
    cards = r.json().get("data", {}).get("cards", [])
    ranked, pinned, seen = [], [], set()

    def collect(it, bucket):
        title = str(it.get("word") or it.get("name") or it.get("title") or "").strip()
        if not title or title in seen:
            return
        seen.add(title)
        bucket.append({
            "title": title,
            "url": it.get("url") or it.get("link") or "",
            "desc": str(it.get("desc") or it.get("brief") or "").strip(),
            "heat": _to_heat(it.get("hotScore") or it.get("heat")),
        })

    for card in cards:
        for it in card.get("content") or []:
            collect(it, ranked)
    for card in cards:
        for it in card.get("topContent") or []:
            collect(it, pinned)

    items = [{"rank": i + 1, **d} for i, d in enumerate(ranked)]
    for d in pinned:
        note = "📌 平台置顶（不计入排名）"
        d["desc"] = f"{d['desc']} {note}".strip()
        items.append({"rank": len(items) + 1, **d})
    return items


# ---------------------------------------------------------------- 国际（RSS / 开放接口）

def _parse_rss(text: str, max_items: int = 30, with_time: bool = False):
    """解析 RSS/Atom，返回 [(title, link, desc[, ts])]，CDATA 与命名空间均兼容。"""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(text.encode("utf-8"))  # 带 encoding 声明的 XML 必须传 bytes
    out = []
    for item in root.iter("item"):  # RSS 2.0
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        ts = _parse_rfc822(item.findtext("pubDate")) if with_time else None
        if title:
            out.append((title, link, desc, ts) if with_time else (title, link, desc))
        if len(out) >= max_items:
            return out
    for entry in root.findall("atom:entry", ns) or root.iter("entry"):  # Atom
        title = (entry.findtext("atom:title", namespaces=ns) or entry.findtext("title") or "").strip()
        link_el = entry.find("atom:link", ns)
        link = (link_el.get("href") if link_el is not None else "") or (entry.findtext("link") or "")
        desc = (entry.findtext("atom:summary", namespaces=ns) or entry.findtext("summary") or "").strip()
        ts = (_parse_rfc822(entry.findtext("atom:updated", namespaces=ns))
              or _parse_rfc822(entry.findtext("atom:published", namespaces=ns))) if with_time else None
        if title:
            out.append((title, link.strip(), desc, ts) if with_time else (title, link.strip(), desc))
        if len(out) >= max_items:
            return out
    return out


def _parse_rfc822(text: str):
    """RFC 822 时间 → epoch 秒；解析失败返回 None。"""
    if not text:
        return None
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(text.strip()).timestamp()
    except Exception:
        return None


def _rss_items(cfg, url, max_items=30, split_source_suffix=False):
    r = build_session(cfg).get(url, timeout=12)
    r.raise_for_status()
    rows = _parse_rss(r.text, max_items, with_time=True)
    items = []
    for i, (title, link, desc, ts) in enumerate(rows):
        if split_source_suffix:  # Google News 标题自带「 - 媒体名」后缀
            parts = title.rsplit(" - ", 1)
            if len(parts) == 2 and len(parts[1]) <= 20:
                title, desc = parts[0].strip(), parts[1].strip()
        # NYT 等源的 description 是 HTML 片段（<p><img...>），剥标签再压缩空白
        desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(desc or ""))).strip()[:140]
        items.append({"rank": i + 1, "title": title, "url": link,
                      "desc": desc, "heat": None, "time": ts})
    return items


def fetch_gnews(cfg):
    return _rss_items(cfg, "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
                      split_source_suffix=True)


def fetch_nyt(cfg):
    return _rss_items(cfg, "https://cn.nytimes.com/rss/")


# ---------------------------------------------------------------- 科技

def fetch_hackernews(cfg):
    r = build_session(cfg).get(
        "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30", timeout=12)
    r.raise_for_status()
    return _collect(
        r.json().get("hits", []),
        title_of=lambda h: (h.get("title") or "").strip(),
        url_of=lambda h, t: h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
        desc_of=lambda h, t: f"{h.get('author', '')} · 💬 {h.get('num_comments') or 0}" if h.get("author") else "",
        heat_of=lambda h, t: _to_heat(h.get("points")),
    )


def fetch_v2ex(cfg):
    r = build_session(cfg).get("https://www.v2ex.com/api/topics/hot.json", timeout=12)
    r.raise_for_status()
    return _collect(
        r.json(),
        title_of=lambda t: (t.get("title") or "").strip(),
        url_of=lambda t, title: t.get("url") or "",
        desc_of=lambda t, title: re.sub(r"<[^>]+>", "", t.get("content") or "").strip()[:120],
        heat_of=lambda t, title: _to_heat(t.get("replies")),
    )


def fetch_github(cfg):
    r = build_session(cfg).get("https://github.com/trending", timeout=15)
    r.raise_for_status()
    articles = re.findall(r'<article class="Box-row">(.*?)</article>', r.text, re.S)

    def repo_of(art):
        m = re.search(r'href="/([\w.-]+/[\w.-]+)"', art)
        return m.group(1) if m else ""  # 空值即跳过，等价于原「正则不匹配 continue」

    def desc_of(art, repo):
        dm = re.search(r'<p class="col-9[^"]*">\s*(.*?)\s*</p>', art, re.S)
        return (re.sub(r"<[^>]+>", "", dm.group(1)).strip() if dm else "")[:120]

    def heat_of(art, repo):
        sm = re.search(r"([\d,]+)\s*stars today", art)
        return _to_heat(sm.group(1).replace(",", "")) if sm else None

    return _collect(
        articles,
        title_of=repo_of,
        url_of=lambda art, repo: f"https://github.com/{repo}",
        desc_of=desc_of,
        heat_of=heat_of,
    )


# ---------------------------------------------------------------- 注册表

# cat: domestic=国内 world=国际 tech=科技；color 用于源徽章
SOURCES: dict = {
    "weibo":      {"name": "微博热搜",   "cat": "domestic", "color": "#e6162d", "fetch": fetch_weibo},
    "zhihu":      {"name": "知乎热榜",   "cat": "domestic", "color": "#0084ff", "fetch": fetch_zhihu},
    "baidu":      {"name": "百度热搜",   "cat": "domestic", "color": "#3936e3", "fetch": fetch_baidu},
    "douyin":     {"name": "抖音热点",   "cat": "domestic", "color": "#fe2c55", "fetch": fetch_douyin},
    "toutiao":    {"name": "今日头条",   "cat": "domestic", "color": "#f04142", "fetch": fetch_toutiao},
    "bilibili":   {"name": "B站热榜",    "cat": "domestic", "color": "#fb7299", "fetch": fetch_bilibili},
    "gnews":      {"name": "Google News", "cat": "world",   "color": "#4285f4", "fetch": fetch_gnews},
    "nyt":        {"name": "纽约时报中文网", "cat": "world", "color": "#000000", "fetch": fetch_nyt},
    "hackernews": {"name": "Hacker News", "cat": "tech",    "color": "#ff6600", "fetch": fetch_hackernews},
    "github":     {"name": "GitHub Trending", "cat": "tech", "color": "#6e5494", "fetch": fetch_github},
    "v2ex":       {"name": "V2EX",       "cat": "tech",     "color": "#1a1a1a", "fetch": fetch_v2ex},
}

CATEGORY_LABELS = {"domestic": "🇨🇳 国内", "world": "🌍 国际", "tech": "💻 科技"}


def sources_of(cat: str):
    return {k: v for k, v in SOURCES.items() if v["cat"] == cat}


def sample_items(source_key: str, topn: int = 20):
    name = SOURCES.get(source_key, {}).get("name", source_key)
    return [{"rank": i + 1, "title": f"示例·{name}热词 {i + 1}", "url": "",
             "desc": "这是示例数据，用于网络不可用时预览界面", "heat": float(1000 - i * 10)}
            for i in range(topn)]
