# -*- coding: utf-8 -*-
"""HOTRADAR · 全网热搜雷达 —— 国内热点 · 国际大事 · 科技动态，一页看清。

多源聚合架构：
    sources.py   数据源注册表与抓取器（统一 schema）
    aggregate.py 跨源交叉榜聚类
    store.py     SQLite 历史快照（新上榜 / 上榜时长）
    styles.py    主题样式（PULSE GLASS 苹果生态风）
"""
import html
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

import aggregate
import sources
import store
from styles import apply_theme

st.set_page_config(page_title="HOTRADAR · 全网热搜雷达", page_icon="📡",
                   layout="wide", initial_sidebar_state="collapsed")

CACHE_TTL = 900   # 成功结果缓存 15 分钟
FAIL_TTL = 120    # 失败/降级/示例结果短缓存：避免重跑时反复冲击已限流的接口，同时保证 2 分钟内自动重试
VIEW_LABELS = ["交叉榜", "国内", "国际", "科技"]
VIEW_KEYS = {"交叉榜": "cross", "国内": "domestic", "国际": "world", "科技": "tech"}
KEY_LABELS = {v: k for k, v in VIEW_KEYS.items()}
SECTION_META = {
    "cross": ("全网交叉焦点", "CROSS-SOURCE FOCUS · 按命中源数排序 · 不跨源比热度"),
    "domestic": ("国内热流", "DOMESTIC PULSE"),
    "world": ("国际动态", "GLOBAL PULSE"),
    "tech": ("科技雷达", "TECH PULSE"),
}
TICKER_KEYS = ("weibo", "zhihu", "baidu", "douyin")


# ---------------------------------------------------------------- 基础工具

def _fmt_age(sec: float) -> str:
    return f"{int(sec // 60)} 分钟前" if sec < 3600 else f"{sec / 3600:.1f} 小时前"


def _cfg() -> dict:
    return {
        "proxy": st.session_state.get("proxy_url", "").strip()
        if st.session_state.get("proxy_enabled") else None,
        "insecure": bool(st.session_state.get("insecure_ssl")),
        "sixty_base": (st.session_state.get("sixty_base") or "").strip() or None,
        "weibo_cookie": (st.session_state.get("weibo_cookie") or "").strip() or None,
    }


def _luma(color: str, floor: float = 0.30, boost: float = 0.62) -> str:
    """过暗的源色（如 V2EX #1a1a1a）在深底上不可见，按需向白色提亮。"""
    c = str(color).lstrip("#")
    if len(c) == 3:
        c = "".join(x * 2 for x in c)
    try:
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    except ValueError:
        return "#9aa3b8"
    if (0.299 * r + 0.587 * g + 0.114 * b) / 255 < floor:
        r = int(r + (255 - r) * boost)
        g = int(g + (255 - g) * boost)
        b = int(b + (255 - b) * boost)
    return f"#{r:02x}{g:02x}{b:02x}"


def _src_badge(name: str, color: str) -> str:
    return f'<span class="src-badge" style="--c:{_luma(color)}"><i></i>{html.escape(name)}</span>'


# ---------------------------------------------------------------- 数据获取（每源缓存 + 失败降级）

def _fetch_one(key: str, cfg: dict, use_sample: bool, cached: Optional[dict]) -> dict:
    """纯函数（不访问 session_state，可安全跑在线程池里）：抓单源并附带历史标记。

    降级链：实时抓取 → 本会话旧缓存 → SQLite 最近快照（≤24h）→ 示例数据 → 失败。
    """
    try:
        items = sources.SOURCES[key]["fetch"](cfg)
        if not items:
            raise RuntimeError("接口返回空数据")
        try:  # 先查旧历史再写快照，顺序不能反，否则「新上榜」永远不触发
            marks = store.first_seen_many(key, [it["title"] for it in items[:60]])
            store.save_snapshot(key, items)
            for it in items:
                it["_first_seen"] = marks.get(it["title"])
        except Exception:
            pass
        return {"ok": True, "items": items, "stale": False, "ts": time.time()}
    except Exception as e:
        if cached and cached.get("items"):
            return {"ok": True, "items": cached["items"], "stale": True,
                    "ts": cached["ts"], "error": str(e)}
        try:  # SQLite 兜底：库里有 ≤24h 内的快照就展示，交叉榜不因个别源限流而残缺
            snap_ts, snap_items = store.last_snapshot(key)
            if snap_items:
                for it in snap_items:
                    it["_first_seen"] = snap_ts
                return {"ok": True, "items": snap_items, "stale": True,
                        "ts": snap_ts.timestamp(), "error": str(e)}
        except Exception:
            pass
        if use_sample:
            return {"ok": False, "items": sources.sample_items(key),
                    "sample": True, "ts": time.time(), "error": str(e)}
        return {"ok": False, "items": [], "ts": time.time(), "error": str(e)}


