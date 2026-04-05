# OpenClaw-friendly Skills

這個 repo 是一個**已整理、已納管的 OpenClaw skill 與相關專案倉庫**。

目前內容分成兩大區塊：

1. **正式納管的 OpenClaw skills**
2. **延伸研究 / 工具型專案**（例如 OpenCLI ChatGPT Web plugin prototype）

## 最新新增專案

### `projects/opencli-chatgpt-web-cli/`

這是一個新的 **OpenCLI-compatible ChatGPT Web plugin prototype**，目標是在 Ubuntu / Linux 上，透過：

- Google Chrome
- OpenCLI daemon + browser extension bridge
- OpenCLI `Page` abstraction

來操作 **ChatGPT Web**，而不是依賴原本偏向 macOS Desktop App automation 的內建 `chatgpt` adapter。

目前已驗證：

- `opencli chatgpt-web status` ✅
- `opencli chatgpt-web open` ✅
- `opencli chatgpt-web new` ✅
- `opencli chatgpt-web debug` ✅
- `opencli chatgpt-web ask "..."` ✅
- `opencli chatgpt-web read` ⚠️（仍待補強）

專案內已包含：

- installable-style plugin layout
- teaching-oriented technical documents
- final PDF / DOCX
- draw.io diagrams
- figure generation script

請直接查看：
- `projects/opencli-chatgpt-web-cli/README.md`

---

## 正式納管的 skills

- `skills/control-gui-setting/`
  - 修復 Linux 桌面環境下 OpenClaw managed browser 無法正常開啟 / 控制的問題
- `skills/desktop-control-wayland/`
  - 診斷 GNOME Wayland 桌面直接控制能力，例如 `ydotool`、portal、截圖權限
- `skills/chatgpt-image-download/`
  - 當 ChatGPT 已生成圖片，但一般 Download / Save 無法正常落地時，透過登入中的瀏覽器 session 可靠抓圖

### 根目錄打包檔

- `control-gui-setting.skill`
- `desktop-control-wayland.skill`
- `chatgpt-image-download.skill`

### 技能邊界

#### `control-gui-setting`
處理：browser 啟動失敗、GUI session 環境傳遞、OpenClaw managed browser 啟動與 tool exposure 判斷。

#### `desktop-control-wayland`
處理：Wayland 桌面控制能力檢查、`ydotoold` / `ydotool` 注入鏈、portal / screenshot / remote desktop capability。

#### `chatgpt-image-download`
處理：ChatGPT 圖片另存失敗、直接抓圖 403、透過登入中的瀏覽器 session 可靠下載圖片。

### 未納管內容

工作區裡可能還存在一些**本地用途**內容，例如：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `memory/`
- `.openclaw/`
- `skills/clawteam/`
- 個人腳本、虛擬環境、簡報檔

這些內容不是這個 repo 的正式技能發布範圍，因此已透過 `.gitignore` 排除。

### 結構

```text
skills/
  chatgpt-image-download/
  control-gui-setting/
  desktop-control-wayland/

projects/
  opencli-chatgpt-web-cli/
```

### 維護原則

- 名稱清楚
- 邊界單一
- SKILL.md 保持精簡
- 細節放到 `references/`
- 打包檔與來源內容同步更新
- 個人工作區資料不要直接混進 repo

---

This repository is a **curated and version-controlled OpenClaw skill and related project collection**.

It now has two major sections:

1. **Officially managed OpenClaw skills**
2. **Related project work / research prototypes** (such as the OpenCLI ChatGPT Web plugin prototype)

## Newly added project

### `projects/opencli-chatgpt-web-cli/`

This is a new **OpenCLI-compatible ChatGPT Web plugin prototype** for Ubuntu / Linux.

Its purpose is to control **ChatGPT Web** through:

- Google Chrome
- OpenCLI daemon + browser extension bridge
- OpenCLI `Page` abstraction

instead of relying on the built-in `chatgpt` adapter's macOS Desktop App automation path.

Current validated status:

- `opencli chatgpt-web status` ✅
- `opencli chatgpt-web open` ✅
- `opencli chatgpt-web new` ✅
- `opencli chatgpt-web debug` ✅
- `opencli chatgpt-web ask "..."` ✅
- `opencli chatgpt-web read` ⚠️ (still needs further hardening)

The project includes:

- an installable-style plugin layout
- teaching-oriented technical documentation
- final PDF / DOCX documents
- draw.io diagrams
- a figure generation script

See:
- `projects/opencli-chatgpt-web-cli/README.md`

---

## Officially managed skills

- `skills/control-gui-setting/`
  - Repair OpenClaw managed browser launch/control issues on Linux desktop environments
- `skills/desktop-control-wayland/`
  - Diagnose GNOME Wayland desktop control capability such as `ydotool`, portals, and screenshot permissions
- `skills/chatgpt-image-download/`
  - Reliably download ChatGPT-generated images through the logged-in browser session when normal Download / Save does not create a file

### Packaged skill bundles at repo root

- `control-gui-setting.skill`
- `desktop-control-wayland.skill`
- `chatgpt-image-download.skill`

### Structure

```text
skills/
  chatgpt-image-download/
  control-gui-setting/
  desktop-control-wayland/

projects/
  opencli-chatgpt-web-cli/
```

### Maintenance principles

- Use clear names
- Keep a single responsibility boundary per skill/project
- Keep SKILL.md concise
- Move details into `references/`
- Keep packaged bundles in sync with source content
- Do not mix personal workspace data into the repository
