# -*- coding: utf-8 -*-
"""sources.py 行为锁定测试（重构基线）。

全部离线：网络入口 build_session/_sixty_get 一律 monkeypatch。
这些测试在重构前写好并跑绿；重构后必须原样通过 = 行为零变更。
"""
import os
import re
import sys

import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sources  # noqa: E402

SCHEMA = {"rank", "title", "url", "desc", "heat"}


# ---------------------------------------------------------------- 假网络对象

class FakeResp:
    def __init__(self, json_data=None, text="", status=200):
        self._json = json_data
        self.text = text
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json


class FakeSession:
    """替换 sources.build_session 的返回值：记录调用，回放固定响应。"""

    def __init__(self, get_resp=None, post_resp=None, cookies=None,
                 get_err=None):
        self.headers = {}
        self.cookies = cookies if cookies is not None else {}
        self._get_resp = get_resp
        self._get_err = get_err
        self._post_resp = post_resp
        self.calls = []

    def get(self, url, **kw):
        self.calls.append(("GET", url, kw))
        if self._get_err is not None:
            raise self._get_err
        return self._get_resp

    def post(self, url, **kw):
        self.calls.append(("POST", url, kw))
        return self._post_resp


# ---------------------------------------------------------------- 纯函数：_norm_items / _to_heat

def test_norm_items_default_keys():
    raw = [{"title": "A", "hot_value": 10, "link": "http://a", "detail": "d1"},
           {"title": "B", "url": "http://b", "word_explain": "d2"}]
    items = sources._norm_items(raw)
    assert len(items) == 2
    assert items[0] == {"rank": 1, "title": "A", "url": "http://a",
                        "desc": "d1", "heat": 10.0}
    # link 缺失时回退 url；desc 回退 word_explain
    assert items[1]["url"] == "http://b"
    assert items[1]["desc"] == "d2"
    assert items[1]["heat"] is None  # 无 hot_value
    for it in items:
        assert set(it) == SCHEMA


def test_norm_items_url_keys_priority():
    raw = [{"title": "T", "link": "", "url": "http://u"}]
    assert sources._norm_items(raw)[0]["url"] == "http://u"  # 第一个非空 key
    assert sources._norm_items([{"title": "T"}])[0]["url"] == ""


def test_norm_items_custom_heat_key():
    items = sources._norm_items([{"title": "T", "score": "3.5"}], heat_key="score")
    assert items[0]["heat"] == 3.5


def test_norm_items_rank_uses_raw_index_gaps_after_filter():
    # rank 按原始下标编号，空 title 过滤后名次留洞——与手动循环的「已收集数递增」不同
    raw = [{"title": "A"}, {"title": "   "}, {"title": "C"}]
    items = sources._norm_items(raw)
    assert [i["rank"] for i in items] == [1, 3]


def test_norm_items_title_coerced_and_stripped():
    items = sources._norm_items([{"title": 123}, {"title": "  x  "}])
    assert [i["title"] for i in items] == ["123", "x"]


def test_to_heat():
    assert sources._to_heat(123) == 123.0
    assert sources._to_heat("45.6") == 45.6
    assert sources._to_heat(None) is None
    assert sources._to_heat("abc") is None
    assert sources._to_heat({}) is None


# ---------------------------------------------------------------- 纯函数：_parse_cn_heat

def test_parse_cn_heat_wan_yi_plain():
    assert sources._parse_cn_heat("2678 万") == 26780000.0
    assert sources._parse_cn_heat("3.5万") == 35000.0
    assert sources._parse_cn_heat("1.2亿") == 120000000.0
    assert sources._parse_cn_heat("4567") == 4567.0
    assert sources._parse_cn_heat("热度 12.3万") == 123000.0  # 文案中嵌数字


def test_parse_cn_heat_failures():
    assert sources._parse_cn_heat("") is None
    assert sources._parse_cn_heat(None) is None
    assert sources._parse_cn_heat("abc") is None
    # 亿优先于万
    assert sources._parse_cn_heat("2万3亿") == 300000000.0


