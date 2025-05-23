\
import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
from pathlib import Path

from .widgets import (
    create_main_layout, setup_left_frame, setup_middle_frame, 
    setup_right_frame, setup_bottom_actions_frame
)
from .actions import SolEditorActions
# sol_handler is used by actions.py, not directly here for now.

class SolEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("Jacksmith .SOL Editor")
        master.geometry("950x750") # Slightly larger for more padding

        # Initialize attributes that don't depend on others first
        self.current_sol_folder = None # Added to ensure it's initialized
        self.current_sol_path = None
        self.current_data = {}
        self.selected_tree_item_id = None 

        # UI elements that need to be accessed/modified by app methods or actions
        # These are initialized to None and assigned actual widgets by setup functions
        self.folder_label = None
        self.sol_files_listbox = None
        self.data_tree = None
        self.key_label_var = tk.StringVar() 
        self.value_text = None
        self.update_button = None
        self.save_button = None
        self.export_button = None
        self.add_all_button = None # Ensure add_all_button is initialized
        self.add_all_label_var = tk.StringVar() # For the descriptive label

        # Setup layout - This must happen AFTER UI element attributes are None-initialized
        # and BEFORE actions are initialized if actions depend on UI elements being queryable (even if None)
        # The setup functions will assign widgets to the self.xxx attributes.
        frames = create_main_layout(master)
        if frames: # Ensure frames were returned
            left_frame, middle_frame, right_frame = frames
            setup_left_frame(left_frame, self)
            setup_middle_frame(middle_frame, self)
            setup_right_frame(right_frame, self)
            setup_bottom_actions_frame(master, self) # Assuming this also assigns to self like self.save_button
        else:
            # Fallback or error if create_main_layout doesn't return frames
            # This indicates an issue with create_main_layout if it happens
            print("[ERROR] Main layout frames not created. UI will be incomplete.")
            # Initialize frames to some default to prevent further errors if possible, though UI will be broken
            left_frame = ttk.Frame(master) 
            middle_frame = ttk.Frame(master)
            right_frame = ttk.Frame(master)

        # Initialize actions controller, passing this app instance
        self.actions = SolEditorActions(self)

        # Initial action - This should be safe now as self.actions is initialized
        # and UI elements are at least None-initialized or assigned by setup_xxx functions
        self.actions.auto_select_sol_folder()

        # --- Style Configuration ---
        self.style = ttk.Style()
        try:
            self.style.theme_use('vista') 
        except tk.TclError:
            try:
                self.style.theme_use('clam')
            except tk.TclError:
                print("Warning: Could not apply 'vista' or 'clam' theme. Using default.")
        
        self.style.configure("TButton", padding=6)
        self.style.configure("TLabel", padding=3)
        self.style.configure("TLabelframe.Label", padding=(5,2))
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

        # Set initial text for the add_all_label_var
        self.add_all_label_var.set("Select 'parts' or 'newdesigntags' in the tree to enable.")

    def update_sol_file_list_display(self, file_names: list[str]):
        """Clears and repopulates the SOL files listbox in the UI."""
        if self.sol_files_listbox:
            self.sol_files_listbox.delete(0, tk.END)
            for name in file_names:
                self.sol_files_listbox.insert(tk.END, name)
        else:
            print("[WARN] sol_files_listbox is not initialized when trying to update display.")

    # --- Methods called by widgets (delegating to self.actions) ---
    def select_sol_folder_gui_action(self): 
        self.actions.select_jacksmith_folder()

    def on_sol_file_select(self, event): 
        self.actions.on_sol_file_select(event)

    def on_tree_item_select(self, event):
        # Ensure data_tree is not None before proceeding
        if not self.data_tree:
            print("[WARN] on_tree_item_select called but data_tree is None.")
            return

        selected_items = self.data_tree.selection()
        if not selected_items:
            self.selected_tree_item_id = None
            self.key_label_var.set("")
            if self.value_text: self.value_text.delete("1.0", tk.END)
            if self.update_button: self.update_button.config(state=tk.DISABLED)
            if hasattr(self, 'add_all_button') and self.add_all_button: # Check add_all_button
                self.add_all_button.config(state=tk.DISABLED)
                self.add_all_label_var.set("Select 'parts' or 'newdesigntags' in the tree to enable.") # Reset label
            return

        self.selected_tree_item_id = selected_items[0]
        key_display = self.data_tree.item(self.selected_tree_item_id, "text")
        self.key_label_var.set(key_display)
        
        actual_value = self._get_value_from_tree_path(self.selected_tree_item_id)
        
        if self.value_text:
            self.value_text.delete("1.0", tk.END)
            if isinstance(actual_value, (dict, list)):
                try:
                    self.value_text.insert(tk.END, json.dumps(actual_value, indent=2, ensure_ascii=False))
                except TypeError:
                    self.value_text.insert(tk.END, str(actual_value) + "\n(Not JSON serializable)")
            elif actual_value is not None:
                self.value_text.insert(tk.END, str(actual_value))
            else:
                self.value_text.insert(tk.END, "")
        
        if self.update_button: self.update_button.config(state=tk.NORMAL)
        
        if self.value_text: self.value_text.focus_set() # Check value_text before calling focus_set

        if hasattr(self, 'add_all_button') and self.add_all_button: # Check add_all_button
            if key_display in ('parts', 'newdesigntags'):
                self.add_all_button.config(state=tk.NORMAL)
                self.add_all_label_var.set(f"Click to add all items for '{key_display}'.") # Update label
            else:
                self.add_all_button.config(state=tk.DISABLED)
                self.add_all_label_var.set("Select 'parts' or 'newdesigntags' in the tree to enable.") # Reset label

    def update_value(self):
        if self.selected_tree_item_id and self.value_text:
            new_value_str = self.value_text.get("1.0", tk.END).strip()
            self.actions.update_value(self.selected_tree_item_id, new_value_str)
        else:
            self.show_feedback("Update Error", "No item selected or value field is missing.", kind='warning')

    def save_sol_file(self):
        self.actions.save_sol_file()

    def export_to_json(self):
        self.actions.export_to_json()

    # --- Core UI logic methods ---
    def clear_data_tree(self):
        if self.data_tree:
            children = self.data_tree.get_children()
            if children: # Check if get_children() returned a non-empty tuple
                for item in children: # type: ignore
                    self.data_tree.delete(item)
        self.key_label_var.set("")
        if self.value_text:
            self.value_text.delete("1.0", tk.END)
        self.selected_tree_item_id = None
        if self.update_button:
            self.update_button.config(state=tk.DISABLED)

    def _populate_tree_recursive(self, data, parent_item):
        if not self.data_tree: return
        if isinstance(data, dict):
            for key, value in sorted(data.items()): # Sort items for consistent display
                # Ensure key is a string for display
                display_key = str(key)
                item_id = self.data_tree.insert(parent_item, tk.END, text=display_key, open=False)
                if isinstance(value, (dict, list)):
                    self._populate_tree_recursive(value, item_id)
                    self.data_tree.item(item_id, values=("(complex type)",))
                else:
                    self.data_tree.item(item_id, values=(str(value),))
        elif isinstance(data, list):
            for i, item_value in enumerate(data):
                item_id = self.data_tree.insert(parent_item, tk.END, text=f"[{i}]", open=False)
                if isinstance(item_value, (dict, list)):
                    self._populate_tree_recursive(item_value, item_id)
                    self.data_tree.item(item_id, values=("(complex type)",))
                else:
                    self.data_tree.item(item_id, values=(str(item_value),))

    def populate_data_tree(self, data):
        self.clear_data_tree()
        if self.data_tree: # Ensure data_tree exists
            self._populate_tree_recursive(data, "")
        else:
            print("[WARN] populate_data_tree called but data_tree is None.")

    def enable_editing_ui(self):
        """Enables editing-related UI elements."""
        if self.update_button:
            self.update_button.config(state=tk.NORMAL)
        if self.value_text:
            self.value_text.config(state=tk.NORMAL)
        # Add other editing controls if necessary

    def disable_editing_ui(self):
        """Disables editing-related UI elements."""
        if self.update_button:
            self.update_button.config(state=tk.DISABLED)
        if self.value_text:
            self.value_text.config(state=tk.DISABLED)
        # Add other editing controls if necessary

    def get_keys_for_item(self, tree_item_id): # Added this method
        """Helper to get the list of keys/indices for a tree item."""
        if not self.data_tree: return []
        path_keys_or_indices = []
        current = tree_item_id
        while current:
            # The 'text' is what we displayed (string key or "[index]")
            path_element_text = self.data_tree.item(current, "text")
            path_keys_or_indices.insert(0, path_element_text)
            current = self.data_tree.parent(current)
        
        # Convert list indices from string "[i]" to int i if necessary for data access
        # For now, this method returns the text representations as seen in the tree.
        # The actual conversion to int for list indices happens in _get_value_from_tree_path
        return path_keys_or_indices

    def _get_value_from_tree_path(self, tree_item_id):
        if not self.data_tree: return None
        
        path_keys_or_indices_text = self.get_keys_for_item(tree_item_id) # Use helper
        
        value = self.current_data
        try:
            for key_or_index_str in path_keys_or_indices_text:
                if isinstance(value, dict):
                    # Assume keys in current_data are strings if they came from SOL/JSON
                    value = value[key_or_index_str] 
                elif isinstance(value, list):
                    if key_or_index_str.startswith("[") and key_or_index_str.endswith("]"):
                        idx = int(key_or_index_str[1:-1])
                        value = value[idx]
                    else: 
                        # This case should ideally not happen if tree is built correctly
                        print(f"[ERROR] Malformed list index string from tree: {key_or_index_str}")
                        return None 
                else:
                    # Path goes deeper than actual data structure
                    return None 
            return value
        except (KeyError, IndexError, TypeError, ValueError) as e:
            print(f"[ERROR] Error accessing value from tree path {' -> '.join(path_keys_or_indices_text)}: {e}")
            # Fallback for safety, though ideally path should always be valid
            tree_values = self.data_tree.item(tree_item_id, "values")
            return tree_values[0] if tree_values and tree_values[0] != "(complex type)" else None

    def _update_tree_display(self, new_value, tree_item_id_to_update):
        if not self.data_tree: return
        if isinstance(new_value, (dict, list)):
            self.data_tree.item(tree_item_id_to_update, values=("(complex type)",))
            # Clear existing children before repopulating
            children = self.data_tree.get_children(tree_item_id_to_update)
            if children: # Check if get_children() returned a non-empty tuple
                for child in children: # type: ignore
                    self.data_tree.delete(child)
            self._populate_tree_recursive(new_value, tree_item_id_to_update)
        else:
            self.data_tree.item(tree_item_id_to_update, values=(str(new_value),))

    def show_feedback(self, title, message, kind='info'):
        # Ensure master window is available for messagebox
        if not self.master: 
            print(f"Feedback ({kind}): {title} - {message} (Master window not available)")
            return
        if kind == 'info':
            messagebox.showinfo(title, message, parent=self.master)
        elif kind == 'warning':
            messagebox.showwarning(title, message, parent=self.master)
        elif kind == 'error':
            messagebox.showerror(title, message, parent=self.master)
        else:
            messagebox.showinfo(title, message, parent=self.master)

    def _convert_value(self, new_value_str, original_value):
        original_type = type(original_value)
        try:
            if original_type == bool:
                if new_value_str.lower() in ("true", "1", "yes"): return True
                if new_value_str.lower() in ("false", "0", "no"): return False
                raise ValueError(f"Cannot convert '{new_value_str}' to boolean.")
            if original_type in (list, dict):
                try:
                    val = json.loads(new_value_str)
                    if not isinstance(val, original_type):
                        raise ValueError(f"Converted JSON type {type(val)} does not match original type {original_type}")
                    return val
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON format: {e}")
            # For int, float, str, try direct conversion
            return original_type(new_value_str)
        except ValueError as e: # Catch specific conversion errors
            print(f"[ERROR] Value conversion failed for '{new_value_str}' to type {original_type.__name__}: {e}")
            self.show_feedback("Conversion Error", f"Could not convert '{new_value_str}' to {original_type.__name__}. Error: {e}", kind='error')
            raise # Re-raise to be caught by the caller (actions.update_value)
        except Exception as e: # Catch any other unexpected errors during conversion
            print(f"[ERROR] Unexpected error during value conversion: {e}")
            self.show_feedback("Conversion Error", f"Unexpected error converting value. Error: {e}", kind='error')
            raise # Re-raise

    def add_all_parts_tags(self):
        if not self.selected_tree_item_id or not self.data_tree:
            self.show_feedback("Error", "No item selected in the tree.", kind='warning')
            return

        selected_key = self.data_tree.item(self.selected_tree_item_id, "text")
        
        # Get the parent data structure to modify
        path_to_parent = self.get_keys_for_item(self.data_tree.parent(self.selected_tree_item_id))
        current_level_data = self.current_data # This will be iteratively accessed to become the parent
        try:
            for key_or_idx_str in path_to_parent:
                if isinstance(current_level_data, dict):
                    current_level_data = current_level_data[key_or_idx_str]
                elif isinstance(current_level_data, list):
                    # Ensure key_or_idx_str is a list index like "[i]"
                    if key_or_idx_str.startswith("[") and key_or_idx_str.endswith("]"):
                        idx = int(key_or_idx_str[1:-1])
                        current_level_data = current_level_data[idx]
                    else:
                        raise ValueError(f"Malformed list index string: {key_or_idx_str}")
                else:
                    # Should not happen if path is valid and data structure is dict/list
                    raise TypeError(f"Cannot traverse non-container type: {type(current_level_data)}")
        except Exception as e:
            self.show_feedback("Error", f"Could not access parent data for update: {e}", kind='error')
            return

        updated_value = None
        if selected_key == 'parts':
            # --- Parts Logic ---
            # Fetch existing parts data from the correct parent (current_level_data)
            existing_parts_data = []
            if isinstance(current_level_data, dict):
                existing_parts_data = current_level_data.get(selected_key, [])
            elif isinstance(current_level_data, list) and selected_key.startswith("[") and selected_key.endswith("]"):
                try:
                    idx = int(selected_key[1:-1])
                    if 0 <= idx < len(current_level_data):
                        existing_parts_data = current_level_data[idx]
                    else: # Index out of bounds, treat as empty
                        existing_parts_data = []
                except ValueError:
                    self.show_feedback("Error", f"Invalid index format for 'parts' key '{selected_key}'.", kind='error')
                    return
            else:
                self.show_feedback("Error", f"Parent for 'parts' is not a dictionary or list, or key '{selected_key}' is malformed.", kind='error')
                return

            # Ensure existing_parts_data is a list for the logic below
            if not isinstance(existing_parts_data, list):
                self.show_feedback("Warning", f"Data for 'parts' key '{selected_key}' is not a list. Initializing as empty list.", kind='warning')
                existing_parts_data = []

            existing_parts_dict = {}
            # The existing_parts_data should be a list of lists, e.g., [["part_sword_grip_1", 10], ...]
            for part_entry in existing_parts_data:
                if isinstance(part_entry, list) and len(part_entry) >= 2:
                    existing_parts_dict[str(part_entry[0])] = part_entry[1] # Ensure key is string
            
            categories = set()
            ids = set()
            for partname in existing_parts_dict:
                m = re.match(r'part_([a-zA-Z0-9_]+)_([a-zA-Z0-9]+)$', partname)
                if m:
                    categories.add(m.group(1))
                    ids.add(m.group(2))
            
            known_categories = {'sword_grip', 'sword_crossguard', 'sword_pommel',
                                'arrow_head', 'arrow_fletching',
                                'mace_shaft', 'mace_head',
                                'shield_body', 'shield_crest', 'shield_paint'}
            final_categories = categories if categories else known_categories
            
            max_id_num = 0
            detected_ids_numeric = set()
            for id_str in ids:
                if id_str.isdigit():
                    detected_ids_numeric.add(int(id_str))
            if detected_ids_numeric:
                max_id_num = max(detected_ids_numeric, default=0)
            
            id_range_to_generate = range(1, max(max_id_num + 1, 51)) # Generate up to 50 or max_id + 1
            
            all_parts_list = []
            # Add existing parts first, ensuring they are updated to 999
            for pname, pval in existing_parts_dict.items():
                all_parts_list.append([pname, 999])

            # Add new parts
            for cat in sorted(list(final_categories)):
                for i in id_range_to_generate:
                    pname_num = f'part_{cat}_{i}'
                    if pname_num not in existing_parts_dict: # Add only if truly new
                        all_parts_list.append([pname_num, 999])
            
            updated_value = sorted(all_parts_list, key=lambda x: x[0])
            
            # Update the data in the correct parent structure (current_level_data)
            if isinstance(current_level_data, dict):
                current_level_data[selected_key] = updated_value
            elif isinstance(current_level_data, list) and selected_key.startswith("[") and selected_key.endswith("]"):
                try:
                    idx = int(selected_key[1:-1])
                    current_level_data[idx] = updated_value
                except (ValueError, IndexError):
                    self.show_feedback("Error", f"Failed to update 'parts' at index '{selected_key}'.", kind='error')
                    return
            else: # Should not be reached if initial fetch was okay
                self.show_feedback("Error", "Data structure error during 'parts' update.", kind='error')
                return
                
            self.show_feedback("Success", "All parts have been processed for the selected item!", kind='info')

        elif selected_key == 'newdesigntags':
            # --- NewDesignTags Logic ---
            design_codes = ['AX', 'BW', 'MA', 'PI', 'SH', 'SW']
            design_nummers = [f'{i:02}' for i in range(1, 15)] # 01 to 14
            all_tags = [f'{code}-{nummer}' for code in design_codes for nummer in design_nummers]
            updated_value = sorted(all_tags)

            # Update the data in the correct parent structure (current_level_data)
            if isinstance(current_level_data, dict):
                current_level_data[selected_key] = updated_value
            elif isinstance(current_level_data, list) and selected_key.startswith("[") and selected_key.endswith("]"):
                try:
                    idx = int(selected_key[1:-1])
                    current_level_data[idx] = updated_value
                except (ValueError, IndexError):
                    self.show_feedback("Error", f"Failed to update 'newdesigntags' at index '{selected_key}'.", kind='error')
                    return
            else: # Should not be reached if initial fetch was okay
                self.show_feedback("Error", "Data structure error during 'newdesigntags' update.", kind='error')
                return

            self.show_feedback("Success", "All design tags have been generated for the selected item!", kind='info')
        else:
            self.show_feedback("Info", "This function is only for 'parts' or 'newdesigntags' keys.", kind='info')
            return

        if updated_value is not None:
            if self.value_text:
                self.value_text.delete("1.0", tk.END)
                self.value_text.insert(tk.END, json.dumps(updated_value, indent=2, ensure_ascii=False))
            self._update_tree_display(updated_value, self.selected_tree_item_id)
        
        if self.update_button: self.update_button.config(state=tk.NORMAL) # Re-enable update button
