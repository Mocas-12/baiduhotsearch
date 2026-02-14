# 作者：Unlimited Box
# 邮箱：a18577y@gmail.com

# 中国热搜（百度）—— 使用说明

本应用是一个基于 Streamlit 的轻量网页前端，实时展示百度热搜榜数据，支持榜单切换（总榜、小说、电影、电视剧）、一键获取最新数据、侧边栏网络设置与示例数据回退等功能。

## 功能特性

- 实时热搜榜：拉取 top.baidu.com 实时榜单并展示
- 榜单切换：总榜 / 小说 / 电影 / 电视剧
- 获取最新数据：一键刷新当前榜单
- 首屏秒开：优先使用缓存或示例数据，避免空白等待
- 侧边栏设置：代理、忽略 SSL 校验、连接测试、一键诊断/连接、示例数据切换
- UI 风格：红橙渐变主题、侧栏折叠、表格样式优化与中文化菜单

## 环境要求

- Python 3.9+（推荐 3.10/3.11）

## 安装与运行

1. 克隆项目

   ```bash
   git clone <your-repo-url>
   cd googletrend
   ```

2. 安装依赖

   ```bash
   pip install -U streamlit pandas requests
   ```

3. 启动应用

   ```bash
   streamlit run app.py
   ```

   终端会显示访问地址（例如 http://localhost:8501 ），浏览器打开即可查看。

## 使用指南

- 页面顶部显示当前榜单数据。右侧提供“获取最新数据”按钮，点击立即刷新。
- 通过页面右上方的榜单切换（总榜 / 小说 / 电影 / 电视剧）查看不同榜单。
- 左侧栏（默认折叠，可点击展开）提供：
  - 启用代理、填写代理地址（支持 http/https/socks5h）
  - 忽略 SSL 证书验证（某些拦截代理需要）
  - 测试连接 / 一键诊断 / 一键连接（尝试自动选择可用代理）
  - 使用示例数据（网络不可用时也能查看界面效果）

## 常见问题

- 首次打开有时需要网络拉取最新数据。为保证首屏观感，应用会优先显示缓存或示例数据；点击“获取最新数据”即可刷新为实时数据。
- 如果连接失败：
  - 检查本机网络；如需代理，在侧栏启用并填写代理地址（如 `http://127.0.0.1:7890`）。
  - 可尝试勾选“忽略 SSL 证书验证”。
  - 使用“一键诊断/一键连接”快速定位并选择可用连接方式。

## 发布到线上

> 说明：GitHub Pages 只支持静态站点，无法直接运行 Python/Streamlit。建议采用“应用部署 + Pages 展示”的方式。

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

## 自定义与二开

- 配色与样式：`app.py` 中的 `apply_theme()` 注入了 CSS/JS，可按需修改颜色、阴影、圆角等。
- 列展示：默认显示“排名/词条/简介/热度/链接”，可在 `render_hot_trends()` 中调整 `display_cols`。
- 榜单类型：通过 `fetch_baidu_board(tab)` 拉取。当前支持映射为“总榜、小说、电影、电视剧”，可在 `board_map` 增加更多候选。

## 许可证

- 个人/内部使用自由。若公开部署，请遵循数据源站点的使用规范与爬取边界，避免高频请求。

