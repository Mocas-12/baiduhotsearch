# -*- coding: utf-8 -*-
"""全局主题样式：PULSE TERMINAL 暗色主题 + 组件 CSS + Streamlit 英文菜单汉化脚本。

设计语言与 GAMECHARTS（steam-live-charts）同族：
深空底色 + 三色极光 + 胶片颗粒 + 玻璃拟态 + 金色主色 + 等宽字终端感，
行式榜单、零 emoji、克制的描边控件。
"""
import streamlit as st

def apply_theme():
    st.markdown(
        """
        <style>
        :root{
          --hs-line: rgba(255,255,255,.08);
          --hs-line-hi: rgba(255,255,255,.18);
          --hs-glass: rgba(15,18,28,.55);
          --hs-text: #eef0f6;
          --hs-muted: #9aa3b8;
          --hs-dim: #6b7285;
          --hs-gold: #f0c75e;
          --hs-gold-2: #ffdf8e;
          --hs-ice: #7dd7ff;
          --hs-ember: #ff7a5c;
          --hs-mono: ui-monospace, "Cascadia Mono", Consolas, monospace;
        }
        html, body, .stApp{
          font-family: "Segoe UI", "Microsoft YaHei", system-ui, sans-serif;
          color: var(--hs-text);
        }
        .stApp{ -webkit-font-smoothing: antialiased; }
        html{ scroll-behavior: smooth; }

        [data-testid="stAppViewContainer"]{
          background:
            radial-gradient(1100px 640px at 86% -12%, rgba(125,215,255,.14), transparent 62%),
            radial-gradient(950px 700px at -12% 16%, rgba(240,199,94,.12), transparent 58%),
            radial-gradient(900px 620px at 50% 115%, rgba(122,92,255,.10), transparent 62%),
            #06070b fixed;
        }
        [data-testid="stMain"], section.stMain, [data-testid="stAppViewContainer"] > div{
          background: transparent;
        }

        /* 胶片颗粒噪点覆盖 —— 去掉"平滑生成感"的关键一层 */
        .stApp::after{
          content: ""; position: fixed; inset: 0; z-index: 99; pointer-events: none; opacity: .05;
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)' opacity='0.6'/%3E%3C/svg%3E");
        }

        /* ===== Streamlit 框架 ===== */
        [data-testid="stHeader"]{
          background: rgba(6,7,11,.55) !important;
          backdrop-filter: blur(14px);
          -webkit-backdrop-filter: blur(14px);
          border-bottom: 1px solid rgba(255,255,255,.05);
        }
        #MainMenu, [data-testid="stStatusWidget"], [data-testid="stToolbar"]{ display: none; }
        footer, [data-testid="stFooter"]{ visibility: hidden; }
        .main .block-container, [data-testid="stMainBlockContainer"]{
          max-width: 1180px;
          margin-inline: auto;
          padding: 4.5rem 1.4rem 2.4rem;
        }
        section[data-testid="stVerticalBlock"]{ gap: .45rem; }
        a{ color: var(--hs-text); }
        .stMarkdown a, .stMarkdown a *{ text-decoration: none !important; }

        /* ===== 玻璃导航栏 ===== */
        .hs-nav{
          background: var(--hs-glass);
          margin: 12px 0 4px;
          padding: 0 20px;
          border: 1px solid var(--hs-line);
          border-radius: 16px;
          height: 56px; display: flex; align-items: center;
          box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 12px 40px rgba(0,0,0,.45);
          backdrop-filter: blur(16px) saturate(1.5);
          -webkit-backdrop-filter: blur(16px) saturate(1.5);
        }
        .hs-nav-inner{ display: flex; align-items: center; gap: 20px; width: 100%; }
        .hs-logo{ display: flex; align-items: center; gap: 10px; }
        .hs-logo-mark{
          width: 12px; height: 12px; border-radius: 4px;
          background: linear-gradient(135deg, var(--hs-gold-2), var(--hs-gold));
          box-shadow: 0 0 14px rgba(240,199,94,.55);
        }
        .hs-logo-word{ font-size: 16px; font-weight: 800; letter-spacing: .5px; color: #fff !important; }
        .hs-logo-word span{ color: var(--hs-gold) !important; }
        .hs-logo-sub{
          font-family: var(--hs-mono); font-size: 10px; font-weight: 600; letter-spacing: 2.5px;
          color: var(--hs-ice) !important; border: 1px solid rgba(125,215,255,.35); padding: 3px 9px;
          border-radius: 99px;
          box-shadow: inset 0 0 12px rgba(125,215,255,.08);
        }
        .hs-nav .spacer{ margin-right: auto; }
        .hs-nav a{
          color: #98a0b3; text-decoration: none !important; font-size: 13px; font-weight: 500;
          padding: 7px 11px; border-radius: 8px;
        }
        .hs-nav a:hover{ color: #e8eaf0; background: rgba(255,255,255,.05); }

        /* ===== 跑马灯资讯条 ===== */
        .hs-ticker{
          background: rgba(255,255,255,.03); border: 1px solid var(--hs-line); border-radius: 12px;
          color: #98a0b3;
          overflow: hidden; height: 34px; display: flex; align-items: center;
          margin: 4px 0 2px;
        }
        .hs-ticker-track{
          display: inline-flex; white-space: nowrap; align-items: center;
          animation: hs-tick 45s linear infinite; will-change: transform;
        }
        .hs-ticker:hover .hs-ticker-track{ animation-play-state: paused; }
        .hs-ticker-track.static{ animation: none; }
        @keyframes hs-tick{ from{ transform: translateX(0); } to{ transform: translateX(-50%); } }
        .hs-ticker .ti{
          color: #98a0b3 !important;
          font-family: var(--hs-mono); font-size: 11.5px; letter-spacing: .5px;
          padding: 0 20px;
        }
        .hs-ticker .ti b{ color: var(--hs-gold) !important; margin-right: 8px; font-weight: 700; }
        .hs-ticker .ti strong{ color: #e8eaf0 !important; font-weight: 600; }

        /* ===== 标题区 ===== */
        .hs-overline{
          font-family: var(--hs-mono); font-size: 11px; letter-spacing: 3px;
          color: var(--hs-dim) !important; text-transform: uppercase; margin: 20px 0 8px;
        }
        .hs-overline .dot{
          display: inline-block; width: 8px; height: 8px; border-radius: 50%;
          background: var(--hs-ember); margin-right: 9px; vertical-align: 0;
          box-shadow: 0 0 10px rgba(255,122,92,.9);
          animation: hs-pulse 1.8s infinite;
        }
        @keyframes hs-pulse{ 50%{ opacity: .3; } }
        .hs-h1{
          font-size: clamp(30px, 4.5vw, 44px); font-weight: 900; letter-spacing: -.5px;
          line-height: 1.08; color: #fff !important; margin: 0;
        }
        .hs-h1 em{
          font-style: normal;
          background: linear-gradient(120deg, var(--hs-gold-2) 10%, var(--hs-gold) 55%, #d99a2b 95%);
          -webkit-background-clip: text; background-clip: text; color: transparent;
        }
        .hs-tagline{ color: var(--hs-muted) !important; font-size: 13px; margin: 8px 0 2px; }

        /* ===== 元信息行（mono + 呼吸点） ===== */
        .hs-meta-line{
          font-family: var(--hs-mono); font-size: 12px; color: #98a0b5;
          display: flex; flex-wrap: wrap; align-items: center; gap: 4px 14px; padding: 2px 2px 4px;
        }
        .hs-meta-line .dot{
          width: 8px; height: 8px; border-radius: 50%; background: var(--hs-ice);
          box-shadow: 0 0 10px rgba(125,215,255,.9); animation: hs-pulse 1.8s infinite;
        }
        .hs-meta-line b{ color: #e8eaf0 !important; font-weight: 700; }

        /* ===== 榜单分区标题 ===== */
        .hs-panel{ margin-top: 14px; }
        .hs-section{
          color: #fff; font-size: 22px; font-weight: 800; letter-spacing: .2px;
          padding: 8px 0 14px; display: flex; align-items: baseline; gap: 12px;
        }
        .hs-section::before{
          content: ""; width: 6px; height: 22px; align-self: center;
          background: linear-gradient(180deg, var(--hs-gold-2), var(--hs-gold));
          border-radius: 3px;
          box-shadow: 0 0 12px rgba(240,199,94,.4);
        }
        .hs-section .sub{
          color: var(--hs-dim) !important; font-size: 11.5px; font-family: var(--hs-mono);
          letter-spacing: 1.5px; font-weight: 400;
        }

        /* ===== 行式榜单 ===== */
        .hs-thead, .hs-row{
          display: grid;
          grid-template-columns: 56px minmax(0,1fr) 168px;
          gap: 16px; align-items: center; padding: 9px 8px;
        }
        .hs-thead{
          color: var(--hs-dim) !important; font-size: 11px; font-weight: 600; letter-spacing: 2px;
          font-family: var(--hs-mono); text-transform: uppercase;
          border-bottom: 1px solid var(--hs-line); padding-bottom: 10px; margin-bottom: 4px;
        }
        .hs-thead .r{ text-align: right; }
        .hs-row{
          position: relative; overflow: hidden;
          border-radius: 13px; text-decoration: none !important;
          background: linear-gradient(90deg, rgba(255,255,255,.025), rgba(255,255,255,.008));
          border: 1px solid transparent;
          transition: background .18s, border-color .18s, transform .18s;
        }
        .hs-row[href]{ cursor: pointer; }
        .hs-row:hover{
          background: rgba(255,255,255,.05);
          border-color: var(--hs-line);
          transform: translateY(-1px);
        }
        .hs-row::after{
          content: ""; position: absolute; inset: 0; pointer-events: none;
          background: linear-gradient(105deg, transparent 42%, rgba(255,255,255,.06) 50%, transparent 58%);
          transform: translateX(-130%);
          transition: transform .7s ease;
        }
        .hs-row:hover::after{ transform: translateX(130%); }
        .hs-row .rank{
          font-family: var(--hs-mono); font-size: 20px; font-weight: 800;
          color: #4d5872 !important; text-align: center;
          transition: color .18s;
        }
        .hs-row:nth-of-type(1) .rank, .hs-row:nth-of-type(2) .rank, .hs-row:nth-of-type(3) .rank{ font-size: 22px; }
        .hs-row:nth-of-type(1) .rank{
          background: linear-gradient(155deg, #ffeaa8 5%, var(--hs-gold) 50%, #c98f1e 95%);
          -webkit-background-clip: text; background-clip: text; color: transparent !important;
          filter: drop-shadow(0 0 10px rgba(240,199,94,.35));
        }
        .hs-row:nth-of-type(2) .rank{
          background: linear-gradient(155deg, #f6f9ff 5%, #cdd8ec 50%, #9fb0d0 95%);
          -webkit-background-clip: text; background-clip: text; color: transparent !important;
        }
        .hs-row:nth-of-type(3) .rank{
          background: linear-gradient(155deg, #ffd4b0 5%, #eda06f 50%, #b06535 95%);
          -webkit-background-clip: text; background-clip: text; color: transparent !important;
        }
        .hs-row:hover .rank{ background: none; color: var(--hs-ice) !important; filter: none; }
        .hs-row .hword{
          color: #fff !important; font-size: 15.5px; font-weight: 700; line-height: 1.35;
        }
        .hs-row:hover .hword{ color: var(--hs-gold) !important; }
        .hs-row .hdesc{
          color: var(--hs-muted) !important; font-size: 12.5px; line-height: 1.5; margin-top: 3px;
          display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden;
        }
        .hs-row .pill-row{
          display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
          margin-top: 6px;
        }
        .hs-row .pill-row:empty{ display: none; }
        .hs-row .hmeta{ display: flex; flex-direction: column; align-items: flex-end; gap: 3px; text-align: right; }
        .hs-row .hmeta .onboard{
          font-family: var(--hs-mono); font-size: 11.5px; color: var(--hs-dim) !important;
          font-variant-numeric: tabular-nums; white-space: nowrap;
        }
        .hs-row .hmeta .hit b{
          display: block; font-family: var(--hs-mono); font-size: 18px; font-weight: 800; color: #fff !important;
          font-variant-numeric: tabular-nums; line-height: 1.2;
        }
        .hs-row .hmeta .hit i{
          display: block; font-style: normal; font-family: var(--hs-mono); font-size: 10px;
          color: var(--hs-dim) !important; letter-spacing: 1.5px; margin-top: 2px;
        }
        .hs-row .tag-new{
          display: inline-block; font-family: var(--hs-mono); font-size: 10px; font-weight: 700;
          letter-spacing: 1.5px; padding: 3px 9px; border-radius: 99px;
          background: rgba(240,199,94,.10); border: 1px solid rgba(240,199,94,.45);
          color: var(--hs-gold) !important; white-space: nowrap;
          animation: hs-pulse 2.2s ease-in-out infinite;
        }

        /* ===== 源徽章（描边 + 色点） ===== */
        .src-badge{
          display: inline-flex; align-items: center; gap: 6px;
          padding: 2.5px 10px; border-radius: 99px;
          font-family: var(--hs-mono); font-size: 11px; font-weight: 600; line-height: 1.5;
          letter-spacing: .5px; white-space: nowrap;
          color: var(--c, #9aa3b8) !important;
          border: 1px solid color-mix(in srgb, var(--c, #9aa3b8) 42%, transparent);
          background: color-mix(in srgb, var(--c, #9aa3b8) 9%, transparent);
        }
        .src-badge i{
          width: 6px; height: 6px; border-radius: 50%; flex: none;
          background: var(--c, #9aa3b8);
          box-shadow: 0 0 8px var(--c, transparent);
        }
        .tag-badge{
          display: inline-flex; align-items: center; gap: 4px;
          padding: 2.5px 9px; border-radius: 99px;
          font-family: var(--hs-mono); font-size: 11px; font-weight: 600; line-height: 1.5;
          background: rgba(255,255,255,.05);
          border: 1px solid rgba(255,255,255,.12);
          color: var(--hs-muted);
        }

        /* ===== 空状态 ===== */
        .hs-empty{ padding: 48px 0 40px; text-align: center; color: #98a0b5; }
        .hs-empty .ghost{
          font-family: var(--hs-mono); font-size: 38px; font-weight: 800; color: #262b36; line-height: 1;
        }
        .hs-empty .etitle{ color: #e8eaf0; font-weight: 700; margin: 14px 0 6px; }
        .hs-empty .esub{ font-size: 12.5px; font-family: var(--hs-mono); color: var(--hs-dim); }

        /* ===== 侧边栏 ===== */
        [data-testid="stSidebar"]{
          background: linear-gradient(180deg, rgba(14,16,24,.97), rgba(9,10,16,.97));
          border-right: 1px solid rgba(255,255,255,.07);
          box-shadow: 6px 0 30px rgba(0,0,0,.35);
        }
        [data-testid="stSidebar"] *{ color: #c6cad7; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
          background: linear-gradient(90deg, var(--hs-gold-2), var(--hs-gold));
          -webkit-background-clip: text; background-clip: text;
          color: transparent !important; font-weight: 800;
        }
        [data-testid="stSidebar"] hr{ border-color: rgba(255,255,255,.08); }
        [data-testid="stSidebar"] [data-testid="stExpander"]{
          background: rgba(255,255,255,.03);
          border: 1px solid var(--hs-line) !important;
          border-radius: 12px;
        }
        input[type="checkbox"]{ accent-color: var(--hs-gold); }

        /* ===== 输入控件 ===== */
        input[type="text"], input[type="password"], input[type="number"], textarea{
          background: rgba(255,255,255,.04) !important;
          color: #e8eaf0 !important;
          border: 1px solid var(--hs-line) !important;
          border-radius: 10px !important;
          font-size: 13px;
        }
        input:focus, textarea:focus{
          border-color: rgba(125,215,255,.55) !important;
          box-shadow: 0 0 0 3px rgba(125,215,255,.12) !important;
        }
        input::placeholder, textarea::placeholder{ color: var(--hs-dim) !important; }

        /* ===== 按钮（克制的描边胶囊；primary 为金色实体） ===== */
        .stButton > button{
          border-radius: 10px !important;
          padding: 9px 18px;
          background: rgba(255,255,255,.05) !important;
          border: 1px solid var(--hs-line-hi) !important;
          color: #e8eaf0 !important;
          font-size: 12.5px; font-weight: 600; letter-spacing: .5px;
          transition: all .15s;
        }
        .stButton > button p{ font-size: 12.5px; font-weight: 600; letter-spacing: .5px; color: #e8eaf0 !important; }
        .stButton > button:not([kind="primary"]):hover{
          background: rgba(125,215,255,.12) !important;
          border-color: rgba(125,215,255,.4) !important;
          color: #fff !important;
        }
        .stButton > button:not([kind="primary"]):hover p{ color: #fff !important; }
        button[kind="primary"]{
          background: linear-gradient(135deg, var(--hs-gold-2), var(--hs-gold)) !important;
          border: none !important;
          box-shadow: 0 4px 18px rgba(240,199,94,.3);
        }
        button[kind="primary"] p{ color: #171204 !important; font-weight: 700 !important; }
        button[kind="primary"]:hover{ filter: brightness(1.08); box-shadow: 0 6px 24px rgba(240,199,94,.45); }
        button[kind="primary"]:active{ transform: scale(0.98); }

        /* ===== 分段切换控件（stRadio react-aria DOM → segmented control） ===== */
        [data-testid="stRadioGroup"]{
          display: inline-flex; flex-wrap: wrap; gap: 2px;
          background: var(--hs-glass); border: 1px solid var(--hs-line);
          border-radius: 13px; padding: 4px;
          box-shadow: inset 0 1px 0 rgba(255,255,255,.07);
          backdrop-filter: blur(12px) saturate(1.4);
          -webkit-backdrop-filter: blur(12px) saturate(1.4);
        }
        [data-testid="stRadioOption"]{
          border-radius: 9px; padding: 8px 16px !important; margin: 0 !important;
          background: transparent !important; border: none !important;
          transition: background .15s; cursor: pointer;
        }
        [data-testid="stRadioOption"]:hover{ background: rgba(255,255,255,.05) !important; }
        [data-testid="stRadioOption"] p{ font-size: 13.5px; font-weight: 600; color: #98a0b3 !important; }
        [data-testid="stRadioOption"][data-selected="true"]{
          background: linear-gradient(135deg, var(--hs-gold-2), var(--hs-gold)) !important;
          box-shadow: 0 4px 18px rgba(240,199,94,.32);
        }
        [data-testid="stRadioOption"][data-selected="true"] p{ color: #171204 !important; font-weight: 700; }
        [data-testid="stRadioOption"] > div > div > div:first-child{ display: none; }

        /* ===== 滑块 ===== */
        .stSlider{ color: var(--hs-dim); }
        .stSlider [role="slider"]{
          background: linear-gradient(135deg, var(--hs-gold-2), var(--hs-gold)) !important;
          border: 2px solid #1a1e2c !important;
          box-shadow: 0 2px 10px rgba(240,199,94,.5);
        }
        .stSlider [data-baseweb="slider"] > div{ background-color: rgba(255,255,255,.12) !important; }

        /* ===== 提示条 ===== */
        [data-testid="stAlert"]{
          background: rgba(20,23,34,.65) !important;
          border: 1px solid rgba(240,199,94,.22) !important;
          border-radius: 13px !important;
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
        }
        [data-testid="stAlert"] p{ color: #c9cdd9 !important; font-size: 13px; }
        [data-testid="stCaptionContainer"], .stCaption{ color: var(--hs-dim) !important; }
        hr{ border-color: rgba(255,255,255,.08); }

        /* ===== 页脚 ===== */
        .hs-footer{
          color: var(--hs-dim) !important; font-size: 12.5px; line-height: 1.8;
          border-top: 1px solid var(--hs-line); padding-top: 14px; margin-top: 22px;
        }
        .hs-footer a{ color: var(--hs-muted) !important; }
        .hs-footer a:hover{ color: var(--hs-gold) !important; }

        ::selection{ background: rgba(240,199,94,.32); color: #fff; }
        ::-webkit-scrollbar{ width: 9px; height: 9px; }
        ::-webkit-scrollbar-thumb{
          background: rgba(255,255,255,.14);
          border-radius: 99px;
          border: 2px solid transparent;
          background-clip: content-box;
        }
        ::-webkit-scrollbar-thumb:hover{
          background: rgba(240,199,94,.45);
          background-clip: content-box;
        }
        ::-webkit-scrollbar-track{ background: transparent; }

        /* ===== 响应式 ===== */
        @media (max-width: 860px){
          .hs-nav{ padding: 0 14px; }
          .hs-nav a{ display: none; }
          .hs-h1{ font-size: 24px; }
          .hs-section{ font-size: 17px; }
          .hs-section::before{ height: 18px; }
          .hs-row, .hs-thead{ grid-template-columns: 34px minmax(0,1fr) auto; gap: 11px; }
          .hs-thead{ display: none; }
          .hs-row .rank{ font-size: 14px; }
          .hs-row .hword{ font-size: 14px; }
          .hs-row .hmeta .onboard{ display: none; }
          .hs-ticker{ height: 30px; }
          .hs-ticker .ti{ font-size: 11px; padding: 0 14px; }
          .hs-footer{ font-size: 11.5px; }
        }
        @media (max-width: 480px){
          .block-container{ padding: 4.2rem .9rem 1.6rem; }
          .hs-row{ grid-template-columns: 28px minmax(0,1fr) auto; gap: 10px; padding: 7px 4px; }
          .hs-row .hword{
            font-size: 13.5px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
          }
          .hs-row .hdesc{ font-size: 11.5px; }
          .hs-empty .ghost{ font-size: 30px; }
          .hs-meta-line{ font-size: 11px; }
        }
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
