# MENU_PROBE.md

Minimal MVP for GNOME Wayland context-menu probing.

## What works now

- GNOME Shell DBus screenshot API
  - fullscreen
  - active window
  - fixed area
- Basic OCR via tesseract (`chi_tra+eng`)
- Before/after fullscreen diff via Pillow
- Optional crop generation when a changed bounding box is found
- JSON report written to `/tmp/menu-probe/report.json`

## Scripts

### Base probe

```bash
./tools_menu_probe.py
```

Outputs:

- `/tmp/menu-probe/before.png`
- `/tmp/menu-probe/window.png`
- `/tmp/menu-probe/area.png`
- `/tmp/menu-probe/before.txt`
- `/tmp/menu-probe/report.json`

### Focused menu crop OCR

```bash
./tools_menu_crop_ocr.py
```

Outputs:

- `/tmp/menu-probe/crop-ocr/menu-raw.png`
- `/tmp/menu-probe/crop-ocr/menu-up2.png`
- `/tmp/menu-probe/crop-ocr/menu-up2-gray.png`
- `/tmp/menu-probe/crop-ocr/menu-up2-gray-contrast.png`
- `/tmp/menu-probe/crop-ocr/menu-up2-bw.png`
- `/tmp/menu-probe/crop-ocr/report.json`

## Current status

This now includes the initial screenshot/OCR backbone, a simple before/after diff step, an AT-SPI dump helper, and a focused menu-crop OCR helper.
It does **not yet** do:

- trigger the context menu itself
- automatically locate the menu crop from OCR/screenshot structure
- OCR bounding boxes for `複製`
- matching OCR result to AT-SPI actionable nodes
- automatic menu action execution

## Planned next steps

1. Add `before` / `after` capture pair
2. Add image diff step to isolate newly appeared menu region
3. OCR cropped menu region
4. Dump AT-SPI subtree around popup menu
5. Match OCR text (`複製`) to actionable `menu item`
6. Try action-first execution
