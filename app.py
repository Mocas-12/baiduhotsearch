import os
import streamlit as st
import pandas as pd
import requests
from typing import Optional, Tuple

st.set_page_config(page_title="中国热搜", layout="wide", initial_sidebar_state="collapsed")

def apply_theme():
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"]{
          background: linear-gradient(135deg, #ff5f6d 0%, #ffc371 60%, #fff 100%);
        }
        [data-testid="stHeader"]{
          background: rgba(0,0,0,0);
        }
        .main .block-container{
          background: rgba(255,255,255,0.92);
          border-radius: 16px;
          box-shadow: 0 8px 24px rgba(0,0,0,0.12);
          padding: 24px 32px;
          backdrop-filter: blur(6px);
        }
        [data-testid="stSidebar"]{
          background: linear-gradient(180deg, #fff1f0 0%, #ffe3dc 60%, #ffeae6 100%);
          border-right: 1px solid #ffb59f;
          box-shadow: 4px 0 16px rgba(255, 90, 90, 0.12);
          color: #1a1a1a;
        }
        [data-testid="stSidebar"] * { color: #1a1a1a; }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label{
          color: #7a1b1d !important;
        }
        [data-testid="stSidebar"] input, 
        [data-testid="stSidebar"] textarea{
          background: #ffffff !important;
          color: #1a1a1a !important;
          border: 1px solid #ffbfb3 !important;
          border-radius: 8px !important;
        }
        [data-testid="stSidebar"] .stCheckbox > label div[role="checkbox"]{
          border-color: #ff7a45 !important;
        }
        .stButton>button{
          background: linear-gradient(90deg, #ff4d4f, #ff7a45);
          color: #fff;
          border: none;
          border-radius: 8px;
          padding: 0.5rem 1rem;
        }
        .stButton>button:hover{
          filter: brightness(1.03);
        }
        .stSlider [role="slider"]{
          color: #ff4d4f;
        }
        .stDataFrame thead tr th{
          background: #ffffff !important;
          color: #111111 !important;
        }
        .stDataFrame tbody tr td:first-child{
          background: #ffffff !important;
          color: #111111 !important;
        }
        footer {visibility: hidden;}
        </style>
        <script>
        (function(){
          const map = new Map([
            ["Deploy","部署"],
            ["Rerun","重新运行"],
            ["Run","运行"],
            ["Settings","设置"],
            ["Print","打印"],
            ["Record a screencast","录制屏幕"],
            ["Developer options","开发者选项"],
            ["Clear cache","清除缓存"],
            ["Sort ascending","升序排序"],
            ["Sort descending","降序排序"],
            ["Format","格式"],
            ["Autosize","自动列宽"],
            ["Autosize all columns","自动调整全部列宽"],
            ["Auto-size this column","自动调整该列宽"],
            ["Pin column","固定列"],
            ["Unpin column","取消固定列"],
            ["Pin left","固定到左侧"],
            ["Pin right","固定到右侧"],
            ["Freeze column","冻结列"],
            ["Unfreeze column","取消冻结列"],
            ["Hide column","隐藏列"],
            ["Show columns","显示列"],
            ["Reset columns","重置列"],
            ["Copy","复制"],
            ["Copy with headers","复制（含表头）"],
            ["Export","导出"],
            ["Download as CSV","下载为 CSV"],
            ["Download as JSON","下载为 JSON"],
            ["Filter rows","筛选行"],
            ["Filter","筛选"],
            ["Search","搜索"],
            ["Expand data","展开数据"],
            ["Fit to width","适配宽度"],
            ["Resize","调整大小"],
            ["Group by","分组"],
            ["Aggregate","汇总"],
            ["Fullscreen","全屏"]
          ]);
          function translateText(txt){
            if(!txt) return txt;
            let out = txt;
            map.forEach((zh,en)=>{
              out = out.replaceAll(en, zh);
            });
            return out;
          }
          function translateAttributes(el){
            ["title","aria-label","aria-description"].forEach(attr=>{
              if(el.hasAttribute && el.hasAttribute(attr)){
                const v = el.getAttribute(attr);
                const nv = translateText(v);
                if(nv !== v) el.setAttribute(attr, nv);
              }
            });
          }
          function translateNode(node){
            if(!node) return;
            if(node.nodeType===3){
              const nv = translateText(node.textContent);
              if(nv !== node.textContent) node.textContent = nv;
              return;
            }
            if(node.nodeType===1){
              const el = node;
              translateAttributes(el);
              if(el.childNodes) el.childNodes.forEach(translateNode);
            }
          }
          const obs = new MutationObserver((muts)=>{
            muts.forEach(m=>{
              m.addedNodes && m.addedNodes.forEach(translateNode);
              if(m.target) translateNode(m.target);
            });
          });
          translateNode(document.body);
          obs.observe(document.body, {subtree:true, childList:true, characterData:true});
          setInterval(()=>{
            document.querySelectorAll("header [role='button'], header a, header button, [title], [aria-label]").forEach(el=>{
              if(el){
                if(el.textContent){
                  const nv = translateText(el.textContent);
                  if(nv !== el.textContent) el.textContent = nv;
                }
                translateAttributes(el);
              }
            });
          }, 900);
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

def render_sidebar():
    env_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or ""
    if "initialized" not in st.session_state:
        st.session_state["initialized"] = True
        st.session_state["use_sample"] = False
        if env_proxy:
            st.session_state["proxy_enabled"] = True
            st.session_state["proxy_url"] = env_proxy
    with st.sidebar:
        st.header("设置")
        st.checkbox("启用代理", key="proxy_enabled", value=st.session_state.get("proxy_enabled", bool(env_proxy)))
        st.text_input("HTTPS代理（示例：https://1.2.3.4:8080）", key="proxy_url", value=st.session_state.get("proxy_url", env_proxy))
        st.checkbox("忽略SSL证书验证（部分拦截代理需开启）", key="insecure_ssl", value=False)
        cols = st.columns(2)
        with cols[0]:
            test = st.button("测试连接")
        with cols[1]:
            st.checkbox("使用示例数据", key="use_sample", value=st.session_state.get("use_sample", False))
        cols2 = st.columns(2)
        with cols2[0]:
            diag = st.button("一键诊断")
        with cols2[1]:
            auto = st.button("一键连接")
        if test:
            ok = False
            try:
                s = requests.Session()
                if st.session_state.get("proxy_enabled") and st.session_state.get("proxy_url"):
                    s.proxies.update({"http": st.session_state["proxy_url"], "https": st.session_state["proxy_url"]})
                r = s.get("https://top.baidu.com/api/board?platform=pc&tab=realtime", timeout=8, verify=not st.session_state.get("insecure_ssl", False))
                ok = r.status_code < 400 and "data" in r.text
            except Exception:
                ok = False
            if ok:
                st.success("连接正常")
            else:
                st.error("无法连接到百度热搜接口，可能需要代理或稍后重试")
        if diag:
            try:
                df = fetch_baidu_board("realtime")
                st.success(f"百度热搜获取成功：{len(df)} 条")
                st.dataframe(df.head(10), width="stretch", hide_index=True)
            except Exception as e:
                st.error(f"百度热搜获取失败：{e}")
        if auto:
            candidates = []
            # 环境变量
            if env_proxy:
                candidates.append(env_proxy)
            # 常见本地端口
            candidates += [
                "https://127.0.0.1:7890",
                "http://127.0.0.1:7890",
                "socks5h://127.0.0.1:1080",
                "https://127.0.0.1:1080",
                "http://127.0.0.1:1080",
                "http://127.0.0.1:8889",
                "http://127.0.0.1:8080",
            ]
            # 先试直连
            ok, used = try_connect(None, not st.session_state.get("insecure_ssl", False))
            if ok:
                st.success("直连可用，已关闭代理")
                st.session_state["proxy_enabled"] = False
                st.session_state["proxy_url"] = ""
                os.environ.pop("HTTPS_PROXY", None)
                os.environ.pop("https_proxy", None)
            else:
                chosen = None
                for proxy in candidates:
                    ok, _ = try_connect(proxy, not st.session_state.get("insecure_ssl", False))
                    if ok:
                        chosen = proxy
                        break
                if chosen:
                    st.session_state["proxy_enabled"] = True
                    st.session_state["proxy_url"] = chosen
                    os.environ["HTTPS_PROXY"] = chosen
                    os.environ["https_proxy"] = chosen
                    st.success(f"已自动选择代理：{chosen}")
                else:
                    st.error("未找到可用的代理，请手动填写再试")

def try_connect(proxy: Optional[str], verify: bool) -> Tuple[bool, Optional[str]]:
    try:
        s = requests.Session()
        s.headers.update({"User-Agent": "Mozilla/5.0"})
        if proxy:
            s.proxies.update({"http": proxy, "https": proxy})
        s.verify = verify
        r = s.get("https://top.baidu.com/api/board?platform=pc&tab=realtime", timeout=8)
        ok = r.status_code == 200 and "data" in r.text
        return ok, proxy
    except Exception:
        return False, proxy

def _http_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Referer": "https://top.baidu.com/",
        "Accept": "application/json, text/plain, */*",
    })
    proxy_enabled = st.session_state.get("proxy_enabled", False)
    proxy_url = st.session_state.get("proxy_url", "").strip()
    if proxy_enabled and proxy_url:
        s.proxies.update({"http": proxy_url, "https": proxy_url})
    s.verify = not st.session_state.get("insecure_ssl", False)
    return s

def fetch_baidu_board(tab: str = "realtime"):
    url = f"https://top.baidu.com/api/board?platform=pc&tab={tab}"
    s = _http_session()
    r = s.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    cards = data.get("data", {}).get("cards", [])
    items = []
    for card in cards:
        # 置顶
        for it in card.get("topContent", []) or []:
            items.append({
                "词条": it.get("word") or it.get("name") or it.get("title"),
                "简介": it.get("desc") or it.get("brief") or "",
                "热度": it.get("hotScore") or it.get("heat") or "",
                "链接": it.get("url") or it.get("link") or "",
            })
        # 普通
        for it in card.get("content", []) or []:
            items.append({
                "词条": it.get("word") or it.get("name") or it.get("title"),
                "简介": it.get("desc") or it.get("brief") or "",
                "热度": it.get("hotScore") or it.get("heat") or "",
                "链接": it.get("url") or it.get("link") or "",
            })
    df = pd.DataFrame(items)
    if not df.empty:
        df.insert(0, "排名", range(1, len(df) + 1))
    return df

def fetch_baidu_board_with_fallback(candidates):
    last_err = None
    for tab in candidates:
        try:
            df = fetch_baidu_board(tab)
            if not df.empty:
                return df, tab
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    return pd.DataFrame(), candidates[0]

def render_hot_trends():
    st.subheader("百度热搜榜")
    cols = st.columns([1.1, 1.1, 1.2])
    with cols[0]:
        topn = st.slider("显示数量", 10, 100, 30, 5)
    with cols[1]:
        board_label = st.radio("榜单", ["总榜", "小说", "电影", "电视剧"], horizontal=True, label_visibility="collapsed")
    with cols[2]:
        refresh = st.button("获取最新数据", type="primary", use_container_width=True)

    board_map = {
        "总榜": ["realtime", "all"],
        "小说": ["novel", "fiction"],
        "电影": ["movie", "film"],
        "电视剧": ["teleplay", "tv", "tvplay", "tv_series"],
    }
    candidates = board_map.get(board_label, ["realtime"])
    st.caption(f"数据源：top.baidu.com（{board_label}）")

    if "hot_df" not in st.session_state:
        st.session_state["hot_df"] = None
        st.session_state["hot_ts"] = None
        st.session_state["hot_tab"] = None
        st.session_state["hot_key"] = None

    if st.session_state.get("use_sample") and st.session_state.get("hot_df") is None and not refresh:
        sample = pd.DataFrame({
            "排名": list(range(1, topn + 1)),
            "词条": [f"示例热词{i+1}" for i in range(topn)],
            "简介": ["" for _ in range(topn)],
            "热度": [int(1e6 - i * 1000) for i in range(topn)],
            "链接": ["" for _ in range(topn)],
        })
        st.info("当前显示示例数据；点击“获取最新数据”可拉取实时数据")
        st.dataframe(sample, width="stretch", hide_index=True)
        return

    if refresh:
        try:
            df_new, ok_tab = fetch_baidu_board_with_fallback(candidates)
            if not df_new.empty:
                st.session_state["hot_df"] = df_new
                st.session_state["hot_ts"] = pd.Timestamp.now()
                st.session_state["hot_tab"] = ok_tab
                st.session_state["hot_key"] = board_label
                st.success("已更新为最新数据")
        except Exception:
            st.error("拉取最新数据失败，请稍后再试或检查网络/代理")

    df_cached = st.session_state.get("hot_df")
    # 如果切换了榜单且没有对应缓存，则拉取
    if df_cached is None or st.session_state.get("hot_key") != board_label:
        try:
            df_cached, ok_tab = fetch_baidu_board_with_fallback(candidates)
            st.session_state["hot_df"] = df_cached
            st.session_state["hot_ts"] = pd.Timestamp.now()
            st.session_state["hot_tab"] = ok_tab
            st.session_state["hot_key"] = board_label
        except Exception:
            sample = pd.DataFrame({
                "排名": list(range(1, topn + 1)),
                "词条": [f"示例热词{i+1}" for i in range(topn)],
                "简介": ["" for _ in range(topn)],
                "热度": [int(1e6 - i * 1000) for i in range(topn)],
                "链接": ["" for _ in range(topn)],
            })
            st.warning("实时数据暂不可用，已显示示例数据")
            st.dataframe(sample, width="stretch", hide_index=True)
            return

    if df_cached is None or df_cached.empty:
        st.info("暂无数据")
        return

    ts = st.session_state.get("hot_ts")
    if ts:
        st.caption(f"上次更新时间：{ts.strftime('%Y-%m-%d %H:%M:%S')}")
    display_cols = [c for c in ["排名", "词条", "简介", "热度", "链接"] if c in df_cached.columns]
    st.dataframe(df_cached[display_cols].head(topn), width="stretch", hide_index=True)

st.title("中国热搜")
apply_theme()
render_sidebar()
render_hot_trends()
