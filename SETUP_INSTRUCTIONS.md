# 🔧 Complete Setup Instructions for DICOM Slicer + Registry Integration

## 📂 **Correct Folder Structure:**

```
AUGMENT CODE DISK/                          ← Your main working directory
├── registry_win.py                         ← Main registry file (EDIT THIS)
├── dicom-slicer/                           ← Git repo (from GitHub)
│   ├── .git/
│   ├── SLICER_DICOM/
│   │   └── dicom_slicer.py                ← Launch target
│   ├── DICOM_VIEWER/
│   │   └── dicom_viewer.py
│   ├── lab_workflow/
│   │   └── exams/
│   │       ├── input/                      ← Put MRI files here
│   │       └── output/                     ← Results appear here
│   ├── README.md
│   ├── requirements.txt
│   └── (other DICOM project files)
└── (your other projects)
```

---

## 🚀 **Setup Steps on MacBook:**

### **Step 1: Pull Latest Changes**

```bash
cd '/Users/michaelcallifronas/AUGMENT CODE DISK/dicom-slicer'
git pull origin main
```

### **Step 2: Edit Your Main registry_win.py**

The file to edit is:
```
/Users/michaelcallifronas/AUGMENT CODE DISK/registry_win.py
```

**NOT:**
```
/Users/michaelcallifronas/AUGMENT CODE DISK/dicom-slicer/registry_win.py
```

---

## ✏️ **Changes to Make in registry_win.py:**

### **Change #1: Update show_tools_menu() method (Line ~768)**

**Find:**
```python
menu.add_command(label="ΕΠΕΞΕΡΓΑΣΙΑ PDF→OCR", command=self._tool_edit_lab_results)
menu.add_separator()
menu.add_command(label="MED5", command=self._tool_med5)
```

**Change to:**
```python
menu.add_command(label="ΕΠΕΞΕΡΓΑΣΙΑ PDF→OCR", command=self._tool_edit_lab_results)
menu.add_command(label="DICOM SLICER (MRI)",  command=self._tool_dicom_slicer)
menu.add_separator()
menu.add_command(label="MED5", command=self._tool_med5)
```

---

### **Change #2: Add new method after _tool_med5() (After line ~805)**

**Add this complete method:**

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

## 🧪 **Testing:**

```bash
# Run your main registry application
cd '/Users/michaelcallifronas/AUGMENT CODE DISK'
python3 registry_win.py

# Then:
# 1. Click "Εργαλεία" (Tools)
# 2. Click "DICOM SLICER (MRI)"
# 3. The DICOM Slicer should launch!
```

---

## ✅ **Result:**

Your Tools menu will show:
- ΕΠΕΞΕΡΓΑΣΙΑ ΕΙΚΟΝΩΝ
- ΕΠΕΞΕΡΓΑΣΙΑ PDF→OCR
- **DICOM SLICER (MRI)** ← NEW!
- ─────────────
- MED5

---

## 📝 **Notes:**

- `registry_win.py` stays in **AUGMENT CODE DISK/**
- `dicom-slicer/` is a **Git repository**
- The integration code finds `dicom_slicer.py` using **relative path** from registry_win.py location
- Both MacBook and Mac Mini can use the same setup (just clone dicom-slicer repo on both machines)

---

## 🔄 **Syncing Between Machines:**

**MacBook Pro:**
```bash
cd '/Users/michaelcallifronas/AUGMENT CODE DISK/dicom-slicer'
git pull
```

**Mac Mini:**
```bash
cd '/Volumes/SAMS. EVO 2022-23/michaelcallifronas/AUGMENT CODE DISK/dicom-slicer'
git pull
```

---

**Ready to edit registry_win.py? The code snippets are above!** ✨
