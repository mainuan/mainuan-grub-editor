"""
User interface module for Mainuan Grub Editor.
Contains all GTK-based UI components, windows, tabs, widgets, and dialogs.
"""

from core.application import APP_VERSION

# UI module information
__version__ = APP_VERSION
__author__ = "David Caixinha"

# UI Constants
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# CSS Classes
CSS_CLASSES = {
    'window': 'mainuan-window', # repo-selector uses mainuan-window, welcome uses mainuan-welcome-window. Sticking to generic or standard.
    'content': 'mainuan-content',
    'tab': 'mainuan-tab',
    'card': 'mainuan-card',
    'button_install': 'mainuan-button-install',
    'button_uninstall': 'mainuan-button-uninstall',
    'button_primary': 'mainuan-button-primary',
    'status_label': 'mainuan-status-label',
    'progress_bar': 'mainuan-progress-bar',
    'icon_large': 'mainuan-icon-large',
    'icon_medium': 'mainuan-icon-medium',
    'icon_small': 'mainuan-icon-small',
    'separator': 'mainuan-separator',
    'welcome_title': 'mainuan-welcome-title',
    'welcome_subtitle': 'mainuan-welcome-subtitle',
    'software_grid': 'mainuan-software-grid',
    'software_item': 'mainuan-software-item',
    'hardware_info': 'mainuan-hardware-info'
}
