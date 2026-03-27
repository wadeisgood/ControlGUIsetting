#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageOps, ImageEnhance

SRC = Path('/tmp/menu-probe/confirm-screen.png')
OUT_DIR = Path('/tmp/menu-probe/crop-ocr')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Initial heuristic crop based on current screenshot layout.
# Can be adjusted after inspection.
CROP = {
    'x': 1180,
    'y': 240,
    'w': 520,
    'h': 760,
}


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'cmd': cmd,
        'returncode': p.returncode,
        'stdout': p.stdout,
        'stderr': p.stderr,
    }


def save_variant(img, name):
    path = OUT_DIR / name
    img.save(path)
    return path


def ocr(path: Path, lang='chi_tra+eng', psm='6'):
    base = str(path.with_suffix(''))
    cmd = ['tesseract', str(path), base, '-l', lang, '--psm', str(psm)]
    res = run(cmd)
    txt = Path(base + '.txt')
    return {
        'call': res,
        'text_path': str(txt),
        'text': txt.read_text(errors='replace') if txt.exists() else '',
    }


def main():
    if not SRC.exists():
        raise SystemExit(f'missing source image: {SRC}')

    img = Image.open(SRC).convert('RGB')
    x, y, w, h = CROP['x'], CROP['y'], CROP['w'], CROP['h']
    crop = img.crop((x, y, x + w, y + h))

    report = {
        'source': str(SRC),
        'crop': CROP,
        'variants': {}
    }

    raw = save_variant(crop, 'menu-raw.png')
    report['variants']['raw'] = {'path': str(raw), 'ocr': ocr(raw)}

    up2 = crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.LANCZOS)
    up2p = save_variant(up2, 'menu-up2.png')
    report['variants']['up2'] = {'path': str(up2p), 'ocr': ocr(up2p)}

    gray = ImageOps.grayscale(up2)
    grayp = save_variant(gray, 'menu-up2-gray.png')
    report['variants']['up2_gray'] = {'path': str(grayp), 'ocr': ocr(grayp)}

    contrast = ImageEnhance.Contrast(gray).enhance(2.2)
    contrastp = save_variant(contrast, 'menu-up2-gray-contrast.png')
    report['variants']['up2_gray_contrast'] = {'path': str(contrastp), 'ocr': ocr(contrastp)}

    bw = contrast.point(lambda p: 255 if p > 180 else 0)
    bwp = save_variant(bw, 'menu-up2-bw.png')
    report['variants']['up2_bw'] = {'path': str(bwp), 'ocr': ocr(bwp)}

    out = OUT_DIR / 'report.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(str(out))


if __name__ == '__main__':
    main()
