# 📝 Final Changes for registry_win.py

## Edit This File:
```
/Users/michaelcallifronas/AUGMENT CODE DISK/registry_win.py
```

---

## ✏️ Change #1: Update show_tools_menu() method

**Location:** Around line 768

**BEFORE:**
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

**AFTER:**
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

**What changed:** Added one line:
```python
menu.add_command(label="DICOM SLICER (MRI)",             command=self._tool_dicom_slicer)
```

---

## ✏️ Change #2: Add new method _tool_dicom_slicer()

**Location:** After the `_tool_med5()` method (around line 805)

**ADD THIS COMPLETE METHOD:**

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

## 🧪 After Editing - Test It:

```bash
cd '/Users/michaelcallifronas/AUGMENT CODE DISK'
python3 registry_win.py

# Click: Εργαλεία → DICOM SLICER (MRI)
# Should launch the DICOM Slicer!
```

---

## 📂 Required Folder Structure:

```
AUGMENT CODE DISK/
├── registry_win.py              ← Edit this file
└── dicom-slicer/                ← Must exist here
    └── SLICER_DICOM/
        └── dicom_slicer.py      ← Will be launched
```

---

## ✅ Verification Checklist:

- [ ] GitHub repo renamed to `dicom-mri-slicer`
- [ ] Updated git remote URL on MacBook
- [ ] Edited `registry_win.py` (2 changes above)
- [ ] Tested: Click Εργαλεία → DICOM SLICER (MRI)
- [ ] DICOM Slicer launches successfully

---

**All changes documented! Ready to implement!** 🚀
