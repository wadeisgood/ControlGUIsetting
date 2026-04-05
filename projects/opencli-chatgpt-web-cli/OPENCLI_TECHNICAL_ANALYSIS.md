# OpenCLI 程式解析與 ChatGPT Web Adapter 技術說明

## 摘要

本文針對目前 Ubuntu / Linux 環境中的 OpenCLI 安裝、執行模型、瀏覽器橋接能力，以及 `chatgpt-web` adapter 的設計與實作方式，進行較為專業的技術解析。本文的重點不只是操作說明，而是從程式結構、執行路徑、模組責任、除錯過程與風險面向，說明 OpenCLI 如何在本機 Chrome 瀏覽器既有登入狀態下，逐步延伸出可用的 ChatGPT Web CLI。

---

## 1. 問題背景

OpenCLI 的定位是把網站、Electron 應用程式與既有 CLI 工具轉換成一致的命令列介面，供人類或 AI Agent 使用。其核心理念是：

1. 透過瀏覽器 session 重用既有登入狀態
2. 透過 browser bridge 與本機 daemon 建立頁面控制能力
3. 以統一 CLI 介面包裝網站操作流程
4. 讓 AI Agent 可以發現、調用、重組這些工具

在這次任務中，需求是讓 OpenCLI 能在 Ubuntu / Linux 上操作 ChatGPT。然而實際檢查內建 `chatgpt` adapter 後，發現它採取的是 **macOS Desktop App automation** 模式，而非 ChatGPT Web automation。

因此問題不在於「OpenCLI 能不能操作 ChatGPT」，而在於：

- 目前內建的 ChatGPT adapter 實作路徑不適用 Linux
- 需要重新建構一個走 **Chrome + ChatGPT Web** 的 adapter

---

## 2. 現有環境與前置條件

本次環境整理後，已確認以下工具在主機上可用：

- Google Chrome
- Node.js 22
- npm
- OpenCLI
- OpenAI Codex CLI
- OpenCLI daemon
- OpenCLI browser extension

這一組前置條件很關鍵，因為 ChatGPT Web adapter 的前提，不只是本機能執行 `opencli`，而是 OpenCLI 背後的 browser bridge 必須已經完成：

- browser extension 可連線
- daemon 可正常提供命令橋接
- Chrome 內已有可重用的登入 session

透過 `opencli doctor` 的結果，可確認 daemon、extension 與 connectivity 均正常，這代表 OpenCLI 的 browser-control 路徑可用。

---

## 3. OpenCLI 的結構觀察

從本機實際安裝結構來看，使用者資料與 adapter 主要位於：

- `~/.opencli/`

而 OpenCLI 的程式主體則位於 npm 全域安裝目錄，例如：

- `~/.npm-global/lib/node_modules/@jackwener/opencli/`

這裡可以看出一個很重要的設計：

### 3.1 使用者層與套件層分離

OpenCLI 把「核心執行程式」與「使用者可擴充 adapter」分開：

- 核心 runtime / browser bridge / registry 在 npm 套件目錄
- 使用者 adapter 與本地 clis 在 `~/.opencli/clis/`

這種結構帶來幾個實務好處：

1. 使用者可以直接新增/覆蓋 adapter
2. 不需要改動 npm 套件本體
3. Adapter 開發與驗證流程更靈活
4. 方便 AI Agent 在本機快速試作新 CLI

### 3.2 Browser 抽象層

OpenCLI 的 browser/page 抽象位於類似以下模組：

- `dist/src/browser/page.js`
- `dist/src/browser/cdp.js`

其中 `Page` 類別的責任，主要是：

- `goto(url)`：導向指定頁面
- `evaluate(js)`：在目標頁面執行 JavaScript
- `tabs()` / `selectTab()`：管理 browser tabs
- `screenshot()`：擷取畫面
- `cdp(...)`：透過 CDP 做低階控制
- `insertText(...)` / `setFileInput(...)` 等 browser automation helper

這代表 OpenCLI 並不是單純用 HTTP 抓網站，而是透過本機瀏覽器實際操作頁面。

### 3.3 Registry 與 CLI 註冊方式

OpenCLI 的 adapter 設計是以 `cli({...})` 方式註冊命令。一般命令定義包含：

- `site`
- `name`
- `description`
- `strategy`
- `browser`
- `args`
- `columns`
- `func`

這種設計讓新命令可以被 OpenCLI 自動發現並整合進 `opencli list`。

換句話說，一個新的 ChatGPT Web adapter 並不需要修改 OpenCLI 核心，只要：