def _cache_kind(res: dict) -> str:
    if res.get("sample"):
        return "sample"
    if res.get("stale"):
        return "stale"
    return "ok" if res.get("ok") and res.get("items") else "fail"


def get_sources(keys: list, force: bool = False) -> dict:
    """批量获取，返回 {source_key: result}。

    缓存分四类：ok 按 CACHE_TTL；stale/fail/sample 按 FAIL_TTL 短缓存——
    既不反复冲击限流接口，又保证 2 分钟后自动重试。force=True 时全部重抓。
    """
    cache_all = st.session_state.setdefault("data_cache", {})
    results = {}
    todo = []
    now = time.time()
    for k in keys:
        c = cache_all.get(k)
        if c and not force and now - c["ts"] < (CACHE_TTL if c.get("kind") == "ok" else FAIL_TTL):
            kind = c.get("kind", "ok")
            res = {"ok": kind in ("ok", "stale"), "items": c.get("items", []),
                   "stale": kind == "stale", "ts": c["ts"]}
            if kind == "sample":
                res["sample"] = True
                res["ok"] = False
            results[k] = res
            continue
        todo.append(k)
    if todo:
        cfg, use_sample = _cfg(), st.session_state.get("use_sample", False)
        with ThreadPoolExecutor(max_workers=4) as ex:  # 4 并发 + 60s API 错峰，控制对公共实例的瞬时压力
            futs = {ex.submit(_fetch_one, k, cfg, use_sample, cache_all.get(k)): k for k in todo}
            for fut in as_completed(futs):
                k = futs[fut]
                try:
                    res = fut.result()
                except Exception as e:
                    res = {"ok": False, "items": [], "ts": time.time(), "error": str(e)}
                results[k] = res
                cache_all[k] = {"ts": res["ts"], "items": res.get("items") or [],
                                "kind": _cache_kind(res)}
    return results


def _view_sources(view_key: str) -> list:
    if view_key == "cross":
        return list(sources.SOURCES.keys())
    return list(sources.sources_of(view_key).keys())


# ---------------------------------------------------------------- 榜单渲染（行式，单个 st.markdown 输出保证前三名渐变生效）

def _word_parts(item: dict) -> tuple:
    """词条/简介/链接三元组。简介折叠成单行，避免 st.markdown 按空行拆碎卡片 HTML。"""
    word = re.sub(r"\s+", " ", str(item.get("title") or "未知词条")).strip()
    desc = re.sub(r"\s+", " ", str(item.get("desc") or "")).strip()
    link = str(item.get("url") or "").strip()
    desc_html = f'<div class="hdesc" title="{html.escape(desc)}">{html.escape(desc)}</div>' if desc else ""
    return html.escape(word), desc_html, link


def _onboard_meta(item: dict) -> str:
    fs = item.get("_first_seen")
    if fs is None:
        return '<span class="tag-new">NEW 上榜</span>'
    hours = max(0.0, (time.time() - fs.timestamp()) / 3600)
    label = f"在榜 {hours:.0f} 小时" if hours >= 1 else "在榜不足 1 小时"
    return f'<span class="onboard">{label}</span>'


def _row(rank: int, word: str, desc_html: str, pills_html: str, meta_html: str, link: str) -> str:
    href = f' href="{html.escape(link, quote=True)}"' if link else ""
    rank_cls = {1: " r1", 2: " r2", 3: " r3"}.get(rank, "")
    return (f'<a class="hs-row"{href} target="_blank" rel="noopener">'
            f'<span class="rank{rank_cls}">{rank}</span>'
            f'<span class="hmain"><div class="hword">{word}</div>{desc_html}{pills_html}</span>'
            f'<span class="hmeta">{meta_html}</span></a>')


