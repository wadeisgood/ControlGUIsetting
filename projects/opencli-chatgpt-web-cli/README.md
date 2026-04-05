# opencli-chatgpt-web-cli

An OpenCLI-compatible ChatGPT Web plugin prototype for Ubuntu / Linux.

## What this repository now provides

This repository is now organized as a cleaner **installable OpenCLI-compatible plugin layout** rather than a loose prototype dump.

The key deliverable is the adapter implementation under:

- `plugin/clis/chatgpt-web/chatgpt-web.js`

This is the file intended to be installed into a local OpenCLI environment.

## Why this plugin exists

The built-in `opencli chatgpt` adapter follows a macOS Desktop App automation path and depends on:

- `osascript`
- `pbcopy`
- `pbpaste`

That does not fit Ubuntu / Linux.

This plugin instead targets:

- Google Chrome
- OpenCLI daemon + browser extension bridge
- OpenCLI `Page` abstraction
- ChatGPT Web

## Install layout

### Plugin payload

Files intended for installation live under:

- `plugin/`

Current adapter path:

- `plugin/clis/chatgpt-web/chatgpt-web.js`

### Documentation

Project documents live under:

- `docs/`

### Figure assets

Architecture and teaching diagrams live under:

- `figures/`

### Scripts

Helper scripts live under:

- `scripts/`

## Suggested manual install

Until this is packaged into a fuller plugin installer format, the expected install path is:

```bash
mkdir -p ~/.opencli/clis/chatgpt-web
cp plugin/clis/chatgpt-web/chatgpt-web.js ~/.opencli/clis/chatgpt-web/chatgpt-web.js
```

Then verify with:

```bash
opencli list | grep -i chatgpt-web
opencli chatgpt-web status
```

## Current validated status

Validated on the target Ubuntu machine:

- `opencli chatgpt-web status` ✅
- `opencli chatgpt-web open` ✅
- `opencli chatgpt-web new` ✅
- `opencli chatgpt-web debug` ✅
- `opencli chatgpt-web scan-dom` ✅
- `opencli chatgpt-web scan-conversation` ✅
- `opencli chatgpt-web ask "..."` ✅
  - verified with a non-empty assistant response
- `opencli chatgpt-web read` ✅
  - returns the latest assistant response after the latest ask by reusing the active ChatGPT tab when possible

## What each command is for

- `status`
  - quick health check for page availability, login markers, and composer visibility
- `open`
  - opens or focuses ChatGPT Web and reports the current page state
- `new`
  - tries to start a fresh conversation
- `ask`
  - types a prompt into the composer, submits it, and waits for the latest response
- `read`
  - reads the latest visible assistant response from the current ChatGPT session
- `debug`
  - compact selector/page-state snapshot for fast troubleshooting
- `scan-dom`
  - returns higher-level DOM-derived state such as composer, send button, stop button, and message counters
- `scan-conversation`
  - returns the latest visible user/assistant snippets and a short conversation preview

## Commands

```bash
opencli chatgpt-web status
opencli chatgpt-web open
opencli chatgpt-web new
opencli chatgpt-web debug
opencli chatgpt-web scan-dom
opencli chatgpt-web scan-conversation
opencli chatgpt-web ask "今天天氣如何？請用繁體中文簡短回答。"
opencli chatgpt-web read
```

## Repository structure

```text
opencli-chatgpt-web-cli/
├── plugin/
│   └── clis/
│       └── chatgpt-web/
│           └── chatgpt-web.js
├── docs/
│   ├── OPENCLI_TECHNICAL_ANALYSIS_PRO.txt
│   ├── OPENCLI_TECHNICAL_ANALYSIS_TEACHING_REVIEW_V2.docx
│   └── OPENCLI_TECHNICAL_ANALYSIS_TEACHING_REVIEW_V2.pdf
├── figures/
│   ├── figure-1-opencli-architecture.*
│   ├── figure-2-adapter-comparison.*
│   ├── figure-3-ask-flow.*
│   ├── figure-4-debugging-map.*
│   ├── figure-5-page-layering.*
│   └── figure-6-ask-control-loops.*
├── scripts/
│   └── generate_opencli_figures.py
└── README.md
```

## Technical focus

This project emphasizes two main ideas:

1. **OpenCLI browser control architecture**
   - CLI / adapter → Page abstraction → daemon → extension / CDP → Chrome → result

2. **Control loops for ChatGPT Web automation**
   - command-forwarding loop
   - state-polling loop

These are documented in the included technical documents and diagrams.

## Documentation entry points

- `docs/OPENCLI_TECHNICAL_ANALYSIS_PRO.txt`
  - plain-text technical writeup
- `docs/OPENCLI_TECHNICAL_ANALYSIS_TEACHING_REVIEW_V2.docx`
  - review-oriented teaching version with diagrams
- `docs/OPENCLI_TECHNICAL_ANALYSIS_TEACHING_REVIEW_V2.pdf`
  - final PDF export

## Recommended usage flow

For the most reliable behavior:

1. `opencli chatgpt-web status`
2. `opencli chatgpt-web new`
3. `opencli chatgpt-web ask "..."`
4. `opencli chatgpt-web read`

Example:

```bash
opencli chatgpt-web status
opencli chatgpt-web new
opencli chatgpt-web ask "請回覆：read 測試成功。"
opencli chatgpt-web read
```

## Debugging workflow

When the ChatGPT UI changes or selectors become unstable, use:

- `debug`
  - compact selector/page-state dump
- `scan-dom`
  - inspect visible DOM-derived state such as composer, send button, stop button, and message counts
- `scan-conversation`
  - inspect the latest visible user/assistant snippets plus a short conversation preview

Suggested troubleshooting order:

1. `opencli chatgpt-web debug`
2. `opencli chatgpt-web scan-dom`
3. `opencli chatgpt-web scan-conversation`

## Known limitations

Current main limitations:

- `read` still depends on reusing the active ChatGPT tab; if no reusable tab exists it may fall back to a fresh page and return empty
- DOM selectors may still drift if ChatGPT changes its layout or experiment bucket
- conversation preview output is intended for debugging, not long-form export

## Next steps

- stabilize `read`
- add model switching
- add conversation/history support
- add attachment upload support
- package this into a more formal OpenCLI plugin install/distribution format
- add regression tests for selector drift and DOM changes
