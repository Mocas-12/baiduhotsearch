<div align="center">

<img src="./logo.svg" width="96" alt="Baidu Hot Search Logo" />

# 🔥 中国热搜（百度）

**实时百度热搜榜 Streamlit 看板 —— 总榜 · 小说 · 电影 · 电视剧，一键刷新**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Live](https://img.shields.io/badge/Streamlit_Cloud-Live-FF4B4B?logo=streamlit&logoColor=white)](https://baiduhotsearch-d9ysnhxbkzeskrnd5apnn5.streamlit.app/)

**[🌐 在线看板（Streamlit Cloud）](https://baiduhotsearch-d9ysnhxbkzeskrnd5apnn5.streamlit.app/)**

[English](./README.md) | **简体中文**

*打开页面 → 查看实时热搜 → 切换榜单 → 一键刷新*

</div>

---

## 📖 目录

- [功能特性](#-功能特性)
- [工作原理](#-工作原理)
- [使用指南](#-使用指南)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [发布到线上](#-发布到线上)
- [自定义与二开](#-自定义与二开)
- [常见问题](#-常见问题)
- [许可证](#-许可证)

## ✨ 功能特性

- 🔥 **实时热搜榜**：拉取 top.baidu.com 实时榜单并展示
- 🗂️ **榜单切换**：总榜 / 小说 / 电影 / 电视剧
- 🔄 **获取最新数据**：一键刷新当前榜单
- ⚡ **首屏秒开**：优先使用缓存或示例数据，避免空白等待
- 🧰 **侧边栏设置**：代理、忽略 SSL 校验、连接测试、一键诊断/连接、示例数据切换
- 🎨 **UI 风格**：红橙渐变主题、侧栏折叠、表格样式优化与中文化菜单

## 🧠 工作原理

```mermaid
flowchart LR
    A[🌐 top.baidu.com<br/>实时榜单] --> B[📥 抓取与解析<br/>requests · pandas]
    B --> C[💾 缓存 / 示例数据回退<br/>首屏秒开]
    C --> D[📊 Streamlit 渲染<br/>榜单切换 · 一键刷新]
    D --> E[⚙️ 侧边栏网络设置<br/>代理 · SSL · 诊断]
```

1. **抓取**：通过 `fetch_baidu_board(tab)` 拉取 top.baidu.com 对应榜单并解析为表格数据
2. **回退**：优先使用缓存或示例数据渲染，保证首屏秒开；网络可用时点击「获取最新数据」刷新为实时数据
3. **网络设置**：侧边栏支持启用代理（http/https/socks5h）、忽略 SSL 证书验证、测试连接与一键诊断/连接
4. **展示**：Streamlit 渲染榜单表格，支持总榜 / 小说 / 电影 / 电视剧切换与中文化菜单

## 📖 使用指南

- 页面顶部显示当前榜单数据。右侧提供「获取最新数据」按钮，点击立即刷新。
- 通过页面右上方的榜单切换（总榜 / 小说 / 电影 / 电视剧）查看不同榜单。
- 左侧栏（默认折叠，可点击展开）提供：
  - 启用代理、填写代理地址（支持 http/https/socks5h）
  - 忽略 SSL 证书验证（某些拦截代理需要）
  - 测试连接 / 一键诊断 / 一键连接（尝试自动选择可用代理）
  - 使用示例数据（网络不可用时也能查看界面效果）

## 📁 项目结构

```text
baiduhotsearch/
├── app.py               # Streamlit 主应用：榜单抓取 / 渲染 / 侧边栏设置 / 主题注入
├── logo.svg             # 项目 Logo
├── docs/
│   └── index.html       # GitHub Pages 跳转页（重定向到 Streamlit Cloud）
└── .streamlit/          # Streamlit 本地配置
```

## 🚀 快速开始

```bash
git clone https://github.com/Mocas-12/baiduhotsearch.git
cd baiduhotsearch
pip install -U streamlit pandas requests
streamlit run app.py
```

> 终端会显示访问地址（例如 http://localhost:8501 ），浏览器打开即可查看。环境要求：Python 3.9+（推荐 3.10/3.11）。

| 命令 | 说明 |
| --- | --- |
| `pip install -U streamlit pandas requests` | 安装依赖 |
| `streamlit run app.py` | 启动应用 |

## 🌐 发布到线上

> 说明：GitHub Pages 只支持静态站点，无法直接运行 Python/Streamlit。建议采用「应用部署 + Pages 展示」的方式。

### 方案 A：Streamlit Community Cloud（推荐，免费）

1. 将本仓库推送到 GitHub。
2. 打开 https://share.streamlit.io/ ，连接你的 GitHub 仓库，选择 `app.py` 作为入口。
3. 部署完成后，会获得一个公开 URL（形如 `https://<your-app>.streamlit.app`）。
4. 在 GitHub Pages 用一个静态页面跳转或内嵌该 URL：
   - 跳转页（推荐，兼容性好）：在仓库新建 `docs/index.html` 内容如下，将 `EXTERNAL_URL` 替换为你的线上地址。

     ```html
     <!doctype html>
     <meta charset="utf-8">
     <meta http-equiv="refresh" content="0; url=EXTERNAL_URL">
     <title>跳转中...</title>
     <a href="EXTERNAL_URL">如果未自动跳转，请点击这里访问应用</a>
     ```

   - 或者尝试 iframe（某些宿主可能限制内嵌）：

     ```html
     <!doctype html>
     <meta charset="utf-8">
     <style>html,body,iframe{height:100%;width:100%;margin:0;border:0;}</style>
     <iframe src="EXTERNAL_URL"></iframe>
     ```

5. 在 GitHub 仓库设置 → Pages 中，将 Source 设置为 `Deploy from a branch`，选择 `main` 分支的 `/docs` 目录。

### 方案 B：自建或第三方平台部署（Railway/Render/Fly.io/Docker 等）

1. 服务器或平台部署：

   ```bash
   pip install -U streamlit pandas requests
   streamlit run app.py --server.address 0.0.0.0 --server.port 80
   ```

   或使用 Docker（可自行添加 Dockerfile）：

   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install -U streamlit pandas requests
   EXPOSE 8501
   CMD ["streamlit","run","app.py","--server.address","0.0.0.0","--server.port","8501"]
   ```

2. 获取公网可访问的 URL 后，按上面 GitHub Pages 的跳转/嵌入方式进行配置。

## 🛠️ 自定义与二开

- 配色与样式：`app.py` 中的 `apply_theme()` 注入了 CSS/JS，可按需修改颜色、阴影、圆角等。
- 列展示：默认显示「排名/词条/简介/热度/链接」，可在 `render_hot_trends()` 中调整 `display_cols`。
- 榜单类型：通过 `fetch_baidu_board(tab)` 拉取。当前支持映射为「总榜、小说、电影、电视剧」，可在 `board_map` 增加更多候选。

## ❓ 常见问题

<details>
<summary><b>首次打开显示的是实时数据吗？</b></summary>

- 为保证首屏观感，应用会优先显示缓存或示例数据；点击「获取最新数据」即可刷新为实时数据
</details>

<details>
<summary><b>连接失败怎么办？</b></summary>

- 检查本机网络；如需代理，在侧栏启用并填写代理地址（如 `http://127.0.0.1:7890`）
- 可尝试勾选「忽略 SSL 证书验证」
- 使用「一键诊断/一键连接」快速定位并选择可用连接方式
</details>

## 📄 许可证

- 个人/内部使用自由。若公开部署，请遵循数据源站点的使用规范与爬取边界，避免高频请求。

---

<div align="center">

**Made with 💙**

🌐 [在线看板](https://baiduhotsearch-d9ysnhxbkzeskrnd5apnn5.streamlit.app/) · 🐛 [问题反馈](https://github.com/Mocas-12/baiduhotsearch/issues)

</div>