def _panel(meta_line: str, view_key: str, thead: str, rows: list,
           empty_title: str, empty_sub: str):
    title, sub = SECTION_META[view_key]
    head = (f'<div class="hs-section">{title}<span class="sub">{sub}</span></div>')
    if not rows:
        body = (f'{head}<div class="hs-empty">'
                f'<div class="etitle">{empty_title}</div>'
                f'<div class="esub">{empty_sub}</div></div>')
    else:
        body = f'{head}{thead}{"".join(rows)}'
    st.markdown(meta_line + f'<div class="hs-panel">{body}</div>', unsafe_allow_html=True)


def render_meta_line(results: dict, keys: list, view_label: str, n_items: int, n_sources: int,
                     item_label: str = "已收录"):
    parts = []
    tss = [r["ts"] for k, r in results.items() if k in keys and r.get("ok")]
    if tss:
        parts.append(f'更新于 <b>{datetime.fromtimestamp(max(tss)).strftime("%H:%M:%S")}</b>')
    parts.append(f'{item_label} <b>{n_items}</b> 条')
    parts.append(f'<b>{n_sources}</b> 个数据源在线')
    parts.append(html.escape(view_label))
    st.markdown('<div class="hs-meta-line"><span class="dot"></span>' + " · ".join(parts) + "</div>",
                unsafe_allow_html=True)


def _warn_states(results: dict, keys: list):
    stale = [(k, r) for k, r in results.items() if k in keys and r.get("stale")]
    samples = [k for k, r in results.items() if k in keys and r.get("sample")]
    failed = [sources.SOURCES[k]["name"] for k in keys
              if not results.get(k, {}).get("ok") or not results.get(k, {}).get("items")]
    if stale:
        names = "、".join(sources.SOURCES[k]["name"] for k, _ in stale)
        ages = "、".join(_fmt_age(time.time() - r["ts"]) for _, r in stale)
        st.warning(f"{names} 实时数据拉取失败，显示的是 {ages} 的缓存快照")
    if samples:
        st.info(f"{'、'.join(sources.SOURCES[k]['name'] for k in samples)} 暂时不可用，正在显示示例数据")
    if failed:
        st.caption(f"以下数据源暂时不可用：{'、'.join(failed)}")


# ---------------------------------------------------------------- 分类视图（单源 / 全部混合流）

def render_category(view_key: str, sub: str, topn: int, force: bool):
    all_keys = _view_sources(view_key)
    keys = all_keys if sub == "全部" else [k for k in all_keys if sources.SOURCES[k]["name"] == sub]
    results = get_sources(keys, force=force)
    _warn_states(results, keys)

    if sub == "全部":  # 多源按名次轮播交错，形成「混合热流」
        lists = [results[k]["items"] for k in keys if results.get(k, {}).get("ok")]
        interleaved = []
        for r in range(max((len(l) for l in lists), default=0)):
            for lst in lists:
                if r < len(lst):
                    interleaved.append(lst[r])
        shown = interleaved[:topn]
        n_sources = len(lists)
    else:
        shown = (results.get(keys[0], {}).get("items") or [])[:topn] if keys else []
        n_sources = 1 if shown else 0

    render_meta_line(results, keys, f"{KEY_LABELS[view_key]} · {sub}", len(shown), n_sources)

    rows = []
    for i, it in enumerate(shown, 1):
        src_key = keys[0] if sub != "全部" else _find_source_key(results, it)
        src_meta = sources.SOURCES.get(src_key) if src_key else None
        badge = _src_badge(src_meta["name"], src_meta["color"]) if src_meta else ""
        pills = f'<div class="pill-row">{badge}</div>' if badge else ""
        word, desc_html, link = _word_parts(it)
        rows.append(_row(i, word, desc_html, pills, _onboard_meta(it), link))

    _panel("", view_key,
           '<div class="hs-thead"><span>词条</span><span class="r">在榜状态</span></div>',
           rows, "暂时没有拿到数据",
           "点击「立即刷新」重试，或稍后再来看看")


def _find_source_key(results: dict, item: dict) -> Optional[str]:
    for k, res in results.items():
        for it in res.get("items", []):
            if it is item:
                return k
    return None


# ---------------------------------------------------------------- 交叉榜视图

