#!/usr/bin/env python3
"""
DICOM MRI Image Slicer - GUI Wrapper
Provides a simple GUI for selecting input/output folders and running the slicer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont
from pathlib import Path
import threading
import sys
from dicom_slicer import DICOMSlicer

# Color constants matching MEDICASOFT-ASCLEPIUS style
BEIGE_COLOR = "#F5E6C4"
BLUE_COLOR = "#4169E1"  # Royal Blue
BUTTON_BG = "white"
BUTTON_FG = "blue"
BORDER_COLOR = "blue"

class DICOMSlicerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM MRI Image Slicer - Επεξεργασία Εικόνων")
        self.root.geometry("800x650")
        self.root.configure(bg=BEIGE_COLOR)

        # Default paths - use absolute path from script location
        script_dir = Path(__file__).resolve().parent.parent
        self.input_path = script_dir / "lab_workflow" / "exams" / "input"
        self.output_path = script_dir / "lab_workflow" / "exams" / "output"

        # Create folders if they don't exist
        self.input_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Create blue border around window
        self._border_strips = []
        self._create_blue_border()

        self.create_widgets()

    def _create_blue_border(self, thickness=4, color=BORDER_COLOR):
        """Create a blue border around the window (like registry_win.py)"""
        edges = (
            dict(relx=0, rely=0, x=0, y=0, relwidth=1, height=thickness),
            dict(relx=0, rely=0, x=0, y=0, width=thickness, relheight=1),
            dict(relx=0, rely=1, x=0, y=-thickness, relwidth=1, height=thickness),
            dict(relx=1, rely=0, x=-thickness, y=0, width=thickness, relheight=1),
        )
        corners = (
            dict(relx=0, rely=0, x=0, y=0, width=thickness, height=thickness),
            dict(relx=1, rely=0, x=-thickness, y=0, width=thickness, height=thickness),
            dict(relx=0, rely=1, x=0, y=-thickness, width=thickness, height=thickness),
            dict(relx=1, rely=1, x=-thickness, y=-thickness, width=thickness, height=thickness),
        )
        for kw in edges + corners:
            strip = tk.Frame(self.root, bg=color, bd=0, highlightthickness=0)
            strip.place(**kw)
            self._border_strips.append(strip)
        self._raise_border()
        self.root.bind("<Configure>", lambda e: self._raise_border(), add="+")

    def _raise_border(self):
        """Keep the border on top"""
        for strip in self._border_strips:
            strip.lift()

    def _draw_pill_button(self, canvas, bg, fg):
        """Draw a pill-shaped button (like registry_win.py round tabs)"""
        canvas.delete("all")
        w, h = canvas._width, canvas._height
        r = h / 2
        outline = "#999999"
        # Filled body
        canvas.create_oval(0, 0, h-1, h-1, fill=bg, outline=bg)
        canvas.create_oval(w-h, 0, w-1, h-1, fill=bg, outline=bg)
        canvas.create_rectangle(r, 0, w-r, h-1, fill=bg, outline=bg)
        # Outline
        canvas.create_arc(0, 0, h-1, h-1, start=90, extent=180, style='arc', outline=outline)
        canvas.create_arc(w-h, 0, w-1, h-1, start=270, extent=180, style='arc', outline=outline)
        canvas.create_line(r, 0, w-r, 0, fill=outline)
        canvas.create_line(r, h-1, w-r, h-1, fill=outline)
        # Label
        canvas.create_text(w/2, h/2, text=canvas._text, font=canvas._font, fill=fg)

    def create_widgets(self):
        # Blue band with title and round buttons (like diagnosis.py)
        title_band = tk.Frame(self.root, bg=BLUE_COLOR, height=80)
        title_band.pack(fill="x", padx=8, pady=8)
        title_band.pack_propagate(False)

        # Title in the blue band
        title = tk.Label(title_band, text="DICOM MRI Image Slicer",
                        font=("Arial", 18, "bold"), fg="white", bg=BLUE_COLOR)
        title.pack(pady=5)

        # Button container for round buttons
        button_container = tk.Frame(title_band, bg=BLUE_COLOR)
        button_container.pack(pady=5)

        # Create round pill-shaped buttons
        self._create_round_button(button_container, "Επιλογή Εισόδου", self.browse_input, width=140)
        self._create_round_button(button_container, "Επιλογή Εξόδου", self.browse_output, width=140)
        self._create_round_button(button_container, "Επεξεργασία", self.process, width=120)

        # Main content area
        content_frame = tk.Frame(self.root, bg=BEIGE_COLOR)
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Input folder display
        input_frame = tk.Frame(content_frame, bg=BEIGE_COLOR)
        input_frame.pack(fill="x", pady=5)

        tk.Label(input_frame, text="Φάκελος Εισόδου (DICOM):",
                font=("Arial", 12, "bold"), fg="blue", bg=BEIGE_COLOR).pack(anchor="w")

        self.input_var = tk.StringVar(value=str(self.input_path))
        input_entry = tk.Entry(input_frame, textvariable=self.input_var,
                              font=("Arial", 11), relief="solid", bd=1)
        input_entry.pack(fill="x", pady=2)

        # Output folder display
        output_frame = tk.Frame(content_frame, bg=BEIGE_COLOR)
        output_frame.pack(fill="x", pady=5)

        tk.Label(output_frame, text="Φάκελος Εξόδου (Αποτελέσματα):",
                font=("Arial", 12, "bold"), fg="blue", bg=BEIGE_COLOR).pack(anchor="w")

        self.output_var = tk.StringVar(value=str(self.output_path))
        output_entry = tk.Entry(output_frame, textvariable=self.output_var,
                               font=("Arial", 11), relief="solid", bd=1)
        output_entry.pack(fill="x", pady=2)

        # Progress log with blue border
        log_outer = tk.Frame(content_frame, bg=BLUE_COLOR, bd=2, relief="solid")
        log_outer.pack(fill="both", expand=True, pady=10)

        log_header = tk.Label(log_outer, text="Αρχείο Καταγραφής",
                             font=("Arial", 12, "bold"), fg="white", bg=BLUE_COLOR)
        log_header.pack(fill="x", pady=2)

        self.log_text = scrolledtext.ScrolledText(log_outer, height=12, wrap=tk.WORD,
                                                  font=("Courier", 10), bg="white")
        self.log_text.pack(fill="both", expand=True, padx=2, pady=2)

        # Status bar
        self.status_var = tk.StringVar(value="Έτοιμο")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             bd=1, relief="sunken", anchor="w",
                             bg=BEIGE_COLOR, fg="green", font=("Arial", 10))
        status_bar.pack(side="bottom", fill="x", padx=8, pady=(0, 8))

    def _create_round_button(self, parent, text, command, width=110, height=32):
        """Create a round pill-shaped button with white background and blue text"""
        canvas = tk.Canvas(parent, width=width, height=height, bg=BLUE_COLOR,
                          bd=0, highlightthickness=0)
        canvas._text = text
        canvas._font = ('Helvetica', 11, 'bold')
        canvas._width = width
        canvas._height = height
        canvas._command = command
        canvas._is_hover = False

        # Initial draw
        self._draw_pill_button(canvas, BUTTON_BG, BUTTON_FG)
        canvas.pack(side="left", padx=4)

        # Hover effects
        canvas.bind("<Enter>", lambda e: self._on_button_enter(canvas))
        canvas.bind("<Leave>", lambda e: self._on_button_leave(canvas))
        canvas.bind("<Button-1>", lambda e: command())

        return canvas

    def _on_button_enter(self, canvas):
        """Button hover effect"""
        canvas._is_hover = True
        self._draw_pill_button(canvas, "#E8F4FF", BUTTON_FG)

    def _on_button_leave(self, canvas):
        """Button leave effect"""
        canvas._is_hover = False
        self._draw_pill_button(canvas, BUTTON_BG, BUTTON_FG)

    def browse_input(self):
        initial_dir = str(self.input_path) if self.input_path.exists() else str(Path.home())
        folder = filedialog.askdirectory(
            title="Select Input Folder with DICOM Files",
            initialdir=initial_dir
        )
        if folder:
            self.input_var.set(folder)

    def browse_output(self):
        initial_dir = str(self.output_path) if self.output_path.exists() else str(Path.home())
        folder = filedialog.askdirectory(
            title="Select Output Folder for Results",
            initialdir=initial_dir
        )
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
            messagebox.showerror("Σφάλμα", f"Ο φάκελος εισόδου δεν υπάρχει:\n{input_folder}")
            return

        # Run in thread to prevent GUI freeze
        thread = threading.Thread(target=self.run_slicer, args=(input_folder, output_folder))
        thread.daemon = True
        thread.start()
        
    def run_slicer(self, input_folder, output_folder):
        """Run the DICOM slicer"""
        self.status_var.set("Επεξεργασία σε εξέλιξη...")
        self.log_text.delete(1.0, tk.END)

        try:
            self.log("="*60)
            self.log("DICOM MRI Image Slicer - Επεξεργασία Εικόνων")
            self.log("="*60)
            self.log(f"Είσοδος:  {input_folder}")
            self.log(f"Έξοδος:   {output_folder}")
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
                self.status_var.set("Η επεξεργασία ολοκληρώθηκε με επιτυχία!")
                messagebox.showinfo("Επιτυχία", f"Η επεξεργασία ολοκληρώθηκε!\n\nΤα αποτελέσματα αποθηκεύτηκαν στο:\n{output_folder}")
            else:
                self.status_var.set("Η επεξεργασία απέτυχε!")
                messagebox.showerror("Σφάλμα", "Η επεξεργασία απέτυχε. Ελέγξτε το αρχείο καταγραφής.")

        except Exception as e:
            self.log(f"\nΣΦΑΛΜΑ: {str(e)}")
            self.status_var.set("Σφάλμα!")
            messagebox.showerror("Σφάλμα", f"Προέκυψε σφάλμα:\n{str(e)}")
        finally:
            pass


def main():
    root = tk.Tk()
    app = DICOMSlicerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
