# -*- coding: utf-8 -*-
"""全局主题样式：暗色卡片风 + 组件 CSS + Streamlit 英文菜单汉化脚本。"""
import streamlit as st

def apply_theme():
    st.markdown(
        """
        <style>
        :root{
          --panel: rgba(255,255,255,0.045);
          --border: rgba(255,255,255,0.08);
          --txt: #f2f4f9;
          --sub: #8f96ab;
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
        @media (max-width: 720px){
          .hot-card{ flex-wrap: wrap; }
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

        /* ===== 源徽章 / 状态徽章 ===== */
        .pill-row{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 5px; align-items: center; }
        .src-badge{
          display: inline-flex; align-items: center; gap: 5px;
          padding: 2.5px 9px; border-radius: 999px;
          font-size: 11.5px; font-weight: 700; color: #fff;
          letter-spacing: 0.3px; line-height: 1.4;
        }
        .tag-badge{
          display: inline-flex; align-items: center; gap: 4px;
          padding: 2.5px 9px; border-radius: 999px;
          font-size: 11.5px; font-weight: 600; line-height: 1.4;
          background: rgba(255,255,255,0.07);
          border: 1px solid rgba(255,255,255,0.12);
          color: #9aa2b5;
        }
        .tag-badge.new{
          background: rgba(64,222,120,0.12);
          border-color: rgba(64,222,120,0.4);
          color: #6ff0a1;
        }
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

