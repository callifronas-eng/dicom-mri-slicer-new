#!/usr/bin/env python3
"""
DICOM MRI Image Slicer - GUI Wrapper
Provides a simple GUI for selecting input/output folders and running the slicer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import sys
from dicom_slicer import DICOMSlicer

class DICOMSlicerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM MRI Image Slicer")
        self.root.geometry("700x600")
        
        # Default paths
        script_dir = Path(__file__).resolve().parent.parent
        self.input_path = script_dir / "lab_workflow" / "exams" / "input"
        self.output_path = script_dir / "lab_workflow" / "exams" / "output"
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="DICOM MRI Image Slicer", 
                        font=("Arial", 16, "bold"), fg="blue")
        title.pack(pady=10)
        
        # Input folder selection
        input_frame = tk.LabelFrame(self.root, text="Input Folder (DICOM Files)", 
                                   font=("Arial", 12), padx=10, pady=10)
        input_frame.pack(fill="x", padx=20, pady=5)
        
        self.input_var = tk.StringVar(value=str(self.input_path))
        tk.Entry(input_frame, textvariable=self.input_var, width=60).pack(side="left", padx=5)
        tk.Button(input_frame, text="Browse...", command=self.browse_input).pack(side="left")
        
        # Output folder selection
        output_frame = tk.LabelFrame(self.root, text="Output Folder (Results)", 
                                    font=("Arial", 12), padx=10, pady=10)
        output_frame.pack(fill="x", padx=20, pady=5)
        
        self.output_var = tk.StringVar(value=str(self.output_path))
        tk.Entry(output_frame, textvariable=self.output_var, width=60).pack(side="left", padx=5)
        tk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side="left")
        
        # Process button
        self.process_btn = tk.Button(self.root, text="Process DICOM Files", 
                                     font=("Arial", 14, "bold"),
                                     bg="green", fg="white",
                                     command=self.process,
                                     height=2)
        self.process_btn.pack(pady=20)
        
        # Progress log
        log_frame = tk.LabelFrame(self.root, text="Processing Log", 
                                 font=("Arial", 12), padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             bd=1, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
        
    def browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder with DICOM Files")
        if folder:
            self.input_var.set(folder)
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder for Results")
        if folder:
            self.output_var.set(folder)
            
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def process(self):
        """Process DICOM files in a separate thread"""
        input_folder = self.input_var.get()
        output_folder = self.output_var.get()
        
        if not Path(input_folder).exists():
            messagebox.showerror("Error", f"Input folder does not exist:\n{input_folder}")
            return
            
        # Run in thread to prevent GUI freeze
        thread = threading.Thread(target=self.run_slicer, args=(input_folder, output_folder))
        thread.daemon = True
        thread.start()
        
    def run_slicer(self, input_folder, output_folder):
        """Run the DICOM slicer"""
        self.process_btn.config(state="disabled")
        self.status_var.set("Processing...")
        self.log_text.delete(1.0, tk.END)
        
        try:
            self.log("="*60)
            self.log("DICOM MRI Image Slicer")
            self.log("="*60)
            self.log(f"Input:  {input_folder}")
            self.log(f"Output: {output_folder}")
            self.log("")
            
            # Create slicer and run
            slicer = DICOMSlicer(input_folder, output_folder)
            
            # Redirect print to log
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                success = slicer.run()
            
            output = f.getvalue()
            self.log(output)
            
            if success:
                self.status_var.set("Processing complete!")
                messagebox.showinfo("Success", f"Processing complete!\n\nResults saved to:\n{output_folder}")
            else:
                self.status_var.set("Processing failed!")
                messagebox.showerror("Error", "Processing failed. Check the log for details.")
                
        except Exception as e:
            self.log(f"\nERROR: {str(e)}")
            self.status_var.set("Error!")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.process_btn.config(state="normal")


def main():
    root = tk.Tk()
    app = DICOMSlicerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
