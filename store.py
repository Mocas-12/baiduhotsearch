# -*- coding: utf-8 -*-
"""SQLite 历史快照：支撑「🆕 新上榜」标记与「上榜时长」。

注意：Streamlit Cloud 的文件系统随应用重建而清空，历史只在本实例生命周期内累积；
自部署挂载持久卷可长期保留。库文件已加入 .gitignore。
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "hot.db"
RETAIN_DAYS = 7


def _conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("""CREATE TABLE IF NOT EXISTS snapshots(
        ts      TEXT NOT NULL,
        source  TEXT NOT NULL,
        title   TEXT NOT NULL,
        url     TEXT,
        heat    REAL,
        rank    INTEGER)""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_st ON snapshots(source, title)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON snapshots(ts)")
    return conn


def save_snapshot(source: str, items: list):
    """某源一次成功抓取即存一份快照，并清理过期数据。"""
    if not items:
        return
    now = datetime.now().isoformat(timespec="seconds")
    conn = _conn()
    try:
        conn.executemany(
            "INSERT INTO snapshots(ts, source, title, url, heat, rank) VALUES(?,?,?,?,?,?)",
            [(now, source, it.get("title", ""), it.get("url", ""),
              it.get("heat"), it.get("rank")) for it in items])
        cutoff = (datetime.now() - timedelta(days=RETAIN_DAYS)).isoformat(timespec="seconds")
        conn.execute("DELETE FROM snapshots WHERE ts < ?", (cutoff,))
        conn.commit()
    finally:
        conn.close()


def first_seen_many(source: str, titles: list) -> dict:
    """批量查询首次上榜时间，返回 {title: datetime|None}。
    必须在本批快照写入 save_snapshot() 之前调用，否则全部会被判为旧词条。"""
    if not titles:
        return {}
    conn = _conn()
    try:
        marks = {}
        for title in titles:
            row = conn.execute(
                "SELECT MIN(ts) FROM snapshots WHERE source=? AND title=?",
                (source, title)).fetchone()
            ts = None
            if row and row[0]:
                try:
                    ts = datetime.fromisoformat(row[0])
                except ValueError:
                    ts = None
            marks[title] = ts
        return marks
    finally:
        conn.close()


def last_snapshot(source: str, max_age_hours: float = 24):
    """某源最近一次成功快照，返回 (快照时间, items)；无记录或超龄返回 (None, [])。

    用途：实时抓取失败（限流/网络）时，用库内最近一份完整数据兜底展示，
    避免交叉榜因个别源失效而只剩零星配对。快照未存 desc 字段，兜底卡片无简介。
    """
    cutoff = (datetime.now() - timedelta(hours=max_age_hours)).isoformat(timespec="seconds")
    conn = _conn()
    try:
        row = conn.execute(
            "SELECT ts FROM snapshots WHERE source=? AND ts>=? ORDER BY ts DESC LIMIT 1",
            (source, cutoff)).fetchone()
        if not row:
            return None, []
        rows = conn.execute(
            "SELECT title, url, heat, rank FROM snapshots WHERE source=? AND ts=?",
            (source, row[0])).fetchall()
        items = [{"rank": rank or (i + 1), "title": title, "url": url or "",
                  "desc": "", "heat": heat}
                 for i, (title, url, heat, rank) in enumerate(rows)]
        items.sort(key=lambda it: it["rank"])
        try:
            return datetime.fromisoformat(row[0]), items
        except ValueError:
            return None, []
    finally:
        conn.close()