def render_cross(topn: int, force: bool):
    keys = _view_sources("cross")
    results = get_sources(keys, force=force)
    _warn_states(results, keys)

    # 各源内部的最大热度（统一口径用：词条的榜内相对位置 = heat / 源内最大值）
    src_max = {k: max((it.get("heat") or 0 for it in r.get("items", [])), default=0)
               for k, r in results.items()}
    all_items = []
    for k, res in results.items():
        if res.get("ok"):
            for it in res["items"]:
                heat = it.get("heat") or 0
                rel = heat / src_max[k] if heat and src_max.get(k) else 0.0
                all_items.append({**it, "source": k, "source_name": sources.SOURCES[k]["name"],
                                  "rel": round(rel, 4)})

    # 聚类较重，仅当输入快照变化时重算
    sig = tuple(sorted((k, round(r["ts"], 2)) for k, r in results.items() if r.get("ok")))
    if st.session_state.get("cross_sig") != sig:
        st.session_state["cross_clusters"] = aggregate.build_clusters(all_items)
        st.session_state["cross_sig"] = sig
    clusters = st.session_state.get("cross_clusters") or []

    ok_sources = len([k for k, r in results.items() if r.get("ok") and r.get("items")])
    render_meta_line(results, keys, "全网交叉榜", len(clusters), ok_sources, item_label="交叉话题")

    if not clusters:
        down = [sources.SOURCES[k]["name"] for k in keys
                if not (results.get(k, {}).get("ok") and results.get(k, {}).get("items"))]
        if down:
            st.warning(
                f"暂时没有交叉话题：当前有 {len(down)} 个源不可用（{'、'.join(down)}），"
                f"命中源越少，能配对的交叉话题就越少。可点击「立即刷新」重试；"
                f"若公共实例持续限流，可在侧边栏填入自部署 60s API 实例地址。")
        else:
            st.info("暂时没有发现跨源同热的焦点事件（各榜单可能还没对齐，稍后再试试）")

    name_to_key = {v["name"]: k for k, v in sources.SOURCES.items()}
    rows = []
    for i, c in enumerate(clusters[:topn], 1):
        seen, badges = set(), []
        for m_name, _m in c["members"]:
            if m_name in seen:
                continue
            seen.add(m_name)
            src_key = name_to_key.get(m_name)
            if src_key:
                badges.append(_src_badge(m_name, sources.SOURCES[src_key]["color"]))
        pills = f'<div class="pill-row">{"".join(badges)}</div>' if badges else ""
        meta = f'<span class="hit"><b>×{len(c["sources"])}</b><i>源命中</i></span>'
        word, desc_html, link = _word_parts(c)
        rows.append(_row(i, word, desc_html, pills, meta, link))

    _panel("", "cross",
           '<div class="hs-thead"><span>话题</span><span class="r">命中源</span></div>',
           rows, "暂时没有交叉话题",
           "各榜单对齐需要时间，稍后再试试")


# ---------------------------------------------------------------- 顶部：导航 / 跑马灯 / 标题

def render_nav():
    st.markdown(
        """
        <div class="hs-nav"><div class="hs-nav-inner">
          <span class="hs-logo">
            <span class="hs-logo-mark"></span>
            <span class="hs-logo-word">HOTRADAR</span>
            <span class="hs-logo-sub">LIVE</span>
          </span>
          <span class="spacer"></span>
          <a href="https://s.weibo.com/top/summary" target="_blank">微博</a>
          <a href="https://top.baidu.com/board" target="_blank">百度</a>
          <a href="https://www.zhihu.com/hot" target="_blank">知乎</a>
          <a href="https://news.ycombinator.com/" target="_blank">Hacker News</a>
          <a href="https://github.com/trending" target="_blank">GitHub</a>
        </div></div>
        """,
        unsafe_allow_html=True,
    )


def _warm_ticker_cache():
    """跑马灯预热：缓存全空时先抓 4 个国内源（与主视图共享缓存），
    让跑马灯首帧就有内容滚动；已有点位则直接返回，不加首屏延迟。"""
    cache = st.session_state.get("data_cache") or {}
    if any(cache.get(k, {}).get("kind") in ("ok", "stale") for k in TICKER_KEYS):
        return
    try:
        get_sources(list(TICKER_KEYS), force=False)
    except Exception:
        pass