1. 放到適當的 `~/.opencli/clis/<site>/...`
2. 以 `cli({...})` 正確註冊
3. 使用 OpenCLI 的 Page/bridge 能力

就能成為新的 CLI command。

---

## 4. 為什麼內建 chatgpt adapter 不適用 Ubuntu

實際檢查 `~/.opencli/clis/chatgpt/*.js` 後，可以看到現有 adapter 使用的方式包括：

- `osascript`
- `pbcopy`
- `pbpaste`
- 啟動 ChatGPT Desktop App
- 利用系統事件做貼上、送出、讀取

這種做法的特徵非常明確：

- 平台依賴是 macOS
- 目標是 ChatGPT Desktop App，不是 Web
- 操作介面是 OS-level automation，不是 browser page automation

因此在 Ubuntu 上會直接失效，錯誤也會表現為找不到：

- `osascript`
- `pbpaste`

這不是 bug，而是架構路線不同。

因此正確的工程策略不是修補這個 macOS adapter，而是建立新的：

- `chatgpt-web`

---

## 5. chatgpt-web Adapter 的設計思路

本次新建的 `chatgpt-web` adapter，核心原則如下：

1. 完全走 Web 路線
2. 依賴 Chrome 既有登入 session
3. 使用 OpenCLI 的 browser/page abstraction
4. 避免任何 macOS-only API
5. 以 CLI 介面對外提供穩定指令

### 5.1 命令設計

規劃的命令包括：

- `opencli chatgpt-web status`
- `opencli chatgpt-web open`
- `opencli chatgpt-web new`
- `opencli chatgpt-web ask "..."`
- `opencli chatgpt-web read`
- `opencli chatgpt-web debug`

其中：

#### status
用於確認：
- 是否能打開 `chatgpt.com`
- 是否找到 composer
- 是否有登入相關標記
- 當前頁面是否可操作

#### open
只做頁面開啟與狀態回報。

#### new
嘗試建立新對話，減少舊內容對 `ask/read` 的干擾。

#### debug
輸出頁面偵測資訊，例如：
- composer 類型
- composer 內容
- send button 狀態
- article count
- last article text

這在 selector 與 DOM 偵錯時非常有價值。

#### ask
這是整個 adapter 的核心：

1. 開頁
2. 建新對話
3. 找到 composer
4. 輸入 prompt
5. 送出 prompt
6. 等待 assistant 回應
7. 回傳非空文本

#### read
純讀取目前最後一則可見回應。這條在現階段還比 `ask` 更難穩定，因為它不掌握送出當下的上下文。

---

## 6. 核心程式邏輯解析

### 6.1 `ensureChatGPT(page)`

此函式負責：

- 導向 `https://chatgpt.com/`
- 等待頁面有基本穩定性

這是所有命令的入口。

### 6.2 `pageSnapshot(page)`

此函式在頁面端用 `evaluate()` 收集關鍵狀態：

- URL
- title
- composer 是否存在
- composer tag / text
- sendButton 狀態
- loginMarkers
- articleNodes 與 articleTexts
- lastArticleText

這是一個非常重要的設計，因為它把複雜 DOM 狀態濃縮成 CLI 可判讀的快照。

### 6.3 `waitForReady(page)`

輪詢頁面狀態，直到：

- composer 出現
- 或 login marker 出現

這避免在頁面尚未載入完成時誤判沒有輸入框。

### 6.4 `clickNewChat(page)`

嘗試尋找新對話按鈕，例如：

- `a[href="/"]`
- 其他新對話按鈕 selector

此函式的價值在於隔離對話上下文，使 `ask` 測試更乾淨。

### 6.5 `focusComposerAndType(page, text)`

這是最困難的一段。

理論上只要：
- 找到 textarea
- 設定 value
- dispatch input/change

但實際上，對於 React/SPA 應用而言，這常常不夠。因為：

- DOM value 改變 ≠ React state 已同步
- 按鈕是否啟用，可能依賴框架內部事件鏈

因此這段程式在多輪修正中，逐步增加：

- native setter
- input/change 事件
- InputEvent
- keydown/keyup 類事件

目標是逼近「像真實使用者輸入」的結果。

### 6.6 `submitComposer(page)`

送出 prompt 的策略包含：

- 優先點 send button
- 若按鈕不可用，送 `Enter`
- 必要時在 Enter 後再檢查 send button 是否變為可用，並補點一次

這種設計是典型的 web automation 多重 fallback。

### 6.7 `waitForAssistantResponse(...)`

等待回應時，不能只看有沒有 article，因為：

- 可能是舊對話內容
- 可能是空白 placeholder
- 可能是尚未完成生成的片段

因此後續的修正方向包括：

