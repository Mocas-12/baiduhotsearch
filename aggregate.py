# -*- coding: utf-8 -*-
"""跨源交叉榜：把多个数据源里报道同一件事的词条聚成一簇。

思路：标题归一化后做相似度匹配（difflib 序列匹配 + 包含关系判定），
任意词条与已有簇代表命中即归入该簇。簇按「命中源数量 → 最高热度」排序。
"""
import re
from difflib import SequenceMatcher

_PUNCT = re.compile(r"[\s\W_【】《》「」『』·—～！？。，：；""'']+", re.UNICODE)

# 相似度阈值：中文标题普遍较短且带后缀修饰，0.55 能聚合同事件不同措辞
THRESHOLD = 0.55
MIN_CLUSTER = 2  # 至少命中几个不同源才算交叉热点


def normalize_title(title: str) -> str:
    return _PUNCT.sub("", str(title)).lower()


def _similar(a: str, b: str) -> bool:
    if not a or not b:
        return False
    if a in b or b in a:  # 短标题被长标题包含，视为同一事件
        return True
    return SequenceMatcher(None, a, b).ratio() >= THRESHOLD


def build_clusters(all_items: list, min_sources: int = MIN_CLUSTER) -> list:
    """all_items: [{"source": 源key, "source_name": 展示名, "rel": 榜内相对热度0-1, ...}, ...]

    返回簇列表，每簇：
    {"title", "url", "desc", "sources": [源名...], "n_sources": int,
     "strength": 榜内相对热度最强值(0-1), "max_heat": 原始最大热度,
     "members": [(源名, 词条)]}
    排序：命中源数优先，同源数下按 strength；composite = 源数 + strength
    是与该字典序完全一致的单一标量，可直接用于展示（保证第一名 ≥ 第二名）。
    """
    clusters = []
    for it in all_items:
        norm = normalize_title(it.get("title", ""))
        rel = it.get("rel") or 0.0
        hit = None
        for c in clusters:
            if _similar(norm, c["norm"]):
                hit = c
                break
        if hit is None:
            clusters.append({
                "norm": norm,
                "title": it.get("title", ""),
                "url": it.get("url", ""),
                "desc": it.get("desc", ""),
                "rank": it.get("rank", 99),
                "sources": [it["source_name"]],
                "strength": rel,
                "max_heat": it.get("heat"),
                "newest": it.get("time"),
                "members": [(it["source_name"], it)],
            })
            continue
        hit["members"].append((it["source_name"], it))
        if it["source_name"] not in hit["sources"]:
            hit["sources"].append(it["source_name"])
        if rel > hit["strength"]:
            hit["strength"] = rel
        if it.get("heat") and (hit["max_heat"] or 0) < it["heat"]:
            hit["max_heat"] = it["heat"]
        if it.get("time") and (hit.get("newest") or 0) < it["time"]:
            hit["newest"] = it["time"]
        # 用榜上排名更靠前的词条当代表（跨源时即取最显眼的提法）
        if it.get("rank", 99) < hit.get("rank", 99):
            hit["title"] = it.get("title", hit["title"])
            hit["url"] = it.get("url", hit["url"])
            hit["norm"] = norm
            hit["rank"] = it.get("rank", 99)
        if len(it.get("desc", "")) > len(hit.get("desc", "")):
            hit["desc"] = it["desc"]

    cross = [c for c in clusters if len(c["sources"]) >= min_sources]
    cross.sort(key=lambda c: (len(c["sources"]) + c["strength"], c["max_heat"] or 0),
               reverse=True)
    for c in cross:
        c["composite"] = len(c["sources"]) + c["strength"]
    return cross