@st.fragment(run_every="60s")
def render_ticker():
    """跑马灯：只读会话缓存，不触发抓取——首帧不阻塞，数据就绪后自动填充。"""
    cache = st.session_state.get("data_cache") or {}
    parts = []
    for k in TICKER_KEYS:
        c = cache.get(k)
        if not c or c.get("kind") not in ("ok", "stale"):
            continue
        name = sources.SOURCES[k]["name"].replace("热搜", "").replace("热点", "").replace("热榜", "")
        for it in (c.get("items") or [])[:2]:
            w = re.sub(r"\s+", " ", str(it.get("title") or "")).strip()
            if w:
                parts.append(f'<span class="ti"><b>{html.escape(name)}</b>'
                             f'<strong>{html.escape(w)}</strong></span>')
    if not parts:
        st.markdown('<div class="hs-ticker"><div class="hs-ticker-track static">'
                    '<span class="ti">正在同步全网热搜 · 首屏加载约几秒，稍候片刻…</span>'
                    "</div></div>",
                    unsafe_allow_html=True)
        return
    seq = "".join(parts)
    st.markdown(f'<div class="hs-ticker"><div class="hs-ticker-track">{seq}{seq}</div></div>',
                unsafe_allow_html=True)


def render_hero(n_sources: int) -> bool:
    head_l, head_r = st.columns([4, 1], vertical_alignment="center")
    with head_l:
        st.markdown(f'<div class="hs-overline"><span class="dot"></span>'
                    f'LIVE · {n_sources} 源实时聚合</div>', unsafe_allow_html=True)
        st.markdown('<div class="hs-h1">全网热搜雷达</div>', unsafe_allow_html=True)
        st.markdown('<div class="hs-tagline">国内热点 · 国际大事 · 科技动态 —— 一页看清全网正在发生的事</div>',
                    unsafe_allow_html=True)
    with head_r:
        return st.button("↻ 立即刷新", type="primary", use_container_width=True)


# ---------------------------------------------------------------- 侧边栏

def render_sidebar():
    env_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or ""
    st.session_state.setdefault("use_sample", False)
    st.session_state.setdefault("proxy_enabled", bool(env_proxy))
    st.session_state.setdefault("proxy_url", env_proxy)
    st.session_state.setdefault("sixty_base", "")
    st.session_state.setdefault("weibo_cookie", "")

    with st.sidebar:
        st.header("设置")
        st.checkbox("使用示例数据（无网络预览）", key="use_sample")
        with st.expander("网络与数据接口", expanded=False):
            st.caption("国内源经 60s API 聚合获取；百度源直连 top.baidu.com，海外网络通常需配置代理。")
            st.text_input("60s API 实例（可选，留空用内置实例）",
                          key="sixty_base", placeholder="https://your-instance.example.com")
            st.text_input("微博 Cookie（可选，填 SUB=... 后微博直连）",
                          key="weibo_cookie",
                          placeholder="登录 weibo.com 后从浏览器复制",
                          type="password")
            st.checkbox("启用代理", key="proxy_enabled")
            st.text_input("HTTPS 代理（示例：https://1.2.3.4:8080）", key="proxy_url")
            st.checkbox("忽略 SSL 证书验证（拦截代理需开启）", key="insecure_ssl", value=False)
            cols = st.columns(2)
            with cols[0]:
                test = st.button("测试连接")
            with cols[1]:
                auto = st.button("一键选代理")
            if test:
                ok = _probe_url("https://top.baidu.com/api/board?platform=pc&tab=realtime")
                if ok:
                    st.success("连接正常")
                else:
                    st.error("无法连接百度接口，可能需要代理或稍后重试")
            if auto:
                _auto_pick_proxy(env_proxy)

        with st.expander("数据源诊断", expanded=False):
            st.caption("并行探测全部数据源，检查可用性与耗时（不影响缓存）。")
            if st.button("运行诊断"):
                cfg = _cfg()
                rows = []
                with ThreadPoolExecutor(max_workers=6) as ex:
                    futs = {ex.submit(_probe_source, k, cfg): k for k in sources.SOURCES}
                    for fut in as_completed(futs):
                        rows.append(fut.result())
                order = {k: i for i, k in enumerate(sources.SOURCES)}
                rows.sort(key=lambda r: order.get(r["源 key"], 99))
                st.dataframe([{k: v for k, v in r.items() if k != "源 key"} for r in rows],
                             width="stretch", hide_index=True)
        st.caption("数据均来自各平台公开榜单，仅供个人学习与信息浏览。")


