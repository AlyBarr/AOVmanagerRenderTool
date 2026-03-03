# AOV Manager — Houdini + Unreal Pipeline Tool
## File Structure

```
aov_manager/
├── aov_config.py       ← EDIT THIS. All passes, presets, naming logic live here.
├── standalone_app.py   ← Double-click app. Works without Houdini. Requires PySide6.
├── houdini_shelf.py    ← Paste into a Houdini shelf tool. Builds actual ROP nodes.
└── README.md           ← This file.
```

---

## Standalone App

### Requirements
```
pip install PySide6
```

### Run
```
python standalone_app.py
```
Or double-click if your OS associates `.py` with Python.

### What it does
- Full AOV Manager UI (pipeline, presets, passes, naming, output path)
- Generates Houdini Python scripts or UE5 MRQ config text
- Copy to clipboard or Save to file
- No Houdini installation required

---

## Houdini Shelf Tool

### Install
1. Copy `aov_config.py` to `$HOUDINI_USER_PREF_DIR/scripts/python/`
2. In Houdini: right-click any shelf → **New Tool**
3. Go to the **Script** tab
4. Paste the entire contents of `houdini_shelf.py`
5. Click **Accept**

### What it does
- Same full UI as the standalone app
- **"Build in Houdini"** button directly creates the Mantra or Karma ROP node
  in your current Houdini session — no copy-paste required
- Also creates output directories on disk
- "Generate Script" still works for previewing or exporting

### Locating aov_config.py
The shelf tool searches these locations in order:
1. `$HOUDINI_USER_PREF_DIR/scripts/python/`
2. `$HIP` (same folder as your .hip file)

---

## Customising

**Everything is driven by `aov_config.py`.** You never need to edit the app files.

### Add a new standard pass
```python
# In STANDARD_PASSES, add a tuple:
("my_pass", "My Pass", "Description of what it does", True),
#   ^id        ^label     ^description                    ^default on/off
```

### Add a new preset
```python
# In PRESETS, add a new key:
"neon": {
    "label":            "⚡ Neon Mode",
    "color_hex":        "#ff0066",
    "naming_template":  "{project}_{layer}_neon_{pass}_v{version}",
    "folder_template":  "{root}/{project}/neon/{layer}/{pass}/",
    "passes": [
        ("neon_glow", "Neon Glow", "Neon light isolation", True),
    ],
},
```
Then add its color to `PRESET_COLORS` in both `standalone_app.py` and `houdini_shelf.py`:
```python
PRESET_COLORS = {
    ...
    "neon": "#ff0066",
}
```

### Change default naming
```python
# In PRESETS["ocean"] (or whichever preset):
"naming_template": "{project}_{layer}_{pass}.v{version}",
```

---

## Pipeline Notes

### Houdini / Mantra
The generated script uses `vm_picture` for the beauty path and `vm_channel_*`
parameters per AOV. Run it in **Houdini's Python Shell** (Alt+Shift+P).

### Houdini / Karma  
Uses `ri_aov_*` parameters. Run the same way.

### Unreal Engine 5
Generates a `.ini`-style Movie Render Queue config. Import via the MRQ settings
browser, or place in your project's saved config directory.