# ---------------------------------------------------------------- 纯函数：_parse_rss / _parse_rfc822

RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item>
    <title><![CDATA[标题一]]></title>
    <link>http://e1</link>
    <description>描述一</description>
    <pubDate>Tue, 10 Sep 2024 08:00:00 GMT</pubDate>
  </item>
  <item>
    <title>标题二</title>
    <link>http://e2</link>
    <description>描述二</description>
    <pubDate>not-a-date</pubDate>
  </item>
  <item>
    <link>http://e3</link>
    <description>无标题应跳过</description>
  </item>
</channel></rss>"""

ATOM_XML = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Atom 条目</title>
    <link href="http://a1" rel="alternate"/>
    <summary>Atom 摘要</summary>
    <updated>Tue, 10 Sep 2024 08:00:00 GMT</updated>
  </entry>
</feed>"""


def test_parse_rss_rss20_with_time():
    rows = sources._parse_rss(RSS_XML, with_time=True)
    assert len(rows) == 2  # 缺 title 的第 3 条跳过
    t1, l1, d1, ts1 = rows[0]
    assert (t1, l1, d1) == ("标题一", "http://e1", "描述一")  # CDATA 已剥
    assert ts1 == 1725955200.0  # 合法 pubDate → epoch
    assert rows[1][3] is None  # 非法 pubDate → None


def test_parse_rss_rss20_without_time_three_tuple():
    rows = sources._parse_rss(RSS_XML)
    assert rows == [("标题一", "http://e1", "描述一"),
                    ("标题二", "http://e2", "描述二")]


def test_parse_rss_max_items():
    assert len(sources._parse_rss(RSS_XML, max_items=1)) == 1
    assert len(sources._parse_rss(RSS_XML, max_items=99)) == 2


def test_parse_rss_atom():
    rows = sources._parse_rss(ATOM_XML, with_time=True)
    assert rows == [("Atom 条目", "http://a1", "Atom 摘要", 1725955200.0)]


def test_parse_rss_invalid_xml_raises():
    with pytest.raises(Exception):
        sources._parse_rss("<not-xml")


def test_parse_rfc822():
    assert sources._parse_rfc822("Tue, 10 Sep 2024 08:00:00 GMT") == 1725955200.0
    assert sources._parse_rfc822("not-a-date") is None
    assert sources._parse_rfc822("") is None
    assert sources._parse_rfc822(None) is None


# ---------------------------------------------------------------- _rss_items（Google News 后缀切分 / NYT HTML 剥标签）

GNEWS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item><title>主标题 - 媒体名称</title><link>http://g1</link>
    <description>原始描述</description><pubDate>Tue, 10 Sep 2024 08:00:00 GMT</pubDate></item>
  <item><title>长后缀标题 - 这是一个超过二十个字符长度的媒体后缀名称测试</title><link>http://g2</link>
    <description>原始描述二</description><pubDate>Tue, 10 Sep 2024 09:00:00 GMT</pubDate></item>
  <item><title>纯标题无后缀</title><link>http://g3</link>
    <description>&lt;p&gt;带&lt;b&gt;标签&lt;/b&gt;的描述&lt;/p&gt;</description>
    <pubDate>Tue, 10 Sep 2024 10:00:00 GMT</pubDate></item>
