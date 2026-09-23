# -*- coding: utf-8 -*-
"""store.first_seen_many 行为锁定测试（查询方式重构前后必须同样通过）。"""

import sqlite3
from datetime import datetime

import pytest

import store


@pytest.fixture()
def db(tmp_path, monkeypatch):
    """把库文件指到临时目录并建表。"""
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "test.db")
    store._conn().close()
    return store


def _seed(source: str, title: str, ts: str):
    conn = sqlite3.connect(store.DB_PATH)
    conn.execute("INSERT INTO snapshots(ts, source, title) VALUES(?,?,?)", (ts, source, title))
    conn.commit()
    conn.close()


def test_first_seen_takes_minimum_across_snapshots(db):
    """同一标题多条快照时取最早的 ts。"""
    _seed("weibo", "甲", "2026-09-20T10:00:00")
    _seed("weibo", "甲", "2026-09-22T10:00:00")
    _seed("weibo", "乙", "2026-09-21T10:00:00")
    marks = store.first_seen_many("weibo", ["甲", "乙"])
    assert marks == {
        "甲": datetime.fromisoformat("2026-09-20T10:00:00"),
        "乙": datetime.fromisoformat("2026-09-21T10:00:00"),
    }


def test_isolated_by_source(db):
    """同标题不同源互不影响。"""
    _seed("weibo", "甲", "2026-09-20T10:00:00")
    _seed("zhihu", "甲", "2026-09-19T10:00:00")
    assert store.first_seen_many("weibo", ["甲"]) == {
        "甲": datetime.fromisoformat("2026-09-20T10:00:00"),
    }


def test_missing_title_maps_to_none(db):
    """库中不存在的标题映射为 None，不能缺席。"""
    assert store.first_seen_many("weibo", ["不存在"]) == {"不存在": None}


def test_invalid_ts_maps_to_none(db):
    """ts 字段非法（解析失败）时映射为 None。"""
    _seed("weibo", "坏时间", "不是时间")
    assert store.first_seen_many("weibo", ["坏时间"]) == {"坏时间": None}


def test_empty_titles(db):
    assert store.first_seen_many("weibo", []) == {}


def test_duplicate_titles_dedup(db):
    """入参重复标题时结果按入参去重，保持单个键。"""
    _seed("weibo", "甲", "2026-09-20T10:00:00")
    assert list(store.first_seen_many("weibo", ["甲", "甲"])) == ["甲"]
