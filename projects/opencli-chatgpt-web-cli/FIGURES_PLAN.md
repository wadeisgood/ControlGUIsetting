# Figures plan for OpenCLI technical analysis

## Figure 1 — OpenCLI system architecture

Show:
- User / CLI
- opencli command layer
- registry / adapters
- browser bridge extension
- daemon
- Chrome session
- target website / ChatGPT Web

Goal:
Explain the full execution path from CLI invocation to website interaction.

## Figure 2 — Adapter layering comparison

Compare:
- built-in chatgpt desktop adapter (macOS, osascript, pbcopy/pbpaste, Desktop App)
- new chatgpt-web adapter (Linux/Ubuntu, Chrome, browser/page abstraction, ChatGPT Web)

Goal:
Explain why the built-in adapter fails on Ubuntu and why a new web adapter is necessary.

## Figure 3 — chatgpt-web command flow

Flow:
- status
- open
- new
- debug
- ask
- read

Or deeper ask flow:
- open page
- wait ready
- new chat
- locate composer
- type prompt
- submit
- wait response
- extract assistant text

Goal:
Explain the internal runtime sequence.

## Figure 4 — ask debugging bottleneck map

Show failure points:
- selector found / not found
- DOM updated but React state unsynced
- send button disabled
- submit fallback
- response detection

Goal:
Explain engineering/debugging logic.
