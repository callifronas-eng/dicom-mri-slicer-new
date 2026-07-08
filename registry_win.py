michaelcallifronas@MacBook-Pro-2020 AUGMENT CODE DISK % cat registry_win.py
#***********************************************
# registry_win.py
# implements class RegistryWin:
# a window that displays the registry entry
# of a patient
#
# Keyboard toggles:
#   Cmd+G   (macOS)   ->  show / hide the diagonal-hatch panel on the right
#   Ctrl+G  (Win/Lin) ->  same
#***********************************************

# imports from external packages
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import unicodedata
from pathlib import Path

# imports from our code
from constants import BEIGE_COLOR, GRID_COLOR
from editform import EditForm
from db_func import WindowsBase, SessionBase
from db_func import SessionPatients, Patient #, PatientText, SessionText

from tab_frame import TabFrame

from history_win import HistoryWin
from med5_window import Med5Window
from ui_tooltip import EllipseToolTip, load_descriptions


# -----------------------------------------------------------
# macOS Text Input Sources (TIS) helper — switches keyboard layout directly
# via the Carbon framework, with no keystroke simulation and no Accessibility
# permission. Lazily initialised so non-macOS imports stay clean.
# -----------------------------------------------------------
class _TIS:
    _ready = None  # None=untried, True=loaded, False=unavailable
    _carbon = None
    _cf = None
    _id_key = None

    @classmethod
    def _load(cls):
        if cls._ready is not None:
            return cls._ready
        try:
            import ctypes
            from ctypes import c_void_p, c_int32, c_long, c_char_p, c_bool
            cls._carbon = ctypes.CDLL(
                '/System/Library/Frameworks/Carbon.framework/Carbon')
            cls._cf = ctypes.CDLL(
                '/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
            cf, carbon = cls._cf, cls._carbon
            cf.CFArrayGetCount.restype = c_long
            cf.CFArrayGetCount.argtypes = [c_void_p]
            cf.CFArrayGetValueAtIndex.restype = c_void_p
            cf.CFArrayGetValueAtIndex.argtypes = [c_void_p, c_long]
            cf.CFStringGetLength.restype = c_long
            cf.CFStringGetLength.argtypes = [c_void_p]
            cf.CFStringGetCString.restype = c_bool
            cf.CFStringGetCString.argtypes = [c_void_p, c_char_p, c_long, c_int32]
            cf.CFRelease.restype = None
            cf.CFRelease.argtypes = [c_void_p]
            carbon.TISCreateInputSourceList.restype = c_void_p
            carbon.TISCreateInputSourceList.argtypes = [c_void_p, c_bool]
            carbon.TISGetInputSourceProperty.restype = c_void_p
            carbon.TISGetInputSourceProperty.argtypes = [c_void_p, c_void_p]
            carbon.TISSelectInputSource.restype = c_int32
            carbon.TISSelectInputSource.argtypes = [c_void_p]
            carbon.TISCopyCurrentKeyboardInputSource.restype = c_void_p
            cls._id_key = c_void_p.in_dll(carbon, 'kTISPropertyInputSourceID')
            cls._ctypes = ctypes
            cls._ready = True
        except Exception:
            cls._ready = False
        return cls._ready

    @classmethod
    def _cfstr(cls, ref):
        if not ref:
            return None
        n = cls._cf.CFStringGetLength(ref)
        buf = cls._ctypes.create_string_buffer(n * 4 + 1)
        if cls._cf.CFStringGetCString(ref, buf, len(buf), 0x08000100):
            return buf.value.decode('utf-8')
        return None

    @classmethod
    def current_id(cls):
        if not cls._load():
            return None
        src = cls._carbon.TISCopyCurrentKeyboardInputSource()
        if not src:
            return None
        sid = cls._cfstr(cls._carbon.TISGetInputSourceProperty(src, cls._id_key))
        cls._cf.CFRelease(src)
        return sid

    @classmethod
    def select_by_substring(cls, needle):
        """Select the first enabled input source whose ID contains `needle`
        (case-insensitive). Returns True on success."""
        if not cls._load():
            return False
        arr = cls._carbon.TISCreateInputSourceList(None, False)
        if not arr:
            return False
        try:
            n = cls._cf.CFArrayGetCount(arr)
            needle = needle.lower()
            for i in range(n):
                src = cls._cf.CFArrayGetValueAtIndex(arr, i)
                sid = cls._cfstr(
                    cls._carbon.TISGetInputSourceProperty(src, cls._id_key))
                if sid and needle in sid.lower():
                    return cls._carbon.TISSelectInputSource(src) == 0
            return False
        finally:
            cls._cf.CFRelease(arr)

# ------------------
class RegistryWin():
    # -----------------------------------------------------------
    def __init__(self, root, win, modal=False):
        self.root = root
        self.win = win
        self.modal = modal

        self.navigation_history = []
        self.current_history_index = -1

        self.set_title("Μητρώο")
        self.win.configure(bg=BEIGE_COLOR)
        self.doctor_no = "1"

        self.win.resizable(True, True)
        self.create_editform()
        self.create_status()
        self.create_tabs()
        self.create_search()

        self.create_diagonal_panel()
        self.set_bindings()
        self.load_last_patient()
        self._draw_window_border()

    # -----------------------------------------------------------
    def create_diagonal_panel(self, spacing=18, line_width=1, color=GRID_COLOR):
        """ Fill the right empty area (columns 2-3, below the search bar)
            with a beige canvas cross-hatched by thin diagonal blue lines.
            Re-drawn on every resize so the pattern always fits. """
        n = len(self.form_spec)
        canvas = tk.Canvas(self.win, bg=BEIGE_COLOR, bd=0, highlightthickness=0)
        canvas.grid(row=2, column=2, columnspan=2, rowspan=n-1,
                    sticky='nsew', padx=(2, 10), pady=2)
        self._diag_canvas   = canvas
        self._diag_spacing  = spacing
        self._diag_width    = line_width
        self._diag_color    = color
        canvas.bind("<Configure>", lambda e: self._redraw_diagonal())
        canvas.grid_remove()      # start hidden; Cmd+G / Ctrl+G makes it appear

    # -----------------------------------------------------------
    def _redraw_diagonal(self):
        canvas = self._diag_canvas
        canvas.delete("hatch")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w <= 1 or h <= 1:
            return
        s, c, lw = self._diag_spacing, self._diag_color, self._diag_width
        # Top-left -> bottom-right
        for x in range(-h, w, s):
            canvas.create_line(x, 0, x + h, h, fill=c, width=lw, tags="hatch")
        # Top-right -> bottom-left
        for x in range(0, w + h, s):
            canvas.create_line(x, 0, x - h, h, fill=c, width=lw, tags="hatch")

    # -----------------------------------------------------------
    def toggle_diagonal_panel(self, event=None):
        """ Cmd+G / Ctrl+G toggle: show / hide the diagonal-hatch panel.
            grid_remove() preserves all grid options so grid() restores it
            in the same row/column/span/sticky/padding as before. """
        canvas = getattr(self, "_diag_canvas", None)
        if canvas is None:
            print("[toggle_diagonal_panel] no canvas")
            return
        if canvas.winfo_manager() == "grid":   # currently visible -> hide
            canvas.grid_remove()
            print("[toggle_diagonal_panel] hidden")
        else:                                  # currently hidden  -> show
            canvas.grid()
            self._redraw_diagonal()
            print("[toggle_diagonal_panel] shown")

    # -----------------------------------------------------------
    # Blue frame around the whole window: 4 edge strips + 4 corner
    # squares placed on top of every other widget. The Configure binding
    # re-lifts the strips after resizes so widgets cannot cover them.
    def _draw_window_border(self, thickness=3, color="blue"):
        self._border_strips = []
        if thickness <= 0:
            return
        edges = (
            dict(relx=0, rely=0, relwidth=1,  height=thickness),
            dict(relx=0, rely=1, y=-thickness, relwidth=1,  height=thickness),
            dict(relx=0, rely=0, width=thickness, relheight=1),
            dict(relx=1, rely=0, x=-thickness, width=thickness, relheight=1),
        )
        corners = (
            dict(relx=0, rely=0, x=0,          y=0,          width=thickness, height=thickness),
            dict(relx=1, rely=0, x=-thickness, y=0,          width=thickness, height=thickness),
            dict(relx=0, rely=1, x=0,          y=-thickness, width=thickness, height=thickness),
            dict(relx=1, rely=1, x=-thickness, y=-thickness, width=thickness, height=thickness),
        )
        for kw in edges + corners:
            strip = tk.Frame(self.win, bg=color, bd=0, highlightthickness=0)
            strip.place(**kw)
            self._border_strips.append(strip)
        self._raise_border()
        self.win.bind("<Configure>", lambda e: self._raise_border(), add="+")

    # -----------------------------------------------------------
    def _raise_border(self):
        for strip in getattr(self, "_border_strips", ()):
            try:
                strip.lift()
            except tk.TclError:
                pass

    # -----------------------------------------------------------
    def set_title(self,title):
        self.win.title(title)

    # -----------------------------------------------------------
    def show_history(self, patient_id_var, modal):
        if not patient_id_var.get().strip():
            messagebox.showwarning("Προσοχή", "Πρέπει να επιλέξετε πρώτα έναν ασθενή")
            return
        history_win = HistoryWin(self.win, patient_id_var.get(), True, self.status_var, self.status_bar.winfo_height(), self.doctor_no)

    # -----------------------------------------------------------
    def set_bindings(self):
        self.win.bind("<Button-1>", self.handle_click)

        self.win.bind("<Shift-Left>", lambda e: self.navigate_patient("prev"))  # Regular up arrow for ID navigation
        self.win.bind("<Shift-Right>", lambda e: self.navigate_patient("next"))  # Regular down arrow for ID navigation
        self.win.bind("<Shift-Up>", lambda e: self.navigate_patient_alphabetically("prev"))  # Shift+Up for previous name
        self.win.bind("<Shift-Down>", lambda e: self.navigate_patient_alphabetically("next"))  # Shift+Down for next name
        # bind_all so the toggle works even when an Entry has focus
        self.win.bind_all("<Command-g>",       self.toggle_diagonal_panel)                       # Cmd+G        (macOS)
        self.win.bind_all("<Command-G>",       self.toggle_diagonal_panel)                       # Cmd+Shift+G  (macOS) - diagnostic fallback
        self.win.bind_all("<Control-g>",       self.toggle_diagonal_panel)                       # Ctrl+G       (Win/Lin)
        self.win.bind_all("<Command-slash>",   self.toggle_diagonal_panel)                       # Cmd+/        (macOS) - safe fallback

    # -----------------------------------------------------------
    # -----------------------------------------------------------
    # Editform-related methods:

    # -----------------------------------------------------------
    def create_editform(self):
        self.form_spec = [
            ["Αριθμός ασθενή",			"patient_id",	False],			# False: readonly
            ["Eπώνυμο",				"last_name"],
            ["Όνομα",				"first_name"],
            ["Αριθμός τηλεφώνου",		"phone_number"],
            ["Διευθυνση EMAIL",			"email"],
            ["Όνομα οδού/αριθμός",		"address"],
            ["Ταχυδρομικός κώδικας",		"postal_code"],
            ["Πόλη",				"city"],
            ["Νομός",				"region"],
            ["Ημερομηνία γέννησης",		"birth_date"],
            ["ΑΜΚΑ",				"amka"],
            ["Ημερομηνία τελευταίας συνταγής",	"last_prescription_date"],
            ["Ημερομηνία τελευταίας επίσκεψης",	"last_visit_date"],
            ["Φύλο",				"gender"],
            ["Ασφαλιστικός Φορέας",		"insurance_org"],
            ["Τύπος ασθενούς",			"patient_type"],
            ["Άμεσος/Έμμεσος",			"direct_indirect"],
            ["Αριθμός μητρώου Φορέα",		"registry_number"],
            ["Ημερομηνία λήξης ασφάλισης",	"insurance_expiry"]
        ]

        self.editform = EditForm(self.win, 30, lambda e: self.auto_save_patient())
        self.editform.add_from_spec(self.form_spec)

        self.win.grid_rowconfigure(len(self.form_spec), weight=1)
        self.win.grid_rowconfigure(len(self.form_spec)+1, weight=0)

        self.win.grid_columnconfigure(1, weight=1)
        self.win.grid_columnconfigure(3, weight=1)

        self.win.columnconfigure(1, weight=1)
        self.win.columnconfigure(3, weight=1)

        self.editform.create_widgets()

    # -----------------------------------------------------------
    def auto_save_patient(self, event=None):
        try:
            patient_id = int(self.editform.get_var("patient_id").get())
            with SessionPatients() as session:
                patient = session.query(Patient).filter_by(patient_id=patient_id).first()
                if not patient:
                    patient = Patient(patient_id=patient_id)
                self.editform.write_to_db(patient)
                session.merge(patient)
                session.commit()
                self.show_status("Αυτόματη αποθήκευση ολοκληρώθηκε!")
        except Exception as e:
            self.show_status(f"Σφάλμα: {str(e)}")

    # -----------------------------------------------------------
    def load_patient_data(self, event):
        patient_id = self.editform.get_var("patient_id").get().strip()
        if not patient_id.isdigit():
           return
        patient_id = int(patient_id)
        session = SessionPatients()
        patient = session.query(Patient).filter_by(patient_id=patient_id).first()
        session.close()
        if patient:
            self.editform.read_from_db(patient)
            self.add_to_nav_history(patient_id)
            self.set_title("Μητρώο ασθενών - "+patient.last_name+" "+patient.first_name)

    # -----------------------------------------------------------
    def load_last_patient(self):
       """ Load data of the last patient in the DB """
       try:
           session = SessionPatients()
           last_patient = session.query(Patient).order_by(Patient.patient_id.desc()).first()
           session.close()

           if last_patient:
               self.editform.get_var("patient_id").set(last_patient.patient_id)
               self.load_patient_data(None)  # This will populate all fields
               self.show_status(f"Φορτώθηκε τελευταίος ασθενής: {last_patient.last_name} {last_patient.first_name}")
               self.set_title("Μητρώο ασθενών - "+last_patient.last_name+" "+last_patient.first_name)
       except Exception as e:
           self.show_status(f"Σφάλμα φόρτωσης: {str(e)}")

    # -----------------------------------------------------------
    def add_new_patient(self):
        """ Will NOT add row to DB - auto_save_patient() will do it """
        session = SessionPatients()
        last_patient = session.query(Patient).order_by(Patient.patient_id.desc()).first()
        next_id = last_patient.patient_id + 1 if last_patient else 1
        self.editform.clear_fields()
        self.editform.get_var("patient_id").set(next_id)
        session.close()
        messagebox.showinfo("New Patient", f"New patient created with ID: {next_id}")

    # -----------------------------------------------------------
    def navigate_patient_alphabetically(self, direction):
        """ Fetch from DB prev/next patient alphabetically """
        try:
            session = SessionPatients()
            all_patients = session.query(Patient).all()

            # Greek-aware sorting in Python
            all_patients.sort(key=lambda p: (p.last_name.lower(), p.first_name.lower()))

            current_id = int(self.editform.get_var("patient_id").get()) if self.editform.get_var("patient_id").get() else None
            current_index = next((i for i, p in enumerate(all_patients) if p.patient_id == current_id), 0)

            if direction == "next":
                new_index = (current_index + 1) % len(all_patients)
            else:
                new_index = (current_index - 1) % len(all_patients)

            patient = all_patients[new_index]
            self.editform.get_var("patient_id").set(patient.patient_id)
            self.load_patient_data(None)
            self.show_status(f"Επιλογή: {patient.last_name} {patient.first_name}")

        except Exception as e:
            self.show_status(f"Σφάλμα: {str(e)}")
        finally:
            session.close()

    # -----------------------------------------------------------
    def previous_patient(self):
        self.navigate_patient_alphabetically("prev")

    # -----------------------------------------------------------
    def next_patient(self):
        self.navigate_patient_alphabetically("next")

    # -----------------------------------------------------------
    def navigate_patient(self, direction):
        """ Fetch from DB prev/next patient by Patient ID """
        all_ids = self.get_all_patient_ids()
        if not all_ids:
            return

        # Ensure current index is synced with selected ID
        try:
            current_id = int(self.editform.get_var("patient_id").get())
            current_patient_index = all_ids.index(current_id)
        except:
            current_patient_index = 0

        # Move index
        if direction == "next":
            current_patient_index = min(current_patient_index + 1, len(all_ids) - 1)
        elif direction == "prev":
            current_patient_index = max(current_patient_index - 1, 0)

        # Update UI
        self.editform.get_var("patient_id").set(all_ids[current_patient_index])
        self.load_patient_data(None)

    # -----------------------------------------------------------
    def get_all_patient_ids(self):
        """ Return sorted array of all patient IDs (read from DB) """
        session = SessionPatients()
        ids = [p.patient_id for p in session.query(Patient).order_by(Patient.patient_id).all()]
        session.close()
        return ids

    # -----------------------------------------------------------
    # -----------------------------------------------------------
    # Status bar-related methods:

    # -----------------------------------------------------------
    def create_status(self):
        """ Create fontrols for status bar """
        size = len(self.form_spec)
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self.win, textvariable=self.status_var, bd=1, relief="sunken",
            anchor="w", bg=BEIGE_COLOR, fg="green"
        )

        self.status_bar.grid(
            row=size+1,					#size=len(labels)
            column=0,
            columnspan=4,
            sticky="ew",
            padx=5,
            pady=5)

    # -----------------------------------------------------------
    def show_status(self, message, delay_ms=15000):
        """Show temporary status message that clears after delay"""
        self.status_var.set(message)
        if delay_ms > 0:
            self.root.after(delay_ms, lambda: self.status_var.set(""))

    # -----------------------------------------------------------
    # -----------------------------------------------------------
    # Tabs-related methods:

    # -----------------------------------------------------------
    def create_tabs(self):
        """ Top button bar: 10 pill-shaped, equal-size tabs (20% smaller
            than the old rectangular tabs), packed right-to-left so the
            user reads them as #1 .. #10 going from right to left. """
        tab_frame = TabFrame(self.win, height=32)
        self._tab_frame = tab_frame

        # (text, command, modifier_command)
        # modifier_command fires on Shift / Control / Command + click.
        specs = [
            ("Νεος",          self.add_new_patient,                                                 None),
            ("Ιστορικο",      lambda: self.show_history(self.editform.get_var("patient_id"), True), None),
            ("<",             lambda: self.navigate_patient("prev"),
                              lambda: self.navigate_patient_alphabetically("prev")),
            (">",             lambda: self.navigate_patient("next"),
                              lambda: self.navigate_patient_alphabetically("next")),
            ("Προηγούμενος",  self.undo_patient,                                                    None),
            ("Επόμενος",      self.redo_patient,                                                    None),
            ("Συνταγές",      self.show_prescriptions,                                              None),
            ("Αποδειξεις",    self.show_receipts,                                                   None),
            ("Λίστες",        self.show_lists,                                                      None),
            ("Εργαλεία",      self.show_tools_menu,                                                 None),
        ]
        self._round_tabs   = tab_frame.create_round_tabs_batch(specs)
        self.tools_button  = self._round_tabs[-1]   # Εργαλεία (leftmost on screen)

        # Elliptical hover tooltips for the 10 top tabs; descriptions are read
        # from tooltip_descriptions.json (section "registry_win"). Empty /
        # missing entries fall back to the placeholder inside EllipseToolTip.
        reg_descs = load_descriptions("registry_win")
        for canvas, spec in zip(self._round_tabs, specs):
            EllipseToolTip(canvas, reg_descs.get(spec[0], ""))

    # -----------------------------------------------------------
    # -----------------------------------------------------------
    # Patient search-related methods:

    # -----------------------------------------------------------
    def create_search(self):
        """ create controls for right-hand search box """

        # Search Bar
        self.search_frame = tk.Frame(self.win, bg=BEIGE_COLOR)
        self.search_frame.grid(row=1, column=2, columnspan=2, sticky='ew', padx=10, pady=5)

        # "Αναζήτηση:" label with the EL/EN circle centred below it.
        label_box = tk.Frame(self.search_frame, bg=BEIGE_COLOR)
        label_box.pack(side='left')
        tk.Label(label_box, text="Αναζήτηση:", font=("Arial", 12, "bold"),
                 fg="blue", bg=BEIGE_COLOR).pack(side='top')
        self._lang_circle = tk.Canvas(label_box, width=36, height=36,
                                      bg=BEIGE_COLOR, highlightthickness=0,
                                      cursor="hand2")
        self._lang_circle.pack(side='top', pady=(2, 0))
        # Initial label reflects the OS's currently-selected input source.
        initial = self._detect_input_source() or "EL"
        self.lang_indicator_var = tk.StringVar(value=initial)
        self._draw_lang_circle(initial)
        # Click on the circle = imitate Ctrl+Space → switch macOS input source.
        self._lang_circle.bind("<Button-1>", self._toggle_lang)
        # Elliptical hover tooltip explaining the toggle.
        EllipseToolTip(self._lang_circle,
                       "Εναλλαγή πληκτρολογίου\nΕλληνικά ⇄ English\n"
                       "(Πατήστε για αλλαγή γλώσσας)",
                       width=240, height=80)
        # Keep the circle in sync with the OS even if the user switches
        # via the menu bar or the Ctrl+Space shortcut directly.
        self.win.after(1000, self._poll_input_source)

        # Grid toggle button (works regardless of focus / launcher / OS shortcut clashes)
        self.grid_toggle_btn = tk.Button(self.search_frame, text="Πλέγμα", fg="blue",
                                         font=("Arial", 11, "bold"),
                                         command=self.toggle_diagonal_panel)
        self.grid_toggle_btn.pack(side='right', padx=(6, 0))

        # Search Entry
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var,
                                     font=("Arial", 12), width=30)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.search_entry.bind("<Down>", lambda e: "break")
        self.search_entry.bind("<Up>", lambda e: "break")

        # Create a canvas for floating search results
        self.search_canvas = tk.Canvas(self.win, bg=BEIGE_COLOR, highlightthickness=0, height=0)
        self.search_result_frame = tk.Frame(self.search_canvas, bg=BEIGE_COLOR)
        self.search_canvas.create_window(0, 0, window=self.search_result_frame, anchor='nw')

        self.search_result_listbox = tk.Listbox(self.search_result_frame, height=4, font=("Arial", 11), selectbackground="lightblue", selectmode=tk.SINGLE)
        self.search_result_scroll = tk.Scrollbar(self.search_result_frame, orient="vertical")
        self.search_result_listbox.config(yscrollcommand=self.search_result_scroll.set)
        self.search_result_scroll.config(command=self.search_result_listbox.yview)

        self.search_result_listbox.pack(side="left", fill="both", expand=True)
        self.search_result_scroll.pack(side="right", fill="y")

        # Bindings
        self.search_entry.bind("<KeyRelease>", self.search_patient)
        self.search_entry.bind("<Return>", lambda e: self.on_select() if self.search_result_listbox.size() > 0 else self.search_patient())
        self.search_entry.bind("<Down>", lambda e: self.search_result_listbox.focus_set())

        self.search_result_listbox.bind("<Double-Button-1>", self.on_select)
        self.search_result_listbox.bind("<Return>", self.on_select)
        self.search_result_listbox.bind("<Up>", lambda e: "break" if self.search_result_listbox.curselection() and self.search_result_listbox.curselection()[0] == 0 else None)
        self.search_result_listbox.bind("<Escape>", lambda e: self.search_canvas.place_forget())

    # -----------------------------------------------------------
    def _draw_lang_circle(self, text):
        """Render the EL/EN indicator as a white circle with a blue border."""
        c = self._lang_circle
        c.delete("all")
        w = int(c.cget("width"))
        h = int(c.cget("height"))
        pad = 2
        c.create_oval(pad, pad, w - pad, h - pad,
                      fill="white", outline="blue", width=2)
        c.create_text(w / 2, h / 2, text=text,
                      font=("Arial", 10, "bold"), fill="blue")

    # -----------------------------------------------------------
    def _detect_input_source(self):
        """Return 'EL' if the macOS keyboard is currently Greek, 'EN' otherwise.
        Returns None if the TIS API is unavailable (e.g. non-macOS)."""
        sid = _TIS.current_id()
        if not sid:
            return None
        return "EL" if "Greek" in sid else "EN"

    # -----------------------------------------------------------
    def _toggle_lang(self, event=None):
        """Click handler: flip the macOS keyboard between Greek and U.S. via
        the TIS API (no keystroke simulation, no Accessibility permission)."""
        cur = _TIS.current_id() or ""
        target = "keylayout.US" if "Greek" in cur else "keylayout.Greek"
        _TIS.select_by_substring(target)
        # Re-read after a short delay so the polling/UI stays consistent.
        self.win.after(80, self._refresh_lang_circle)

    # -----------------------------------------------------------
    def _refresh_lang_circle(self):
        """Re-read the OS input source and redraw the circle if it changed."""
        new = self._detect_input_source()
        if new and new != self.lang_indicator_var.get():
            self.lang_indicator_var.set(new)
            self._draw_lang_circle(new)

    # -----------------------------------------------------------
    def _poll_input_source(self):
        """Periodically sync the circle with the OS-selected input source."""
        self._refresh_lang_circle()
        try:
            self.win.after(1000, self._poll_input_source)
        except tk.TclError:
            pass  # window closed

    # -----------------------------------------------------------
    def search_patient(self, event=None):
        query = self.search_var.get().strip()

        if len(query) < 1:
            self.search_canvas.place_forget()
            return

        session = SessionPatients()
        try:
            if query.isdigit():
                if len(query) == 11:
                    patients = session.query(Patient).filter(Patient.amka == query).all()
                else:
                    patients = session.query(Patient).filter(Patient.patient_id == int(query)).all()
            elif "/" in query:
                patients = session.query(Patient).filter(Patient.last_visit_date.like(f"%{query}%")).all()
            else:
                # Case- AND accent-insensitive match (Α↔α, ά↔α, Ώ↔ω, …).
                # SQLite's ILIKE only folds ASCII, so we fold in Python.
                def _fold(s):
                    if not s:
                        return ""
                    return "".join(c for c in unicodedata.normalize("NFD", s)
                                   if not unicodedata.combining(c)).casefold()
                q_cf = _fold(query)
                # Prefix match (any length): the typed letters must equal the
                # START of the surname or first name (accent- + case-insensitive).
                def _hit(field):
                    return bool(field) and _fold(field).startswith(q_cf)
                patients = [p for p in session.query(Patient).all()
                            if _hit(p.last_name) or _hit(p.first_name)]
        finally:
            session.close()

        self.search_result_listbox.delete(0, tk.END)
        for p in patients:
            self.search_result_listbox.insert(tk.END, f"{p.patient_id} - {p.last_name}, {p.first_name} ({p.phone_number})")

        if patients:
            self.position_results()
            self.search_result_listbox.selection_set(0)  # Auto-select first result
        else:
            self.search_canvas.place_forget()

    # -----------------------------------------------------------
    def on_select(self, event=None):
        try:
            selected = self.search_result_listbox.get(self.search_result_listbox.curselection())
            if selected:
                patient_id = selected.split(" - ")[0]
                self.editform.get_var("patient_id").set(patient_id)
                self.load_patient_data(None)
                self.search_canvas.place_forget()
                self.search_entry.focus_set()  # Return focus to search entry
        except tk.TclError:
            pass

    # -----------------------------------------------------------
    def position_results(self):
        x = self.search_entry.winfo_rootx() - self.win.winfo_rootx()
        y = self.search_entry.winfo_rooty() - self.win.winfo_rooty() + self.search_entry.winfo_height()
        self.search_canvas.place(x=x, y=y, width=self.search_entry.winfo_width(), height=100)

    # -----------------------------------------------------------
    def handle_click(self, event):
        """ Only hide results if clicking outside both search entry and results """
        x, y = event.x_root, event.y_root
        search_geo = (self.search_entry.winfo_rootx(), self.search_entry.winfo_rooty(),
                     self.search_entry.winfo_width(), self.search_entry.winfo_height())
        results_geo = (self.search_canvas.winfo_rootx(), self.search_canvas.winfo_rooty(),
                      self.search_canvas.winfo_width(), self.search_canvas.winfo_height())

        # Check if click is outside both areas
        if not (search_geo[0] <= x <= search_geo[0]+search_geo[2] and
                search_geo[1] <= y <= search_geo[1]+search_geo[3]) and \
            not (results_geo[0] <= x <= results_geo[0]+results_geo[2] and
                 results_geo[1] <= y <= results_geo[1]+results_geo[3]):
            self.search_canvas.place_forget()
        return self

    # -----------------------------------------------------------
    # -----------------------------------------------------------
    # Navigation history related methods:

    # -----------------------------------------------------------
    def navigate_history(self, direction):
        """Go back/forward in navigation history"""
        if not self.navigation_history:
            return

        if direction == "back":
            if self.current_history_index > 0:
                self.current_history_index -= 1
        else:  # forward
            if self.current_history_index < len(self.navigation_history) - 1:
                self.current_history_index += 1

        patient_id = self.navigation_history[self.current_history_index]
        self.editform.get_var("patient_id").set(patient_id)
        self.load_patient_data(None)
        self.show_status(f"Ιστορικό: {self.current_history_index + 1}/{len(self.navigation_history)}", 2000)

    # -----------------------------------------------------------
    def undo_patient(self):
        self.navigate_history("back")

    # -----------------------------------------------------------
    def add_to_nav_history(self, patient_id):
        """Record patient views in navigation history"""

        # Don't add duplicates if we're just going back/forward
        if self.navigation_history and self.navigation_history[self.current_history_index] == patient_id:
            return

        # Truncate future history if we're navigating back in time
        if self.current_history_index < len(self.navigation_history) - 1:
            self.navigation_history = self.navigation_history[:self.current_history_index + 1]

        self.navigation_history.append(patient_id)
        self.current_history_index = len(self.navigation_history) - 1

    # -----------------------------------------------------------
    def redo_patient(self):
        """ Επόμενος: forward in the navigation history (patients we've
            already opened in this session), ending at the most recent. """
        self.navigate_history("forward")

    # -----------------------------------------------------------
    # -----------------------------------------------------------
    # future modules:
    def show_settings(self):
        messagebox.showinfo("Settings", "Not Ready Yet")

    # -----------------------------------------------------------
    def show_prescriptions(self):
        """ Συνταγές tab — placeholder until the prescriptions window exists. """
        messagebox.showinfo("Συνταγές", "Το παράθυρο συνταγών δεν είναι έτοιμο ακόμα.")

    # -----------------------------------------------------------
    def show_receipts(self):
        """ Αποδειξεις tab — dummy for now. """
        messagebox.showinfo("Αποδειξεις", "Το παράθυρο αποδείξεων δεν είναι έτοιμο ακόμα.")

    # -----------------------------------------------------------
    def show_lists(self):
        """ Λίστες tab — dummy for now. """
        messagebox.showinfo("Λίστες", "Το παράθυρο λιστών δεν είναι έτοιμο ακόμα.")

    # -----------------------------------------------------------
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

    # -----------------------------------------------------------
    def _tool_edit_images(self):
        messagebox.showinfo("Εργαλεία", "ΕΠΕΞΕΡΓΑΣΙΑ ΕΙΚΟΝΩΝ — δεν είναι έτοιμο ακόμα.")

    # -----------------------------------------------------------
    def _tool_edit_lab_results(self):
        """ Launch the PDF→OCR→Excel/Chart workflow (lab_workflow_win.py). """
        script_dir = Path(__file__).resolve().parent
        script = script_dir / "lab_workflow_win.py"
        if not script.exists():
            messagebox.showerror("PDF→OCR", f"Δεν βρέθηκε το αρχείο:\n{script.name}")
            return
        py = "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
        if not Path(py).exists():
            py = sys.executable
        try:
            subprocess.Popen(
                [py, str(script)],
                cwd=str(script_dir),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as e:
            messagebox.showerror("PDF→OCR", f"Αποτυχία εκκίνησης:\n{e}")

    # -----------------------------------------------------------
    def _tool_med5(self):
        Med5Window(self.win, editform=self.editform)

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