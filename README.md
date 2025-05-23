# jacksmith-weaponsandwarriors_steam_cheat

A .SOL file editor for Jacksmith (Weapons and Warriors - Steam Version).

## Description

This tool allows users to open, view, and modify `.sol` save files from the game Jacksmith (Steam version). It enables the adjustment of various game parameters stored locally.

## Features

*   **Load and View:** Open `.sol` files and view the data in a clear tree structure.
*   **Automatic Folder Detection:** Attempts to automatically find the Jacksmith (Steam) save folder.
*   **Manual Folder Selection:** Option to manually choose the folder containing `.sol` files.
*   **Backup Filter:** `.sol` files with "backup" in their name are automatically ignored in the list.
*   **Data Editing:** Select an item in the tree structure to see and modify its key/index and value.
*   **Auto-Save:** Changes are automatically saved after clicking "Update Value".
*   **Manual Save:** A separate button to explicitly save changes to the `.sol` file.
*   **"Add All Parts/Tags" Button:** A helper function to quickly add all `parts` or `newdesigntags`. First, select the respective key (`parts` or `newdesigntags`) in the data structure for the button to function correctly.

## Requirements

*   Python 3.x
*   The `pyamf` library
*   Other dependencies as specified in `requirements.txt` (mainly Tkinter, which usually comes standard with Python).

## Installation / Setup

1.  **Download/Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/jacksmith-weaponsandwarriors_steam_cheat.git
    cd jacksmith-weaponsandwarriors_steam_cheat
    ```
    (Replace `yourusername` with the actual username/organization of the repository if you forked it or if it's hosted elsewhere). If you downloaded the code as a ZIP, extract it.

2.  **Install Dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    # source venv/bin/activate  # macOS/Linux
    ```
    Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    If `pyamf` is not in `requirements.txt` or if the file is missing, install it manually:
    ```bash
    pip install pyamf
    ```

## How to Start

Run the main script from the project's root folder:

```bash
python main.py
```

## User Guide

1.  **Start the Application:** Run `main.py` as described above.
2.  **Select Folder:**
    *   The application attempts to automatically find the Jacksmith save folder for the Steam version (e.g., in `C:\Program Files (x86)\Steam\userdata\<YourSteamID>\208190\remote`, where `208190` is the AppID for Jacksmith).
    *   If the folder is not found automatically, or if you are using a different version of the game, click the "Choose Jacksmith Folder" button and navigate to the folder where your `.sol` files are stored.
3.  **Select .SOL File:**
    *   After selecting the folder, a list of available `.sol` files (e.g., `jacksmith1.sol`, `jacksmith2.sol`, etc.) will appear. Files with "backup" in their name are hidden.
    *   Click on the `.sol` file you want to edit.
4.  **Navigate and View Data:**
    *   The content of the selected `.sol` file is displayed in a tree structure in the middle panel.
    *   Click the arrows (or double-click items) to expand nested data structures (like dictionaries and lists).
5.  **Edit Data:**
    *   Select an item in the tree structure.
    *   In the right panel ("Edit Item"), you will see the `Key/Index` and `Value`.
    *   Modify the `Value` in the text field. For complex values (lists/dictionaries), the JSON representation is shown, which you can edit directly.
    *   Click the "Update Value" button. The change is immediately processed in the program's data structure **and automatically saved to the `.sol` file.**
6.  **"Add All Parts/Tags" Button:**
    *   This button is context-dependent. To use it, first select the main key `parts` (to unlock all weapon parts) or `newdesigntags` (to unlock all design tags) in the tree structure.
    *   The label below the button indicates which action will be performed.
    *   Click the button to perform the action. Changes are also automatically saved here.
7.  **Manual Save:**
    *   Although changes are automatically saved after each "Update Value" or "Add All Parts/Tags" action, you can also click the "Save (.sol)" button to explicitly write the current state of the data to the selected `.sol` file.
8.  **Export to JSON (Optional):**
    *   There is an "Export (.json)" button. This functionality may not yet be fully implemented. If working, it allows you to export the current data to a `.json` file for analysis or backup.

## Disclaimer

*   **ALWAYS MAKE A BACKUP OF YOUR ORIGINAL .SOL FILES** before making changes with this tool.
*   Incorrect modifications can lead to corrupt save data, potentially causing loss of game progress.
*   Use at your own risk. The developers are not responsible for any damage to your savegames.

## Contributions

Feel free to report issues or submit pull requests if you have improvements.
