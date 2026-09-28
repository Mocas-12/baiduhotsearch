# -*- coding: utf-8 -*-
"""全局主题样式：PULSE GLASS 苹果生态风主题 + 组件 CSS + Streamlit 英文菜单汉化脚本。

设计语言：石墨深底 + 磨砂玻璃（visionOS）+ 系统红点缀（热搜语义色）+ SF 系字体栈
+ iOS 分段控件/大面积留白。不用渐变文字、噪点纹理、扫光特效。
"""
import streamlit as st

def apply_theme():
    st.markdown(
        """
        <style>
        :root{
          --hs-hairline: rgba(255,255,255,.08);
          --hs-hairline-hi: rgba(255,255,255,.14);
          --hs-glass: rgba(28,28,32,.55);
          --hs-fill: rgba(255,255,255,.05);
          --hs-text: #f5f5f7;
          --hs-text-2: #a1a1aa;
          --hs-text-3: #6e6e76;
          --hs-red: #ff453a;
          --hs-red-soft: #ff6b5e;
          --hs-orange: #ff9f0a;
          --hs-yellow: #ffd60a;
          --hs-green: #30d158;
          --hs-blue: #0a84ff;
        }
        html, body, .stApp{
          font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI",
                       "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
          color: var(--hs-text);
        }
        .stApp{ -webkit-font-smoothing: antialiased; }
        html{ scroll-behavior: smooth; }

        [data-testid="stAppViewContainer"]{
          background:
            radial-gradient(1100px 620px at 82% -12%, rgba(90,90,220,.08), transparent 62%),
            radial-gradient(900px 560px at -8% 8%, rgba(255,69,58,.055), transparent 58%),
            linear-gradient(180deg, #0b0b0e 0%, #101014 100%);
          background-attachment: fixed;
        }
        [data-testid="stMain"], section.stMain, [data-testid="stAppViewContainer"] > div{
          background: transparent;
        }

        /* ===== Streamlit 框架 ===== */
        [data-testid="stHeader"]{
          background: rgba(11,11,14,.6) !important;
          backdrop-filter: blur(20px) saturate(1.8);
          -webkit-backdrop-filter: blur(20px) saturate(1.8);
          border-bottom: 1px solid rgba(255,255,255,.05);
        }
        #MainMenu, [data-testid="stStatusWidget"], [data-testid="stToolbar"]{ display: none; }
        footer, [data-testid="stFooter"]{ visibility: hidden; }
        .main .block-container, [data-testid="stMainBlockContainer"]{
          position: relative;
          max-width: 1120px;
          margin-inline: auto;
          padding: 4.5rem 1.4rem 2.4rem;
        }
        /* 雷达同心环装饰：项目「雷达」意象的唯一签名元素，极低对比度 */
        .main .block-container::before, [data-testid="stMainBlockContainer"]::before{
          content: ""; position: absolute; right: -30px; top: -20px; z-index: 0;
          width: 460px; height: 460px; border-radius: 50%; pointer-events: none;
          background:
            radial-gradient(circle at center, transparent 139px, rgba(255,255,255,.05) 140px, rgba(255,255,255,.05) 141px, transparent 142px),
            radial-gradient(circle at center, transparent 179px, rgba(255,255,255,.038) 180px, rgba(255,255,255,.038) 181px, transparent 182px),
            radial-gradient(circle at center, transparent 219px, rgba(255,255,255,.028) 220px, rgba(255,255,255,.028) 221px, transparent 222px);
        }
        section[data-testid="stVerticalBlock"]{ gap: .45rem; }
        section[data-testid="stVerticalBlock"] > div{ z-index: 1; }
        a{ color: var(--hs-text); }
        .stMarkdown a, .stMarkdown a *{ text-decoration: none !important; }

        /* ===== 磨砂导航栏 ===== */
        .hs-nav{
          position: relative; z-index: 1;
          background: var(--hs-glass);
          margin: 12px 0 4px;
          padding: 0 20px;
          border: 1px solid var(--hs-hairline);
          border-radius: 18px;
          height: 56px; display: flex; align-items: center;
          box-shadow: 0 10px 36px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.06);
          backdrop-filter: blur(24px) saturate(1.8);
          -webkit-backdrop-filter: blur(24px) saturate(1.8);
        }
        .hs-nav-inner{ display: flex; align-items: center; gap: 20px; width: 100%; }
        .hs-logo{ display: flex; align-items: center; gap: 11px; }
        /* App 图标式徽标：红渐变圆角方块 + 白色雷达点环 */
        .hs-logo-mark{
          position: relative; width: 26px; height: 26px; border-radius: 7.5px; flex: none;
          background: linear-gradient(135deg, #ff7a6b, #ff453a 70%);
          box-shadow: 0 3px 10px rgba(255,69,58,.35), inset 0 1px 0 rgba(255,255,255,.28);
        }
        .hs-logo-mark::before{
          content: ""; position: absolute; inset: 0; margin: auto;
          width: 15px; height: 15px; border-radius: 50%;
          border: 1.5px solid rgba(255,255,255,.75);
        }
        .hs-logo-mark::after{
          content: ""; position: absolute; inset: 0; margin: auto;
          width: 6px; height: 6px; border-radius: 50%; background: #fff;
        }
        .hs-logo-word{ font-size: 15.5px; font-weight: 700; letter-spacing: .3px; color: var(--hs-text) !important; }
        .hs-logo-sub{
          position: relative; display: inline-flex; align-items: center; gap: 6px;
          font-size: 10px; font-weight: 800; letter-spacing: 1.8px;
          color: var(--hs-red-soft) !important;
          background: rgba(255,69,58,.14); padding: 4px 11px; border-radius: 99px;
        }
        .hs-logo-sub::before{
          content: ""; width: 5px; height: 5px; border-radius: 50%;
          background: var(--hs-red-soft); animation: hs-pulse 1.8s infinite;
        }
        .hs-nav .spacer{ margin-right: auto; }
        .hs-nav a{
          color: var(--hs-text-2) !important; text-decoration: none !important;
          font-size: 13px; font-weight: 500;
          padding: 7px 12px; border-radius: 9px;
          transition: color .15s, background .15s;
        }
        .hs-nav a:hover{ color: var(--hs-text) !important; background: var(--hs-fill); }

        /* ===== 跑马灯资讯条 ===== */
        .hs-ticker{
          position: relative; z-index: 1;
          background: var(--hs-glass);
          border: 1px solid var(--hs-hairline); border-radius: 13px;
          color: var(--hs-text-2);
          overflow: hidden; height: 38px; display: flex; align-items: center;
          margin: 4px 0 2px;
          backdrop-filter: blur(20px) saturate(1.6);
          -webkit-backdrop-filter: blur(20px) saturate(1.6);
        }
        .hs-ticker-track{
          display: inline-flex; white-space: nowrap; align-items: center;
          animation: hs-tick 45s linear infinite; will-change: transform;
        }
        .hs-ticker:hover .hs-ticker-track{ animation-play-state: paused; }
        .hs-ticker-track.static{ animation: none; }
        @keyframes hs-tick{ from{ transform: translateX(0); } to{ transform: translateX(-50%); } }
        .hs-ticker .ti{
          color: var(--hs-text-2) !important; font-size: 12.5px;
          padding: 0 18px; border-left: 1px solid rgba(255,255,255,.06);
        }
        .hs-ticker .ti:first-child{ border-left: none; }
        .hs-ticker .ti b{ color: #d5d5db !important; margin-right: 8px; font-weight: 600; }
        .hs-ticker .ti strong{ color: var(--hs-text) !important; font-weight: 500; }

        /* ===== 标题区 ===== */
        .hs-overline{
          display: flex; align-items: center; gap: 9px;
          font-size: 12.5px; font-weight: 600; letter-spacing: .4px;
          color: var(--hs-text-2) !important; margin: 20px 0 8px;
        }
        .hs-overline .dot, .hs-meta-line .dot{
          width: 7px; height: 7px; border-radius: 50%; flex: none;
        }
        .hs-overline .dot{
          background: var(--hs-red);
          box-shadow: 0 0 8px rgba(255,69,58,.8);
          animation: hs-pulse 1.8s infinite;
        }
        @keyframes hs-pulse{ 50%{ opacity: .35; } }
        .hs-h1{
          font-size: clamp(30px, 4vw, 40px); font-weight: 700; letter-spacing: -.4px;
          line-height: 1.1; color: var(--hs-text) !important; margin: 0;
        }
        .hs-tagline{ color: var(--hs-text-2) !important; font-size: 14.5px; margin: 8px 0 2px; }

        /* ===== 元信息行 ===== */
        .hs-meta-line{
          display: flex; flex-wrap: wrap; align-items: center; gap: 4px 14px;
          font-size: 12.5px; color: var(--hs-text-2) !important;
          padding: 4px 2px; font-variant-numeric: tabular-nums;
        }
        .hs-meta-line .dot{
          background: var(--hs-green);
          box-shadow: 0 0 7px rgba(48,209,88,.7);
          animation: hs-pulse 1.8s infinite;
        }
        .hs-meta-line b{ color: var(--hs-text) !important; font-weight: 600; }

        /* ===== 榜单分区标题 ===== */
        .hs-panel{ margin-top: 14px; }
        .hs-section{
          color: var(--hs-text); font-size: 20px; font-weight: 700; letter-spacing: -.2px;
          padding: 10px 0 14px; display: flex; align-items: baseline; gap: 12px;
        }
        .hs-section .sub{ color: var(--hs-text-3) !important; font-size: 12.5px; font-weight: 400; }

        /* ===== 行式榜单 ===== */
        .hs-thead, .hs-row{
          display: grid;
          grid-template-columns: 44px minmax(0,1fr) 150px;
          gap: 14px; align-items: center; padding: 8px;
        }
        .hs-thead{
          color: var(--hs-text-3) !important; font-size: 12px; font-weight: 500;
          border-bottom: 1px solid var(--hs-hairline); padding-bottom: 10px; margin-bottom: 6px;
        }
        .hs-thead .r{ text-align: right; }
        .hs-row{
          position: relative;
          border-radius: 14px; text-decoration: none !important;
          background: rgba(255,255,255,.035);
          border: 1px solid transparent;
          margin-bottom: 7px;
          transition: background .15s, border-color .15s, transform .15s;
        }
        .hs-row[href]{ cursor: pointer; }
        .hs-row:hover{
          background: rgba(255,255,255,.065);
          border-color: var(--hs-hairline);
          transform: translateY(-1px);
        }
        .hs-row .rank{
          font-size: 15px; font-weight: 700; text-align: center;
          color: var(--hs-text-3) !important;
          font-variant-numeric: tabular-nums;
          transition: color .15s;
        }
        .hs-row .rank.r1{ color: var(--hs-red-soft) !important; }
        .hs-row .rank.r2{ color: var(--hs-orange) !important; }
        .hs-row .rank.r3{ color: var(--hs-yellow) !important; }
        .hs-row .rank.r1, .hs-row .rank.r2, .hs-row .rank.r3{ font-size: 16.5px; }
        .hs-row .hword{
          color: #ececf0 !important; font-size: 15px; font-weight: 600; line-height: 1.4;
          transition: color .15s;
        }
        .hs-row:hover .hword{ color: #fff !important; }
        .hs-row .hdesc{
          color: var(--hs-text-2) !important; font-size: 12.5px; line-height: 1.55; margin-top: 3px;
          display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden;
        }
        .hs-row .pill-row{
          display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
          margin-top: 6px;
        }
        .hs-row .pill-row:empty{ display: none; }
        .hs-row .hmeta{ display: flex; flex-direction: column; align-items: flex-end; gap: 3px; text-align: right; }
        .hs-row .hmeta .onboard{
          font-size: 12px; color: var(--hs-text-3) !important;
          font-variant-numeric: tabular-nums; white-space: nowrap;
        }
        .hs-row .hmeta .hit b{
          display: block; font-size: 16px; font-weight: 700; color: var(--hs-text) !important;
          font-variant-numeric: tabular-nums; line-height: 1.2;
        }
        .hs-row .hmeta .hit i{
          display: block; font-style: normal; font-size: 11px;
          color: var(--hs-text-3) !important; margin-top: 2px;
        }
        .hs-row .tag-new{
          display: inline-block; font-size: 11px; font-weight: 600;
          padding: 3.5px 10px; border-radius: 7px;
          background: rgba(255,69,58,.14);
          color: var(--hs-red-soft) !important; white-space: nowrap;
        }

        /* ===== 源徽章（无边框着色胶囊） ===== */
        .src-badge{
          display: inline-flex; align-items: center; gap: 6px;
          padding: 3px 10px; border-radius: 99px;
          font-size: 11.5px; font-weight: 600; line-height: 1.5; white-space: nowrap;
          color: var(--c, var(--hs-text-2)) !important;
          background: color-mix(in srgb, var(--c, #a1a1aa) 15%, transparent);
        }
        .src-badge i{
          width: 5px; height: 5px; border-radius: 50%; flex: none;
          background: var(--c, var(--hs-text-2));
        }
        .tag-badge{
          display: inline-flex; align-items: center; gap: 4px;
          padding: 3px 10px; border-radius: 99px;
          font-size: 11.5px; font-weight: 500; line-height: 1.5;
          background: var(--hs-fill);
          color: var(--hs-text-2) !important;
        }

        /* ===== 空状态 ===== */
        .hs-empty{ padding: 52px 0 44px; text-align: center; }
        .hs-empty .etitle{ color: #d5d5db; font-weight: 600; font-size: 15px; margin-bottom: 6px; }
        .hs-empty .esub{ font-size: 12.5px; color: var(--hs-text-3) !important; }

        /* ===== 侧边栏 ===== */
        [data-testid="stSidebar"]{
          background: linear-gradient(180deg, #131317, #0e0e11);
          border-right: 1px solid rgba(255,255,255,.06);
        }
        [data-testid="stSidebar"] *{ color: #c9c9ce; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
          color: var(--hs-text) !important; font-weight: 700; letter-spacing: -.2px;
        }
        [data-testid="stSidebar"] hr{ border-color: rgba(255,255,255,.07); }
        [data-testid="stSidebar"] [data-testid="stExpander"]{
          background: rgba(255,255,255,.03);
          border: 1px solid var(--hs-hairline) !important;
          border-radius: 12px;
        }
        input[type="checkbox"]{ accent-color: var(--hs-red); }

        /* ===== 输入控件 ===== */
        input[type="text"], input[type="password"], input[type="number"], textarea{
          background: rgba(255,255,255,.06) !important;
          color: var(--hs-text) !important;
          border: 1px solid var(--hs-hairline) !important;
          border-radius: 10px !important;
          font-size: 13px;
        }
        input:focus, textarea:focus{
          border-color: rgba(10,132,255,.6) !important;
          box-shadow: 0 0 0 3.5px rgba(10,132,255,.18) !important;
        }
        input::placeholder, textarea::placeholder{ color: var(--hs-text-3) !important; }

        /* ===== 按钮 ===== */
        .stButton > button{
          border-radius: 10px !important;
          padding: 9px 18px;
          background: rgba(255,255,255,.07) !important;
          border: 1px solid var(--hs-hairline-hi) !important;
          color: #f0f0f4 !important;
          font-size: 13px; font-weight: 600;
          transition: background .15s, border-color .15s, filter .15s;
        }
        .stButton > button p{ font-size: 13px; font-weight: 600; color: #f0f0f4 !important; }
        .stButton > button:not([kind="primary"]):hover{
          background: rgba(255,255,255,.12) !important;
          border-color: rgba(255,255,255,.2) !important;
        }
        button[kind="primary"]{
          background: var(--hs-red) !important;
          border: none !important;
          box-shadow: 0 4px 16px rgba(255,69,58,.28);
        }
        button[kind="primary"] p{ color: #fff !important; font-weight: 600 !important; }
        button[kind="primary"]:hover{ filter: brightness(1.07); box-shadow: 0 6px 20px rgba(255,69,58,.36); }
        button[kind="primary"]:active{ transform: scale(0.98); }

        /* ===== iOS 风分段切换控件（stRadio react-aria DOM） ===== */
        [data-testid="stRadioGroup"]{
          display: inline-flex; flex-wrap: wrap; gap: 2px;
          background: rgba(118,118,128,.22);
          border-radius: 11px; padding: 3px;
        }
        [data-testid="stRadioOption"]{
          border-radius: 8.5px; padding: 7px 16px !important; margin: 0 !important;
          background: transparent !important; border: none !important;
          transition: background .15s; cursor: pointer;
        }
        [data-testid="stRadioOption"]:hover{ background: rgba(255,255,255,.06) !important; }
        [data-testid="stRadioOption"] p{ font-size: 13px; font-weight: 500; color: var(--hs-text-2) !important; }
        [data-testid="stRadioOption"][data-selected="true"]{
          background: rgba(128,130,138,.62) !important;
          box-shadow: 0 2px 8px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.12);
        }
        [data-testid="stRadioOption"][data-selected="true"] p{ color: #fff !important; font-weight: 600; }
        [data-testid="stRadioOption"] > div > div > div:first-child{ display: none; }

        /* ===== 滑块 ===== */
        .stSlider{ color: var(--hs-text-3); }
        .stSlider [data-baseweb="slider"] > div{ background-color: rgba(255,255,255,.14) !important; }

        /* ===== 提示条 ===== */
        [data-testid="stAlert"]{
          background: rgba(30,30,34,.72) !important;
          border: 1px solid var(--hs-hairline) !important;
          border-radius: 12px !important;
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
        }
        [data-testid="stAlert"] p{ color: #d5d5db !important; font-size: 13px; }
        [data-testid="stCaptionContainer"], .stCaption{ color: var(--hs-text-3) !important; }
        hr{ border-color: rgba(255,255,255,.07); }

        /* ===== 页脚 ===== */
        .hs-footer{
          color: var(--hs-text-3) !important; font-size: 12.5px; line-height: 1.8;
          border-top: 1px solid var(--hs-hairline); padding-top: 14px; margin-top: 24px;
        }
        .hs-footer a{ color: var(--hs-text-2) !important; }
        .hs-footer a:hover{ color: var(--hs-red-soft) !important; }

        ::selection{ background: rgba(255,69,58,.32); color: #fff; }
        ::-webkit-scrollbar{ width: 9px; height: 9px; }
        ::-webkit-scrollbar-thumb{
          background: rgba(255,255,255,.14);
          border-radius: 99px;
          border: 2px solid transparent;
          background-clip: content-box;
        }
        ::-webkit-scrollbar-thumb:hover{
          background: rgba(255,255,255,.22);
          background-clip: content-box;
        }
        ::-webkit-scrollbar-track{ background: transparent; }

        /* ===== 响应式 ===== */
        @media (max-width: 860px){
          .hs-nav{ padding: 0 14px; }
          .hs-nav a{ display: none; }
          .hs-h1{ font-size: 26px; }
          .hs-section{ font-size: 17px; }
          .hs-row, .hs-thead{ grid-template-columns: 34px minmax(0,1fr) auto; gap: 11px; }
          .hs-thead{ display: none; }
          .hs-row .hmeta .onboard{ display: none; }
          .hs-ticker{ height: 34px; }
          .hs-ticker .ti{ font-size: 11.5px; padding: 0 13px; }
          .hs-footer{ font-size: 11.5px; }
          .main .block-container::before, [data-testid="stMainBlockContainer"]::before{ display: none; }
        }
        @media (max-width: 480px){
          .block-container{ padding: 4.2rem .9rem 1.6rem; }
          .hs-row{ grid-template-columns: 30px minmax(0,1fr) auto; gap: 10px; padding: 7px 4px; }
          .hs-row .hword{
            font-size: 14px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
          }
          .hs-row .hdesc{ font-size: 11.5px; }
          .hs-meta-line{ font-size: 11.5px; }
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
