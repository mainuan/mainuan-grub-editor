"""
Boot Entries View for Mainuan Grub Editor.
FIXED: Compact table styling matching other Mainuan apps.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango

from core.i18n_manager import _


class BootEntriesView(Gtk.Box):
    """Boot entries management tab - compact styling."""
    
    def __init__(self, parent_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.parent_window = parent_window
        self.grub_manager = parent_window.grub_manager
        self.entries = []

        # Compact margins
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        
        self._create_ui()
        self._load_entries()
        
    def _create_ui(self):
        """Create compact UI."""
        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        # TreeView with compact styling
        self.store = Gtk.ListStore(int, str, str, str, bool)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_headers_visible(True)
        self.tree.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        
        # CRITICAL: Remove card class, it adds too much padding
        # self.tree.get_style_context().add_class('mainuan-card')  # ← REMOVED
        
        # Column: # (Number)
        renderer_num = Gtk.CellRendererText()
        renderer_num.set_padding(4, 2)  # Compact padding
        col_num = Gtk.TreeViewColumn("#", renderer_num, text=0)
        col_num.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_num.set_fixed_width(40)
        col_num.set_resizable(False)
        self.tree.append_column(col_num)
        
        # Column: Name
        renderer_name = Gtk.CellRendererText()
        renderer_name.set_padding(4, 2)
        col_name = Gtk.TreeViewColumn(_("Name:"), renderer_name, text=1)
        col_name.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_name.set_fixed_width(400)
        col_name.set_resizable(True)
        col_name.set_expand(True)
        col_name.set_cell_data_func(renderer_name, self._dim_if_disabled)
        self.tree.append_column(col_name)

        # Column: Type
        renderer_type = Gtk.CellRendererText()
        renderer_type.set_padding(4, 2)
        col_type = Gtk.TreeViewColumn(_("Type:"), renderer_type, text=2)
        col_type.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_type.set_fixed_width(100)
        col_type.set_resizable(True)
        col_type.set_cell_data_func(renderer_type, self._dim_if_disabled)
        self.tree.append_column(col_type)
        
        # Column: Path
        renderer_path = Gtk.CellRendererText()
        renderer_path.set_padding(4, 2)
        col_path = Gtk.TreeViewColumn(_("Path"), renderer_path, text=3)
        col_path.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_path.set_fixed_width(150)
        col_path.set_resizable(True)
        self.tree.append_column(col_path)
        
        # Column: Enabled (checkbox) - COMPACT
        renderer_enabled = Gtk.CellRendererToggle()
        renderer_enabled.set_padding(4, 2)
        renderer_enabled.connect("toggled", self._on_entry_toggled)
        col_enabled = Gtk.TreeViewColumn(_("Enabled"), renderer_enabled, active=4)
        col_enabled.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_enabled.set_fixed_width(80)
        col_enabled.set_resizable(True)
        self.tree.append_column(col_enabled)
        
        scrolled.add(self.tree)
        self.pack_start(scrolled, True, True, 0)
        
        # Button bar - compact spacing
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_top(5)
        
        add_btn = Gtk.Button(label=_("Add entry"))
        add_btn.get_style_context().add_class('suggested-action')
        add_btn.connect('clicked', self._on_add_entry)
        button_box.pack_start(add_btn, False, False, 0)
        
        remove_btn = Gtk.Button(label=_("Remove entry"))
        remove_btn.get_style_context().add_class('destructive-action')
        remove_btn.connect('clicked', self._on_remove_entry)
        button_box.pack_start(remove_btn, False, False, 0)
        
        self.pack_start(button_box, False, False, 0)
        
        self.show_all()
    
    def _load_entries(self):
        """Load boot entries from GRUB configuration."""
        self.store.clear()

        # Parse grub.cfg for menu entries. Recovery and os-prober entries
        # are excluded here: they're already managed as a category in
        # "General settings" (GRUB_DISABLE_RECOVERY / GRUB_DISABLE_OS_PROBER),
        # so keeping them here too would just be a second, redundant control
        # for the same switch.
        entries = [
            e for e in self.grub_manager.get_menu_entries()
            if self._entry_category(e) not in ('recovery', 'os-prober')
        ]
        self.entries = entries

        for i, entry in enumerate(entries):
            # Show hierarchical name in the list for clarity
            full_name = entry.get('name', _('Entry {}').format(i))
            if '>' in full_name:
                display_name = full_name.replace('>', ' » ')
            else:
                display_name = entry.get('display_name', full_name)
                
            self.store.append([
                i,
                display_name,
                entry.get('type', _('system')),
                entry.get('path', ''),
                entry.get('enabled', True)
            ])
    
    @staticmethod
    def _memtest_binary_for_title(display_name):
        """Return the /boot binary filename for a memtest entry title, or None."""
        title = display_name.lower()
        if 'mt86+x64' in title or 'x86_64' in title:
            return 'mt86+x64'
        if 'mt86+ia32' in title or 'ia32' in title:
            return 'mt86+ia32'
        return None

    def _entry_category(self, entry):
        """Classify an entry so toggling/removing it can pick the right action."""
        # Checked first: a user-written title could contain "x86_64" and would
        # otherwise be mistaken for a memtest entry.
        if entry.get('source_script') == '40_custom':
            return 'custom'
        if self._memtest_binary_for_title(entry.get('display_name', '')):
            return 'memtest'
        if 'recovery' in entry.get('display_name', '').lower():
            return 'recovery'
        if entry.get('source_script') == '30_os-prober':
            return 'os-prober'
        if entry.get('source_script') == '10_linux':
            return 'kernel'
        return 'other'

    def _dim_if_disabled(self, column, cell, model, treeiter, data=None):
        """Gray out rows for entries that are currently disabled."""
        enabled = model[treeiter][4]
        cell.set_property('sensitive', enabled)

    def _ask_update_grub(self):
        """Ask the user whether to run update-grub now, and run it if so."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Run update-grub now to apply changes?")
        )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            self.grub_manager.update_grub()

    def _show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=_("Error")
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def _show_kernel_entry_dialog(self):
        """Explain why kernel/OS entries can't be toggled or removed here."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("Not supported")
        )
        dialog.format_secondary_text(
            _("This entry belongs to an installed kernel or operating system. "
              "GRUB regenerates it automatically from what's installed on your "
              "disk, so it can't be disabled or removed individually here — "
              "you would need to uninstall the kernel or operating system "
              "itself.")
        )
        dialog.run()
        dialog.destroy()

    def _on_entry_toggled(self, renderer, path):
        """Toggle entry enabled state, routed by category."""
        row_index = int(path)
        entry = self.entries[row_index] if row_index < len(self.entries) else None
        if not entry:
            return

        title = entry.get('display_name', '')
        currently_enabled = self.store[path][4]
        new_state = not currently_enabled
        category = self._entry_category(entry)

        if category in ('memtest', 'custom'):
            script = entry.get('source_script')
            if self.grub_manager.set_grub_d_entry_enabled(script, title, new_state):
                self._ask_update_grub()
                self._load_entries()
            else:
                self._show_error_dialog(_("Could not update the entry"))
        else:
            self._show_kernel_entry_dialog()
            self._load_entries()

    def _on_add_entry(self, button):
        """Add a custom boot entry, written to /etc/grub.d/40_custom."""
        dialog = Gtk.Dialog(
            title=_("Add Entry"),
            transient_for=self.parent_window,
            flags=Gtk.DialogFlags.MODAL,
        )
        dialog.add_buttons(
            _("Cancel"), Gtk.ResponseType.CANCEL,
            _("Save"), Gtk.ResponseType.OK
        )
        dialog.set_default_size(560, 320)

        content = dialog.get_content_area()
        content.set_spacing(8)
        content.set_margin_start(10)
        content.set_margin_end(10)
        content.set_margin_top(10)
        content.set_margin_bottom(10)

        label = Gtk.Label(label=_(
            "Write the raw GRUB menuentry block (this is appended to "
            "/etc/grub.d/40_custom):"
        ))
        label.set_halign(Gtk.Align.START)
        label.set_line_wrap(True)
        content.pack_start(label, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        text_view = Gtk.TextView()
        text_view.set_monospace(True)
        buffer = text_view.get_buffer()
        buffer.set_text(
            "menuentry 'My custom entry' {\n"
            "\n"
            "}\n"
        )
        scrolled.add(text_view)
        content.pack_start(scrolled, True, True, 0)

        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            start, end = buffer.get_bounds()
            text = buffer.get_text(start, end, False)
            dialog.destroy()
            if text.strip():
                if self.grub_manager.append_custom_entry(text):
                    self._ask_update_grub()
                    self._load_entries()
                else:
                    self._show_error_dialog(_("Failed to save the custom entry"))
        else:
            dialog.destroy()

    def _on_remove_entry(self, button):
        """Remove selected boot entry, routed by category."""
        selection = self.tree.get_selection()
        model, treeiter = selection.get_selected()
        if not treeiter:
            return

        row_index = model[treeiter][0]
        entry = self.entries[row_index] if row_index < len(self.entries) else None
        if not entry:
            return

        category = self._entry_category(entry)

        if category == 'memtest':
            binary = self._memtest_binary_for_title(entry.get('display_name', ''))
            dialog = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=_("Remove Entry")
            )
            dialog.format_secondary_text(
                _("Delete '{}' from /boot? This also removes its serial-console "
                  "variant, since both share the same file.").format(binary)
            )
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                if self.grub_manager.delete_memtest_binary(binary):
                    self._ask_update_grub()
                    self._load_entries()
        elif category == 'custom':
            title = entry.get('display_name', '')
            dialog = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=_("Remove Entry")
            )
            dialog.format_secondary_text(
                _("Delete '{}' from /etc/grub.d/40_custom? This cannot be "
                  "undone.").format(title)
            )
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                if self.grub_manager.delete_grub_d_entry('40_custom', title):
                    self._ask_update_grub()
                    self._load_entries()
                else:
                    self._show_error_dialog(_("Could not update the entry"))
        else:
            self._show_kernel_entry_dialog()
