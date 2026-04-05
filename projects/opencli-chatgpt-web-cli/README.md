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
- `opencli chatgpt-web ask "..."` ✅
  - verified with a non-empty assistant response
- `opencli chatgpt-web read` ✅
  - now returns the latest assistant response after the latest ask (uses active ChatGPT tab)

## Commands

```bash
opencli chatgpt-web status
opencli chatgpt-web open
opencli chatgpt-web new
opencli chatgpt-web debug
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

## Known limitation

Current main limitation:

- `read` depends on reusing the active ChatGPT tab; if no active tab exists it may open a fresh page and return empty.

Recommended flow:

1. `status`
2. `new`
3. `ask`
4. `read`

## Next steps

- stabilize `read`
- add model switching
- add conversation/history support
- add attachment upload support
- package this into a more formal OpenCLI plugin install/distribution format
- add regression tests for selector drift and DOM changes
