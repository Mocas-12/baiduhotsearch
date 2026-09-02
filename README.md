# China Hot Search (Baidu) — User Guide

**English** | [简体中文](./README.zh-CN.md)

This app is a lightweight Streamlit web frontend that displays Baidu hot-search rankings in real time, with board switching (Overall, Novels, Movies, TV Series), one-click refresh of the latest data, sidebar network settings, and sample-data fallback.

## Features

- Real-time hot search: pulls the live ranking from top.baidu.com and displays it
- Board switching: Overall / Novels / Movies / TV Series
- Fetch latest data: one-click refresh of the current board
- Instant first paint: cached or sample data is shown first to avoid a blank wait
- Sidebar settings: proxy, ignore SSL verification, connection test, one-click diagnose/connect, sample-data toggle
- UI style: red-orange gradient theme, collapsible sidebar, polished table styles and localized menus

## Requirements

- Python 3.9+ (3.10/3.11 recommended)

## Installation & Running

1. Clone the project

   ```bash
   git clone <your-repo-url>
   cd googletrend
   ```

2. Install dependencies

   ```bash
   pip install -U streamlit pandas requests
   ```

3. Start the app

   ```bash
   streamlit run app.py
   ```

   The terminal prints the visit URL (e.g. http://localhost:8501); open it in a browser.

## Usage Guide

- The top of the page shows the current board. The "Fetch Latest Data" (获取最新数据) button on the right refreshes it immediately.
- Use the board switcher at the top right (Overall / Novels / Movies / TV Series) to view different boards.
- The left sidebar (collapsed by default, click to expand) provides:
  - Enable proxy and fill in a proxy address (http/https/socks5h supported)
  - Ignore SSL certificate verification (needed by some intercepting proxies)
  - Test connection / one-click diagnose / one-click connect (tries to auto-pick a working proxy)
  - Use sample data (view the UI even when the network is unavailable)

## FAQ

- The first open sometimes needs the network to fetch fresh data. To keep the first screen fast, the app prefers cached or sample data; click "Fetch Latest Data" to switch to real-time data.
- If the connection fails:
  - Check your network; if a proxy is needed, enable it in the sidebar and fill in the address (e.g. `http://127.0.0.1:7890`).
  - Try checking "Ignore SSL certificate verification".
  - Use "one-click diagnose / one-click connect" to quickly locate a working connection mode.

## Publishing Online

> Note: GitHub Pages only serves static sites and cannot run Python/Streamlit. The recommended approach is "app deployment + Pages presentation".

### Option A: Streamlit Community Cloud (recommended, free)

1. Push this repository to GitHub.
2. Open https://share.streamlit.io/ , connect your GitHub repo, and pick `app.py` as the entry point.
3. After deployment you get a public URL (shaped like `https://<your-app>.streamlit.app`).
4. On GitHub Pages, use a static page to redirect to or embed that URL:
   - Redirect page (recommended, best compatibility): create `docs/index.html` in the repo with the following content, replacing `EXTERNAL_URL` with your online address.

     ```html
     <!doctype html>
     <meta charset="utf-8">
     <meta http-equiv="refresh" content="0; url=EXTERNAL_URL">
     <title>跳转中...</title>
     <a href="EXTERNAL_URL">如果未自动跳转，请点击这里访问应用</a>
     ```

   - Or try an iframe (some hosts may block embedding):

     ```html
     <!doctype html>
     <meta charset="utf-8">
     <style>html,body,iframe{height:100%;width:100%;margin:0;border:0;}</style>
     <iframe src="EXTERNAL_URL"></iframe>
     ```

5. In the GitHub repo settings → Pages, set Source to `Deploy from a branch` and pick the `/docs` directory of the `main` branch.

### Option B: Self-hosted or third-party platforms (Railway/Render/Fly.io/Docker etc.)

1. Deploy on a server or platform:

   ```bash
   pip install -U streamlit pandas requests
   streamlit run app.py --server.address 0.0.0.0 --server.port 80
   ```

   Or with Docker (add your own Dockerfile if desired):

   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install -U streamlit pandas requests
   EXPOSE 8501
   CMD ["streamlit","run","app.py","--server.address","0.0.0.0","--server.port","8501"]
   ```

2. Once you have a publicly accessible URL, configure the GitHub Pages redirect/embed as described above.

## Customization

- Colors & styles: `apply_theme()` in `app.py` injects CSS/JS; modify colors, shadows, radii, etc. as needed.
- Displayed columns: defaults to 排名/词条/简介/热度/链接 (rank / title / summary / heat / link); adjust `display_cols` in `render_hot_trends()`.
- Board types: fetched via `fetch_baidu_board(tab)`. Currently mapped to Overall / Novels / Movies / TV Series; add more candidates in `board_map`.

## License

- Free for personal/internal use. For public deployments, follow the data source site's usage rules and scraping limits; avoid high-frequency requests.
