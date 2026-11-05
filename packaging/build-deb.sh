#!/usr/bin/env bash
# Builds mainuan-grub-editor_<version>_all.deb from this repository.
# Usage: ./packaging/build-deb.sh [output-dir]      (default output: ./dist)
# Needs: dpkg-deb, python3 with Pillow (python3-pil), gzip
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/dist}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

VERSION="$(sed -n 's/^Version: //p' "$ROOT/packaging/control")"
APP=/usr/share/mainuan-grub-editor
export PYTHONDONTWRITEBYTECODE=1

install -d "$STAGE/DEBIAN" "$STAGE$APP" "$STAGE/usr/bin" \
           "$STAGE/usr/share/applications" "$STAGE/usr/share/metainfo" \
           "$STAGE/usr/share/pixmaps" "$STAGE/usr/share/man/man1" \
           "$STAGE/usr/share/doc/mainuan-grub-editor"

# Application files (everything except packaging, VCS and build leftovers)
tar -C "$ROOT" \
    --exclude='./packaging' --exclude='./dist' --exclude='./.git' \
    --exclude='.gitignore' --exclude='.gitkeep' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='*.deb' -cf - . | tar -C "$STAGE$APP" -xf -

# Launcher, desktop entry, metainfo, docs
install -m 0755 "$ROOT/debian/mainuan-grub-editor" "$STAGE/usr/bin/mainuan-grub-editor"
install -m 0644 "$ROOT/assets/org.mainuan.grubeditor.desktop" "$STAGE/usr/share/applications/"
install -m 0644 "$ROOT/debian/org.mainuan.grubeditor.metainfo.xml" "$STAGE/usr/share/metainfo/"
install -m 0644 "$ROOT/debian/copyright" "$STAGE/usr/share/doc/mainuan-grub-editor/copyright"
gzip -9n -c "$ROOT/docs/mainuan-grub-editor.1" > "$STAGE/usr/share/man/man1/mainuan-grub-editor.1.gz"

# Icons: one correctly sized PNG per hicolor size, generated from the 1024px master
python3 - "$ROOT/assets/icons/org.mainuan.grubeditor.png" "$STAGE" <<'PY'
import sys, os
from PIL import Image
src, stage = sys.argv[1], sys.argv[2]
master = Image.open(src).convert("RGBA")
for s in (16, 22, 24, 32, 48, 64, 128, 256):
    d = os.path.join(stage, f"usr/share/icons/hicolor/{s}x{s}/apps")
    os.makedirs(d, exist_ok=True)
    master.resize((s, s), Image.LANCZOS).save(os.path.join(d, "org.mainuan.grubeditor.png"), optimize=True)
master.resize((128, 128), Image.LANCZOS).save(os.path.join(stage, "usr/share/pixmaps/org.mainuan.grubeditor.png"), optimize=True)
PY

install -m 0644 "$ROOT/packaging/control" "$STAGE/DEBIAN/control"

# Sane permissions
find "$STAGE" -type d -exec chmod 0755 {} +
find "$STAGE$APP" -type f -exec chmod 0644 {} +

mkdir -p "$OUT"
DEB="$OUT/mainuan-grub-editor_${VERSION}_all.deb"
dpkg-deb --root-owner-group --build "$STAGE" "$DEB"
echo "Built: $DEB"
