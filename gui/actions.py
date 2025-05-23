\
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import json

from sol_handler import read_sol, write_sol, find_jacksmith_sol_folder

class SolEditorActions:
    def __init__(self, app_instance):
        self.app = app_instance # Reference to the main SolEditorApp instance

    def auto_select_sol_folder(self):
        folder = find_jacksmith_sol_folder()
        if folder:
            self.app.folder_label.config(text=str(folder))
            self.load_sol_files_to_listbox(folder)
        else:
            self.app.folder_label.config(text="Automatisch map niet gevonden. Kies handmatig.")

    def select_sol_folder_gui_action(self):
        user_path_str = filedialog.askdirectory(title="Selecteer Jacksmith .sol map")
        if user_path_str:
            target_folder = Path(user_path_str)
            if target_folder.is_dir():
                self.app.folder_label.config(text=str(target_folder))
                self.load_sol_files_to_listbox(target_folder)
            else:
                messagebox.showwarning("Ongeldige Map", f"{user_path_str} is geen geldige map.")
        else:
            if not self.app.current_sol_path:
                 self.app.folder_label.config(text="Map selectie geannuleerd.")

    def load_sol_files_to_listbox(self, folder_path):
        self.app.sol_files_listbox.delete(0, tk.END)
        self.app.clear_data_tree()
        self.app.current_sol_path = None
        self.app.current_data = {}
        self.app.update_button.config(state=tk.DISABLED)
        self.app.save_button.config(state=tk.DISABLED)
        self.app.export_button.config(state=tk.DISABLED)
        try:
            sol_files = sorted(list(Path(folder_path).glob('*.sol')), key=lambda p: p.name.lower())
            if not sol_files:
                self.app.sol_files_listbox.insert(tk.END, "Geen .sol bestanden gevonden")
                return
            for sol_file in sol_files:
                 if "backup" not in sol_file.name.lower():
                    self.app.sol_files_listbox.insert(tk.END, sol_file.name)
        except Exception as e:
            messagebox.showerror("Fout bij laden bestandslijst", f"Fout: {e}")

    def on_sol_file_select(self, event):
        selection = self.app.sol_files_listbox.curselection()
        if not selection:
            return
        
        selected_file_name = self.app.sol_files_listbox.get(selection[0])
        folder_text = self.app.folder_label.cget("text")
        if not folder_text or not Path(folder_text).is_dir():
            messagebox.showerror("Fout", "Geselecteerde map is niet (meer) geldig.")
            return
            
        self.app.current_sol_path = Path(folder_text) / selected_file_name
        
        try:
            self.app.current_data = read_sol(str(self.app.current_sol_path))
            self.app.populate_data_tree(self.app.current_data)
            self.app.save_button.config(state=tk.NORMAL)
            self.app.export_button.config(state=tk.NORMAL)
        except FileNotFoundError as e:
            messagebox.showerror("Fout bij lezen .sol", f"{e}")
            self._handle_sol_read_error()
        except ValueError as e: 
            messagebox.showwarning("Leeg bestand", f"{selected_file_name} is leeg of kon niet correct gelezen worden.")
            self._handle_sol_read_error()
        except Exception as e:
            messagebox.showerror("Fout bij lezen .sol", f"Kon {selected_file_name} niet lezen: {e}")
            self._handle_sol_read_error()

    def _handle_sol_read_error(self):
        self.app.current_data = {}
        self.app.clear_data_tree()
        self.app.save_button.config(state=tk.DISABLED)
        self.app.export_button.config(state=tk.DISABLED)

    def on_tree_item_select(self, event):
        selected_items = self.app.data_tree.selection()
        if not selected_items:
            self.app.selected_tree_item_id = None
            self.app.key_label_var.set("")
            self.app.value_text.delete("1.0", tk.END)
            self.app.update_button.config(state=tk.DISABLED)
            return

        self.app.selected_tree_item_id = selected_items[0]
        key_display = self.app.data_tree.item(self.app.selected_tree_item_id, "text")
        self.app.key_label_var.set(key_display)
        
        actual_value = self.app._get_value_from_tree_path(self.app.selected_tree_item_id)
        self.app.value_text.delete("1.0", tk.END)

        if isinstance(actual_value, (dict, list)):
            try:
                self.app.value_text.insert(tk.END, json.dumps(actual_value, indent=2, ensure_ascii=False))
            except TypeError: 
                 self.app.value_text.insert(tk.END, str(actual_value) + "\n(Niet-JSON serialiseerbaar)")
        elif actual_value is not None:
            self.app.value_text.insert(tk.END, str(actual_value))
        else: 
            self.app.value_text.insert(tk.END, "") 
        
        self.app.update_button.config(state=tk.NORMAL)

    def update_value(self):
        if not self.app.selected_tree_item_id or not self.app.current_data:
            messagebox.showwarning("Geen selectie", "Selecteer een item om bij te werken.")
            return

        new_value_str = self.app.value_text.get("1.0", tk.END).strip()
        
        path_to_element = []
        current_tree_node_id = self.app.selected_tree_item_id
        while current_tree_node_id:
            path_to_element.insert(0, self.app.data_tree.item(current_tree_node_id, "text"))
            current_tree_node_id = self.app.data_tree.parent(current_tree_node_id)

        target_container = self.app.current_data
        key_or_index_for_update = None
        
        try:
            for i in range(len(path_to_element)):
                current_segment = path_to_element[i]
                is_last_segment = (i == len(path_to_element) - 1)

                if isinstance(target_container, dict):
                    if is_last_segment:
                        key_or_index_for_update = current_segment
                        break
                    target_container = target_container[current_segment]
                elif isinstance(target_container, list):
                    if current_segment.startswith("[") and current_segment.endswith("]"):
                        idx = int(current_segment[1:-1])
                        if is_last_segment:
                            key_or_index_for_update = idx
                            break
                        target_container = target_container[idx]
                    else:
                        raise ValueError("Ongeldig lijst index formaat in tree path.")
                else:
                     raise ValueError("Kon pad niet volgen in datastructuur.")
            
            if key_or_index_for_update is None:
                messagebox.showerror("Fout", "Kon item niet vinden om bij te werken.")
                return

            original_value = None
            if isinstance(target_container, dict):
                original_value = target_container.get(key_or_index_for_update)
            elif isinstance(target_container, list) and isinstance(key_or_index_for_update, int) and 0 <= key_or_index_for_update < len(target_container):
                original_value = target_container[key_or_index_for_update]

            converted_value = self.app._convert_value(new_value_str, original_value)
            if converted_value is None and new_value_str != "None": # Conversion failed
                return

            if isinstance(target_container, dict):
                target_container[key_or_index_for_update] = converted_value
            elif isinstance(target_container, list) and isinstance(key_or_index_for_update, int):
                if 0 <= key_or_index_for_update < len(target_container):
                    target_container[key_or_index_for_update] = converted_value
                else:
                    messagebox.showerror("Fout", "Index buiten bereik voor lijstupdate."); return
            
            self.app._update_tree_display(converted_value)
            messagebox.showinfo("Update", "Waarde bijgewerkt in editor. Vergeet niet op te slaan.")

        except Exception as e:
            messagebox.showerror("Update Fout", f"Kon waarde niet bijwerken: {e}")

    def save_sol_file(self):
        if not self.app.current_sol_path or not self.app.current_data:
            messagebox.showwarning("Geen data", "Geen .sol bestand geladen of data om op te slaan.")
            return
        try:
            write_sol(str(self.app.current_sol_path), self.app.current_data)
            messagebox.showinfo("Opgeslagen", f"Bestand {self.app.current_sol_path.name} opgeslagen.")
        except Exception as e:
            messagebox.showerror("Opslaan Fout", f"Kon bestand niet opslaan: {e}")

    def export_to_json(self):
        if not self.app.current_sol_path or not self.app.current_data:
            messagebox.showwarning("Geen data", "Geen data om te exporteren.")
            return
        
        try:
            initial_name = Path(self.app.current_sol_path).with_suffix('.json').name
            save_path = filedialog.asksaveasfilename(
                initialdir=Path(self.app.current_sol_path).parent,
                initialfile=initial_name,
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if not save_path:
                return 

            with open(save_path, 'w', encoding='utf-8') as jf:
                json.dump(self.app.current_data, jf, indent=2, ensure_ascii=False, default=str)
            messagebox.showinfo("Geëxporteerd", f"Data geëxporteerd naar {save_path}")
        except Exception as e:
            messagebox.showerror("Exporteren Fout", f"Kon niet exporteren naar JSON: {e}")
