\
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import json
import traceback # Added import

from sol_handler import read_sol, write_sol, find_jacksmith_sol_folder

class SolEditorActions:
    def __init__(self, app_instance):
        self.app = app_instance

    def select_jacksmith_folder(self):
        # Renamed from select_sol_folder_gui_action to match the call from app.py
        # Also, the original select_jacksmith_folder was more comprehensive, so we keep its logic.
        initial_dir = Path.home() / "AppData" / "Roaming" / "com.flipline.jacksmith" / "Local Store" / "#SharedObjects"
        folder_path = filedialog.askdirectory(initialdir=initial_dir, title="Choose Jacksmith Folder")
        if folder_path:
            self.app.current_sol_folder = Path(folder_path)
            # Use the app's method to update the listbox display
            self.app.update_sol_file_list_display([]) # Clear old list
            
            # Attempt to find .sol files or use the selected folder
            # find_jacksmith_sol_folder might return a more specific path (e.g., inside #SharedObjects)
            sol_files_path = find_jacksmith_sol_folder() 
            if sol_files_path and sol_files_path.exists() and sol_files_path.is_dir():
                 # If find_jacksmith_sol_folder() gives a valid directory, prefer it if it's within the selected one or a known good one
                 # For simplicity now, we'll just use the one from filedialog if it was chosen, 
                 # but ideally, there'd be logic to see if sol_files_path is a sub-path of folder_path or vice-versa.
                 # For now, let's assume the user's explicit selection is what they want for current_sol_folder
                 # but we can still use sol_files_path to list files if it's more accurate.
                 pass # current_sol_folder is already set from filedialog
            
            # List .sol files from the currently set self.app.current_sol_folder
            if self.app.current_sol_folder and self.app.current_sol_folder.exists():
                sol_files_all = self.app.current_sol_folder.glob("*.sol")
                sol_files = [f for f in sol_files_all if "backup" not in f.name.lower()] # Filter out backups
                if sol_files:
                    self.app.update_sol_file_list_display([f.name for f in sol_files])
                    self.app.show_feedback("Folder Selected", f"Folder '{self.app.current_sol_folder.name}' selected. Found {len(sol_files)} .sol files (backups excluded).", kind='info')
                else:
                    self.app.update_sol_file_list_display([])
                    self.app.show_feedback("No .sol Files", f"No .sol files found in '{self.app.current_sol_folder}'.", kind='warning')
            else:
                self.app.update_sol_file_list_display([])
                self.app.show_feedback("Folder Error", "Could not access the selected folder.", kind='error')

    def on_sol_file_select(self, event):
        """Handles the selection of a .sol file from the listbox."""
        if not self.app.sol_files_listbox: # Check if listbox exists
            print("[WARN] on_sol_file_select called but sol_files_listbox is None")
            return

        widget = event.widget
        selected_indices = widget.curselection()
        if not selected_indices:
            return # No selection
        
        selected_filename = widget.get(selected_indices[0])
        self.load_sol_file(selected_filename) # Delegate to existing load_sol_file method

    def load_sol_file(self, filename):
        if not self.app.current_sol_folder:
            self.app.show_feedback("Error", "No folder selected.", kind='error')
            return
        
        sol_path = self.app.current_sol_folder / filename
        if not sol_path.exists():
            self.app.show_feedback("Error", f"File {filename} not found.", kind='error')
            return

        try:
            self.app.current_data = read_sol(sol_path)
            self.app.current_sol_path = sol_path # Store Path object
            self.app.populate_data_tree(self.app.current_data)
            self.app.show_feedback("Loaded", f"File {filename} loaded.", kind='info')
            self.app.enable_editing_ui()
        except Exception as e:
            print(f"[ERROR] Loading {filename}: {type(e).__name__} - {e}")
            detailed_traceback = traceback.format_exc()
            print(detailed_traceback)
            self.app.show_feedback("Error", f"Could not load file {filename}.\n{e}", kind='error')
            self.app.current_data = None
            self.app.current_sol_path = None
            self.app.clear_data_tree()
            self.app.disable_editing_ui()

    def update_value(self, item_id, new_value_str):
        if not self.app.current_data:
            self.app.show_feedback("Error", "No data loaded.", kind='error')
            return

        keys_path = self.app.get_keys_for_item(item_id)
        if not keys_path:
            self.app.show_feedback("Error", "Could not find item path.", kind='error')
            return

        current_level = self.app.current_data
        for i, key_text in enumerate(keys_path[:-1]):
            if isinstance(current_level, dict):
                current_level = current_level[key_text]
            elif isinstance(current_level, list):
                if key_text.startswith("[") and key_text.endswith("]"):
                    try:
                        idx = int(key_text[1:-1])
                        current_level = current_level[idx]
                    except (ValueError, IndexError) as e:
                        self.app.show_feedback("Error", f"Error accessing list element '{key_text}': {e}", kind='error')
                        return
                else:
                    self.app.show_feedback("Error", f"Malformed list index '{key_text}' in path.", kind='error')
                    return
            else:
                self.app.show_feedback("Error", f"Cannot traverse path at '{key_text}'. Not a dict or list.", kind='error')
                return
        
        last_key_text = keys_path[-1]
        original_value = None

        if isinstance(current_level, dict):
            original_value = current_level[last_key_text]
        elif isinstance(current_level, list):
            if last_key_text.startswith("[") and last_key_text.endswith("]"):
                try:
                    idx = int(last_key_text[1:-1])
                    original_value = current_level[idx]
                except (ValueError, IndexError) as e:
                    self.app.show_feedback("Error", f"Error accessing list element '{last_key_text}' for original value: {e}", kind='error')
                    return
            else:
                self.app.show_feedback("Error", f"Malformed list index '{last_key_text}' for original value.", kind='error')
                return
        else:
            self.app.show_feedback("Error", "Cannot get original value. Parent is not a dict or list.", kind='error')
            return

        try:
            converted_value = self.app._convert_value(new_value_str, original_value)
            
            if isinstance(current_level, dict):
                current_level[last_key_text] = converted_value
            elif isinstance(current_level, list):
                idx = int(last_key_text[1:-1]) 
                current_level[idx] = converted_value
            
            self.app._update_tree_display(converted_value, item_id) 
            print(f"[INFO] Value updated for {' -> '.join(map(str, keys_path))} to: {converted_value}")
            self.save_sol_file() # Auto-save after successful update

        except ValueError as e: 
            print(f"[ERROR] Value Update Error for {' -> '.join(keys_path)}: {type(e).__name__} - {e}")
            detailed_traceback = traceback.format_exc()
            print(detailed_traceback)
            self.app.show_feedback("Update Error", f"Invalid value: {e}", kind='error')
        except Exception as e:
            print(f"[ERROR] Value Update Error for {' -> '.join(keys_path)}: {type(e).__name__} - {e}")
            detailed_traceback = traceback.format_exc()
            print(detailed_traceback)
            self.app.show_feedback("Update Error", f"Could not update value.\nError: {e}", kind='error')

    def save_sol_file(self):
        if not self.app.current_sol_path or not self.app.current_data:
            self.app.show_feedback("No data", "No .sol file loaded or data to save.", kind='warning')
            return
        try:
            # current_sol_path should be a Path object from load_sol_file
            sol_path_obj = self.app.current_sol_path 
            
            if not isinstance(sol_path_obj, Path):
                # This is a fallback/recovery if current_sol_path is not a Path object
                # This was the suspected area of the 'dict' object has no attribute 'name' error
                print(f"[DEBUG] current_sol_path is not a Path object. Type: {type(self.app.current_sol_path)}, Value: {self.app.current_sol_path}")
                if isinstance(self.app.current_sol_path, dict):
                    path_str = self.app.current_sol_path.get('path')
                    if not path_str:
                         raise ValueError("Invalid file path stored (dictionary without 'path' key).")
                    sol_path_obj = Path(path_str)
                elif isinstance(self.app.current_sol_path, str):
                    sol_path_obj = Path(self.app.current_sol_path)
                else:
                    raise ValueError(f"Invalid file path type: {type(self.app.current_sol_path)}")

            write_sol(sol_path_obj, self.app.current_data) # write_sol expects a Path object or string
            self.app.show_feedback("Saved", f"File {sol_path_obj.name} saved.", kind='info')

        except Exception as e:
            print(f"--- Detailed Save Error ---")
            print(f"Current SOL Path: {self.app.current_sol_path}")
            print(f"Current SOL Path Type: {type(self.app.current_sol_path)}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {e}")
            print(f"Traceback:")
            detailed_traceback = traceback.format_exc()
            print(detailed_traceback)
            print(f"--- End Detailed Save Error ---")
            
            path_repr = "the file"
            try:
                if self.app.current_sol_path:
                    if isinstance(self.app.current_sol_path, Path):
                        path_repr = self.app.current_sol_path.name
                    elif isinstance(self.app.current_sol_path, dict):
                        path_repr = str(self.app.current_sol_path.get('path', self.app.current_sol_path))
                    else:
                        path_repr = str(self.app.current_sol_path)
            except:
                pass # Keep default "the file" if representation fails
            
            self.app.show_feedback(
                "Save Error", 
                f"Could not save file '{path_repr}'.\nError: {e}\n(See console for more details)", 
                kind='error'
            )

    def export_to_json(self):
        if not self.app.current_data:
            self.app.show_feedback("No data", "No data to export.", kind='warning')
            return

        # current_sol_path should be a Path object from load_sol_file
        current_path_obj = self.app.current_sol_path
        
        if not current_path_obj: # If no file was ever loaded
            default_filename = "export.json"
            initial_dir = Path.cwd()
        elif isinstance(current_path_obj, Path):
            default_filename = current_path_obj.with_suffix(".json").name
            initial_dir = current_path_obj.parent
        else: # Fallback if current_sol_path is not a Path object for some reason
            print(f"[DEBUG] current_sol_path for JSON export is not a Path. Type: {type(current_path_obj)}, Value: {current_path_obj}")
            default_filename = "export.json"
            initial_dir = Path.cwd() # Default to current working directory
            if isinstance(current_path_obj, str): # If it's a string path, try to use its parent
                try:
                    initial_dir = Path(current_path_obj).parent
                except: pass # Keep cwd if string is not a valid path
            elif isinstance(current_path_obj, dict): # If it's a dict, try to get 'path'
                 path_str = current_path_obj.get('path')
                 if path_str:
                     try:
                         initial_dir = Path(path_str).parent
                     except: pass # Keep cwd

        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir=initial_dir,
            initialfile=default_filename,
            title="Export to JSON"
        )

        if not save_path:
            return # User cancelled

        try:
            with open(save_path, 'w') as f:
                json.dump(self.app.current_data, f, indent=4)
            self.app.show_feedback("Exported", f"Data exported to {Path(save_path).name}", kind='info')
        except Exception as e:
            print(f"[ERROR] Exporting to JSON: {type(e).__name__} - {e}")
            detailed_traceback = traceback.format_exc()
            print(detailed_traceback)
            self.app.show_feedback("Export Error", f"Could not export to JSON.\nError: {e}", kind='error')

    def add_new_item(self):
        # This is a placeholder for future functionality
        self.app.show_feedback("Not Implemented", "Adding new items is not yet implemented.", kind='info')

    def delete_item(self):
        # This is a placeholder for future functionality
        self.app.show_feedback("Not Implemented", "Deleting items is not yet implemented.", kind='info')

    def auto_select_sol_folder(self):
        print("[INFO] Attempting to auto-select Jacksmith folder...")
        
        auto_detected_folder = find_jacksmith_sol_folder() 
        
        if auto_detected_folder and auto_detected_folder.exists() and auto_detected_folder.is_dir():
            self.app.current_sol_folder = auto_detected_folder
            sol_files_all = auto_detected_folder.glob("*.sol")
            sol_files = [f for f in sol_files_all if "backup" not in f.name.lower()] # Filter out backups
            
            if sol_files:
                self.app.update_sol_file_list_display([f.name for f in sol_files])
                self.app.show_feedback(
                    "Folder Auto-Selected", 
                    f"Folder '{auto_detected_folder.name}' auto-selected. Found {len(sol_files)} .sol files (backups excluded).", 
                    kind='info'
                )
            else:
                self.app.update_sol_file_list_display([]) # Clear list
                self.app.show_feedback(
                    "Folder Auto-Selected", 
                    f"Folder '{auto_detected_folder.name}' auto-selected, but no .sol files found (backups excluded).", 
                    kind='warning'
                )
        else:
            if auto_detected_folder: # Path was returned but not valid
                print(f"[WARN] find_jacksmith_sol_folder() returned: {auto_detected_folder}, but it's not a valid directory.")
            else: # find_jacksmith_sol_folder() returned None
                print("[INFO] find_jacksmith_sol_folder() did not locate a Jacksmith .sol folder.")
            
            self.app.update_sol_file_list_display([]) # Clear list
            self.app.show_feedback(
                "Auto-Select Information", 
                "Could not automatically find the Jacksmith .sol folder. Please use the 'Choose Jacksmith Folder' button to select it manually.", 
                kind='info'
            )