def _probe_url(url: str) -> bool:
    try:
        r = sources.build_session(_cfg()).get(url, timeout=8)
        return r.status_code < 400
    except Exception:
        return False


def _probe_source(key: str, cfg: dict) -> dict:
    meta = sources.SOURCES[key]
    t0 = time.time()
    try:
        items = meta["fetch"](cfg)
        status, count = "✅ 正常", len(items)
    except Exception as e:
        status, count = f"❌ {str(e)[:40]}", 0
    return {"源": meta["name"], "分类": sources.CATEGORY_LABELS.get(meta["cat"], ""),
            "状态": status, "条数": count, "耗时s": round(time.time() - t0, 2), "源 key": key}


def _auto_pick_proxy(env_proxy: str):
    import requests
    candidates = ([env_proxy] if env_proxy else []) + [
        "https://127.0.0.1:7890", "http://127.0.0.1:7890",
        "socks5h://127.0.0.1:1080", "https://127.0.0.1:1080", "http://127.0.0.1:1080",
        "http://127.0.0.1:8889", "http://127.0.0.1:8080",
    ]
    for proxy in [None] + candidates:  # 先试直连
        try:
            s = requests.Session()
            s.headers.update({"User-Agent": sources.UA})
            if proxy:
                s.proxies.update({"http": proxy, "https": proxy})
            r = s.get("https://top.baidu.com/api/board?platform=pc&tab=realtime", timeout=8)
            if r.status_code == 200 and "data" in r.text:
                if proxy:
                    st.session_state["proxy_enabled"] = True
                    st.session_state["proxy_url"] = proxy
                    os.environ["HTTPS_PROXY"] = proxy
                    os.environ["https_proxy"] = proxy
                    st.success(f"已选择代理：{proxy}")
                else:
                    st.session_state["proxy_enabled"] = False
                    st.session_state["proxy_url"] = ""
                    st.success("直连可用，已关闭代理")
                return
        except Exception:
            continue
    st.error("未找到可用代理，请手动填写再试")


# ---------------------------------------------------------------- 页脚

def render_counter():
    components.html(
        """
        <style>body{background:transparent;margin:0;}</style>
        <div style="color: #6b7285; font-family: ui-monospace, Consolas, monospace; font-size: 11.5px;">
            <span id="busuanzi_container_site_pv" style="display:none">
                总浏览量 <span id="busuanzi_value_site_pv" style="font-weight:bold; color:#f0c75e;"></span>
            </span>
            <span style="margin: 0 10px; color: #323a4e;">|</span>
            <span id="busuanzi_container_site_uv" style="display:none">
                独立访客 <span id="busuanzi_value_site_uv" style="font-weight:bold; color:#f0c75e;"></span>
            </span>
        </div>
        <script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
        """,
        height=40,
    )


def render_footer():
    st.markdown(
        '<div class="hs-footer">数据来自各平台公开榜单，仅供个人学习与信息浏览 · '
        'HOTRADAR by <a href="mailto:a18577y@gmail.com">Unlimited Box</a></div>',
        unsafe_allow_html=True,
    )
    render_counter()


# ---------------------------------------------------------------- 页面骨架

def main():
    apply_theme()
    render_sidebar()
    render_nav()
    _warm_ticker_cache()
    render_ticker()

    force = render_hero(len(sources.SOURCES))

    cols = st.columns([2.4, 1], vertical_alignment="center")
    with cols[0]:
        view_label = st.radio("视图", VIEW_LABELS, horizontal=True, label_visibility="collapsed")
    with cols[1]:
        topn = st.slider("显示数量", 10, 50, 30, 5)

    view_key = VIEW_KEYS[view_label]
    if view_key == "cross":
        render_cross(topn, force)
    else:
        names = [sources.SOURCES[k]["name"] for k in _view_sources(view_key)]
        sub = st.radio("数据源", ["全部"] + names, horizontal=True, label_visibility="collapsed")
        render_category(view_key, sub, topn, force)

    render_footer()


if __name__ == "__main__":
    main()
