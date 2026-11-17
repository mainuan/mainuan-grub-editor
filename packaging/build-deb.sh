#!/usr/bin/env bash
# Builds mainuan-grub-editor_<version>_all.deb from this repository.
# Usage: ./packaging/build-deb.sh [output-dir]      (default output: ./dist)
# Needs: dpkg-deb, python3 with Pillow (python3-pil), gzip, gettext (msgfmt)
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
    --exclude='./locale' --exclude='./po' --exclude='./tests' --exclude='*.desktop.in' --exclude='*.metainfo.xml.in' \
    --exclude='.gitignore' --exclude='.gitkeep' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='*.deb' -cf - . | tar -C "$STAGE$APP" -xf -

# Launcher, desktop entry, metainfo, docs
install -m 0755 "$ROOT/debian/mainuan-grub-editor" "$STAGE/usr/bin/mainuan-grub-editor"
install -m 0644 "$ROOT/debian/copyright" "$STAGE/usr/share/doc/mainuan-grub-editor/copyright"
gzip -9n -c "$ROOT/docs/mainuan-grub-editor.1" > "$STAGE/usr/share/man/man1/mainuan-grub-editor.1.gz"

# Translations: catalogs from locale/<lang>/LC_MESSAGES/*.po (listed in po/LINGUAS)
# become /usr/share/locale/<lang>/LC_MESSAGES/mainuan-grub-editor.mo.
"$ROOT/po/i18n.sh" compile "$STAGE/usr/share/locale"
# Desktop entry: Name/Comment/Keywords translated from the same catalogs.
# msgfmt --desktop wants <lang>.po + LINGUAS in one directory.
DESKTOP_PO="$(mktemp -d)"
trap 'rm -rf "$STAGE" "$DESKTOP_PO"' EXIT
cp "$ROOT/po/LINGUAS" "$DESKTOP_PO/LINGUAS"
for lang in $(grep -vE '^\s*(#|$)' "$ROOT/po/LINGUAS"); do
    ln -s "$ROOT/locale/$lang/LC_MESSAGES/mainuan-grub-editor.po" "$DESKTOP_PO/$lang.po"
done
msgfmt --desktop --template="$ROOT/assets/org.mainuan.grubeditor.desktop.in" -d "$DESKTOP_PO" \
       -o "$STAGE/usr/share/applications/org.mainuan.grubeditor.desktop"
chmod 0644 "$STAGE/usr/share/applications/org.mainuan.grubeditor.desktop"
# AppStream metainfo: name, summary, description and keywords from the same
# catalogs. msgfmt writes BCP 47 tags (pt-BR); AppStream and software centres
# match POSIX locale names (pt_BR), so convert them.
msgfmt --xml --template="$ROOT/debian/org.mainuan.grubeditor.metainfo.xml.in" -d "$DESKTOP_PO" \
       -o "$STAGE/usr/share/metainfo/org.mainuan.grubeditor.metainfo.xml"
sed -i -E 's/xml:lang="([a-z]{2,3})-(Hans-|Hant-)?([A-Z]{2})"/xml:lang="\1_\3"/g' \
    "$STAGE/usr/share/metainfo/org.mainuan.grubeditor.metainfo.xml"
chmod 0644 "$STAGE/usr/share/metainfo/org.mainuan.grubeditor.metainfo.xml"

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
