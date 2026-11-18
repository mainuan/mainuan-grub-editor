#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def generate_translated_metadata():
    """Desktop entry and AppStream metainfo are templates (*.in) translated
    from the gettext catalogs, as in packaging/build-data.sh."""
    import re
    import subprocess
    import tempfile
    out_dir = os.path.join(HERE, 'build', 'metadata')
    os.makedirs(out_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as po_dir:
        with open(os.path.join(HERE, 'po', 'LINGUAS'), encoding='utf-8') as handle:
            languages = [line.strip() for line in handle if line.strip() and not line.startswith('#')]
        with open(os.path.join(po_dir, 'LINGUAS'), 'w', encoding='utf-8') as handle:
            handle.write('\n'.join(languages) + '\n')
        for lang in languages:
            os.symlink(os.path.join(HERE, 'locale', lang, 'LC_MESSAGES', 'mainuan-grub-editor.po'),
                       os.path.join(po_dir, lang + '.po'))
        desktop = os.path.join(out_dir, 'org.mainuan.grubeditor.desktop')
        metainfo = os.path.join(out_dir, 'org.mainuan.grubeditor.metainfo.xml')
        subprocess.run(['msgfmt', '--desktop', '--template',
                        os.path.join(HERE, 'assets', 'org.mainuan.grubeditor.desktop.in'),
                        '-d', po_dir, '-o', desktop], check=True)
        subprocess.run(['msgfmt', '--xml', '--template',
                        os.path.join(HERE, 'debian', 'org.mainuan.grubeditor.metainfo.xml.in'),
                        '-d', po_dir, '-o', metainfo], check=True)
    with open(metainfo, encoding='utf-8') as handle:
        text = handle.read()
    # AppStream matches POSIX locale names (pt_BR), msgfmt writes BCP 47 (pt-BR).
    text = re.sub(r'xml:lang="([a-z]{2,3})-(?:Hans-|Hant-)?([A-Z]{2})"', r'xml:lang="\1_\2"', text)
    with open(metainfo, 'w', encoding='utf-8') as handle:
        handle.write(text)
    return desktop, metainfo


DESKTOP_FILE, METAINFO_FILE = generate_translated_metadata()

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return 'Official GRUB graphical editor for Mainuan Linux'

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'PyGObject>=3.36.0',
        'pycairo>=1.16.2',
        'python-xlib>=0.27',
        'polib>=1.1.0',
        'python-dbus>=1.2.16',
        'Pillow>=8.0.0'
    ]

setup(
    name='mainuan-grub-editor',
    version='2.1.0',
    description='Official GRUB graphical editor for Mainuan Linux',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='David Caixinha',
    author_email='tugatechlab.contacto@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'mainuan_grub_editor': [
            'translations/locales/*.py',
            'assets/icons/*.png',
            'assets/*.desktop',
            'debian/*.xml',
            'debian/control',
        ],
    },
    install_requires=read_requirements(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'mainuan-grub-editor=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: System :: Boot',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Environment :: X11 Applications :: GTK',
        'Natural Language :: Portuguese',
        'Natural Language :: Brazil',
        'Natural Language :: Spanish',
        'Natural Language :: English',
        'Natural Language :: French',
        'Natural Language :: German',
        'Natural Language :: Italian',
        'Natural Language :: Russian',
        'Natural Language :: Romanian',
    ],
    keywords='grub bootloader configuration linux mainuan internationalization i18n',
    zip_safe=False,
    data_files=[
        ('share/applications', [os.path.relpath(DESKTOP_FILE, HERE)]),
        ('share/icons/hicolor/128x128/apps', ['assets/icons/org.mainuan.grubeditor.png']),
        ('share/metainfo', [os.path.relpath(METAINFO_FILE, HERE)]),
    ],
)
