# -*- coding: utf-8 -*-
"""全网热搜雷达 —— 国内热点 · 国际大事 · 科技动态，一页看清。

多源聚合架构：
    sources.py   数据源注册表与抓取器（统一 schema）
    aggregate.py 跨源交叉榜聚类
    store.py     SQLite 历史快照（新上榜 / 上榜时长）
    styles.py    主题样式
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

st.set_page_config(page_title="全网热搜雷达", layout="wide", initial_sidebar_state="collapsed")

CACHE_TTL = 900   # 成功结果缓存 15 分钟
FAIL_TTL = 120    # 失败/降级/示例结果短缓存：避免重跑时反复冲击已限流的接口，同时保证 2 分钟内自动重试
VIEW_LABELS = ["交叉榜", "国内", "国际", "科技"]
VIEW_KEYS = {"交叉榜": "cross", "国内": "domestic", "国际": "world", "科技": "tech"}
KEY_LABELS = {v: k for k, v in VIEW_KEYS.items()}


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


def _pill(color: str, label: str) -> str:
    return f'<span class="src-badge" style="background:{color};opacity:0.92">{html.escape(label)}</span>'


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


# ---------------------------------------------------------------- 公共渲染

def _rank_badge(rank: int) -> str:
    cls = {1: "rank r1", 2: "rank r2", 3: "rank r3"}.get(rank, "rank")
    return f'<div class="{cls}">{rank}</div>'


def _tag_pills(item: dict) -> str:
    fs = item.get("_first_seen")
    if fs is None:
        return '<div class="pill-row"><span class="tag-badge new">🆕 新上榜</span></div>'
    hours = max(0.0, (time.time() - fs.timestamp()) / 3600)
    label = f"⏱ 在榜 {hours:.0f} 小时" if hours >= 1 else "⏱ 在榜不足 1 小时"
    return f'<div class="pill-row"><span class="tag-badge">{label}</span></div>'


def _card_shell(rank: int, pill_html: str, word_html: str, desc_html: str, tail_html: str):
    st.markdown(
        f'<div class="hot-card{" top1" if rank == 1 else ""}" style="--i:{min(rank - 1, 25)}">'
        f'{_rank_badge(rank)}'
        f'<div class="hot-main">{pill_html}{word_html}{desc_html}{tail_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _word_desc_html(item: dict):
    # 简介若含换行/空行，st.markdown 会按 Markdown 段落拆碎卡片 HTML，必须折叠成单行
    word = re.sub(r"\s+", " ", str(item.get("title") or "未知词条")).strip()
    desc = re.sub(r"\s+", " ", str(item.get("desc") or "")).strip()
    link = str(item.get("url") or "").strip()
    if link:
        word_html = (f'<a class="hot-word" href="{html.escape(link, quote=True)}" '
                     f'target="_blank" rel="noopener">{html.escape(word)}</a>')
    else:
        word_html = f'<span class="hot-word">{html.escape(word)}</span>'
    desc_html = f'<div class="hot-desc" title="{html.escape(desc)}">{html.escape(desc)}</div>' if desc else ""
    return word_html, desc_html


def render_meta_chips(results: dict, keys: list, view_label: str, n_items: int, n_sources: int,
                      item_label: str = "已收录"):
    chips = []
    tss = [r["ts"] for k, r in results.items() if k in keys and r.get("ok")]
    if tss:
        chips.append(f'<span class="meta-chip">🕒 更新于 <b>{datetime.fromtimestamp(max(tss)).strftime("%H:%M:%S")}</b></span>')
    chips.append(f'<span class="meta-chip">📊 {item_label} <b>{n_items}</b></span>')
    chips.append(f'<span class="meta-chip">🛰 <b>{n_sources}</b> 个数据源</span>')
    chips.append(f'<span class="meta-chip">🏷 {html.escape(view_label)}</span>')
    st.markdown('<div class="meta-row">' + "".join(chips) + "</div>", unsafe_allow_html=True)


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
        st.caption(f"⚠️ 以下数据源暂时不可用：{'、'.join(failed)}")


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

    render_meta_chips(results, keys, f"{KEY_LABELS[view_key]} · {sub}", len(shown), n_sources)

    if not shown:
        st.info("暂无数据，请点击「获取最新数据」或稍后再试")
        return

    for i, it in enumerate(shown, 1):
        src_key = keys[0] if sub != "全部" else _find_source_key(results, it)
        src_meta = sources.SOURCES.get(src_key) if src_key else None
        pill_html = _pill(src_meta["color"], src_meta["name"]) if src_meta else ""
        pill_html = f'<div class="pill-row">{pill_html}</div>' if pill_html else ""
        word_html, desc_html = _word_desc_html(it)
        _card_shell(i, pill_html, word_html, desc_html, _tag_pills(it))


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
    render_meta_chips(results, keys, "全网交叉榜", len(clusters), ok_sources, item_label="⚡ 交叉话题")

    if not clusters:
        down = [sources.SOURCES[k]["name"] for k in keys
                if not (results.get(k, {}).get("ok") and results.get(k, {}).get("items"))]
        if down:
            st.warning(
                f"暂时没有交叉话题：当前有 {len(down)} 个源不可用（{'、'.join(down)}），"
                f"命中源越少，能配对的交叉话题就越少。可点击「获取最新数据」重试；"
                f"若公共实例持续限流，可在侧边栏填入自部署 60s API 实例地址。")
        else:
            st.info("暂时没有发现跨源同热的焦点事件（各榜单可能还没对齐，稍后再试试）")
        return

    st.caption(f"以下 {min(len(clusters), topn)} 个话题正被 ≥{aggregate.MIN_CLUSTER} 个数据源同时关注，"
               f"按命中源数量排序（同源数按综合热度，统一口径为各源榜内相对位置，不展示跨源热度数字）")
    shown = clusters[:topn]
    name_to_key = {v["name"]: k for k, v in sources.SOURCES.items()}
    for i, c in enumerate(shown, 1):
        seen, pills = set(), []
        for m_name, _m in c["members"]:
            if m_name in seen:
                continue
            seen.add(m_name)
            src_key = name_to_key.get(m_name)
            if src_key:
                pills.append(_pill(sources.SOURCES[src_key]["color"], m_name))
        pills.append(f'<span class="tag-badge">⚡ {len(c["sources"])} 源命中</span>')
        pill_html = f'<div class="pill-row">{"".join(pills)}</div>'
        word_html, desc_html = _word_desc_html(c)
        _card_shell(i, pill_html, word_html, desc_html, "")


# ---------------------------------------------------------------- 侧边栏

def render_sidebar():
    env_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or ""
    st.session_state.setdefault("use_sample", False)
    st.session_state.setdefault("proxy_enabled", bool(env_proxy))
    st.session_state.setdefault("proxy_url", env_proxy)
    st.session_state.setdefault("sixty_base", "")
    st.session_state.setdefault("weibo_cookie", "")

    with st.sidebar:
        st.header("⚙️ 设置")
        st.checkbox("使用示例数据（无网络预览）", key="use_sample")
        with st.expander("🌐 网络与数据接口", expanded=False):
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

        with st.expander("🩺 数据源诊断", expanded=False):
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


# ---------------------------------------------------------------- 页面骨架

def render_hero():
    n = len(sources.SOURCES)
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-badge"><span class="live-dot"></span>LIVE · {n} 源实时聚合</div>
          <h1 class="hero-title"><span class="flame">🔥</span>全网<span class="grad">热搜雷达</span></h1>
          <p class="hero-sub">国内热点 · 国际大事 · 科技动态 —— 一页看清全网正在发生的事</p>
          <div class="hero-rule"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_author_badge():
    st.markdown(
        """
        <div class="author-badge">
          作者：Unlimited Box&nbsp;&nbsp;|&nbsp;&nbsp;邮箱：<a href="mailto:a18577y@gmail.com">a18577y@gmail.com</a>
        </div>
        <style>
        .author-badge{
          position: fixed; left: 16px; bottom: 16px;
          background: rgba(20,22,32,0.78);
          border: 1px solid rgba(255,255,255,0.10);
          color: #c9cdd9; padding: 9px 15px; border-radius: 999px;
          font-size: 12.5px; z-index: 9999;
          box-shadow: 0 10px 28px rgba(0,0,0,0.4); backdrop-filter: blur(10px);
        }
        .author-badge a{ color: #ffb37e; text-decoration: none; }
        .author-badge a:hover{ text-decoration: underline; }
        @media (max-width: 640px){
          .author-badge{ left: 8px; bottom: 8px; font-size: 12px; padding: 6px 12px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_counter():
    components.html(
        """
        <style>body{background:transparent;margin:0;}</style>
        <div style="color: #8f96ab; font-family: sans-serif; font-size: 13px; text-align: center;">
            <span id="busuanzi_container_site_pv" style="display:none">
                总浏览量: <span id="busuanzi_value_site_pv" style="font-weight:bold; color:#ff9a3c;"></span> 次
            </span>
            <span style="margin: 0 10px; color: #3c4152;">|</span>
            <span id="busuanzi_container_site_uv" style="display:none">
                独立访客: <span id="busuanzi_value_site_uv" style="font-weight:bold; color:#ff9a3c;"></span> 人
            </span>
        </div>
        <script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
        """,
        height=50,
    )


def main():
    apply_theme()
    render_sidebar()
    render_hero()

    cols = st.columns([0.85, 2.05, 1.0])
    with cols[0]:
        topn = st.slider("显示数量", 10, 50, 30, 5)
    with cols[1]:
        view_label = st.radio("视图", VIEW_LABELS, horizontal=True, label_visibility="collapsed")
    with cols[2]:
        refresh = st.button("🔄 获取最新数据", type="primary", use_container_width=True)

    view_key = VIEW_KEYS[view_label]
    if view_key == "cross":
        render_cross(topn, refresh)
    else:
        names = [sources.SOURCES[k]["name"] for k in _view_sources(view_key)]
        sub = st.radio("数据源", ["全部"] + names, horizontal=True, label_visibility="collapsed")
        render_category(view_key, sub, topn, refresh)

    render_author_badge()
    render_counter()


if __name__ == "__main__":
    main()
