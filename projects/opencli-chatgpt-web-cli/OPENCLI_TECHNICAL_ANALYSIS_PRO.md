# OpenCLI 技術解析報告

## 副標題
以 Ubuntu / Chrome / ChatGPT Web Adapter 開發案例為中心的系統分析

## 一、前言

本報告的目的，不是單純列出 OpenCLI 的使用指令，而是從實際工程實作的角度，解析 OpenCLI 在本機環境中的執行模型、模組分工、瀏覽器控制路徑，以及如何以它為基礎，擴充出一個可在 Ubuntu 上操作 ChatGPT 網頁版的 CLI Adapter。

這份報告以一個具體案例為核心：原本內建的 `opencli chatgpt` 命令在 Ubuntu 環境中無法達成需求，原因並不只是「平台不同」，而是其實作路徑本身偏向 macOS Desktop App automation，而不是 ChatGPT Web automation。因此，真正的工程任務不是修補既有命令，而是理解 OpenCLI 的抽象層與執行機制，並基於其 browser/page 能力設計新的 `chatgpt-web` adapter。

本報告將從環境條件、系統架構、程式結構、模組責任、問題分析、修正策略、Codex 輔助開發流程、測試結果與後續工程建議等面向進行完整說明。

## 二、專案背景與需求定義

在這次任務中，需求可以明確表述如下：

1. 在 Ubuntu / Linux 環境中使用 OpenCLI
2. 依賴 Google Chrome 既有登入狀態
3. 讓 CLI 可以操作 ChatGPT 網頁版，而不是 ChatGPT Desktop App
4. 能以命令列形式執行以下動作：
   - 開啟 ChatGPT
   - 建立新對話
   - 送出 prompt
   - 讀取回應
   - 回報當前狀態

這類需求本質上屬於「Browser-backed CLI」問題，也就是把一個原本需要在瀏覽器內互動的網站操作流程，轉成可以在命令列中調用的 deterministic interface。

如果從工具定位來看，OpenCLI 本身就是為這類問題而設計的；但問題在於內建的 ChatGPT adapter 並未採用 Browser-backed 路徑，而是採取 OS-level desktop automation。於是，需求與現有命令之間產生了落差。

## 三、環境盤點與前置條件

要讓 OpenCLI 類型的工具真正可用，前置條件遠比一個 `npm install` 複雜。這次實際工作中整理與驗證完成的環境包括：

- Google Chrome Stable
- Node.js 22
- npm
- OpenCLI
- OpenAI Codex CLI
- OpenCLI daemon
- OpenCLI browser extension

其中最重要的不是安裝本身，而是下列條件必須同時成立：

### 3.1 Chrome 可作為執行載體
OpenCLI 不是只靠 HTTP request 擷取網站資料。對於互動式網站操作，它依賴真實的瀏覽器 session。因此 Chrome 不只是顯示容器，而是整個 automation path 的核心。

### 3.2 Browser extension 已正常連線
OpenCLI 需要透過 browser extension 與 daemon 建立 browser bridge。如果 extension 未連線，即便本機安裝了 opencli，很多依賴頁面操作的命令也無法工作。

### 3.3 Daemon 正常運作
OpenCLI 的 browser operations 背後需要 daemon 提供命令執行橋接，例如頁面導向、evaluate、CDP 指令傳遞等。如果 daemon 未啟動，CLI 無法完成實際 automation。

### 3.4 Browser session 已登入
對 ChatGPT、X、Bilibili、YouTube 等服務來說，OpenCLI 的優勢之一是直接重用本機瀏覽器既有登入狀態。因此使用者的登入 session 必須已存在於 Chrome 裡。

### 3.5 驗證方式
這些條件最後透過 `opencli doctor` 完成驗證。doctor 結果顯示：

- daemon 正常
- extension 已連線
- connectivity 正常

這代表 browser bridge 的整條路徑已建立完成，具備開發新 adapter 的基礎。

