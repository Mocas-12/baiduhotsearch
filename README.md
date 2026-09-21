<div align="center">

<img src="./logo.svg" width="96" alt="Hot Search Radar Logo" />

# 🔥 Hot Search Radar (全网热搜雷达)

**Domestic buzz · World news · Tech trends — 12 live sources aggregated on one page**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Live](https://img.shields.io/badge/Streamlit_Cloud-Live-FF4B4B?logo=streamlit&logoColor=white)](https://baiduhotsearch-d9ysnhxbkzeskrnd5apnn5.streamlit.app/)

**[🌐 Live Dashboard (Streamlit Cloud)](https://baiduhotsearch-d9ysnhxbkzeskrnd5apnn5.streamlit.app/)**

[简体中文](./README.zh-CN.md) | **English**

*Formerly "Baidu Hot Search" — a single-board dashboard, now a multi-source trending radar*

</div>

---

## 📸 Screenshots

| 🌐 Cross-source board — same-event clustering | 🇨🇳 Domestic mixed stream — interleaved by rank |
|:---:|:---:|
| ![Cross-source board](./docs/screenshots/cross-board.png) | ![Domestic mixed stream](./docs/screenshots/domestic-mixed.png) |

---

## 📖 Table of Contents

- [Why](#-why)
- [Features](#-features)
- [Data Sources](#-data-sources)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [FAQ](#-faq)
- [License](#-license)

## 🎯 Why

One board shows you one platform's view — and Baidu's skews entertainment. This project aggregates **domestic life trends** (Weibo / Zhihu / Douyin / Toutiao / Baidu / Bilibili), **world news in Chinese** (Google News / NYT Chinese / 60s Daily) and **tech circles** (Hacker News / GitHub Trending / V2EX) onto a single page, then algorithmically clusters topics that **multiple sources are reporting at the same time** — when several independent boards hit the same story, that's the news that actually matters.

## ✨ Features

- 🌐 **Cross-source board (flagship)**: title-similarity clustering merges entries about the same event from ≥2 sources, ranked by hit count and heat — tell "platform noise" from "global news" at a glance
- 🗂️ **Three category views**: 🇨🇳 Domestic / 🌍 World / 💻 Tech — single source, or a "mixed stream" that interleaves all sources by rank
- 🆕 **New / time-on-board badges**: SQLite snapshots mark first-seen topics and how long an entry has been trending
- 🛡️ **Three-tier fallback, never blank**: live data → 15-min cached snapshot (with age notice) → sample data
- 🩺 **Source diagnostics panel**: probes all 12 sources in parallel, reporting availability, item count and latency
- ⚖️ **Rate-limit friendly**: per-source caching, short-lived failure caching, staggered requests and 429 backoff
- 🎨 **Dark "ember" theme**: glassy cards, fire-gradient accents, TOP-3 medals, heat bars, LIVE pulse, brand-colored source badges

## 📡 Data Sources

| Category | Sources | Access |
|---|---|---|
| 🇨🇳 Domestic | Weibo / Zhihu / Douyin / Toutiao / Bilibili | [60s API](https://github.com/vikiboss/60s) aggregator (official + community failover) |
| 🇨🇳 Domestic | Baidu | Direct top.baidu.com (proxy supported) |
| 🌍 World | Google News 中文 / NYT Chinese | RSS (stdlib parser, zero deps) |
| 🌍 World | 60s Daily | 60s API |
| 💻 Tech | Hacker News | Official Algolia API |
| 💻 Tech | GitHub Trending | Page parsing |
| 💻 Tech | V2EX | Official open API |

## 🧠 How It Works

```mermaid
flowchart LR
    A[12 sources<br/>60s API · RSS · open APIs] --> B[Parallel fetch sources.py<br/>unified schema]
    B --> C[Per-source cache 15min<br/>fallback snapshot/sample]
    B --> D[SQLite snapshots store.py<br/>new badges · time-on-board]
    B --> E[Title clustering aggregate.py<br/>cross-source board]
    C --> F[Streamlit rendering<br/>category views · mixed stream · badges]
    D --> F
    E --> F
```

## 📁 Project Structure

```
├── app.py          # Page shell: view nav, cache orchestration, fallbacks, cards
├── sources.py      # Source registry & fetchers (unified schema, streamlit-free)
├── aggregate.py    # Cross-source board: title normalization + similarity clustering
├── store.py        # SQLite history snapshots (new / time-on-board)
├── styles.py       # Theme CSS & component styles
└── logo.svg
```

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ⚙️ Configuration

Everything lives in the sidebar — no code changes needed:

- **60s API instance**: built-in official + community instances with automatic failover; public instances are rate-limited, so you can point to your [self-hosted instance](https://github.com/vikiboss/60s) (Docker / Node, one-click to Vercel / Zeabur)
- **Proxy**: the Baidu source connects directly to top.baidu.com and usually needs an HTTPS proxy outside mainland China; "Test connection / auto-pick proxy" included
- **Sample data**: preview the full UI with no network

## ❓ FAQ

**A source shows "temporarily unavailable"?**
Usually public-instance rate limiting or an upstream hiccup — it auto-retries within 5 minutes. Check the diagnostics panel, or switch to a self-hosted 60s API instance.

**Is history (new badges) kept forever?**
Streamlit Cloud wipes the filesystem on redeploy, so history only accumulates within one instance's lifetime. Self-host with a persistent volume to keep it long-term (7 days retained by default).

**Why can't heat numbers be compared across sources?**
Every platform scores heat differently; bars are relative within the current view. The cross-source board ranks by hit count first.

## 👤 Author

**Unlimited Box** · [a18577y@gmail.com](mailto:a18577y@gmail.com)

All data comes from public boards of each platform, for personal learning and information browsing only.

## 📄 License

MIT
