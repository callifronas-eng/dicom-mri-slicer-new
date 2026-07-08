# ============================================================
# ADD THIS METHOD TO registry_win.py
# Add it after the _tool_med5() method (around line 804)
# ============================================================

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


# ============================================================
# MODIFY show_tools_menu() method (around line 764)
# ============================================================
# Change this line:
#     menu.add_command(label="ΕΠΕΞΕΡΓΑΣΙΑ PDF→OCR", command=self._tool_edit_lab_results)
# 
# Add this line after it:
#     menu.add_command(label="DICOM SLICER (MRI)", command=self._tool_dicom_slicer)
#
# So it becomes:
#     menu.add_command(label="ΕΠΕΞΕΡΓΑΣΙΑ PDF→OCR", command=self._tool_edit_lab_results)
#     menu.add_command(label="DICOM SLICER (MRI)",  command=self._tool_dicom_slicer)
#     menu.add_separator()
#     menu.add_command(label="MED5", command=self._tool_med5)