## 四、OpenCLI 的系統架構觀察

從實際安裝結構來看，OpenCLI 的設計有一個很重要的特色：它將「核心執行程式」與「使用者層 adapter / 配置」分離。

### 4.1 使用者層目錄
使用者層的主要資料位於：

- `~/.opencli/`

這裡包含：
- adapter manifest
- clis 目錄
- browser 相關檔案
- 本地插件與額外依賴
- 本機 adapter 的可編輯實作

### 4.2 套件層目錄
OpenCLI 的核心程式通常位於全域 npm 套件路徑，例如：

- `~/.npm-global/lib/node_modules/@jackwener/opencli/`

這裡包含：
- browser abstraction
- registry API
- daemon runtime
- base page / CDP utilities
- 各種內建核心支援模組

### 4.3 工程上的意義
這種分層讓 OpenCLI 很適合做本地客製化：

1. 使用者可以在 `~/.opencli/clis/` 新增命令
2. 不需要直接改 npm 套件本體
3. 更新 OpenCLI 核心與本地 adapter 可以分開進行
4. 非常適合讓 AI Agent 在本機迭代新 CLI 能力

這一點對本次 `chatgpt-web` adapter 的開發極其重要。因為我們不必修改 OpenCLI 核心，只要新增新的 adapter 即可。

## 五、Browser / Page 抽象層的角色

OpenCLI 能把網站轉成 CLI，不是靠單純抓 HTML，而是透過 browser/page abstraction。這層能力大致集中在以下模組：

- `dist/src/browser/page.js`
- `dist/src/browser/cdp.js`
- `dist/src/browser/*`

從 `Page` 類別可觀察到的能力包括：

- `goto(url)`：導向指定頁面
- `evaluate(js)`：在頁面上下文執行 JavaScript
- `tabs()` / `selectTab()`：管理 browser tabs
- `screenshot()`：擷取頁面畫面
- `cdp(...)`：透過 CDP 執行更低階控制
- `insertText(...)`：插入文字
- `setFileInput(...)`：設定 file input
- network capture / intercept 類能力

### 5.1 工程上的意義
這表示 OpenCLI 並不是一個單純「網站爬蟲 CLI」。對需要登入、需要互動、需要保持單頁應用狀態的網站來說，它比較像是一層建立在 Chrome session 之上的 automation SDK，再透過 registry 包裝成命令列介面。

換句話說，OpenCLI 的真正優勢不是「抓資料」，而是：

- 重用 session
- 保留前端應用狀態
- 在頁面內執行邏輯
- 把這些能力統一暴露成 CLI

## 六、Registry 機制與命令定義模式

OpenCLI 的命令通常透過 `cli({...})` 註冊。這裡反映出它的 registry-driven 設計。

典型命令定義包含：

- `site`：命令所屬站點/命名空間
- `name`：子命令名稱
- `description`：描述
- `strategy`：公開、cookie、intercept 等策略
- `browser`：是否依賴 browser
- `args`：命令參數
- `columns`：輸出欄位
- `func`：實際執行函式

### 6.1 對 adapter 開發的意義
這讓新命令不需要侵入 OpenCLI 核心，而只需要：

1. 放到正確位置
2. 正確註冊
3. 使用 browser/page 能力
4. 輸出符合 OpenCLI CLI 風格的結果

對本次任務而言，這就是 `chatgpt-web` 能被自然加入 `opencli list` 的原因。

## 七、為什麼內建 chatgpt 命令在 Ubuntu 上不可用

實際檢查 `~/.opencli/clis/chatgpt/ask.js`、`send.js`、`read.js` 後，可以清楚看到這個 adapter 的設計假設是：

- 平台是 macOS
- 目標是 ChatGPT Desktop App
- 透過 `osascript` 激活應用程式
- 透過 `pbcopy/pbpaste` 處理 clipboard
- 用 OS-level keystroke 模擬貼上與送出

