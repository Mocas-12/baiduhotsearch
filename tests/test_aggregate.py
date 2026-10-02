# -*- coding: utf-8 -*-
"""aggregate.py 聚类行为锁定测试（纯离线，不触网）。"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aggregate


def _item(source, name, title, rank=99, heat=None, rel=0.0, url="", desc=""):
    return {"source": source, "source_name": name, "title": title,
            "rank": rank, "heat": heat, "rel": rel, "url": url, "desc": desc}


# ---------------------------------------------------------------- normalize_title / _similar

def test_normalize_title_strips_punct_and_lowers():
    assert aggregate.normalize_title("台风「梅花」过境！ABC") == "台风梅花过境abc"
    assert aggregate.normalize_title("  苹果 发布会  ") == "苹果发布会"


def test_similar_containment_beats_threshold():
    # 短标题被长标题包含 → 同一事件
    assert aggregate._similar("台风", "台风梅花过境") is True
    assert aggregate._similar("台风梅花过境", "台风") is True


def test_similar_ratio_threshold():
    # 4 字中 3 字相同（ratio 0.75 ≥ 0.55）→ 相似
    assert aggregate._similar("甲乙丙丁", "甲乙丙戊") is True
    # 仅 1 字重合（ratio < 0.55）→ 不相似
    assert aggregate._similar("苹果发布会", "谷歌开发者大会") is False


def test_similar_empty_is_never_similar():
    assert aggregate._similar("", "台风") is False
    assert aggregate._similar("台风", "") is False


# ---------------------------------------------------------------- build_clusters

def test_build_clusters_groups_same_event_across_sources():
    items = [
        _item("weibo", "微博", "台风梅花过境", rank=1, heat=100.0, rel=1.0,
              url="http://w", desc="短"),
        _item("zhihu", "知乎", "台风梅花过境！", rank=2, heat=500.0, rel=0.5,
              url="http://z", desc="更长的描述"),
    ]
    clusters = aggregate.build_clusters(items)
    assert len(clusters) == 1
    c = clusters[0]
    assert c["title"] == "台风梅花过境"      # rank 更小者当代表
    assert c["url"] == "http://w"
    assert c["desc"] == "更长的描述"          # 取更长的 desc
    assert c["sources"] == ["微博", "知乎"]
    assert c["strength"] == 1.0              # 榜内相对热度取最强
    assert c["max_heat"] == 500.0            # 原始热度取最大
    assert [(n, it["title"]) for n, it in c["members"]] == [
        ("微博", "台风梅花过境"), ("知乎", "台风梅花过境！")]


def test_build_clusters_later_higher_rank_takes_over():
    # 后到的词条榜上排名更靠前 → 代表词条/链接让位
    items = [
        _item("weibo", "微博", "某事件引发关注", rank=2, url="http://w"),
        _item("zhihu", "知乎", "某事件引发关注啦", rank=1, url="http://z"),
    ]
    c = aggregate.build_clusters(items)[0]
    assert c["title"] == "某事件引发关注啦"
    assert c["url"] == "http://z"
    assert c["rank"] == 1


def test_build_clusters_filters_single_source_by_default():
    # 同源相似词条聚成一簇但只命中 1 个源，默认 MIN_CLUSTER=2 → 滤除
    items = [
        _item("weibo", "微博", "台风梅花过境"),
        _item("weibo", "微博", "台风梅花过境啦"),
    ]
    assert aggregate.build_clusters(items) == []
    # min_sources=1 时保留单源簇
    kept = aggregate.build_clusters(items, min_sources=1)
    assert len(kept) == 1 and kept[0]["sources"] == ["微博"]


def test_build_clusters_sort_by_sources_then_strength():
    items = [
        # 簇甲：3 源命中，strength 0.9 → 键 3.9
        _item("a", "源A", "台风梅花登陆", rank=1, rel=0.9),
        _item("b", "源B", "台风梅花登陆了", rank=1, rel=0.1),
        _item("c", "源C", "台风梅花登陆现场", rank=1, rel=0.1),
        # 簇乙：2 源命中，strength 0.2 → 键 2.2
        _item("a", "源A", "地震预警发布", rank=2, rel=0.2),
        _item("b", "源B", "地震预警发布了", rank=2, rel=0.2),
    ]
    clusters = aggregate.build_clusters(items)
    assert [c["title"] for c in clusters] == ["台风梅花登陆", "地震预警发布"]


def test_build_clusters_empty_input():
    assert aggregate.build_clusters([]) == []


def test_build_clusters_dissimilar_titles_never_merge():
    items = [
        _item("weibo", "微博", "苹果发布会"),
        _item("zhihu", "知乎", "谷歌开发者大会"),
    ]
    assert aggregate.build_clusters(items) == []
