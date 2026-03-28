---
name: chatgpt-image-download
description: Reliably extract and save ChatGPT-generated images from the OpenClaw managed browser when normal Download/Save clicks do not create a file. Use when ChatGPT image generation succeeds in the browser preview but the site download flow fails, saves the wrong file, returns 403 outside the logged-in session, or requires capturing the image through the active browser session.
---

# ChatGPT Image Download

Use this skill when a ChatGPT image is visible in the browser but ordinary save/download actions are unreliable.

## Goal

Save the actual generated image as a local file by using the logged-in browser session instead of a direct unauthenticated HTTP fetch.

## Fast path

1. Ensure the image is visible in ChatGPT.
2. Open the image preview if needed.
3. Extract the in-session image URL with `openclaw browser evaluate`.
4. Prefer `openclaw browser waitfordownload <name>` plus a browser click on **Save** or **Download**.
5. Copy the downloaded file from `/tmp/openclaw/downloads/` to the user destination.
6. Verify the result with `file` and `stat`.

## Why this skill exists

ChatGPT image assets can be protected by the logged-in browser session. Typical failure modes:

- Clicking **Download** or **Save** appears to work, but no file lands in `~/Downloads`
- The wrong file gets saved
- Direct `curl` / Python / urllib download returns `403 Forbidden`
- The preview clearly shows the image, but the host cannot retrieve it outside the browser session

In these cases, use the browser session itself as the trusted download path.

## Workflow

### 1. Confirm the image is present

Capture a snapshot:

```bash
openclaw browser --browser-profile openclaw snapshot --limit 260
```

Look for image cards or preview dialogs with labels such as generated image titles, plus **Download** / **Save** controls.

### 2. Open preview when possible

If the page shows an image card, click it to open the preview dialog. The preview often exposes a more reliable **Save** button than the inline card.

Example:

```bash
openclaw browser --browser-profile openclaw click <image-ref>
```

### 3. Extract the real image URL from the live page

Use browser-side JS so the logged-in session resolves the real `img.src` / `currentSrc` values.

Example:

```bash
openclaw browser --browser-profile openclaw evaluate --fn '() => Array.from(document.images).map((img,i)=>({i,alt:img.alt||"",src:img.currentSrc||img.src||"",w:img.naturalWidth,h:img.naturalHeight})).filter(x=>x.src)'
```

Pick the entry whose `alt` or dimensions match the target image.

### 4. Do not rely on direct external fetch

If the extracted URL points at ChatGPT backend content, a direct fetch may fail even though the browser can see it.

Typical failure:

```text
HTTP Error 403: Forbidden
```

Treat this as expected. Do not keep retrying unauthenticated HTTP downloads.

### 5. Use browser-managed download capture

Arm the next browser download event first:

```bash
openclaw browser --browser-profile openclaw waitfordownload orange.png
```

Run it in background when needed, then click the page control that triggers the download:

```bash
openclaw browser --browser-profile openclaw click <save-or-download-ref>
```

If you are orchestrating from shell, use your process manager to wait for completion. Success looks like:

```text
downloaded: /tmp/openclaw/downloads/orange.png
```

### 6. Move the file to the destination

Copy the captured file into the user-facing directory:

```bash
cp -f /tmp/openclaw/downloads/orange.png "$HOME/下載/orange.png"
```

Adjust the destination and filename as requested.

### 7. Verify the result

Always verify type and size:

```bash
file -b --mime-type "$HOME/下載/orange.png"
stat -c 'size=%s bytes' "$HOME/下載/orange.png"
```

Healthy result example:

```text
image/png
size=1416031 bytes
```

## Decision guide

### If inline Download fails

- Open the preview dialog
- Try **Save** from preview
- If no file appears, switch to `waitfordownload`

### If direct HTTP fetch returns 403

- Stop using external fetches
- Continue only through the logged-in browser session

### If the wrong file appears in Downloads

- Ignore the naive download result
- Extract the actual image URL for confirmation
- Re-run with `waitfordownload` bound to the specific save action

## Recommended command sequence

Use this sequence when the image preview is already open:

```bash
openclaw browser --browser-profile openclaw evaluate --fn '() => Array.from(document.images).map((img,i)=>({i,alt:img.alt||"",src:img.currentSrc||img.src||"",w:img.naturalWidth,h:img.naturalHeight})).filter(x=>x.src)'
openclaw browser --browser-profile openclaw waitfordownload orange.png
openclaw browser --browser-profile openclaw click <save-ref>
cp -f /tmp/openclaw/downloads/orange.png "$HOME/下載/orange.png"
file -b --mime-type "$HOME/下載/orange.png"
stat -c 'size=%s bytes' "$HOME/下載/orange.png"
```

## Notes

- Prefer the browser session over `curl`, Python `urllib`, or other external fetch methods for protected ChatGPT assets.
- Use `waitfordownload` when ordinary UI clicks do not reliably land a file.
- Verify the saved file before telling the user the task is complete.
- If needed, rename the file to something human-friendly after verification.

## Reference files

- Read `references/troubleshooting.md` for symptom-to-fix mapping and a copy-paste recovery flow.
