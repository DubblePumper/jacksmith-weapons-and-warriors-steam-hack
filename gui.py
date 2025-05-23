'''
GUI componenten voor de SOL Editor.
'''
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from pathlib import Path

from sol_handler import read_sol, write_sol

class SolEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("Jacksmith .SOL Editor")
        master.geometry("900x700") # Iets breder voor betere weergave

        self.current_sol_path = None
        self.current_data = {}
        self.selected_tree_item_id = None # Hernoemd voor duidelijkheid

        # --- Layout --- 
        # Hoofd PanedWindow voor resizable secties
        main_paned_window = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Linker frame (bestandsselectie)
        left_frame = ttk.Frame(main_paned_window, width=250)
        main_paned_window.add(left_frame, weight=1)

        # Midden frame (Treeview)
        middle_frame = ttk.Frame(main_paned_window)
        main_paned_window.add(middle_frame, weight=3)

        # Rechter frame (bewerking)
        right_frame = ttk.Frame(main_paned_window, width=300)
        main_paned_window.add(right_frame, weight=2)

        # --- Linker Frame: Map en Bestandsselectie ---
        folder_select_frame = ttk.LabelFrame(left_frame, text="Map Selectie", padding="5")
        folder_select_frame.pack(fill=tk.X, pady=(0,5))

        self.select_folder_button = ttk.Button(folder_select_frame, text="Kies Jacksmith Map", command=self.select_sol_folder_gui_action)
        self.select_folder_button.pack(fill=tk.X, pady=2)
        self.folder_label = ttk.Label(folder_select_frame, text="Nog geen map geselecteerd", wraplength=230)
        self.folder_label.pack(fill=tk.X, pady=2)

        files_frame = ttk.LabelFrame(left_frame, text=".SOL Bestanden", padding="5")
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        self.sol_files_listbox = tk.Listbox(files_frame, exportselection=False)
        self.sol_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sol_files_listbox.bind('<<ListboxSelect>>', self.on_sol_file_select)

        sol_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.sol_files_listbox.yview)
        sol_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sol_files_listbox.config(yscrollcommand=sol_scrollbar.set)

        # --- Midden Frame: Data Treeview ---
        tree_frame = ttk.LabelFrame(middle_frame, text="Data Structuur", padding="5")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.data_tree = ttk.Treeview(tree_frame, columns=("Value"), selectmode="browse")
        self.data_tree.heading("#0", text="Key/Index")
        self.data_tree.heading("Value", text="Waarde")
        self.data_tree.column("#0", width=200, stretch=tk.YES)
        self.data_tree.column("Value", width=300, stretch=tk.YES)
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.data_tree.bind('<<TreeviewSelect>>', self.on_tree_item_select)

        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.config(yscrollcommand=tree_scrollbar_y.set)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_tree.config(xscrollcommand=tree_scrollbar_x.set)

        # --- Rechter Frame: Bewerking ---
        edit_controls_frame = ttk.LabelFrame(right_frame, text="Item Bewerken", padding="5")
        edit_controls_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(edit_controls_frame, text="Key/Index:").grid(row=0, column=0, sticky=tk.NW, padx=5, pady=2)
        self.key_label_var = tk.StringVar()
        ttk.Label(edit_controls_frame, textvariable=self.key_label_var, wraplength=280).grid(row=0, column=1, sticky=tk.NW, padx=5, pady=2)

        ttk.Label(edit_controls_frame, text="Waarde:").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=2)
        self.value_text = tk.Text(edit_controls_frame, height=10, width=35, wrap=tk.WORD)
        self.value_text.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=2)
        edit_controls_frame.grid_rowconfigure(1, weight=1) # Laat Text widget groeien
        edit_controls_frame.grid_columnconfigure(1, weight=1)

        self.update_button = ttk.Button(edit_controls_frame, text="Update Waarde", command=self.update_value, state=tk.DISABLED)
        self.update_button.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        # --- Bottom Frame voor globale actieknoppen --- 
        bottom_actions_frame = ttk.Frame(master, padding="10")
        bottom_actions_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.save_button = ttk.Button(bottom_actions_frame, text="Opslaan (.sol)", command=self.save_sol_file, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.export_button = ttk.Button(bottom_actions_frame, text="Exporteren (.json)", command=self.export_to_json, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_actions_frame, text="Sluiten", command=master.quit).pack(side=tk.RIGHT, padx=5)

        # Probeer automatisch de map te vinden bij opstarten
        self.auto_select_sol_folder()

    def auto_select_sol_folder(self):
        folder = find_jacksmith_sol_folder()
        if folder:
            self.folder_label.config(text=str(folder))
            self.load_sol_files_to_listbox(folder)
        else:
            self.folder_label.config(text="Automatisch map niet gevonden. Kies handmatig.")

    def select_sol_folder_gui_action(self):
        user_path_str = filedialog.askdirectory(title="Selecteer Jacksmith .sol map")
        if user_path_str:
            target_folder = Path(user_path_str)
            if target_folder.is_dir():
                self.folder_label.config(text=str(target_folder))
                self.load_sol_files_to_listbox(target_folder)
            else:
                messagebox.showwarning("Ongeldige Map", f"{user_path_str} is geen geldige map.")
        else:
            # Gebruiker annuleerde, doe niets of geef feedback
            if not self.current_sol_path: # Alleen als er nog geen map was
                 self.folder_label.config(text="Map selectie geannuleerd.")

    def load_sol_files_to_listbox(self, folder_path):
        self.sol_files_listbox.delete(0, tk.END)
        self.clear_data_tree() # Maak treeview leeg als map verandert
        self.current_sol_path = None
        self.current_data = {}
        self.update_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
        try:
            sol_files = sorted(list(Path(folder_path).glob('*.sol')), key=lambda p: p.name.lower())
            if not sol_files:
                self.sol_files_listbox.insert(tk.END, "Geen .sol bestanden gevonden")
                return
            for sol_file in sol_files:
                 if "backup" not in sol_file.name.lower():
                    self.sol_files_listbox.insert(tk.END, sol_file.name)
        except Exception as e:
            messagebox.showerror("Fout bij laden bestandslijst", f"Fout: {e}")

    def on_sol_file_select(self, event):
        selection = self.sol_files_listbox.curselection()
        if not selection:
            return
        
        selected_file_name = self.sol_files_listbox.get(selection[0])
        folder_text = self.folder_label.cget("text")
        if not folder_text or not Path(folder_text).is_dir():
            messagebox.showerror("Fout", "Geselecteerde map is niet (meer) geldig.")
            return
            
        self.current_sol_path = Path(folder_text) / selected_file_name
        
        try:
            self.current_data = read_sol(str(self.current_sol_path))
            self.populate_data_tree(self.current_data)
            self.save_button.config(state=tk.NORMAL)
            self.export_button.config(state=tk.NORMAL)
        except FileNotFoundError as e:
            messagebox.showerror("Fout bij lezen .sol", f"{e}")
            self.current_data = {}
            self.clear_data_tree()
            self.save_button.config(state=tk.DISABLED)
            self.export_button.config(state=tk.DISABLED)
        except ValueError as e: # Leeg bestand
            messagebox.showwarning("Leeg bestand", f"{selected_file_name} is leeg of kon niet correct gelezen worden.")
            self.current_data = {}
            self.clear_data_tree()
            self.save_button.config(state=tk.DISABLED)
            self.export_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Fout bij lezen .sol", f"Kon {selected_file_name} niet lezen: {e}")
            self.current_data = {}
            self.clear_data_tree()
            self.save_button.config(state=tk.DISABLED)
            self.export_button.config(state=tk.DISABLED)

    def clear_data_tree(self):
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        self.key_label_var.set("")
        self.value_text.delete("1.0", tk.END)
        self.selected_tree_item_id = None
        self.update_button.config(state=tk.DISABLED)

    def _populate_tree_recursive(self, data, parent_item):
        if isinstance(data, dict):
            for key, value in sorted(data.items()): # Sorteer voor consistente weergave
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
        self._populate_tree_recursive(data, "") # Start met root als parent

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
                 self.value_text.insert(tk.END, str(actual_value) + "\n(Niet-JSON serialiseerbaar)")
        elif actual_value is not None:
            self.value_text.insert(tk.END, str(actual_value))
        else: # Value is None or kon niet worden opgehaald
            self.value_text.insert(tk.END, "") # Leeg als waarde None is
        
        self.update_button.config(state=tk.NORMAL)

    def _get_value_from_tree_path(self, tree_item_id):
        path_keys_or_indices = []
        current = tree_item_id
        while current: # Bouw pad van geselecteerd item naar root
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
                        return None # Ongeldig pad
                else:
                    return None # Pad is ongeldig
            return value
        except (KeyError, IndexError, TypeError, ValueError):
            # Fallback als het pad niet direct overeenkomt, of data corrupt is
            # Dit kan gebeuren als de tree en data niet perfect synchroon zijn.
            # Probeer de waarde direct uit de treeview kolom te halen als laatste redmiddel.
            tree_values = self.data_tree.item(tree_item_id, "values")
            return tree_values[0] if tree_values and tree_values[0] != "(complex type)" else None

    def update_value(self):
        if not self.selected_tree_item_id or not self.current_data:
            messagebox.showwarning("Geen selectie", "Selecteer een item om bij te werken.")
            return

        new_value_str = self.value_text.get("1.0", tk.END).strip()
        
        # Reconstruct path to the data element
        path_to_element = []
        current_tree_node_id = self.selected_tree_item_id
        while current_tree_node_id:
            path_to_element.insert(0, self.data_tree.item(current_tree_node_id, "text"))
            current_tree_node_id = self.data_tree.parent(current_tree_node_id)

        # Navigate to the parent container in self.current_data
        target_container = self.current_data
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

            converted_value = new_value_str
            if isinstance(original_value, (dict, list)):
                try:
                    converted_value = json.loads(new_value_str)
                except json.JSONDecodeError as e:
                    messagebox.showerror("JSON Fout", f"Ongeldige JSON voor complexe waarde: {e}\n\nZorg ervoor dat de tekst valide JSON is, bijv. {{\"key\": \"value\"}} of [1, 2, 3].")
                    return
            elif isinstance(original_value, bool):
                converted_value = new_value_str.lower() in ['true', '1', 'yes', 'aan']
            elif isinstance(original_value, int):
                try: converted_value = int(new_value_str)
                except ValueError: messagebox.showerror("Type Fout", f"'{new_value_str}' is geen geldig geheel getal."); return
            elif isinstance(original_value, float):
                try: converted_value = float(new_value_str)
                except ValueError: messagebox.showerror("Type Fout", f"'{new_value_str}' is geen geldig decimaal getal."); return
            # Anders blijft het een string (default)

            # Update de waarde in de datastructuur
            if isinstance(target_container, dict):
                target_container[key_or_index_for_update] = converted_value
            elif isinstance(target_container, list) and isinstance(key_or_index_for_update, int):
                if 0 <= key_or_index_for_update < len(target_container):
                    target_container[key_or_index_for_update] = converted_value
                else:
                    messagebox.showerror("Fout", "Index buiten bereik voor lijstupdate."); return
            
            # Update de treeview display
            if isinstance(converted_value, (dict, list)):
                 self.data_tree.item(self.selected_tree_item_id, values=("(complex type)",))
                 # Ververs de kinderen van dit item
                 for child in self.data_tree.get_children(self.selected_tree_item_id):
                     self.data_tree.delete(child)
                 self._populate_tree_recursive(converted_value, self.selected_tree_item_id)
            else:
                 self.data_tree.item(self.selected_tree_item_id, values=(str(converted_value),))
            
            messagebox.showinfo("Update", "Waarde bijgewerkt in editor. Vergeet niet op te slaan.")

        except Exception as e:
            messagebox.showerror("Update Fout", f"Kon waarde niet bijwerken: {e}")

    def save_sol_file(self):
        if not self.current_sol_path or not self.current_data:
            messagebox.showwarning("Geen data", "Geen .sol bestand geladen of data om op te slaan.")
            return
        try:
            # Voordat we opslaan, moeten we mogelijk de 'pretty' dicts (met alleen data attributen)
            # terug converteren naar de structuur die pyamf verwacht, als dat nodig is.
            # Voor nu gaan we ervan uit dat de self.current_data structuur direct bruikbaar is.
            write_sol(str(self.current_sol_path), self.current_data)
            messagebox.showinfo("Opgeslagen", f"Bestand {self.current_sol_path.name} opgeslagen.")
        except Exception as e:
            messagebox.showerror("Opslaan Fout", f"Kon bestand niet opslaan: {e}")

    def export_to_json(self):
        if not self.current_sol_path or not self.current_data:
            messagebox.showwarning("Geen data", "Geen data om te exporteren.")
            return
        
        try:
            initial_name = Path(self.current_sol_path).with_suffix('.json').name
            save_path = filedialog.asksaveasfilename(
                initialdir=Path(self.current_sol_path).parent,
                initialfile=initial_name,
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if not save_path:
                return 

            with open(save_path, 'w', encoding='utf-8') as jf:
                json.dump(self.current_data, jf, indent=2, ensure_ascii=False, default=str)
            messagebox.showinfo("Geëxporteerd", f"Data geëxporteerd naar {save_path}")
        except Exception as e:
            messagebox.showerror("Exporteren Fout", f"Kon niet exporteren naar JSON: {e}")

