# DICOM MRI Image Slicer

A Python application for processing DICOM MRI images with configurable input/output folders. Extracts individual slices from DICOM series and saves them as PNG images for analysis.

## 🔒 Data Privacy & Git Structure

```
✅ DICOM_VIEWER/      → Tracked in Git (viewer code)
✅ SLICER_DICOM/      → Tracked in Git (slicer code)
🔒 DICOM/            → Protected (patient data - NOT in Git)
🔒 DICOM_DATA/       → Protected (patient data - NOT in Git)
✅ lab_workflow/      → Tracked in Git (workflow structure)
```

**Important:** The `.gitignore` file automatically protects `DICOM/` and `DICOM_DATA/` folders from being committed to Git, ensuring patient data privacy.

## 📁 Project Structure

```
.
├── DICOM_VIEWER/              # Viewer application
│   └── dicom_viewer.py        # Interactive DICOM image viewer
├── SLICER_DICOM/              # Slicer application  
│   └── dicom_slicer.py        # DICOM slice extraction tool
├── lab_workflow/
│   └── exams/
│       ├── input/             # Place DICOM files here
│       └── output/            # Processed slices saved here
├── DICOM/                     # Protected patient data folder
├── DICOM_DATA/                # Protected patient data folder
├── requirements.txt           # Python dependencies
├── config.json                # Configuration file
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Process DICOM Images

**Option A: Use default paths (lab_workflow/exams/input → lab_workflow/exams/output)**
```bash
cd SLICER_DICOM
python dicom_slicer.py
```

**Option B: Specify custom input/output folders**
```bash
cd SLICER_DICOM
python dicom_slicer.py -i /path/to/dicom/files -o /path/to/output
```

**Option C: Use protected data folders**
```bash
cd SLICER_DICOM
python dicom_slicer.py -i ../DICOM -o ../DICOM_DATA/processed
```

### 3. View Results

**View original DICOM files:**
```bash
cd DICOM_VIEWER
python dicom_viewer.py -f ../lab_workflow/exams/input
```

**View processed slices:**
```bash
cd DICOM_VIEWER
python dicom_viewer.py -f ../lab_workflow/exams/output
```

## 📖 Detailed Usage

### DICOM Slicer (`dicom_slicer.py`)

Processes DICOM files and extracts individual slices as PNG images.

**Features:**
- Automatically scans input folder for DICOM files
- Organizes images by series
- Extracts metadata (patient ID, study date, modality, etc.)
- Saves each slice as normalized PNG image
- Generates processing summary and results JSON

**Command-line options:**
```bash
python dicom_slicer.py [-h] [-i INPUT] [-o OUTPUT]

Options:
  -h, --help            Show help message
  -i, --input INPUT     Input folder containing DICOM files
  -o, --output OUTPUT   Output folder for processed slices
```

**Output structure:**
```
output/
├── series_<uid>/
│   ├── slice_0000.png
│   ├── slice_0001.png
│   ├── ...
│   ├── metadata.json
│   └── processing_results.json
└── processing_summary.json
```

### DICOM Viewer (`dicom_viewer.py`)

Interactive viewer for DICOM images and processed slices using matplotlib.

**Features:**
- Automatically detects DICOM or PNG files
- Grid layout display for multiple slices
- Grayscale visualization optimized for MRI
- Displays series information and metadata

**Command-line options:**
```bash
python dicom_viewer.py [-h] -f FOLDER

Options:
  -h, --help            Show help message
  -f, --folder FOLDER   Folder containing DICOM files or processed slices (required)
```

## 🔧 Configuration

Edit `config.json` to customize default settings:

```json
{
  "folders": {
    "input_default": "lab_workflow/exams/input",
    "output_default": "lab_workflow/exams/output"
  },
  "processing": {
    "normalize_images": true,
    "output_format": "png"
  }
}
```

## 🧪 Example Workflow

1. **Place DICOM files** in `lab_workflow/exams/input/`
2. **Run the slicer:**
   ```bash
   cd SLICER_DICOM
   python dicom_slicer.py
   ```
3. **Check output** in `lab_workflow/exams/output/`
4. **View results:**
   ```bash
   cd DICOM_VIEWER  
   python dicom_viewer.py -f ../lab_workflow/exams/output
   ```

## 📋 Requirements

- Python 3.8+
- pydicom >= 2.4.0
- numpy >= 1.24.0
- Pillow >= 10.0.0
- matplotlib >= 3.7.0

## 🔐 Privacy & Security

- **Patient data protection:** DICOM/ and DICOM_DATA/ folders are automatically excluded from Git
- **Metadata preservation:** Processing metadata is saved but can be anonymized
- **Local processing:** All processing happens locally, no data sent to external services

## ⚙️ Advanced Features

### Process specific folder:
```bash
python dicom_slicer.py -i /path/to/mri/study -o /path/to/results
```

### View specific series:
```bash
python dicom_viewer.py -f ../lab_workflow/exams/output/series_1234567890
```

## 🐛 Troubleshooting

**No DICOM files found:**
- Ensure files are valid DICOM format
- Check file permissions
- Verify input folder path

**Import errors:**
- Run `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

**Viewer not displaying:**
- Ensure matplotlib backend is configured
- Try setting `export MPLBACKEND=TkAgg` on Linux/Mac

## 📝 License

MIT License - Free to use and modify for medical imaging research and clinical applications.
