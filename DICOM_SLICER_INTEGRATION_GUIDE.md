# 🔧 DICOM Slicer Integration Guide

## Add DICOM Slicer to your registry_win.py Tools Menu

Follow these steps to integrate the DICOM Slicer into your existing application.

---

## Step 1: Update the `show_tools_menu()` method

**Location:** Around line 764 in `registry_win.py`

**Find this:**
```python
def show_tools_menu(self):
    """ Εργαλεία tab — drop-down submenu. """
    menu = tk.Menu(self.win, tearoff=0)
    menu.add_command(label="ΕΠΕΞΕΡΓΑΣΙΑ ΕΙΚΟΝΩΝ",            command=self._tool_edit_images)
    menu.add_command(label="ΕΠΕΞΕΡΓΑΣΙΑ PDF→OCR",            command=self._tool_edit_lab_results)
    menu.add_separator()
    menu.add_command(label="MED5",                           command=self._tool_med5)
    btn = self.tools_button
    x = btn.winfo_rootx()
    y = btn.winfo_rooty() + btn.winfo_height()
    menu.tk_popup(x, y)
```

**Replace with:**
```python
def show_tools_menu(self):
    """ Εργαλεία tab — drop-down submenu. """
    menu = tk.Menu(self.win, tearoff=0)
    menu.add_command(label="ΕΠΕΞΕΡΓΑΣΙΑ ΕΙΚΟΝΩΝ",            command=self._tool_edit_images)
    menu.add_command(label="ΕΠΕΞΕΡΓΑΣΙΑ PDF→OCR",            command=self._tool_edit_lab_results)
    menu.add_command(label="DICOM SLICER (MRI)",             command=self._tool_dicom_slicer)
    menu.add_separator()
    menu.add_command(label="MED5",                           command=self._tool_med5)
    btn = self.tools_button
    x = btn.winfo_rootx()
    y = btn.winfo_rooty() + btn.winfo_height()
    menu.tk_popup(x, y)
```

---

## Step 2: Add the `_tool_dicom_slicer()` method

**Location:** After the `_tool_med5()` method (around line 804)

**Add this new method:**
```python
# -----------------------------------------------------------
def _tool_dicom_slicer(self):
    """ Launch the DICOM MRI Image Slicer application. """
    script_dir = Path(__file__).resolve().parent
    script = script_dir / "dicom-slicer" / "SLICER_DICOM" / "dicom_slicer.py"
    
    if not script.exists():
        messagebox.showerror("DICOM Slicer", f"Δεν βρέθηκε το αρχείο:\n{script.name}")
        return
    
    py = "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
    if not Path(py).exists():
        py = sys.executable
    
    try:
        subprocess.Popen(
            [py, str(script)],
            cwd=str(script.parent.parent),  # Run from dicom-slicer/ directory
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        messagebox.showerror("DICOM Slicer", f"Αποτυχία εκκίνησης:\n{e}")
```

---

## Step 3: Verify the folder structure

Make sure your AUGMENT CODE DISK has this structure:

```
AUGMENT CODE DISK/
├── registry_win.py                        ← Your main registry file
├── dicom-slicer/                          ← DICOM Slicer project
│   ├── SLICER_DICOM/
│   │   └── dicom_slicer.py               ← The script to launch
│   ├── DICOM_VIEWER/
│   │   └── dicom_viewer.py
│   └── lab_workflow/
│       └── exams/
│           ├── input/                     ← Put MRI files here
│           └── output/                    ← Results appear here
└── (other files...)
```

---

## 📝 Summary of Changes

1. **Added menu item** "DICOM SLICER (MRI)" to the Tools menu
2. **Created handler method** `_tool_dicom_slicer()` that launches the DICOM slicer
3. **Follows same pattern** as your existing PDF→OCR integration

---

## ✅ After Integration

Users can now:
1. Click **Εργαλεία** (Tools) button
2. Select **DICOM SLICER (MRI)** from the dropdown
3. The DICOM Slicer application will launch in a new window
4. Process MRI DICOM files from `lab_workflow/exams/input/`
5. View results in `lab_workflow/exams/output/`

---

## 🧪 Testing

After making these changes:

```bash
# On MacBook or Mac Mini
cd '/Users/michaelcallifronas/AUGMENT CODE DISK'

# Run your registry application
python3 registry_win.py

# Click: Εργαλεία → DICOM SLICER (MRI)
# The DICOM Slicer should launch!
```

---

**Need help?** Let me know if you encounter any errors!