這種設計在 macOS 是合理的，但在 Ubuntu 上就會直接失效。錯誤訊息如：

- `osascript: not found`
- `pbpaste: not found`

因此問題並不是「OpenCLI 壞了」，而是現有 adapter 的平台假設不成立。

## 八、chatgpt-web Adapter 的設計原則

針對上述落差，本次建立了新的 `chatgpt-web` adapter，其設計原則如下：

1. 明確鎖定 ChatGPT Web，而非 Desktop App
2. 明確鎖定 Ubuntu / Linux + Chrome 環境
3. 完全使用 OpenCLI 的 browser/page infrastructure
4. 不使用任何 macOS-only automation API
5. 將功能拆成多個可獨立驗證的命令

### 8.1 命令設計

設計出的命令包括：

- `status`
- `open`
- `new`
- `debug`
- `ask`
- `read`

這不是任意拆分，而是工程上刻意分層：

- `status` 解決「頁面是否可用」
- `open` 解決「能不能開頁」
- `new` 解決「能不能建立新上下文」
- `debug` 解決「selector / DOM 狀態是否正確」
- `ask` 解決「真正互動是否成功」
- `read` 解決「如何穩定讀最後回答」

這種分層讓 debug 比較可控，也比較適合 AI 協作。

## 九、核心函式解析

### 9.1 `ensureChatGPT(page)`

此函式的責任很單純：
- 開啟 `https://chatgpt.com/`
- 做最基本的等待

它是所有命令的共同入口。

### 9.2 `pageSnapshot(page)`

這是整個 adapter 的核心觀測點。它會從頁面中抽出：

- URL
- title
- composer 是否存在
- composer tag 與當前文字
- send button 狀態
- login markers
- article 數量
- 最後文章文字
- assistant texts

這個函式的價值在於把複雜 DOM 狀態壓縮成一個穩定的快照，使 CLI 與 debug 都有統一觀測基礎。

### 9.3 `waitForReady(page)`

此函式透過輪詢等待頁面進入可操作狀態。這是必要的，因為單頁應用載入過程中，DOM 結構常會經歷多輪變化。若沒有這層等待，selector 找不到並不代表頁面真的不可用。

### 9.4 `clickNewChat(page)`

新對話建立不是附加功能，而是降低上下文污染的關鍵。若直接在既有對話頁送 prompt，`read` 與 `response detection` 都容易誤判。

### 9.5 `focusComposerAndType(page, text)`

這是技術上最敏感的區塊。直覺上只要改 textarea value 即可，但實際上：

- DOM value 改變不代表 React state 更新
- React 可能依賴原生 setter 與特定事件鏈
- send button 的 enabled 狀態通常綁定框架內部 state

因此這段實作加入了：

- native setter
- input/change event
- InputEvent
- keydown/keyup 類事件

這些都是為了更接近「真實輸入」效果。

### 9.6 `submitComposer(page)`

送出策略採多重 fallback：

1. 先找 send button，若可用直接點擊
2. 若按鈕不可用，送出 Enter 類事件
3. 事件後再次檢查 send button 是否變為可用，必要時補點一次

這是針對前端互動不穩定時的實務工程手法。

### 9.7 `waitForAssistantResponse(...)`

此函式的工作不只是等待，而是正確判斷「新回應是否產生」與「回應是否穩定」。

若只看最後一個 article，容易遇到：
- 舊內容誤判
- 空白 placeholder 誤判
- 尚未完成生成的片段誤判

因此後續透過：
- assistantTexts 比對
- stableCount
- stop button / generating 狀態
- 非空文本判定

來提高穩定度。

## 十、Debug 過程中的重要發現

在多輪測試中，取得了幾個關鍵觀察：

### 10.1 `status` 成功
表示：
- opencli 已載入新 adapter
- ChatGPT 網頁可開啟
- composer 可找到

### 10.2 `debug` 顯示 `TEXTAREA`
表示輸入框 selector 並非完全錯誤，問題不在「找不到輸入框」，而在「如何正確觸發前端狀態更新」。