</channel></rss>"""


def _rss_items_with(xml, **kw):
    sess = FakeSession(get_resp=FakeResp(text=xml))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        return sources._rss_items({}, "http://feed.example/rss", **kw)
    finally:
        sources.build_session = old


def test_rss_items_schema_and_time():
    items = _rss_items_with(RSS_XML)
    assert [(i["rank"], i["title"], i["url"]) for i in items] == [
        (1, "标题一", "http://e1"), (2, "标题二", "http://e2")]
    assert all(set(i) == SCHEMA | {"time"} for i in items)
    assert all(i["heat"] is None for i in items)
    assert items[0]["time"] == 1725955200.0
    assert items[1]["time"] is None


def test_rss_items_split_source_suffix_short():
    items = _rss_items_with(GNEWS_XML, split_source_suffix=True)
    assert items[0]["title"] == "主标题"
    assert items[0]["desc"] == "媒体名称"  # 后缀顶替 desc


def test_rss_items_split_source_suffix_long_suffix_kept():
    items = _rss_items_with(GNEWS_XML, split_source_suffix=True)
    # 后缀 >20 字符：不切分，title 原样，desc 走原始描述
    assert items[1]["title"].startswith("长后缀标题 - ")
    assert items[1]["desc"] == "原始描述二"


def test_rss_items_desc_html_stripped_and_truncated():
    items = _rss_items_with(GNEWS_XML)
    assert items[2]["desc"] == "带 标签 的描述"  # 标签替换为空格再压缩
    long_desc = "x" * 300
    xml = ('<rss version="2.0"><channel><item><title>T</title>'
           f'<description>{long_desc}</description></item></channel></rss>')
    assert len(_rss_items_with(xml)[0]["desc"]) == 140


# ---------------------------------------------------------------- _chain 回退链

def test_chain_first_success_wins():
    calls = []
    fn2 = lambda c: calls.append("fn2") or [_mk(1)]
    out = sources._chain(lambda c: [_mk(1)], fn2)({})
    assert out == [_mk(1)]
    assert calls == []  # 第一通道成功则不触碰后续


def _mk(rank):
    return {"rank": rank, "title": "t", "url": "", "desc": "", "heat": None}


def test_chain_skips_empty_result():
    out = sources._chain(lambda c: [], lambda c: [_mk(1)])({})
    assert out == [_mk(1)]  # 空列表视为失败，继续下一通道


def test_chain_falls_back_on_exception():
    def boom(c):
        raise ValueError("x")
    out = sources._chain(boom, lambda c: [_mk(1)])({})
    assert out == [_mk(1)]


def test_chain_all_fail_raises():
    def boom(c):
        raise ValueError("x")
    with pytest.raises(RuntimeError, match="所有通道失败.*x"):
        sources._chain(boom, boom)({})


# ---------------------------------------------------------------- fetcher 级：weibo

def test_weibo_direct_with_cookie():
    sess = FakeSession(
        get_resp=FakeResp(json_data={"data": {"realtime": [
            {"word": "热搜A", "num": 12345},
            {"word": "   "},           # 空词跳过
            {"word": "热搜B", "num": "678"},
        ]}}))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        items = sources._weibo_direct({"weibo_cookie": "SUB=x"})
    finally:
        sources.build_session = old
    method, url, _ = sess.calls[0]
    assert (method, url) == ("GET", "https://weibo.com/ajax/side/hotSearch")
    assert sess.headers["Cookie"] == "SUB=x"
    assert sess.headers["Referer"] == "https://weibo.com/"
    assert [i["rank"] for i in items] == [1, 2]  # 跳过后名次连续
    assert [i["title"] for i in items] == ["热搜A", "热搜B"]
    assert items[0]["url"] == "https://s.weibo.com/weibo?q=" + requests.utils.quote("热搜A")
    assert [i["heat"] for i in items] == [12345.0, 678.0]
    assert all(set(i) == SCHEMA and i["desc"] == "" for i in items)


def test_weibo_direct_no_cookie_raises():
    with pytest.raises(RuntimeError, match="未配置微博 Cookie"):
        sources._weibo_direct({})


def test_weibo_direct_error_response_raises():
    sess = FakeSession(get_resp=FakeResp(json_data={"data": {}}))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        with pytest.raises(RuntimeError, match="微博接口返回异常"):
            sources._weibo_direct({"weibo_cookie": "SUB=x"})
    finally:
        sources.build_session = old


def test_fetch_weibo_falls_back_to_sixty():
    # 未配置 Cookie：直连通道立刻抛错 → 回退 60s API（_norm_items 管道）
    seen = {}

    def fake_sixty(cfg, endpoint):
        seen["endpoint"] = endpoint
        return [{"title": "T1", "hot_value": 1, "link": "http://t1"}]

    old_sixty = sources._sixty_get
    sources._sixty_get = fake_sixty
    try:
        items = sources.fetch_weibo({})
    finally:
        sources._sixty_get = old_sixty
    assert seen["endpoint"] == "weibo"
    assert items == [{"rank": 1, "title": "T1", "url": "http://t1",
                      "desc": "", "heat": 1.0}]


# ---------------------------------------------------------------- fetcher 级：douyin

def test_douyin_direct_sorts_by_position():
    sess = FakeSession(
        post_resp=FakeResp(json_data={}),
        cookies={"ttwid": "tt-1"},
        get_resp=FakeResp(json_data={"data": {"word_list": [
            {"word": "抖音A", "hot_value": 100, "position": 2},
            {"word": "抖音B", "hot_value": "50", "position": 1},
            {"word": "抖音C", "hot_value": None},   # 无 position → 递增序号
            {"word": "  "},                          # 空词跳过
        ]}}))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        items = sources._douyin_direct({})
    finally:
        sources.build_session = old
    assert sess.calls[0][0] == "POST"
    assert "ttwid.bytedance.com" in sess.calls[0][1]
    assert sess.calls[1][0] == "GET"
    assert "douyin.com/aweme/v1/web/hot/search/list/" in sess.calls[1][1]
    assert sess.calls[1][2]["headers"]["Referer"] == "https://www.douyin.com/"
    # position 打乱后按 rank 排序；缺 position 的条目按序号补 3
    assert [i["rank"] for i in items] == [1, 2, 3]
    assert [i["title"] for i in items] == ["抖音B", "抖音A", "抖音C"]
    assert [i["heat"] for i in items] == [50.0, 100.0, None]
    assert items[0]["url"] == "https://www.douyin.com/search/" + requests.utils.quote("抖音B")


def test_douyin_direct_ttwid_failure_raises():
    sess = FakeSession(post_resp=FakeResp(json_data={}), cookies={})
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        with pytest.raises(RuntimeError, match="ttwid 注册失败"):
            sources._douyin_direct({})
    finally:
        sources.build_session = old


def test_fetch_douyin_falls_back_to_sixty():
    seen = {}

    def fake_sixty(cfg, endpoint):
        seen["endpoint"] = endpoint
        return [{"title": "D", "hot_value": 9, "link": "http://d"}]

    old_direct, old_sixty = sources._douyin_direct, sources._sixty_get
    sources._douyin_direct = lambda c: (_ for _ in ()).throw(RuntimeError("no"))
    sources._sixty_get = fake_sixty
    try:
        items = sources.fetch_douyin({})
    finally:
        sources._douyin_direct, sources._sixty_get = old_direct, old_sixty
    assert seen["endpoint"] == "douyin"
    assert [i["title"] for i in items] == ["D"]


# ---------------------------------------------------------------- fetcher 级：toutiao

def test_toutiao_direct_capitalized_keys():
    sess = FakeSession(get_resp=FakeResp(json_data={"data": [
        {"Title": "头条A", "Url": "http://tt1", "HotValue": 999},
        {"Title": ""},                      # 空标题跳过
        {"Title": "头条B", "Url": "", "HotValue": "12.5"},
    ]}))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        items = sources._toutiao_direct({})
    finally:
        sources.build_session = old
    assert sess.calls[0][1].startswith("https://www.toutiao.com/hot-event/hot-board/")
    assert [i["rank"] for i in items] == [1, 2]
    assert items[0] == {"rank": 1, "title": "头条A", "url": "http://tt1",
                        "desc": "", "heat": 999.0}
    assert items[1]["url"] == "" and items[1]["heat"] == 12.5


def test_fetch_toutiao_direct_down_sixty_fallback():
    seen = {}

    def fake_sixty(cfg, endpoint):
        seen["endpoint"] = endpoint
        return [{"title": "TT", "hot_value": 5, "link": "http://tt"}]

    sess = FakeSession(get_err=requests.ConnectionError("down"))
    old_sess, old_sixty = sources.build_session, sources._sixty_get
    sources.build_session = lambda cfg: sess
    sources._sixty_get = fake_sixty
    try:
        items = sources.fetch_toutiao({})
    finally:
        sources.build_session, sources._sixty_get = old_sess, old_sixty
    assert seen["endpoint"] == "toutiao"
    assert [i["heat"] for i in items] == [5.0]


# ---------------------------------------------------------------- fetcher 级：bilibili

def test_bilibili_direct_position_and_show_name_fallback():
    sess = FakeSession(get_resp=FakeResp(json_data={"data": {"list": [
        {"keyword": "K1", "position": 7, "hot_score": 123},
        {"show_name": "K2"},                # keyword 缺失回退 show_name；无 position → 序号
        {"keyword": ""},                     # 空 title 跳过
    ]}}))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        items = sources._bilibili_direct({})
    finally:
        sources.build_session = old
    assert sess.calls[0][1] == "https://app.bilibili.com/x/v2/search/trending/ranking"
    assert [i["rank"] for i in items] == [7, 2]  # position 原样保留（不排序）
    assert [i["title"] for i in items] == ["K1", "K2"]
    assert items[0]["url"] == "https://search.bilibili.com/all?keyword=K1"
    assert [i["heat"] for i in items] == [123.0, None]


def test_fetch_bilibili_falls_back_to_sixty():
    seen = {}

    def fake_sixty(cfg, endpoint):
        seen["endpoint"] = endpoint
        return [{"title": "B", "hot_value": 8, "link": "http://b"}]

    old_direct, old_sixty = sources._bilibili_direct, sources._sixty_get
    sources._bilibili_direct = lambda c: (_ for _ in ()).throw(RuntimeError("no"))
    sources._sixty_get = fake_sixty
    try:
        items = sources.fetch_bilibili({})
    finally:
        sources._bilibili_direct, sources._sixty_get = old_direct, old_sixty
    assert seen["endpoint"] == "bili"
    assert [i["title"] for i in items] == ["B"]


# ---------------------------------------------------------------- fetcher 级：zhihu

def test_fetch_zhihu_cn_heat_and_detail():
    seen = {}

    def fake_sixty(cfg, endpoint):
        seen["endpoint"] = endpoint
        return [{"title": "知乎A", "link": "http://z1", "detail": "简介A",
                 "hot_value_desc": "2678 万"},
                {"title": "知乎B", "hot_value_desc": "1.2亿"},
                {"title": "  ", "link": "http://skip"}]  # 空标题跳过 → 名次连续

    old = sources._sixty_get
    sources._sixty_get = fake_sixty
    try:
        items = sources.fetch_zhihu({})
    finally:
        sources._sixty_get = old
    assert seen["endpoint"] == "zhihu"
    assert [i["rank"] for i in items] == [1, 2]
    assert items[0] == {"rank": 1, "title": "知乎A", "url": "http://z1",
                        "desc": "简介A", "heat": 26780000.0}
    assert items[1]["desc"] == "" and items[1]["heat"] == 120000000.0


# ---------------------------------------------------------------- fetcher 级：hackernews

def test_fetch_hackernews_url_fallback_and_desc():
    sess = FakeSession(get_resp=FakeResp(json_data={"hits": [
        {"title": "HN1", "url": "http://h1", "author": "alice",
         "num_comments": 42, "points": 100, "objectID": "1"},
        {"title": "HN2", "objectID": "2", "points": None},  # 无 url/author
        {"title": ""},                                       # 跳过
    ]}))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        items = sources.fetch_hackernews({})
    finally:
        sources.build_session = old
    assert "hn.algolia.com" in sess.calls[0][1]
    assert "hitsPerPage=30" in sess.calls[0][1]
    assert [i["rank"] for i in items] == [1, 2]
    assert items[0] == {"rank": 1, "title": "HN1", "url": "http://h1",
                        "desc": "alice · 💬 42", "heat": 100.0}
    assert items[1]["url"] == "https://news.ycombinator.com/item?id=2"
    assert items[1]["desc"] == "" and items[1]["heat"] is None


# ---------------------------------------------------------------- fetcher 级：v2ex

def test_fetch_v2ex_strips_html_truncates_desc():
    sess = FakeSession(get_resp=FakeResp(json_data=[
        {"title": "V1", "url": "http://v1", "content": "<p>hello <b>world</b></p>",
         "replies": 5},
        {"title": "V2", "content": "y" * 300, "replies": "7"},  # 截断到 120
        {"title": ""},                                           # 跳过
    ]))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        items = sources.fetch_v2ex({})
    finally:
        sources.build_session = old
    assert sess.calls[0][1] == "https://www.v2ex.com/api/topics/hot.json"
    assert [i["rank"] for i in items] == [1, 2]
    assert items[0] == {"rank": 1, "title": "V1", "url": "http://v1",
                        "desc": "hello world", "heat": 5.0}
    assert len(items[1]["desc"]) == 120
    assert items[1]["heat"] == 7.0


# ---------------------------------------------------------------- fetcher 级：github

GH_HTML = """<html><body>
<article class="Box-row">
  <h2><a href="/alice/repo-one">repo-one</a></h2>
  <p class="col-9 color-fg-muted my-1 pr-4">Simple description</p>
  <span>1,234 stars today</span>
