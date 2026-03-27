# Session Cleanup

## Purpose

Use this guide when the OpenClaw UI still shows many old sub sections, branches, or historical entries that are no longer needed.

This guide focuses on **main agent session history cleanup** on disk.

## What to keep

Keep:

- the currently active session file
- the active session entry inside `sessions.json`

Optionally keep:

- recent backups until the UI looks correct
- `.reset.*` files if you are not yet sure they are safe to remove

## Inventory

List session files by recency:

```bash
python3 - <<'PY'
import os, time
base=os.path.expanduser('~/.openclaw/agents/main/sessions')
current='CURRENT-SESSION-ID-HERE'
files=[]
for name in os.listdir(base):
    if name.endswith('.jsonl'):
        path=os.path.join(base,name)
        st=os.stat(path)
        files.append((st.st_mtime,name,st.st_size))
files.sort(reverse=True)
print('CURRENT', current)
for mtime,name,size in files:
    sid=name[:-6]
    mark='KEEP-CURRENT' if sid==current else 'CANDIDATE'
    print(f'{mark}\t{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))}\t{size}\t{name}')
PY
```

## Backup + cleanup

```bash
set -e
BASE="$HOME/.openclaw/agents/main/sessions"
BACKUP="/tmp/openclaw-session-backup-$(date +%F)"
CURRENT="CURRENT-SESSION-ID-HERE.jsonl"
mkdir -p "$BACKUP"
cd "$BASE"
for f in *.jsonl; do
  if [ "$f" != "$CURRENT" ]; then
    cp -a "$f" "$BACKUP/"
    rm -f "$f"
  fi
done
```

## Trim `sessions.json`

Keep only the active session entry:

```bash
python3 - <<'PY'
import json, os
path=os.path.expanduser('~/.openclaw/agents/main/sessions/sessions.json')
current_key='CURRENT-SESSION-KEY-HERE'
current_file='CURRENT-SESSION-ID-HERE.jsonl'
with open(path,'r',encoding='utf-8') as f:
    data=json.load(f)
new={}
for k,v in data.items():
    sf=v.get('sessionFile','')
    if k==current_key or sf.endswith(current_file):
        new[k]=v
with open(path,'w',encoding='utf-8') as f:
    json.dump(new,f,ensure_ascii=False,indent=2)
    f.write('\n')
print('sessions.json entries kept:', len(new))
PY
```

## Verify

After cleanup, inspect:

```bash
ls -1 ~/.openclaw/agents/main/sessions
```

You should mainly see:

- the active `.jsonl`
- `sessions.json`
- optional `.lock`
- optional `.reset.*` leftovers

## `.reset.*` leftovers

These are usually not active session files. Treat them as a separate cleanup pass only after the UI looks correct.

## Notes

- UI clutter may come from session history even if tmux or ClawTeam runtime is already gone.
- Removing old `.jsonl` session files is often what actually reduces old UI sub sections.
- Always back up first.
