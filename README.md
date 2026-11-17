# Mainuan GRUB Editor

[![License: GPL-3.0+](https://img.shields.io/badge/License-GPL--3.0%2B-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-2.0.2--8-green.svg)]()

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

## 🛠️ Requirements

- Python 3.8+
- GTK 3.0
- GRUB 2.x installed
- Dependencies: PyGObject (GTK 3), pkexec, unzip

## 📥 Installation

```bash
# System dependencies
sudo apt install python3-gi gir1.2-gtk-3.0 grub2-common pkexec unzip

# Python installation
pip3 install -r requirements.txt

# Manual installation
sudo python3 setup.py install

# Install desktop files and icons
# (setup.py generates the translated files in build/metadata/; requires gettext)
sudo cp build/metadata/org.mainuan.grubeditor.desktop /usr/share/applications/
sudo cp assets/icons/org.mainuan.grubeditor.png /usr/share/icons/hicolor/128x128/apps/
sudo cp build/metadata/org.mainuan.grubeditor.metainfo.xml /usr/share/metainfo/
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

The package is built from the standard `debian/` directory (debhelper) on
Kubuntu/Ubuntu 26.04:

```bash
sudo apt build-dep ./
dpkg-buildpackage -us -uc -b      # writes ../mainuan-grub-editor_<version>_all.deb
sudo apt install ../mainuan-grub-editor_*_all.deb
```

The package version comes from `debian/changelog`. The GitHub Actions
workflow (`.github/workflows/ci.yml`) builds and tests the package on every
pull request and push, checks it with lintian, installs and removes it in a
clean Ubuntu 26.04 container, and publishes a release only for a `v*` tag.

## 🌊 Wayland Compatibility

The application is **fully compatible with Wayland** and works perfectly on:

- **Plasma 6 + Wayland** (Mainuan Linux)
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

- ✅ **Mainuan Linux** (Plasma 6 + Wayland)

## 📄 License

This project is licensed under [GPL-3.0+](https://www.gnu.org/licenses/gpl-3.0.html).

## 👥 Developers

Developed by David Caixinha




