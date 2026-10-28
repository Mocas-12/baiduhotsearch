# -*- coding: utf-8 -*-
"""HotRadar 新闻索引主题与现有 Streamlit 菜单汉化脚本。"""
from pathlib import Path

import streamlit as st


def apply_theme():
    st.markdown(
        "<style>\n" + Path(__file__).with_name("theme.css").read_text(encoding="utf-8")
        + "\n</style>\n" + """
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


