#!/usr/bin/env python3
"""
Hoofdbestand voor de Jacksmith .sol Editor GUI.
"""

import tkinter as tk
from gui import SolEditorApp # Importeren van de SolEditorApp klasse

def main():
    """
    Initialiseert en start de SolEditorApp.
    """
    root = tk.Tk()
    app = SolEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()