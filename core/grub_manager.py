"""
GRUB Manager module for Mainuan Grub Editor.
Handles reading and writing configurations to /etc/default/grub,
interacting with grub-mkconfig, and managing grub-btrfs integration.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import log_info, log_error, log_warning
from core.i18n_manager import _


class GrubManager:
    """
    Manages GRUB configuration and system interactions.
    """
    
    GRUB_DEFAULT_PATH = "/etc/default/grub"
    
    def __init__(self):
        """Initialize the GRUB manager."""
        self.config_path = Path(self.GRUB_DEFAULT_PATH)
        self.config_data = {}
        
    def read_config(self) -> Dict[str, str]:
        """
        Read the current GRUB configuration.
        
        Returns:
            Dictionary with configuration keys and values
        """
        self.config_data = {}
        
        if not self.config_path.exists():
            log_error(_("GRUB config not found at {}").format(self.config_path))
            return {}
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"').strip("'")
                        self.config_data[key.strip()] = value
                        
            return self.config_data
        except Exception as e:
            log_error(_("Error reading GRUB config: {}").format(e))
            return {}
            
    def save_config(self, new_config: Dict[str, str]) -> bool:
        """
        Save configuration to /etc/default/grub.
        Modifies existing keys in place. Deletes keys with empty values.
        Only adds new keys if they don't exist.
        """
        import os
        
        try:
            # Read file
            lines = []
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # Build result while tracking what we've processed
            result_lines = []
            processed_keys = set()
            
            for line in lines:
                stripped = line.strip()
                
                # Skip lines that are our own "Modified by" comments
                if '# Modified by Mainuan GRUB Editor' in stripped:
                    continue
                # Skip commented-out lines we previously created
                if '# Cleared by Mainuan' in stripped or '# Removed by Mainuan' in stripped:
                    continue
                
                # Check if this is a commented key=value that we want to uncomment
                if stripped.startswith('#') and '=' in stripped:
                    # Extract key from commented line (e.g., "#GRUB_TIMEOUT_STYLE=hidden")
                    uncommented = stripped.lstrip('#').strip()
                    key = uncommented.split('=')[0].strip()
                    
                    if key in new_config and key not in processed_keys:
                        value = new_config[key]
                        processed_keys.add(key)
                        
                        # Empty value = keep it commented (or delete)
                        if value == '':
                            result_lines.append(line)  # Keep commented
                        else:
                            # Uncomment and set new value
                            if ' ' in value:
                                value = f'"{value}"'
                            result_lines.append(f'{key}={value}\n')
                        continue
                    else:
                        # Not a key we're modifying, keep original commented line
                        result_lines.append(line)
                        continue
                
                # Keep other comments and empty lines
                if not stripped or stripped.startswith('#'):
                    result_lines.append(line)
                    continue
                
                # Parse uncommented key=value lines
                if '=' in stripped:
                    key = stripped.split('=')[0].strip()
                    
                    # Skip if we already processed this key (handle duplicates)
                    if key in processed_keys:
                        continue
                    
                    if key in new_config:
                        value = new_config[key]
                        processed_keys.add(key)
                        
                        # Empty value = delete the line (don't add it to result)
                        if value == '':
                            continue
                        
                        # Write the updated value
                        if ' ' in value:
                            value = f'"{value}"'
                        result_lines.append(f'{key}={value}\n')
                    else:
                        # Key not in our config, keep original line
                        result_lines.append(line)
                else:
                    result_lines.append(line)
            
            # Add only truly new keys (don't exist in file and have non-empty values)
            new_keys = []
            for key, value in new_config.items():
                if key not in processed_keys and value != '':
                    if ' ' in value:
                        value = f'"{value}"'
                    new_keys.append(f'{key}={value}\n')
            
            # Remove trailing empty lines
            while result_lines and result_lines[-1].strip() == '':
                result_lines.pop()
            
            if new_keys:
                # Add a single blank line before our section if file doesn't end with one
                if result_lines and result_lines[-1].strip() != '':
                    result_lines.append('\n')
                result_lines.append('# Modified by Mainuan GRUB Editor\n')
                result_lines.extend(new_keys)
            
            # Write file
            is_root = os.geteuid() == 0
            if is_root:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    f.writelines(result_lines)
                self.read_config()  # Reload to keep state in sync
                log_info(_("Successfully saved config to {path}").format(path=self.config_path))
                return True
            else:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.grub') as tmp:
                    tmp.writelines(result_lines)
                    tmp_path = tmp.name
                
                result = subprocess.run(['pkexec', 'cp', tmp_path, str(self.config_path)], 
                                        capture_output=True, text=True)
                os.unlink(tmp_path)
                
                if result.returncode == 0:
                    self.read_config()  # Reload to keep state in sync
                    log_info(_("Successfully saved config using pkexec"))
                    return True
                else:
                    log_error(_("Failed to save config: {err}").format(err=result.stderr))
                    return False
                    
        except Exception as e:
            log_error(_("Error saving GRUB config: {err}").format(err=e))
            return False


    def remove_config_key(self, key: str) -> bool:
        """
        Remove a configuration key from /etc/default/grub.
        The line is commented out rather than deleted to preserve structure.
        """
        import os
        
        try:
            lines = []
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            updated_lines = []
            found = False
            for line in lines:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('#') and '=' in line_stripped:
                    line_key = line_stripped.split('=')[0].strip()
                    if line_key == key:
                        # Delete the line by not adding it to result
                        found = True
                        continue
                updated_lines.append(line)
            
            if not found:
                return True  # Key already doesn't exist
            
            is_root = os.geteuid() == 0
            if is_root:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                log_info(_("Removed key {key} from config").format(key=key))
                return True
            else:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.grub') as tmp:
                    tmp.writelines(updated_lines)
                    tmp_path = tmp.name
                cmd = ['pkexec', 'cp', tmp_path, str(self.config_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                os.unlink(tmp_path)
                if result.returncode == 0:
                    log_info(_("Removed key {key} from config").format(key=key))
                    return True
                return False
                
        except Exception as e:
            log_error(_("Error removing config key: {err}").format(err=e))
            return False

    def set_theme_scripts_active(self, active: bool) -> bool:
        """
        Enable/Disable the GRUB theme scripts (05_debian_theme and 05_mainuan_theme).
        This prevents conflicts with our custom settings and stops
        the scripts from injecting unwanted background images.
        """
        paths = [
            "/etc/grub.d/05_debian_theme",
            "/etc/grub.d/05_mainuan_theme",
        ]
        
        is_root = os.geteuid() == 0
        mode = '+x' if active else '-x'
        success = True
        
        for path in paths:
            if not os.path.exists(path):
                continue
            try:
                if is_root:
                    subprocess.run(['chmod', mode, path], check=True)
                else:
                    subprocess.run(['pkexec', 'chmod', mode, path], check=True)
                log_info(_("Set {script} active={active}").format(script=os.path.basename(path), active=active))
            except Exception as e:
                log_error(_("Failed to change {script} permissions: {err}").format(script=os.path.basename(path), err=e))
                success = False
        
        # When disabling, also clean up any cached background images
        if not active:
            self._cleanup_background_cache()
        
        return success

    # Keep backward compatibility
    def set_debian_theme_active(self, active: bool) -> bool:
        """Backward compatibility wrapper."""
        return self.set_theme_scripts_active(active)

    def _cleanup_background_cache(self):
        """
        Remove .background_cache files from /boot/grub/.
        These are created by 05_debian_theme/05_mainuan_theme and can cause
        'invalid argument' errors if the cached image is a progressive JPEG.
        """
        cache_files = [
            "/boot/grub/.background_cache.jpeg",
            "/boot/grub/.background_cache.png",
            "/boot/grub/.background_cache.tga",
            "/boot/grub/.background_cache.jpg",
        ]
        
        is_root = os.geteuid() == 0
        
        for cache_file in cache_files:
            if os.path.exists(cache_file):
                try:
                    if is_root:
                        os.remove(cache_file)
                    else:
                        subprocess.run(['pkexec', 'rm', '-f', cache_file],
                                      capture_output=True, text=True)
                    log_info(_("Removed background cache: {path}").format(path=cache_file))
                except Exception as e:
                    log_warning(_("Failed to remove cache {path}: {err}").format(path=cache_file, err=e))

    def save_custom_ui_settings(self, bg_path: str, color_normal: str, color_highlight: str) -> bool:
        """
        Save custom appearance settings to /boot/grub/custom.cfg
        and clean up conflicting settings in /etc/default/grub.
        """
        # 1. Disable conflicting theme in /etc/default/grub
        # Fix: Save BACKGROUND here so 05_mainuan_theme can see it.
        clean_config = {
            'GRUB_THEME': '',
            'GRUB_BACKGROUND': bg_path,   # Save background here
            'GRUB_COLOR_NORMAL': '',      # Remove from here (managed in custom.cfg)
            'GRUB_COLOR_HIGHLIGHT': '',   # Remove from here (managed in custom.cfg)
        }
        if not self.save_config(clean_config):
            return False
            
        # 2. Write to custom.cfg
        # Fix: Only write colors here. Background is now in default/grub.
        content = [
            "# Generated by Mainuan GRUB Editor",
            "# Custom appearance settings",
            ""
        ]
        
        if color_normal:
            content.append(f"set color_normal={color_normal}")
            
        if color_highlight:
            content.append(f"set color_highlight={color_highlight}")
            
        content.append("")
        
        if not self._write_custom_cfg("\n".join(content)):
            return False
            
        # 3. Disable theme scripts to prevent override and clean cache
        self.set_theme_scripts_active(False)
        
        return True

    def apply_theme_settings(self, theme_path: str) -> bool:
        """
        Apply a full GRUB theme.
        Sets variable in /etc/default/grub and clears custom.cfg.
        """
        # 1. Set theme in /etc/default/grub and clear standalone colors
        new_config = {
            'GRUB_THEME': theme_path,
            'GRUB_BACKGROUND': '',
            'GRUB_COLOR_NORMAL': '',
            'GRUB_COLOR_HIGHLIGHT': '',
            'GRUB_FONT': '',
        }
        if not self.save_config(new_config):
            return False
            
        # 2. Clear custom.cfg to prevent conflicts
        if not self._write_custom_cfg("# Custom settings cleared by Mainuan GRUB Editor\n"):
            return False
            
        # 3. Disable theme scripts to prevent conflicts
        self.set_theme_scripts_active(False)
        
        return True
        
    def _write_custom_cfg(self, content: str) -> bool:
        """Write content to /boot/grub/custom.cfg"""
        cfg_path = "/boot/grub/custom.cfg"
        try:
            is_root = os.geteuid() == 0
            if is_root:
                with open(cfg_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            else:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cfg') as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                
                # Use tee to write (handles permissions better than cp sometimes for existing root files)
                # or just cp. custom.cfg might not exist.
                # 'cp' is safer to ensure ownership/creation if missing.
                result = subprocess.run(['pkexec', 'cp', tmp_path, cfg_path], 
                                      capture_output=True, text=True)
                os.unlink(tmp_path)
                
                if result.returncode == 0:
                    return True
                else:
                    log_error(_("Failed to write custom.cfg: {err}").format(err=result.stderr))
                    return False
        except Exception as e:
            log_error(_("Error writing custom.cfg: {err}").format(err=e))
            return False

    def update_grub(self) -> bool:
        """
        Run update-grub to apply changes.
        Uses full path and detects if running as root.
        """
        import os
        
        # Check if running as root
        is_root = os.geteuid() == 0
        
        # Find update-grub path
        update_grub_paths = ['/usr/sbin/update-grub', '/sbin/update-grub', 'update-grub']
        update_grub_cmd = None
        for path in update_grub_paths:
            if os.path.exists(path):
                update_grub_cmd = path
                break
        
        if not update_grub_cmd:
            log_error(_("update-grub not found"))
            return False
        
        try:
            if is_root:
                cmd = [update_grub_cmd]
            else:
                cmd = ['pkexec', update_grub_cmd]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                log_info(_("Successfully updated GRUB"))
                return True
            else:
                log_error(_("Failed to update GRUB: {err}").format(err=result.stderr))
                return False
        except Exception as e:
            log_error(_("Error running update-grub: {err}").format(err=e))
            return False        
    
    @property
    def config(self) -> Dict[str, str]:
        """Return current config, loading if needed."""
        if not self.config_data:
            self.read_config()
        return self.config_data
    
    def silent_update_grub(self) -> bool:
        """
        Run update-grub silently.
        Does not use pkexec if already root, otherwise attempts pkexec.
        """
        import os
        is_root = os.geteuid() == 0
        
        update_grub_paths = ['/usr/sbin/update-grub', '/sbin/update-grub', 'update-grub']
        update_grub_cmd = None
        for path in update_grub_paths:
            if os.path.exists(path):
                update_grub_cmd = path
                break
        
        if not update_grub_cmd:
            return False
            
        try:
            cmd = [update_grub_cmd] if is_root else ['pkexec', update_grub_cmd]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def get_menu_entries(self) -> List[Dict]:
        """
        Parse grub.cfg to get menu entries, including submenus.
        Returns a flat list of entries with hierarchical names (e.g. "Submenu > Entry")
        
        Returns:
            List of dictionaries with entry information
        """
        # Return cached entries if available
        if hasattr(self, '_cached_entries') and self._cached_entries:
            return self._cached_entries
            
        entries = []
        grub_cfg = Path("/boot/grub/grub.cfg")
        
        content = ""
        # Try reading directly first
        try:
            with open(grub_cfg, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except PermissionError:
            try:
                result = subprocess.run(['pkexec', 'cat', str(grub_cfg)], 
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    content = result.stdout
            except Exception:
                pass
        except FileNotFoundError:
            return entries
            
        if not content:
            return entries
            
        try:
            import re
            lines = content.splitlines()
            entries = []
            stack = []
            brace_depth = 0
            current_entry = None
            entry_capture_depth = 0
            current_platform = 'efi' if Path('/sys/firmware/efi').exists() else 'pc'
            # Tracks inclusion state of nested `if`/`fi` blocks. GRUB config
            # generators wrap platform-specific entries (e.g. memtest) in
            # `if [ "$grub_platform" = "pc" ] ... fi` blocks for both "pc"
            # and "efi", so a flat scan would list both sets. Only the
            # branch matching the real platform is kept; CPU architecture
            # (grub_cpu) is intentionally NOT filtered, so entries like the
            # ia32 memtest variant stay visible and manageable in the UI.
            # Some GRUB-generated lines pack multiple `if`/`fi` statements on
            # a single line (e.g. "if [ ... ]; then if cpuid -l ; then" and
            # its matching "fi ; fi"), so tokens are scanned left to right
            # instead of assuming one keyword per line.
            if_stack = []
            current_script = None

            def _condition_includes(cond_text: str) -> bool:
                # Only collapse the real pc/efi text duplication. Different
                # CPU architectures (grub_cpu) are kept visible even if they
                # don't match this machine, so entries like the ia32 memtest
                # variant stay manageable (and deletable) from the UI.
                if 'grub_platform' not in cond_text:
                    return True
                include = True
                if re.search(r'grub_platform["\']?\s*=\s*"?x?efi', cond_text):
                    include = include and (current_platform == 'efi')
                if re.search(r'grub_platform["\']?\s*=\s*"?x?pc', cond_text):
                    include = include and (current_platform == 'pc')
                return include

            for line in lines:
                line = line.strip()

                # Track which /etc/grub.d/ script generated the entries that
                # follow, so callers can locate the source of a given entry
                # (e.g. to comment out or delete it).
                m_begin = re.match(r'###\s*BEGIN\s+(\S+)\s*###', line)
                if m_begin:
                    current_script = Path(m_begin.group(1)).name
                    continue
                if re.match(r'###\s*END\s', line):
                    current_script = None
                    continue

                if not line or line.startswith('#'):
                    continue

                # Process if/else/fi tokens left to right (handles several
                # statements packed on one line)
                control_tokens = list(re.finditer(r'\bif\b|\bfi\b|\belse\b', line))
                if control_tokens:
                    for tok in control_tokens:
                        word = tok.group()
                        if word == 'if':
                            rest = line[tok.end():]
                            then_pos = rest.find('then')
                            cond_text = rest[:then_pos] if then_pos != -1 else rest
                            if_stack.append(_condition_includes(cond_text))
                        elif word == 'fi':
                            if if_stack:
                                if_stack.pop()
                        elif word == 'else':
                            if if_stack:
                                if_stack[-1] = not if_stack[-1]
                    continue

                # Skip content inside a platform/arch branch that doesn't match
                if if_stack and not all(if_stack):
                    continue

                # Check for submenu
                m_sub = re.search(r"submenu\s+['\"]([^'\"]+)['\"]", line)
                if m_sub and '{' in line:
                    stack.append(m_sub.group(1))
                    brace_depth += 1
                    continue
                
                # Check for menuentry
                m_ent = re.search(r"menuentry\s+['\"]([^'\"]+)['\"]", line)
                if m_ent and '{' in line:
                    entry_title = m_ent.group(1)
                    # Hierarchical name for GRUB_DEFAULT
                    full_name = ">".join(stack + [entry_title])
                    
                    entry_type = _('system')
                    if 'recovery' in entry_title.lower():
                        entry_type = _('recovery')
                    elif 'memtest' in entry_title.lower() or 'memory test' in entry_title.lower() or 'mt86' in entry_title.lower():
                        entry_type = _('memtest')
                    elif 'uefi' in entry_title.lower() or 'firmware' in entry_title.lower():
                        entry_type = _('firmware')
                        
                    entries.append({
                        'name': full_name,
                        'display_name': entry_title,
                        'type': entry_type,
                        'enabled': True,
                        'source_script': current_script,
                        'path': ''
                    })
                    brace_depth += 1
                    current_entry = entries[-1]
                    entry_capture_depth = brace_depth
                    continue

                # While inside a menuentry's own block, capture the kernel
                # or binary path from its boot command (linux/chainloader/
                # multiboot), so the UI can show what actually gets loaded.
                if current_entry is not None and not current_entry['path']:
                    m_path = re.match(
                        r'(linux(?:16)?|linuxefi|chainloader|multiboot2?)\s+(\S+)', line
                    )
                    if m_path:
                        current_entry['path'] = m_path.group(2)

                # Tracking braces to maintain stack
                if '{' in line:
                    brace_depth += line.count('{')

                if '}' in line:
                    closed_count = line.count('}')
                    for i_b in range(closed_count):
                        # If a submenu level is being closed
                        if len(stack) > 0 and brace_depth == len(stack):
                            stack.pop()
                        if brace_depth > 0:
                            brace_depth -= 1
                    if current_entry is not None and brace_depth < entry_capture_depth:
                        current_entry = None

        except Exception as e:
            log_error(_("Error parsing grub.cfg: {}").format(e))

        # Disabled (commented-out) memtest entries don't appear in grub.cfg
        # at all, so they'd otherwise vanish from the list once toggled off
        # and become impossible to re-enable or delete. Merge them back in
        # from the source script, marked as disabled.
        existing_titles = {e['display_name'] for e in entries}
        for title, script_name in self._scan_disabled_script_titles().items():
            if title not in existing_titles:
                if 'memtest' in script_name:
                    entry_type = _('memtest')
                    title_lower = title.lower()
                    if 'ia32' in title_lower:
                        path = '/mt86+ia32'
                    elif 'x64' in title_lower:
                        path = '/mt86+x64'
                    else:
                        path = ''
                else:
                    entry_type = _('system')
                    path = ''
                entries.append({
                    'name': title,
                    'display_name': title,
                    'type': entry_type,
                    'enabled': False,
                    'source_script': script_name,
                    'path': path
                })

        # Cache the results
        self._cached_entries = entries
        return entries

    def _scan_disabled_script_titles(self) -> Dict[str, str]:
        """
        Read the /etc/grub.d/ scripts this app can toggle (memtest and the
        user-defined 40_custom) directly, not grub.cfg, to find every
        menuentry title they define, whether currently commented out or not.

        Returns:
            Dict mapping entry title -> source script filename, for titles
            that are currently disabled (commented out) in the script.
        """
        import re
        disabled_titles = {}
        grub_d = Path('/etc/grub.d')
        if not grub_d.is_dir():
            return disabled_titles

        script_paths = list(grub_d.glob('*memtest*'))
        custom_path = grub_d / '40_custom'
        if custom_path.exists():
            script_paths.append(custom_path)

        for script_path in script_paths:
            if not script_path.is_file():
                continue
            try:
                content = script_path.read_text(encoding='utf-8')
            except Exception:
                continue

            title_enabled = {}
            for raw_line in content.splitlines():
                core = raw_line.lstrip('#')
                m = re.search(r'menuentry\s+[\'"]([^\'"]+)[\'"]', core)
                if m and '{' in core:
                    title = m.group(1)
                    is_enabled_here = not raw_line.lstrip().startswith('#')
                    title_enabled[title] = title_enabled.get(title, False) or is_enabled_here

            for title, enabled in title_enabled.items():
                if not enabled:
                    disabled_titles[title] = script_path.name

        return disabled_titles

    def delete_memtest_binary(self, filename: str) -> bool:
        """
        Delete a memtest86+ binary from /boot. Removing it makes the
        /etc/grub.d/20_memtest86+ script stop emitting the menuentries
        built from it (both the normal and serial-console variants) the
        next time update-grub runs.

        Args:
            filename: binary name, e.g. "mt86+x64" or "mt86+ia32"

        Returns:
            True if the binary was deleted (or already absent).
        """
        if not filename.startswith('mt86+') or '/' in filename:
            log_error(_("Refusing to delete unexpected file: {}").format(filename))
            return False

        boot_path = Path('/boot') / filename
        try:
            if boot_path.exists():
                boot_path.unlink()
            self._cached_entries = None
            return True
        except Exception as e:
            log_error(_("Could not delete {}: {}").format(boot_path, e))
            return False

    def append_custom_entry(self, menuentry_text: str) -> bool:
        """
        Append a raw menuentry block to /etc/grub.d/40_custom, the file
        GRUB itself reserves for user-defined entries.

        Args:
            menuentry_text: raw GRUB script text (e.g. a full menuentry {...} block)

        Returns:
            True on success.
        """
        custom_path = Path('/etc/grub.d/40_custom')
        try:
            content = custom_path.read_text(encoding='utf-8') if custom_path.exists() else ''
            if not content.endswith('\n'):
                content += '\n'
            content += '\n' + menuentry_text.strip() + '\n'
            custom_path.write_text(content, encoding='utf-8')
            self._cached_entries = None
            return True
        except Exception as e:
            log_error(_("Could not write to {}: {}").format(custom_path, e))
            return False

    def set_grub_d_entry_enabled(self, script_name: str, entry_title: str, enabled: bool) -> bool:
        """
        Comment out (disable) or uncomment (re-enable) a specific menuentry
        block inside a /etc/grub.d/ script, matched by its title. GRUB
        ignores lines starting with '#', so a fully-commented block simply
        stops appearing after the next update-grub.

        Args:
            script_name: basename of the script, e.g. "20_memtest86+"
            entry_title: exact menuentry title to locate
            enabled: True to uncomment, False to comment out

        Returns:
            True if the block was found and updated.
        """
        import re
        script_path = Path('/etc/grub.d') / script_name

        try:
            original_lines = script_path.read_text(encoding='utf-8').splitlines(keepends=True)
        except Exception as e:
            log_error(_("Could not read {}: {}").format(script_path, e))
            return False

        result_lines = []
        depth = 0
        in_target = False
        found = False
        title_pattern = re.compile(r'menuentry\s+[\'"]' + re.escape(entry_title) + r'[\'"]')

        for line in original_lines:
            core = line.lstrip('#')
            if not in_target:
                if title_pattern.search(core) and '{' in core:
                    in_target = True
                    found = True
                    depth = core.count('{') - core.count('}')
                    result_lines.append(('#' + core) if not enabled else core)
                    if depth <= 0:
                        in_target = False
                    continue
                result_lines.append(line)
                continue

            depth += core.count('{') - core.count('}')
            result_lines.append(('#' + core) if not enabled else core)
            if depth <= 0:
                in_target = False

        if not found:
            log_warning(_("Entry '{}' not found in {}").format(entry_title, script_path))
            return False

        try:
            script_path.write_text(''.join(result_lines), encoding='utf-8')
            self._cached_entries = None
            return True
        except Exception as e:
            log_error(_("Could not write {}: {}").format(script_path, e))
            return False

    def delete_grub_d_entry(self, script_name: str, entry_title: str) -> bool:
        """
        Delete a whole menuentry block from a /etc/grub.d/ script, matched by
        its title. Used for the user-defined entries in 40_custom: they are
        written by this app, so they're the only ones it can safely remove.
        Kernel and OS entries are regenerated from the disk and are not
        deletable this way.

        Args:
            script_name: basename of the script, e.g. "40_custom"
            entry_title: exact menuentry title to locate

        Returns:
            True if the block was found and removed.
        """
        import re
        script_path = Path('/etc/grub.d') / script_name

        try:
            original_lines = script_path.read_text(encoding='utf-8').splitlines(keepends=True)
        except Exception as e:
            log_error(_("Could not read {}: {}").format(script_path, e))
            return False

        result_lines = []
        depth = 0
        in_target = False
        found = False
        title_pattern = re.compile(r'menuentry\s+[\'"]' + re.escape(entry_title) + r'[\'"]')

        for line in original_lines:
            # Commented-out blocks are matched too, so a disabled entry can
            # still be removed instead of staying in the file forever.
            core = line.lstrip('#')
            if not in_target:
                if title_pattern.search(core) and '{' in core:
                    in_target = True
                    found = True
                    depth = core.count('{') - core.count('}')
                    if depth <= 0:
                        in_target = False
                    continue
                result_lines.append(line)
                continue

            depth += core.count('{') - core.count('}')
            if depth <= 0:
                in_target = False

        if not found:
            log_warning(_("Entry '{}' not found in {}").format(entry_title, script_path))
            return False

        try:
            script_path.write_text(''.join(result_lines), encoding='utf-8')
            self._cached_entries = None
            return True
        except Exception as e:
            log_error(_("Could not write {}: {}").format(script_path, e))
            return False

    def get_available_themes(self) -> List[str]:
        """
        Get list of installed GRUB themes.
        
        Returns:
            List of theme names
        """
        themes = []
        themes_dir = Path("/boot/grub/themes")
        
        if themes_dir.exists():
            for item in themes_dir.iterdir():
                if item.is_dir():
                    theme_file = item / "theme.txt"
                    if theme_file.exists():
                        themes.append(item.name)
                        
        return sorted(themes)
    
    def is_btrfs_root(self) -> bool:
        """Check if root filesystem is BTRFS."""
        try:
            result = subprocess.run(['findmnt', '-n', '-o', 'FSTYPE', '/'], 
                                    capture_output=True, text=True)
            return result.stdout.strip().lower() == 'btrfs'
        except Exception:
            return False


THEME_ARCHIVE_SUFFIXES = ('.tar.gz', '.tgz', '.tar.xz', '.tar.bz2', '.zip')


def theme_install_name(theme_folder: str, extract_root: str, archive_path: str) -> str:
    """Name of the /boot/grub/themes/<name> folder for an extracted theme.

    theme.txt inside a folder: that folder's name. theme.txt at the top of
    the archive (theme_folder is the extraction directory itself): the
    archive name without its extension, never the temporary directory name.
    """
    if os.path.normpath(theme_folder) != os.path.normpath(extract_root):
        return os.path.basename(os.path.normpath(theme_folder))
    name = os.path.basename(archive_path)
    for suffix in THEME_ARCHIVE_SUFFIXES:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return os.path.splitext(name)[0]


# Global instance
_grub_manager = None

def get_grub_manager() -> GrubManager:
    """Returns the global GRUB manager instance."""
    global _grub_manager
    if _grub_manager is None:
        _grub_manager = GrubManager()
    return _grub_manager
