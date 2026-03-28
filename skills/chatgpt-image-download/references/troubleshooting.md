# Troubleshooting

## Symptom: Download button reacts but nothing appears in Downloads

Cause:
- The site action did not produce a real browser download event
- Or the browser automation path did not catch the file write

Fix:
1. Open image preview
2. Arm `waitfordownload`
3. Click **Save** or **Download** from the preview
4. Check `/tmp/openclaw/downloads/`

## Symptom: Direct URL fetch returns 403

Cause:
- The asset is protected and tied to the logged-in browser session

Fix:
- Use `openclaw browser evaluate` to inspect the page
- Use `openclaw browser waitfordownload` to capture the browser-managed download
- Do not keep retrying direct unauthenticated fetches

## Symptom: Wrong file got saved

Cause:
- The page may have multiple images or a stale previous download

Fix:
1. Inspect `document.images` from the live page
2. Match by `alt`, dimensions, and preview state
3. Trigger a fresh preview save while `waitfordownload` is armed
4. Rename the file after verification

## Copy-paste recovery flow

```bash
openclaw browser --browser-profile openclaw snapshot --limit 260
openclaw browser --browser-profile openclaw click <image-ref>
openclaw browser --browser-profile openclaw evaluate --fn '() => Array.from(document.images).map((img,i)=>({i,alt:img.alt||"",src:img.currentSrc||img.src||"",w:img.naturalWidth,h:img.naturalHeight})).filter(x=>x.src)'
openclaw browser --browser-profile openclaw waitfordownload orange.png
openclaw browser --browser-profile openclaw click <save-ref>
cp -f /tmp/openclaw/downloads/orange.png "$HOME/下載/orange.png"
file -b --mime-type "$HOME/下載/orange.png"
stat -c 'size=%s bytes' "$HOME/下載/orange.png"
```