</article>
<article class="Box-row">
  <h2><a href="/bob/repo-two">repo-two</a></h2>
</article>
<article class="Box-row">
  <h2><a href="/trending">not a repo, no slash after first segment</a></h2>
</article>
</body></html>"""


def test_fetch_github_rows_and_skips():
    sess = FakeSession(get_resp=FakeResp(text=GH_HTML))
    old = sources.build_session
    sources.build_session = lambda cfg: sess
    try:
        items = sources.fetch_github({})
    finally:
        sources.build_session = old
    assert sess.calls[0][1] == "https://github.com/trending"
    assert len(items) == 2  # 第三块无 repo 匹配被跳过
    assert items[0] == {"rank": 1, "title": "alice/repo-one",
                        "url": "https://github.com/alice/repo-one",
                        "desc": "Simple description", "heat": 1234.0}
    assert items[1] == {"rank": 2, "title": "bob/repo-two",
                        "url": "https://github.com/bob/repo-two",
                        "desc": "", "heat": None}  # 无 stars 片段 → None
    assert all(set(i) == SCHEMA for i in items)


# ---------------------------------------------------------------- 注册表与包装

def test_registry_shape():
    assert len(sources.SOURCES) == 11
    for key, meta in sources.SOURCES.items():
        assert callable(meta["fetch"])
        assert meta["cat"] in {"domestic", "world", "tech"}
    assert set(sources.sources_of("tech")) == {"hackernews", "github", "v2ex"}


def test_gnews_and_nyt_wrap_rss_items():
    calls = []

    def fake_rss_items(cfg, url, max_items=30, split_source_suffix=False):
        calls.append((url, max_items, split_source_suffix))
        return [_mk(1)]

    old = sources._rss_items
    sources._rss_items = fake_rss_items
    try:
        assert sources.fetch_gnews({}) == [_mk(1)]
        assert sources.fetch_nyt({}) == [_mk(1)]
    finally:
        sources._rss_items = old
    assert calls == [
        ("https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans", 30, True),
        ("https://cn.nytimes.com/rss/", 30, False),
    ]
