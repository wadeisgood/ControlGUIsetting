# ControlGUIsetting

An OpenClaw skill for diagnosing and fixing Linux desktop GUI browser control, especially when the OpenClaw-managed browser cannot open a visible Chrome window due to missing desktop session environment variables.

## What this repo contains

- `skills/control-gui-setting/`
  - the skill source
- `control-gui-setting.skill`
  - packaged distributable skill bundle

## What problem this skill solves

This skill is for cases where:

- `openclaw browser --browser-profile openclaw start` fails
- the browser feature is enabled and Chrome is detected
- logs show errors such as:
  - `Missing X server or $DISPLAY`
  - `The platform failed to initialize. Exiting.`
  - `Could not find DevToolsActivePort`

A common real-world cause is that the `openclaw-gateway.service` user service is running without the GUI desktop environment variables from the active GNOME/KDE login session.

## What the skill does

The skill guides an agent through:

1. Confirming OpenClaw browser support is enabled
2. Reading the true error from gateway logs
3. Verifying that the machine really has a live desktop session
4. Comparing shell environment vs `systemd --user` environment
5. Importing `DISPLAY`, `WAYLAND_DISPLAY`, `XDG_SESSION_TYPE`, `XDG_RUNTIME_DIR`, and `DBUS_SESSION_BUS_ADDRESS` into `systemd --user`
6. Restarting the OpenClaw gateway
7. Validating that the managed browser launches successfully
8. Distinguishing **browser launch success** from **browser tool exposure in the current chat session**
9. Using `openclaw browser ... open <url>` as a practical fallback when the host browser works but the live agent session still lacks the `browser` tool

## Intended environment

- Linux desktop
- GNOME or KDE session
- Wayland or X11/Xwayland
- OpenClaw browser feature enabled
- Chrome/Chromium/Brave available

## Skill name

The skill folder uses the normalized skill-spec name:

- `control-gui-setting`

The repository title uses the requested presentation name:

- `ControlGUIsetting`

## Key files

- `skills/control-gui-setting/SKILL.md`
- `skills/control-gui-setting/references/linux-gui-browser-repair.md`
- `skills/control-gui-setting/references/error-signatures.md`
- `skills/control-gui-setting/references/session-cleanup.md`

## Packaged skill

The packaged skill file is included at the repo root:

- `control-gui-setting.skill`

## Usage note

This repository is focused on the skill itself, not a full OpenClaw installation guide. It assumes OpenClaw is already installed and the browser feature is available, but the GUI browser launch path needs repair.
