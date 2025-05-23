\
import tkinter as tk
from tkinter import ttk, messagebox
import json
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

        # --- Style Configuration ---
        self.style = ttk.Style()
        # Available themes: self.style.theme_names() -> ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        # 'vista' or 'winnative' often look good on Windows. 'clam' is a good cross-platform option.
        try:
            self.style.theme_use('vista') 
        except tk.TclError:
            try:
                self.style.theme_use('clam')
            except tk.TclError:
                print("Warning: Could not apply 'vista' or 'clam' theme. Using default.")
        
        # Configure default font for all ttk widgets (if desired)
        # default_font = ("Segoe UI", 10) # Example font
        # self.style.configure('.', font=default_font, padding=3) # Global padding for all ttk widgets
        
        # Specific widget styling (examples)
        self.style.configure("TButton", padding=6)
        self.style.configure("TLabel", padding=3)
        self.style.configure("TLabelframe.Label", padding=(5,2)) # Padding for LabelFrame title
        self.style.configure("Treeview", rowheight=25) # Increase row height for readability
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold')) # Style for treeview headings

        self.current_sol_path = None
        self.current_data = {}
        self.selected_tree_item_id = None 
        
        # UI elements that need to be accessed/modified by app methods or actions
        self.folder_label = None
        self.sol_files_listbox = None
        self.data_tree = None
        self.key_label_var = tk.StringVar() 
        self.value_text = None
        self.update_button = None
        self.save_button = None
        self.export_button = None

        # Setup layout
        left_frame, middle_frame, right_frame = create_main_layout(master)
        # Pass self (app_instance) to widget setup functions
        setup_left_frame(left_frame, self)
        setup_middle_frame(middle_frame, self)
        setup_right_frame(right_frame, self)
        setup_bottom_actions_frame(master, self)

        # Initialize actions controller, passing this app instance
        self.actions = SolEditorActions(self)

        # Initial action
        self.actions.auto_select_sol_folder()

    # --- Methods called by widgets (delegating to self.actions) ---
    # These methods are expected if widgets.py binds commands directly to app_instance.method_name
    def select_sol_folder_gui_action(self): 
        self.actions.select_sol_folder_gui_action()

    def on_sol_file_select(self, event): 
        self.actions.on_sol_file_select(event)

    def on_tree_item_select(self, event):
        selected_items = self.data_tree.selection()
        if not selected_items:
            self.selected_tree_item_id = None
            self.key_label_var.set("")
            self.value_text.delete("1.0", tk.END)
            self.update_button.config(state=tk.DISABLED)
            return

        self.selected_tree_item_id = selected_items[0]
        key_display = self.data_tree.item(self.selected_tree_item_id, "text")
        self.key_label_var.set(key_display)
        
        actual_value = self._get_value_from_tree_path(self.selected_tree_item_id)
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
        self.update_button.config(state=tk.NORMAL)
        # Focus the value_text widget for editing
        self.value_text.focus_set()

    def update_value(self):
        self.actions.update_value()

    def save_sol_file(self):
        self.actions.save_sol_file()

    def export_to_json(self):
        self.actions.export_to_json()

    # --- Core UI logic methods ---
    def clear_data_tree(self):
        if self.data_tree:
            for item in self.data_tree.get_children():
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
            for key, value in sorted(data.items()):
                item_id = self.data_tree.insert(parent_item, tk.END, text=str(key), open=False)
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
        self._populate_tree_recursive(data, "")

    def _get_value_from_tree_path(self, tree_item_id):
        if not self.data_tree: return None
        path_keys_or_indices = []
        current = tree_item_id
        while current:
            path_keys_or_indices.insert(0, self.data_tree.item(current, "text"))
            current = self.data_tree.parent(current)
        
        value = self.current_data
        try:
            for key_or_index_str in path_keys_or_indices:
                if isinstance(value, dict):
                    value = value[key_or_index_str]
                elif isinstance(value, list):
                    if key_or_index_str.startswith("[") and key_or_index_str.endswith("]"):
                        idx = int(key_or_index_str[1:-1])
                        value = value[idx]
                    else: 
                        return None 
                else:
                    return None 
            return value
        except (KeyError, IndexError, TypeError, ValueError):
            # Fallback for safety, though ideally path should always be valid
            tree_values = self.data_tree.item(tree_item_id, "values")
            return tree_values[0] if tree_values and tree_values[0] != "(complex type)" else None

    def _update_tree_display(self, new_value, tree_item_id_to_update):
        if not self.data_tree: return
        if isinstance(new_value, (dict, list)):
            self.data_tree.item(tree_item_id_to_update, values=("(complex type)",))
            for child in self.data_tree.get_children(tree_item_id_to_update):
                self.data_tree.delete(child)
            self._populate_tree_recursive(new_value, tree_item_id_to_update)
            # self.data_tree.item(tree_item_id_to_update, open=True) # Optionally open
        else:
            self.data_tree.item(tree_item_id_to_update, values=(str(new_value),))
