#!/usr/bin/env bash
# Generates the files the package installs outside the application folder:
#   DESTDIR/usr/share/locale/<lang>/LC_MESSAGES/mainuan-grub-editor.mo
#   DESTDIR/usr/share/applications/org.mainuan.grubeditor.desktop   (translated)
#   DESTDIR/usr/share/metainfo/org.mainuan.grubeditor.metainfo.xml  (translated)
#   DESTDIR/usr/share/icons/hicolor/<size>/apps/org.mainuan.grubeditor.png
#   DESTDIR/usr/share/pixmaps/org.mainuan.grubeditor.png
# Used by debian/rules.  Needs gettext (msgfmt) and python3-pil.
# Usage: packaging/build-data.sh DESTDIR
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:?usage: $0 DESTDIR}"
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"
PO_DIR="$(mktemp -d)"
trap 'rm -rf "$PO_DIR"' EXIT

install -d "$DEST/usr/share/applications" "$DEST/usr/share/metainfo" "$DEST/usr/share/pixmaps"

# Catalogs: locale/<lang>/LC_MESSAGES/*.po (listed in po/LINGUAS)
"$ROOT/po/i18n.sh" compile "$DEST/usr/share/locale"

# msgfmt --desktop/--xml want <lang>.po and LINGUAS in one directory.
cp "$ROOT/po/LINGUAS" "$PO_DIR/LINGUAS"
for lang in $(grep -vE '^\s*(#|$)' "$ROOT/po/LINGUAS"); do
    cp "$ROOT/locale/$lang/LC_MESSAGES/mainuan-grub-editor.po" "$PO_DIR/$lang.po"
done
msgfmt --desktop --template="$ROOT/assets/org.mainuan.grubeditor.desktop.in" -d "$PO_DIR" \
       -o "$DEST/usr/share/applications/org.mainuan.grubeditor.desktop"
# AppStream metainfo: msgfmt writes BCP 47 tags (pt-BR); AppStream and
# software centres match POSIX locale names (pt_BR), so convert them.
msgfmt --xml --template="$ROOT/debian/org.mainuan.grubeditor.metainfo.xml.in" -d "$PO_DIR" \
       -o "$DEST/usr/share/metainfo/org.mainuan.grubeditor.metainfo.xml"
sed -i -E 's/xml:lang="([a-z]{2,3})-(Hans-|Hant-)?([A-Z]{2})"/xml:lang="\1_\3"/g' \
    "$DEST/usr/share/metainfo/org.mainuan.grubeditor.metainfo.xml"

# Icons: one correctly sized PNG per hicolor size, from the 1024 px master
python3 - "$ROOT/assets/icons/org.mainuan.grubeditor.png" "$DEST" <<'PY'
import os
import sys
from PIL import Image
src, dest = sys.argv[1], sys.argv[2]
master = Image.open(src).convert("RGBA")
for size in (16, 22, 24, 32, 48, 64, 128, 256):
    folder = os.path.join(dest, f"usr/share/icons/hicolor/{size}x{size}/apps")
    os.makedirs(folder, exist_ok=True)
    master.resize((size, size), Image.LANCZOS).save(
        os.path.join(folder, "org.mainuan.grubeditor.png"), optimize=True)
master.resize((128, 128), Image.LANCZOS).save(
    os.path.join(dest, "usr/share/pixmaps/org.mainuan.grubeditor.png"), optimize=True)
PY

find "$DEST" -type f -exec chmod 0644 {} +