- 比對先前 assistant texts
- 只接受新的非空文本
- 觀察穩定次數
- 避免過早返回空白

這段也是 `ask` 最終成功的關鍵之一。

---

## 7. 實作中遇到的關鍵工程問題

### 7.1 DOM 變動不等於真正送出

最初的 `ask` 流程雖然可以跑完，但 assistant response 一直是空的。這表示：

- 流程上看似有輸入與 submit
- 但 ChatGPT 前端未必真的接受到 prompt

這是 web automation 最典型的陷阱之一。

### 7.2 `new` 與 `send button` 狀態的交互

debug 過程中看到：

- `new` 前 `sendButton = true`
- `new` 後 `sendButton = false`

這很可能是因為新對話剛建立時，輸入框為空，按鈕自然 disabled。關鍵在於後續輸入流程能否正確把按鈕重新喚醒。

### 7.3 `read` 比 `ask` 更難

`ask` 擁有上下文：
- 知道送出前有哪些 texts
- 知道等待的是哪一輪新回覆

但 `read` 沒有這些上下文，所以只靠靜態 selector 抽最後文本，往往比較容易誤判或抓不到。

這也是為什麼目前 `ask` 已成功，而 `read` 還未完全穩定。

---

## 8. Codex 在這次工作中的角色

本次工作並非完全由 Codex 從零生成，而是：

1. 先由本地人工建立規格與初版實作
2. 再把問題整理成 `CODEX_TASK.md`
3. 交由 Codex 針對 `ask` 的最後一公里進行修補

這種合作方式的好處是：

- 問題邊界清楚
- Codex 不需要從零猜需求
- 可把時間集中在最麻煩的 selector / submit / response 偵測問題

Codex 介入後，主要價值在於：

- 收斂 `ask` 問題
- 改善 assistant text 偵測方式
- 協助同步 patch 到 `~/.opencli/clis/chatgpt-web/`

這是相當典型的 AI-assisted engineering workflow：

- 人類做架構與問題分解
- AI 做局部程式修正與測試迭代

---

## 9. 最終實測結果

目前已成功驗證：

- `opencli chatgpt-web status`
- `opencli chatgpt-web open`
- `opencli chatgpt-web new`
- `opencli chatgpt-web debug`
- `opencli chatgpt-web ask "今天天氣如何？請用繁體中文簡短回答。"`

其中 `ask` 已成功取得非空回答，例如：

> 我現在無法可靠取得即時天氣資料。請告訴我你的地點，我再幫你查；或我也可以直接幫你查「板橋」目前天氣。

這代表：

- OpenCLI → Chrome → ChatGPT Web 的控制鏈已經成立
- 新 adapter 至少已達到可實際問答的程度

目前仍待改進項目：

- `opencli chatgpt-web read`

---

## 10. OpenCLI 的實務使用建議

### 10.1 基本診斷

```bash
opencli doctor
opencli list
```

### 10.2 網頁讀取

```bash
opencli web read --url "https://example.com"
```

### 10.3 ChatGPT Web Adapter

```bash
opencli chatgpt-web status
opencli chatgpt-web open
opencli chatgpt-web new
opencli chatgpt-web debug
opencli chatgpt-web ask "今天天氣如何？請用繁體中文簡短回答。"
opencli chatgpt-web read
```

### 10.4 實務流程建議

若以穩定性為優先，建議流程是：

1. `status`
2. `new`
3. `ask`
4. 暫時不要過度依賴 `read`

也就是先把 `ask` 當主要接口，直到 `read` 的 selector 更穩定為止。

---

## 11. 後續工程建議

若要把這個原型提升到更完整的生產等級，建議後續做：

1. 強化 `read` selector 與結構化萃取
2. 支援 model 切換
3. 支援 conversation/history 管理
4. 支援附件上傳
5. 提供更穩定的 completion detection
6. 整理成獨立 plugin 專案與測試框架
7. 增加回歸測試，避免 ChatGPT DOM 變更時整體失效

---

## 12. 結論

從工程角度來看，這次工作證明了：

- OpenCLI 的 browser/page abstraction 足以支撐新的 Web CLI adapter
- 內建 adapter 不適用，不代表平台不支援，只代表實作路線不對
- 在 Ubuntu + Chrome + 已登入 session 的條件下，ChatGPT Web CLI 是可行的
- 把問題拆成 `status / debug / new / ask / read`，有助於逐步收斂 selector 與 submit 問題
- Codex 適合作為局部修補與迭代工具，而不是取代整體架構思考

目前成果已足以視為 **可用的技術原型**，並且已具備往正式 OpenCLI plugin 演進的基礎。
