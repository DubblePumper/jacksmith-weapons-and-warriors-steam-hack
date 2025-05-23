import tkinter as tk
from tkinter import ttk

def create_main_layout(master):
    """Creates the main paned window and frames for the application."""
    main_paned_window = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
    main_paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    left_frame = ttk.Frame(main_paned_window, width=280, padding=(5,5))  # Increased width slightly
    main_paned_window.add(left_frame, weight=1)

    middle_frame = ttk.Frame(main_paned_window, padding=(5,5))
    main_paned_window.add(middle_frame, weight=3)

    right_frame = ttk.Frame(main_paned_window, width=320, padding=(5,5))  # Increased width slightly
    main_paned_window.add(right_frame, weight=2)
    
    return left_frame, middle_frame, right_frame

def setup_left_frame(parent_frame, app_instance):
    """Sets up the folder selection and SOL files listbox in the left frame."""
    folder_select_frame = ttk.LabelFrame(parent_frame, text="Map Selectie", padding="10")  # Increased padding
    folder_select_frame.pack(fill=tk.X, pady=(0,10))  # Added bottom margin
    app_instance.select_folder_button = ttk.Button(folder_select_frame, text="Kies Jacksmith Map", command=app_instance.select_sol_folder_gui_action)
    app_instance.select_folder_button.pack(fill=tk.X, pady=5)
    app_instance.folder_label = ttk.Label(folder_select_frame, text="Nog geen map geselecteerd", wraplength=240)  # Increased wraplength
    app_instance.folder_label.pack(fill=tk.X, pady=5)

    files_frame = ttk.LabelFrame(parent_frame, text=".SOL Bestanden", padding="10")  # Increased padding
    files_frame.pack(fill=tk.BOTH, expand=True)
    
    app_instance.sol_files_listbox = tk.Listbox(files_frame, exportselection=False)
    app_instance.sol_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    app_instance.sol_files_listbox.bind('<<ListboxSelect>>', app_instance.on_sol_file_select)

    sol_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=app_instance.sol_files_listbox.yview)
    sol_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app_instance.sol_files_listbox.config(yscrollcommand=sol_scrollbar.set)

def setup_middle_frame(parent_frame, app_instance):
    """Sets up the data treeview in the middle frame."""
    tree_frame = ttk.LabelFrame(parent_frame, text="Data Structuur", padding="10")  # Increased padding
    tree_frame.pack(fill=tk.BOTH, expand=True)
    app_instance.data_tree = ttk.Treeview(tree_frame, columns=("Value"), selectmode="browse")
    app_instance.data_tree.heading("#0", text="Key/Index")
    app_instance.data_tree.heading("Value", text="Waarde")
    app_instance.data_tree.column("#0", width=220, stretch=tk.YES, anchor=tk.W)  # Anchor West
    app_instance.data_tree.column("Value", width=320, stretch=tk.YES, anchor=tk.W)  # Anchor West
    app_instance.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=app_instance.data_tree.yview)
    tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    app_instance.data_tree.config(yscrollcommand=tree_scrollbar_y.set)
    tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=app_instance.data_tree.xview)
    tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    app_instance.data_tree.config(xscrollcommand=tree_scrollbar_x.set)

def setup_right_frame(parent_frame, app_instance):
    """Sets up the item editing controls in the right frame."""
    edit_controls_frame = ttk.LabelFrame(parent_frame, text="Item Bewerken", padding="10")  # Increased padding
    edit_controls_frame.pack(fill=tk.BOTH, expand=True)
    ttk.Label(edit_controls_frame, text="Key/Index:").grid(row=0, column=0, sticky=tk.NW, padx=5, pady=(5,2))
    app_instance.key_label_var = tk.StringVar()
    key_display_entry = ttk.Entry(edit_controls_frame, textvariable=app_instance.key_label_var, state='readonly')  # Read-only Entry
    key_display_entry.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=(5,2))

    ttk.Label(edit_controls_frame, text="Waarde:").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=2)
    text_area_frame = ttk.Frame(edit_controls_frame)
    text_area_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=2)
    edit_controls_frame.grid_rowconfigure(1, weight=1)
    edit_controls_frame.grid_columnconfigure(1, weight=1)
    
    app_instance.value_text = tk.Text(text_area_frame, height=10, width=35, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)  # Added relief/border
    app_instance.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    value_scrollbar = ttk.Scrollbar(text_area_frame, orient=tk.VERTICAL, command=app_instance.value_text.yview)
    value_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app_instance.value_text.config(yscrollcommand=value_scrollbar.set)

    app_instance.update_button = ttk.Button(edit_controls_frame, text="Update Waarde", command=app_instance.update_value, state=tk.DISABLED)
    app_instance.update_button.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=(10,5))  # Added more vertical padding

def setup_bottom_actions_frame(master, app_instance):
    """Sets up the global action buttons at the bottom of the window."""
    bottom_actions_frame = ttk.Frame(master, padding="10")
    bottom_actions_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5,0))
    app_instance.save_button = ttk.Button(bottom_actions_frame, text="Opslaan (.sol)", command=app_instance.save_sol_file, state=tk.DISABLED)
    app_instance.save_button.pack(side=tk.LEFT, padx=(0,5))  # Adjusted padding
    app_instance.export_button = ttk.Button(bottom_actions_frame, text="Exporteren (.json)", command=app_instance.export_to_json, state=tk.DISABLED)
    app_instance.export_button.pack(side=tk.LEFT, padx=5)
    ttk.Separator(bottom_actions_frame, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)  # Added separator
    ttk.Button(bottom_actions_frame, text="Sluiten", command=master.quit).pack(side=tk.RIGHT, padx=(5,0))  # Adjusted padding
