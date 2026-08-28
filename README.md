# Cyber PyInstaller Pro

A PySide6-based GUI wrapper for PyInstaller. All command-line options are visualized — pick a script, tick the boxes, and pack your Python script into an exe without touching the terminal.

## Features

- **Full PyInstaller options in a GUI**: onefile, noconsole, UPX compression, debug mode
- **One-click Windows version info**: company, product, version, description, copyright (auto-generates the version file, no manual `.spec` editing)
- **Resource management**: additional data, additional binaries, hidden imports, hooks directory
- **Optional bytecode encryption** with a custom key (leave blank to disable)
- **Real-time build logs** in a background thread (UI never freezes)
- **Config save/load**: settings are restored automatically next launch
- **Preview the command**: click "Generate Command" to see the full PyInstaller command before packing

## Screenshots

(TBD)

## Requirements

- Python 3.9+

```bash
pip install -r requirements.txt
```

> Tip: the "encrypt bytecode" option requires `pycryptodome`, which is already in requirements.txt.

## Run

```bash
python "Pyinstall GUI.py"
```

## Usage

1. On the **Basic** tab, select the main script to pack (output goes to `output\` by default)
2. On the **Pack** tab, tick the options and fill in version info (company, etc.)
3. On the **Resources / Security / Advanced** tabs, add data, binaries, hidden imports, encryption as needed
4. Click **Start Packing** and watch the live log
5. The exe appears in `output\`

Click **Generate Command** first to preview the exact command line.

## Project Structure

```
Pyinstall GUI.py    Main program
requirements.txt    Dependencies
temp_build\         Build temp dir (auto-cleaned)
output\             Output dir for packed exe
```

## License

[MIT](LICENSE)

Copyright (c) 2025 zhongtianshan
