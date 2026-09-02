import os
import html
import streamlit as st
import pandas as pd
import requests
from typing import Optional, Tuple
import streamlit.components.v1 as components

st.set_page_config(page_title="中国热搜", layout="wide", initial_sidebar_state="collapsed")

def apply_theme():
    st.markdown(
        """
        <style>
        :root{
          --bg: #0d0f16;
          --panel: rgba(255,255,255,0.045);
          --border: rgba(255,255,255,0.08);
          --txt: #f2f4f9;
          --sub: #8f96ab;
          --fire1: #ff512f;
          --fire2: #ff9a3c;
        }
        html, body, .stApp, [data-testid="stAppViewContainer"]{
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;
        }
        .stApp{ -webkit-font-smoothing: antialiased; }
        html{ scroll-behavior: smooth; }

        [data-testid="stAppViewContainer"]{
          background:
            radial-gradient(1100px 520px at 12% -8%, rgba(255,81,47,0.16), transparent 62%),
            radial-gradient(900px 480px at 108% 6%, rgba(255,154,60,0.12), transparent 58%),
            radial-gradient(700px 420px at 50% 115%, rgba(255,77,109,0.08), transparent 60%),
            linear-gradient(180deg, #0d0f16 0%, #111420 100%);
          background-attachment: fixed;
        }
        [data-testid="stMain"], section.stMain, [data-testid="stAppViewContainer"] > div{
          background: transparent;
        }
        [data-testid="stHeader"]{
          background: rgba(13,15,22,0.55) !important;
          backdrop-filter: blur(12px);
          border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .main .block-container, [data-testid="stMainBlockContainer"]{
          max-width: 1180px;
          margin-inline: auto;
          padding: 1.2rem 1.4rem 3.4rem;
        }

        /* ===== Hero ===== */
        .hero{ padding: 24px 6px 2px; }
        .hero-badge{
          display: inline-flex; align-items: center; gap: 8px;
          padding: 7px 15px; border-radius: 999px;
          background: rgba(255,90,45,0.12);
          border: 1px solid rgba(255,110,60,0.35);
          color: #ffb59e; font-size: 13px; font-weight: 600; letter-spacing: 0.5px;
        }
        .live-dot{
          width: 8px; height: 8px; border-radius: 50%;
          background: #ff4d2e;
          animation: pulse 1.6s infinite;
        }
        @keyframes pulse{
          0%{ box-shadow: 0 0 0 0 rgba(255,77,46,0.55); }
          70%{ box-shadow: 0 0 0 9px rgba(255,77,46,0); }
          100%{ box-shadow: 0 0 0 0 rgba(255,77,46,0); }
        }
        .hero-title{
          font-size: clamp(38px, 6vw, 62px);
          font-weight: 900; line-height: 1.12;
          margin: 14px 0 6px; color: var(--txt); letter-spacing: 1px;
        }
        .hero-title .grad{
          background: linear-gradient(120deg, #ff512f 10%, #ff9a3c 60%, #ffd166 100%);
          -webkit-background-clip: text; background-clip: text; color: transparent;
        }
        .flame{
          display: inline-block;
          animation: flick 1.8s ease-in-out infinite;
          filter: drop-shadow(0 4px 14px rgba(255,102,0,0.55));
          margin-right: 6px;
        }
        @keyframes flick{
          0%, 100%{ transform: scale(1) rotate(-2deg); }
          50%{ transform: scale(1.12) rotate(3deg); }
        }
        .hero-sub{ color: var(--sub); font-size: 15.5px; margin: 0 0 6px; }
        .hero-rule{
          height: 3px; width: 96px; border-radius: 99px;
          background: linear-gradient(90deg, #ff512f, #ff9a3c, transparent);
          margin: 16px 0 8px;
        }

        /* ===== 元信息 chips ===== */
        .meta-row{ display: flex; flex-wrap: wrap; gap: 10px; margin: 4px 0 16px; }
        .meta-chip{
          display: inline-flex; align-items: center; gap: 7px;
          padding: 7px 14px; border-radius: 999px;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.09);
          color: #aeb3c5; font-size: 13px;
        }
        .meta-chip b{ color: #eef0f6; font-weight: 700; }

        /* ===== 热搜卡片 ===== */
        .hot-list{ margin-top: 4px; }
        .hot-card{
          display: flex; align-items: flex-start; gap: 14px;
          padding: 14px 16px; border-radius: 18px;
          background: var(--panel);
          border: 1px solid var(--border);
          margin-bottom: 10px;
          transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease, background 0.22s ease;
          animation: cardIn 0.45s cubic-bezier(0.2, 0.7, 0.3, 1) both;
          animation-delay: calc(var(--i) * 22ms);
        }
        .hot-card:hover{
          transform: translateY(-3px);
          border-color: rgba(255,140,60,0.45);
          background: rgba(255,255,255,0.07);
          box-shadow: 0 14px 34px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,120,60,0.12), 0 8px 30px rgba(255,90,40,0.12);
        }
        @keyframes cardIn{
          from{ opacity: 0; transform: translateY(14px) scale(0.985); }
          to{ opacity: 1; transform: none; }
        }
        .hot-card.top1{
          border-color: rgba(255,170,60,0.4);
          background: linear-gradient(135deg, rgba(255,120,40,0.10), rgba(255,255,255,0.04));
        }
        .rank{
          flex: 0 0 44px; height: 44px; border-radius: 14px;
          display: flex; align-items: center; justify-content: center;
          font-weight: 800; font-size: 16px; color: #c8cbd8;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.08);
        }
        .rank.r1{ background: linear-gradient(135deg, #ffb300, #ff7a00); color: #fff; box-shadow: 0 6px 18px rgba(255,140,0,0.35); border: none; }
        .rank.r2{ background: linear-gradient(135deg, #c9d1e0, #8f9bb0); color: #141824; border: none; }
        .rank.r3{ background: linear-gradient(135deg, #e0955c, #a9632f); color: #fff; border: none; }
        .hot-main{ flex: 1 1 auto; min-width: 0; }
        .hot-word{
          font-size: 16.5px; font-weight: 700; color: #f2f4f9; text-decoration: none;
        }
        .hot-word:hover{ color: #ffb37e; }
        .hot-desc{
          margin-top: 4px; color: var(--sub); font-size: 13px; line-height: 1.5;
          display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }
        .hot-heat{ flex: 0 0 190px; text-align: right; }
        .heat-num{
          font-weight: 800; color: #ff9a3c; font-size: 14.5px;
          font-variant-numeric: tabular-nums;
        }
        .heat-bar{
          margin-top: 7px; height: 6px; border-radius: 99px;
          background: rgba(255,255,255,0.08); overflow: hidden;
        }
        .heat-fill{
          height: 100%; border-radius: 99px;
          background: linear-gradient(90deg, #ff512f, #ff9a3c);
          box-shadow: 0 0 10px rgba(255,120,40,0.5);
          transition: width 0.6s ease;
        }
        @media (max-width: 720px){
          .hot-card{ flex-wrap: wrap; }
          .hot-heat{ flex: 1 1 100%; text-align: left; }
        }

        /* ===== 侧边栏 ===== */
        [data-testid="stSidebar"]{
          background: linear-gradient(180deg, rgba(22,25,36,0.97), rgba(16,18,27,0.97));
          border-right: 1px solid rgba(255,255,255,0.07);
          box-shadow: 6px 0 30px rgba(0,0,0,0.35);
        }
        [data-testid="stSidebar"] *{ color: #c6cad7; }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3{
          background: linear-gradient(90deg, #ff9a3c, #ff512f);
          -webkit-background-clip: text; background-clip: text;
          color: transparent !important; font-weight: 800;
        }
        [data-testid="stSidebar"] hr{ border-color: rgba(255,255,255,0.08); }

        /* ===== 输入控件 ===== */
        input[type="text"], input[type="number"], textarea{
          background: rgba(255,255,255,0.06) !important;
          color: #eef0f6 !important;
          border: 1px solid rgba(255,255,255,0.12) !important;
          border-radius: 12px !important;
        }
        input:focus, textarea:focus{
          border-color: rgba(255,140,60,0.6) !important;
          box-shadow: 0 0 0 3px rgba(255,110,60,0.15) !important;
        }

        /* ===== 按钮 ===== */
        .stButton > button{
          border-radius: 999px !important;
          border: 1px solid rgba(255,255,255,0.12) !important;
          background: rgba(255,255,255,0.06) !important;
          color: #eef0f6 !important;
          padding: 0.42rem 1.05rem;
          font-weight: 600;
          transition: all 0.22s ease;
        }
        .stButton > button:not([kind="primary"]):hover{
          transform: translateY(-1px);
          border-color: rgba(255,140,60,0.55) !important;
          background: rgba(255,120,60,0.14) !important;
          color: #fff !important;
        }
        button[kind="primary"]{
          background: linear-gradient(135deg, #ff512f, #ff9a3c) !important;
          border: none !important;
          color: #fff !important;
          box-shadow: 0 8px 22px rgba(255,81,47,0.35);
        }
        button[kind="primary"]:hover{
          transform: translateY(-1px);
          box-shadow: 0 12px 28px rgba(255,81,47,0.5);
          filter: saturate(1.06);
        }
        button[kind="primary"]:active{ transform: scale(0.98); }

        /* ===== 榜单切换 chips ===== */
        [data-testid="stRadio"] label{
          padding: 5px 13px !important; margin-right: 6px;
          border-radius: 999px;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.09);
          transition: all 0.2s ease;
        }
        [data-testid="stRadio"] label:hover{ border-color: rgba(255,140,60,0.5); }
        [data-testid="stRadio"] label:has(input:checked){
          background: rgba(255,120,60,0.16) !important;
          border-color: rgba(255,140,60,0.6) !important;
        }
        [data-testid="stRadio"] label:has(input:checked) p,
        [data-testid="stRadio"] label:has(input:checked) div{
          color: #ffd9c2 !important; font-weight: 700;
        }

        /* ===== 滑块 / 提示条 / 其他 ===== */
        .stSlider{ color: var(--sub); }
        .stSlider [role="slider"]{
          background: linear-gradient(135deg, #ff512f, #ff9a3c) !important;
          border: 2px solid #1a1e2c !important;
          box-shadow: 0 2px 10px rgba(255,81,47,0.5);
        }
        [data-testid="stAlert"]{
          border-radius: 14px !important; overflow: hidden;
          backdrop-filter: blur(8px);
        }
        [data-testid="stCaptionContainer"], .stCaption{ color: #78809a !important; }
        [data-testid="stCollapseSidebar"]{ border-radius: 10px; }
        hr{ border-color: rgba(255,255,255,0.08); }

        ::selection{ background: rgba(255,120,60,0.35); color: #fff; }
        ::-webkit-scrollbar{ width: 9px; height: 9px; }
        ::-webkit-scrollbar-thumb{
          background: rgba(255,255,255,0.14);
          border-radius: 99px;
          border: 2px solid transparent;
          background-clip: content-box;
        }
        ::-webkit-scrollbar-thumb:hover{
          background: rgba(255,140,60,0.45);
          background-clip: content-box;
        }
        ::-webkit-scrollbar-track{ background: transparent; }
        footer { visibility: hidden; }
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

def render_hero():
    st.markdown(
        """
        <div class="hero">
          <div class="hero-badge"><span class="live-dot"></span>LIVE · 百度实时热搜</div>
          <h1 class="hero-title"><span class="flame">🔥</span>中国<span class="grad">热搜</span></h1>
          <p class="hero-sub">一眼看尽全网正在发生的事 · 数据实时同步自百度热搜榜</p>
          <div class="hero-rule"></div>
        </div>
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

def _fmt_heat(v):
    try:
        return f"{int(v):,}"
    except (TypeError, ValueError):
        s = str(v) if v is not None else ""
        return s if s else "—"

def render_hot_cards(df, topn):
    rows = df.head(topn).reset_index(drop=True)
    if "热度" in rows.columns:
        heat_vals = pd.to_numeric(rows["热度"], errors="coerce")
    else:
        heat_vals = pd.Series([float("nan")] * len(rows))
    max_heat = float(heat_vals.max()) if heat_vals.notna().any() else 0.0
    if max_heat <= 0:
        max_heat = 1.0
    cards = []
    for i, row in rows.iterrows():
        try:
            rank = int(row.get("排名", i + 1))
        except (TypeError, ValueError):
            rank = i + 1
        word = str(row.get("词条") or "未知词条")
        desc = str(row.get("简介") or "").strip()
        link = str(row.get("链接") or "").strip()
        hv = heat_vals.iloc[i] if i < len(heat_vals) else float("nan")
        hv = 0.0 if pd.isna(hv) else float(hv)
        pct = int(max(4, min(100, round(hv / max_heat * 100))))
        delay = min(i, 25)
        if rank == 1:
            rank_cls, top_cls = "rank r1", " top1"
        elif rank == 2:
            rank_cls, top_cls = "rank r2", ""
        elif rank == 3:
            rank_cls, top_cls = "rank r3", ""
        else:
            rank_cls, top_cls = "rank", ""
        if link:
            word_html = f'<a class="hot-word" href="{html.escape(link, quote=True)}" target="_blank" rel="noopener">{html.escape(word)}</a>'
        else:
            word_html = f'<span class="hot-word">{html.escape(word)}</span>'
        desc_html = f'<div class="hot-desc" title="{html.escape(desc)}">{html.escape(desc)}</div>' if desc else ""
        cards.append(
            f'<div class="hot-card{top_cls}" style="--i:{delay}">'
            f'<div class="{rank_cls}">{rank}</div>'
            f'<div class="hot-main">{word_html}{desc_html}</div>'
            f'<div class="hot-heat"><span class="heat-num">🔥 {_fmt_heat(row.get("热度"))}</span>'
            f'<div class="heat-bar"><div class="heat-fill" style="width:{pct}%"></div></div></div>'
            f'</div>'
        )
    st.markdown('<div class="hot-list">' + "".join(cards) + "</div>", unsafe_allow_html=True)

def render_meta_chips(df, board_label):
    chips = []
    ts = st.session_state.get("hot_ts")
    if ts is not None:
        chips.append(f'<span class="meta-chip">🕒 更新于 <b>{ts.strftime("%H:%M:%S")}</b></span>')
    chips.append(f'<span class="meta-chip">📊 已收录 <b>{len(df)}</b> 条</span>')
    if "热度" in df.columns:
        hv = pd.to_numeric(df["热度"], errors="coerce").max()
        if pd.notna(hv):
            chips.append(f'<span class="meta-chip">🔥 最高热度 <b>{_fmt_heat(hv)}</b></span>')
    chips.append(f'<span class="meta-chip">🏷️ {html.escape(str(board_label))}</span>')
    st.markdown('<div class="meta-row">' + "".join(chips) + "</div>", unsafe_allow_html=True)

def render_hot_trends():
    cols = st.columns([1.1, 1.4, 1.2])
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
        render_hot_cards(sample, topn)
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
            render_hot_cards(sample, topn)
            return

    if df_cached is None or df_cached.empty:
        st.info("暂无数据")
        return

    render_meta_chips(df_cached, board_label)
    render_hot_cards(df_cached, topn)
    render_counter()

def render_author_badge():
    st.markdown(
        """
        <div class="author-badge">
          作者：Unlimited Box&nbsp;&nbsp;|&nbsp;&nbsp;邮箱：<a href="mailto:a18577y@gmail.com">a18577y@gmail.com</a>
        </div>
        <style>
        .author-badge{
          position: fixed;
          left: 16px;
          bottom: 16px;
          background: rgba(20,22,32,0.78);
          border: 1px solid rgba(255,255,255,0.10);
          color: #c9cdd9;
          padding: 9px 15px;
          border-radius: 999px;
          font-size: 12.5px;
          z-index: 9999;
          box-shadow: 0 10px 28px rgba(0,0,0,0.4);
          backdrop-filter: blur(10px);
        }
        .author-badge a{
          color: #ffb37e;
          text-decoration: none;
        }
        .author-badge a:hover{
          text-decoration: underline;
        }
        @media (max-width: 640px){
          .author-badge{
            left: 8px;
            bottom: 8px;
            font-size: 12px;
            padding: 6px 12px;
          }
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
        """,
        height=50,
    )

apply_theme()
render_sidebar()
render_hero()
render_hot_trends()
render_author_badge()