### 10.3 `new` 成功
表示新對話路徑是可達的，對話上下文可被重設。

### 10.4 `ask` 初期回空
這是重要訊號：
- 命令流程不是完全失敗
- 但 ChatGPT 沒有回傳有效結果

這使得問題範圍收斂到：
- 輸入沒真正送進前端 state
- submit 沒真正發生
- response 抓取邏輯不夠精確

### 10.5 最終 `ask` 成功取得非空回應
這證明整條控制鏈最終是可打通的：

- OpenCLI → Chrome → ChatGPT Web → 回應擷取

這是這次工程中最重要的驗證結果。

## 十一、Codex 在開發流程中的角色

這次工作並不是把所有事情交給 Codex 從零完成，而是採取較成熟的 AI 協作模式：

1. 人先建立問題框架與初版程式
2. 人先完成環境安裝與工具接通
3. 人先做第一輪 debug，把問題縮到 `ask` 的最後一公里
4. 再把問題精準整理成 `CODEX_TASK.md`
5. 讓 Codex 專注修 `ask` 的最後關鍵段落

這樣的流程有幾個優點：

- AI 不需要猜問題背景
- 需求與限制被明確描述
- Codex 的輸出更集中在高價值區域
- 人仍然保有架構與品質控制權

從實際效果來看，Codex 對以下部分特別有幫助：

- response detection 收斂
- assistantTexts 比對
- 送出後穩定判定邏輯
- patch 同步流程

## 十二、當前成果評估

### 已達成

- OpenCLI 在 Ubuntu 上正常運作
- Chrome / Node / npm / Codex 均已安裝並驗證
- `chatgpt-web` adapter 已成功掛入 OpenCLI
- `ask` 已能取得非空 assistant response
- 專案文件、技術報告、PDF 已整理完成

### 尚未完全完成

- `read` 仍不夠穩定
- 尚未做完整 conversation/history 設計
- 尚未做 model management
- 尚未做附件上傳支援
- 尚未做正式獨立 plugin packaging

## 十三、使用建議與工程建議

### 實務操作建議

若目前要實際使用，建議流程為：

1. `opencli chatgpt-web status`
2. `opencli chatgpt-web new`
3. `opencli chatgpt-web ask "..."`

在 `read` 完全穩定前，優先信任 `ask` 的直接回傳結果。

### 工程演進建議

後續若要把它提升到更正式的生產等級，建議優先做：

1. 強化 `read` selector
2. 補 model switch
3. 補 history / conversation API
4. 補附件上傳
5. 建立 regression tests
6. 整理成獨立 plugin project
7. 提供更正式的 adapter manifest 與安裝路徑

## 十四、結論

這次案例很有代表性，因為它展示了幾個重要結論：

第一，OpenCLI 的核心能力並不侷限於內建命令本身，而是其 browser/page abstraction 與 registry 架構。只要理解這層抽象，許多原本不存在的 CLI 都可以被建構出來。

第二，當現有 adapter 與需求不相符時，真正的解法常常不是 patch 原始命令，而是重新辨識它的執行模型，然後沿著正確的抽象層重建命令。

第三，Ubuntu + Chrome + ChatGPT Web 的 CLI 路線是可行的。雖然其中最困難的部分在於 React/SPA 的輸入與提交行為，但透過 page-level automation、fallback submit 策略與 response detection 收斂，實際上已經可以得到可用成果。

第四，Codex 適合作為局部工程問題的加速器，而不是整體架構思考的替代品。當人先把問題拆解清楚，再交由 Codex 補最關鍵的一段，其效果是很高的。

總結而言，本次工作已經成功把 OpenCLI 在 Ubuntu 上的 ChatGPT 能力，從原本不適用的平台路線，推進到一個可實際使用的 ChatGPT Web CLI 原型，並且已具備後續演進為正式 plugin 的基礎。
