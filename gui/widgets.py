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
    folder_select_frame = ttk.LabelFrame(parent_frame, text="Folder Selection", padding="10")
    folder_select_frame.pack(fill=tk.X, pady=(0,10))
    app_instance.select_folder_button = ttk.Button(folder_select_frame, text="Choose Jacksmith Folder", command=app_instance.select_sol_folder_gui_action)
    app_instance.select_folder_button.pack(fill=tk.X, pady=5)
    app_instance.folder_label = ttk.Label(folder_select_frame, text="No folder selected yet", wraplength=240)
    app_instance.folder_label.pack(fill=tk.X, pady=5)

    files_frame = ttk.LabelFrame(parent_frame, text=".SOL Files", padding="10")
    files_frame.pack(fill=tk.BOTH, expand=True)
    
    app_instance.sol_files_listbox = tk.Listbox(files_frame, exportselection=False)
    app_instance.sol_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    app_instance.sol_files_listbox.bind('<<ListboxSelect>>', app_instance.on_sol_file_select)

    sol_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=app_instance.sol_files_listbox.yview)
    sol_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app_instance.sol_files_listbox.config(yscrollcommand=sol_scrollbar.set)

def setup_middle_frame(parent_frame, app_instance):
    """Sets up the data treeview in the middle frame."""
    tree_frame = ttk.LabelFrame(parent_frame, text="Data Structure", padding="10")
    tree_frame.pack(fill=tk.BOTH, expand=True)
    app_instance.data_tree = ttk.Treeview(tree_frame, columns=("Value"), selectmode="browse")
    app_instance.data_tree.heading("#0", text="Key/Index")
    app_instance.data_tree.heading("Value", text="Value")
    app_instance.data_tree.column("#0", width=220, stretch=tk.YES, anchor=tk.W)  # Anchor West
    app_instance.data_tree.column("Value", width=320, stretch=tk.YES, anchor=tk.W)  # Anchor West
    app_instance.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=app_instance.data_tree.yview)
    tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    app_instance.data_tree.config(yscrollcommand=tree_scrollbar_y.set)
    tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=app_instance.data_tree.xview)
    tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    app_instance.data_tree.config(xscrollcommand=tree_scrollbar_x.set)

    # Bind double-click to edit value
    app_instance.data_tree.bind('<Double-1>', app_instance.on_tree_item_select)
    # Optionally, also bind single click to select
    app_instance.data_tree.bind('<<TreeviewSelect>>', app_instance.on_tree_item_select)

def setup_right_frame(parent_frame, app_instance):
    """Sets up the editing controls and 'Add All' functionality in the right frame."""
    edit_frame = ttk.LabelFrame(parent_frame, text="Edit Selected Item", padding="10")
    edit_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=5)

    # Key display (read-only)
    key_frame = ttk.Frame(edit_frame)
    key_frame.pack(fill=tk.X, pady=(5, 2))
    ttk.Label(key_frame, text="Key/Index:").pack(side=tk.LEFT, padx=(0,5))
    key_display_label = ttk.Label(key_frame, textvariable=app_instance.key_label_var, font=('Segoe UI', 10, 'bold'))
    key_display_label.pack(side=tk.LEFT)

    # Value entry
    value_label_frame = ttk.Frame(edit_frame)
    value_label_frame.pack(fill=tk.X, pady=(8,2))
    ttk.Label(value_label_frame, text="Value:").pack(anchor=tk.W)

    value_text_frame = ttk.Frame(edit_frame) # Frame to hold text and scrollbar
    value_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5))

    app_instance.value_text = tk.Text(value_text_frame, height=10, width=35, undo=True, wrap=tk.WORD)
    app_instance.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    value_scrollbar = ttk.Scrollbar(value_text_frame, orient=tk.VERTICAL, command=app_instance.value_text.yview)
    value_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app_instance.value_text.config(yscrollcommand=value_scrollbar.set)

    # Update button
    app_instance.update_button = ttk.Button(edit_frame, text="Update Value", command=app_instance.update_value, state=tk.DISABLED)
    app_instance.update_button.pack(fill=tk.X, pady=5)

    # --- Add All Parts/Tags Button and Label ---
    add_all_container = ttk.LabelFrame(edit_frame, text="Bulk Add", padding="10")
    add_all_container.pack(fill=tk.X, pady=(10,5))

    app_instance.add_all_button = ttk.Button(
        add_all_container,
        text="Add All Parts/DesignTags",
        command=app_instance.add_all_parts_tags,
        state=tk.DISABLED
    )
    app_instance.add_all_button.pack(fill=tk.X, pady=(0,5))

    # Informative label for the "Add All" button
    add_all_info_label = ttk.Label(
        add_all_container,
        textvariable=app_instance.add_all_label_var, # This will be set in app.py
        font=('Segoe UI', 8),
        wraplength=280 # Adjust as needed
    )
    add_all_info_label.pack(fill=tk.X)
    # --- End Add All Parts/Tags ---

def setup_bottom_actions_frame(master, app_instance):
    """Sets up save and export buttons in the bottom actions frame."""
    bottom_frame = ttk.Frame(master, padding="10")
    bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5,10))

    app_instance.save_button = ttk.Button(bottom_frame, text="Save .SOL File", command=app_instance.save_sol_file)
    app_instance.save_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    app_instance.export_button = ttk.Button(bottom_frame, text="Export to JSON", command=app_instance.export_to_json)
    app_instance.export_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
