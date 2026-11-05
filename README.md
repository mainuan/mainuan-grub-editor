# Mainuan GRUB Editor

[![License: GPL-3.0+](https://img.shields.io/badge/License-GPL--3.0%2B-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-2.0.2--8-green.svg)]()

Advanced graphical editor for GRUB2 configuration, compatible with XFCE, Plasma and GNOME.

*Editor gráfico avanzado para la configuración de GRUB2, compatible con XFCE, Plasma y GNOME.*

## 📝 Description

A GTK3 graphical interface to configure and customize the GRUB2 bootloader: entries, themes, fonts, backgrounds, advanced parameters and more, with complete internationalization support.

## ✨ Features

- 🗂️ Visual editing of GRUB2 configuration
- 🎨 Theme and background management and installation
- 🔤 Custom font conversion and installation
- 📝 Custom boot entry management
- ⚙️ Advanced kernel parameter configuration

### 🚀 Recent Updates (v2.0.2)
- **Hierarchical Submenus**: Full support for selecting kernels in submenus.
- **Background Sync**: Automatic silent `update-grub` on startup.
- **UI Optimizations**: Compact layouts and improved path selection.
- **Localization**: Updated translations for all 8 supported languages.
- 💾 Automatic backup and restore
- 🌍 Complete internationalization (8 languages)
- 🖥️ Compatible with XFCE, Plasma and GNOME
- 🌊 **Full support for Wayland and X11**
- ⌨️ Keyboard shortcuts for all actions

## 📸 Screenshots

![General Configuration](https://raw.githubusercontent.com/MainuanLinux/mainuan-grub-editor/main/assets/screenshots/screenshot1.png)
*General Configuration*

![Boot Entries Management](https://raw.githubusercontent.com/MainuanLinux/mainuan-grub-editor/main/assets/screenshots/screenshot2.png)
*Boot Entries Management*

![Theme Selector](https://raw.githubusercontent.com/MainuanLinux/mainuan-grub-editor/main/assets/screenshots/screenshot3.png)
*Theme Selector*

![Background Selector](https://raw.githubusercontent.com/MainuanLinux/mainuan-grub-editor/main/assets/screenshots/screenshot4.png)
*Background Selector*

![Font Selector](https://raw.githubusercontent.com/MainuanLinux/mainuan-grub-editor/main/assets/screenshots/screenshot5.png)
*Font Selector*

## 🛠️ Requirements

- Python 3.8+
- GTK 3.0
- GRUB 2.x installed
- Dependencies: PyGObject, pycairo, python-xlib, polib, python-dbus, Pillow

## 📥 Installation

```bash
# System dependencies
sudo apt install python3-gi gir1.2-gtk-3.0 python3-gi-cairo grub2-common pkexec imagemagick python3-cairo python3-xlib python3-polib python3-dbus python3-pil

# Python installation
pip3 install -r requirements.txt

# Manual installation
sudo python3 setup.py install

# Install desktop files and icons
sudo cp assets/org.mainuan.grubeditor.desktop /usr/share/applications/
sudo cp assets/icons/org.mainuan.grubeditor.png /usr/share/icons/hicolor/128x128/apps/
sudo cp debian/org.mainuan.grubeditor.metainfo.xml /usr/share/metainfo/
sudo update-desktop-database
sudo gtk-update-icon-cache /usr/share/icons/hicolor/
```

## 🚀 Usage

```bash
# Run the application
mainuan-grub-editor
```

The application will automatically request administrator privileges using `pkexec`.

## 📦 Building the .deb package

```bash
# Needs dpkg-deb and python3-pil
./packaging/build-deb.sh          # writes dist/mainuan-grub-editor_<version>_all.deb
sudo apt install ./dist/mainuan-grub-editor_*_all.deb
```

The package version comes from `packaging/control`.

## 🌊 Wayland Compatibility

The application is **fully compatible with Wayland** and works perfectly on:

- **Plasma 6 + Wayland** (Mainuan Linux Tyson)
- **GNOME + Wayland**
- **Sway** and other Wayland compositors
- **X11** (all traditional environments)

### Wayland Specific Features:
- ✅ Automatic window protocol detection
- ✅ Automatic theme application (including dark theme on Plasma 6)
- ✅ Correct scaling on HiDPI monitors
- ✅ Native integration with the compositor

### Theme Troubleshooting:

If the application is not using the correct theme:

```bash
# Force dark theme
GTK_THEME=Adwaita:dark mainuan-grub-editor

# Force light theme
GTK_THEME=Adwaita mainuan-grub-editor

# For Plasma with Breeze theme
GTK_THEME=Breeze-Dark mainuan-grub-editor
```

## 🖥️ Main Features

- **General**: Timeout, default entry, resolution, kernel parameters, OS detection
- **Appearance**: Themes, fonts, colors, backgrounds
- **Entries**: Add, edit and manage custom boot entries
- **Security**: Automatic backups before applying changes
- **Validation**: Syntax and structure verification before saving

## 🌐 Supported Languages

- 🇪🇸 Spanish
- 🇺🇸 English
- 🇵🇹 Portuguese
- 🇫🇷 French
- 🇩🇪 German
- 🇮🇹 Italian
- 🇷🇴 Romanian
- 🇷🇺 Russian

## 🐧 Distribution Compatibility

- ✅ **Mainuan Linux Boro** (GNOME + Wayland)
- ✅ **Mainuan Linux Tyron** (XFCE + X11)
- ✅ **Mainuan Linux Tyson** (Plasma 6 + Wayland)

## 📄 License

This project is licensed under [GPL-3.0+](https://www.gnu.org/licenses/gpl-3.0.html).

## 👥 Developers

Developed by David Caixinha

## 🆕 New in version 2.0.2-8 (August 1, 2026)

- **Added**: "Default Boot Mode" selector with three explicit choices: fixed entry, last installed kernel, or last booted kernel.
- **Added**: The boot entry selector is greyed out unless "Fixed entry" is chosen.
- **Fixed**: Applying changes in General settings no longer pins the boot entry to the current kernel, which prevented newly installed kernels from ever being booted.

## 🆕 New in version 2.0.2-7 (July 29, 2026)

- **Fixed**: Screen resolution was saved using its translated label instead of its real value, producing `GRUB_GFXMODE=automatisch` on German systems.
- **Fixed**: Custom entries added with "Add entry" can now be enabled, disabled and deleted, instead of being mistaken for kernel entries.
- **Fixed**: Disabled custom entries stay listed so they can be re-enabled or removed later.
- **Fixed**: Launcher wrapper now registers the window as `org.mainuan.grubeditor`, matching the desktop file.

## 🆕 New in version 2.0.2-6 (July 23, 2026)

- **Fixed**: Boot entries parser no longer lists duplicate memtest entries generated by GRUB's `pc`/`efi` platform conditionals.
- **Fixed**: Boot entry type label now correctly recognizes "Memory test" titles.
- **Fixed**: The boot entry path column now actually shows the kernel/binary path.
- **Added**: Memtest entries can now be disabled or permanently removed for real from the Boot Entries tab.
- **Added**: "Add entry" now writes a real custom `menuentry` to `/etc/grub.d/40_custom`.
- **Changed**: Recovery-mode and other-OS entries are managed only from "General settings" now, removing a redundant duplicate control.

## 🆕 New in version 2.0.2-5 (July 7, 2026)

- **Build**: Build dependency `python3-all` replaced with `python3`.

## 🆕 New in version 2.0.2-4 (May 22, 2026)

- **Docs**: Aligned Tyson legacy 1.x release timeline to correct July 2025 timestamps and cleaned up obsolete metadata tags in metainfo.xml.

## 🆕 New in version 2.0.2-3 (May 18, 2026)

- **Documentation**: Historical correction of Tyron legacy versioning — the August 2025 package mislabelled as `1.0.4` is now correctly documented as `1.0.9`; the original Tyron `1.0.4` from May 2025 has been restored to the changelog (its `.deb` was overwritten and lost by the packaging error).

## 🆕 New in version 2.0.2-2 (April 30, 2026)

- **UI**: Simplified the footer UI text to match the modern Mainuan standard layout (`XFCE · X11`).

## 🆕 New in version 2.0.2-1 (March 21, 2026)

### Added
- **F1 shortcut**: Press F1 to open the About dialog.
- **GNOME menu About**: Application menu About action now opens the actual dialog.
- **Ctrl+Shift+Tab**: Keyboard shortcut to navigate to the previous tab.

### Fixed
- Notebook tab labels no longer appear orange in inactive tabs.
- Icon files renamed from `com.mainuan` to `org.mainuan` for naming consistency.
- Duplicate `GTK_THEME` environment variable entry in the pkexec launcher eliminated.
- Wrong i18n domain corrected to `mainuan-grub-editor`.
- Inline `import subprocess` statements moved to module level.
- Debug print statement removed from production code.

### Improved
- CSS architecture refactored to `base.css` + `dark.css`/`light.css` (color variables only).
- About dialog appearance standardized across XFCE, GNOME and KDE.

## 🆕 New in version 2.0.1 (March 7, 2026)

### Fixes
- **Robust Theme Management**: Prevents system conflicts by reliably disabling background defaults from Debian and Mainuan scripts.
- **Cache Cleanup**: Solves the "invalid argument" GRUB crash by deleting stale progressive JPEG `.background_cache` files.
- **Smart UI Automation**: Automatically grays out and unchecks the "Show boot menu" option when Timeout is exactly 0.

## 🆕 New in version 2.0.0 (January 10, 2026)

### New Features
- **Complete Internationalization** - Native support for 8 languages (ES, EN, DE, FR, IT, PT, RO, RU)
- **Smart Light/Dark Theme Detection** - Compatible with GNOME, KDE and XFCE
- **Improved Desktop & Environment Detection** - Accurate detection of Wayland/X11 and DE
- **Refined UI Layout** - Compact two-column design for advanced options
- **GRUB Theme Installer/Remover** - Support for .tar.gz, .zip, .tar.xz
- **UUID Option** - Control of GRUB_DISABLE_LINUX_UUID
- **Expanded Resolutions** - 16:9, 16:10, 4:3 and 4K

### Improvements
- GRUB configuration without duplicate lines
- Colors loaded from real GRUB values
- Theme preview with jpg/png support

### Documentation
- Man page added
- Debian Copyright added
- Metainfo updated in 8 languages

---

## Legacy 1.x — Tyron branch (XFCE + X11)

### 🆕 New in version 1.0.9 — August 3, 2025 *(Tyron only)*

> ⚠️ Published under the label `1.0.4` by packaging error — correct version is `1.0.9`.

- Complete internationalisation: 8 languages via `translations/strings.py` and `app_locale/`.
- Full Tyron desktop integration with window manager and taskbars.
- Massive optimisation of screenshots and icon assets; multi-size icon packaging (48×48, 64×64, 128×128).
- Authorship updated to David Caixinha &lt;tugatechlab.contacto@gmail.com&gt; in `setup.py`.

### 🆕 New in version 1.0.8 — May 8, 2025 *(Tyron only)*

- Stability and compatibility: internal fixes and improvements for the Tyron environment.

### 🆕 New in version 1.0.7 — May 8, 2025 *(Tyron only)*

- Application ID restored to `com.mainuan.grubeditor`.
- Strings module relocated back to `translations/strings.py`.

### 🆕 New in version 1.0.6 — May 7, 2025 *(Tyron only)*

- Minor UI and compatibility fixes for the Tyron build.

### 🆕 New in version 1.0.5 — May 7, 2025 *(Tyron only)*

- Internal cleanup and minor corrections for the Tyron build.

### 🆕 New in version 1.0.4 — May 7, 2025 *(Tyron only)*

> ⚠️ Package lost — the `.deb` was overwritten when the August 2025 packaging error reused this version number (see 1.0.9).

### 🆕 New in version 1.0.3 — May 6, 2025 *(Tyron only)*

- Metainfo updated for AppStream/DEP-11 compliance.
- Screenshots renamed to `screenshot1.png`, `screenshot2.png`, etc.
- Minor documentation and metadata improvements. No functional changes.

### 🆕 New in version 1.0.2 — May 5, 2025 *(Tyron only)*

- UI strings extracted to `strings.py` in the project root.
- Application ID changed to `com.mainuangrubeditor`.

### 🆕 New in version 1.0.1 — April 25, 2025 *(Tyron only)*

- More robust TTF/OTF → PF2 font conversion pipeline.
- Improved error handling during font installation.
- More responsive UI under heavy operations.
- Fixed TTF/OTF conversion errors, permission issues in `/boot/grub/fonts/`, UI crashes and memory errors.

### 🆕 New in version 1.0.0 — April 13, 2025 *(Tyron only)*

- Initial Tyron release — complete GTK3 GRUB2 editor.
- Theme management, font conversion, background configuration, custom boot entries.
- Advanced kernel configuration, automatic OS detection, automatic backup system.
- Secure `update-grub` integration, keyboard shortcuts and validation.

---

## Legacy 1.x — Tyson branch (Plasma 6 + Wayland)

### 🆕 New in version 1.0.5 — July 27, 2025 *(Tyson only)*

- Metainfo finalized for AppStream/DEP-11 compliance.
- Program icons added in 48×48, 64×64 and 128×128 for software center compatibility.
- Program icon updated.

### 🆕 New in version 1.0.4 — July 15, 2025 *(Tyson only)*

- Metainfo finalized for AppStream/DEP-11 compliance.
- Program icons added in 48×48, 64×64 and 128×128 for software center compatibility.
- Minor structure and tag improvements.

### 🆕 New in version 1.0.3 — July 14, 2025 *(Tyson only)*

- Final metainfo corrections to ensure full visibility in software centers.
- Validated across Plasma Discover, GNOME Software and other AppStream-compatible centers.

### 🆕 New in version 1.0.2 — June 24, 2025 *(Tyson only)*

- Dynamic translation system with on-demand loading.
- 8 languages fully supported (ES, EN, FR, PT, DE, IT, RU, RO) with automatic `$LANG` detection.
- New `translations/` module structure with centralised `strings.py` and per-language `locales/`.
- Plasma Discover compatibility via updated AppStream metainfo.

### 🆕 New in version 1.0.1 — June 15, 2025 *(Tyson only)*

- More robust TTF/OTF → PF2 font conversion pipeline.
- Improved error handling during font installation.
- More responsive UI under heavy operations.
- Fixed TTF/OTF conversion errors, permission issues in `/boot/grub/fonts/`, UI crashes and memory errors.

### 🆕 New in version 1.0.0 — May 9, 2025 *(Tyson only)*

- Initial Tyson release — complete GTK3 GRUB2 editor.
- Theme management, font conversion, background configuration, custom boot entries.
- Advanced kernel configuration, automatic OS detection, automatic backup system.
- Secure `update-grub` integration, keyboard shortcuts and validation.
