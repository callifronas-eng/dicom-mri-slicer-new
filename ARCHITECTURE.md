# 🏗️ Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DICOM MRI Image Slicer                        │
│                         Application                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   DICOM_VIEWER/      │         │   SLICER_DICOM/      │
│  ┌────────────────┐  │         │  ┌────────────────┐  │
│  │ dicom_viewer.py│  │         │  │dicom_slicer.py │  │
│  │                │  │         │  │                │  │
│  │ • Load DICOM   │  │         │  │ • Scan folder  │  │
│  │ • Load PNG     │  │         │  │ • Load series  │  │
│  │ • Display grid │  │         │  │ • Extract      │  │
│  │ • Matplotlib   │  │         │  │ • Save PNG     │  │
│  └────────────────┘  │         │  │ • Metadata     │  │
│                      │         │  └────────────────┘  │
│  Interactive Viewer  │         │   Processing Engine  │
└──────────────────────┘         └──────────────────────┘
         ▲                                  │
         │                                  │
         │                                  ▼
         │              ┌──────────────────────────────┐
         │              │     lab_workflow/exams/      │
         │              │  ┌────────┐   ┌──────────┐  │
         └──────────────┼──│ input/ │──>│ output/  │──┘
                        │  └────────┘   └──────────┘  │
                        │                              │
                        │  DICOM Files  →  PNG Slices  │
                        └──────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Protected Data Areas 🔒                       │
│  ┌─────────────┐              ┌─────────────┐                   │
│  │   DICOM/    │              │ DICOM_DATA/ │                   │
│  │ (ignored)   │              │ (ignored)   │                   │
│  └─────────────┘              └─────────────┘                   │
│         Patient Data - Never committed to Git                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Processing Pipeline

```
1. INPUT                2. DISCOVERY          3. ORGANIZATION
┌──────────┐           ┌──────────┐          ┌──────────┐
│ DICOM    │──────────>│ Scan     │─────────>│ Group by │
│ Files    │           │ Files    │          │ Series   │
└──────────┘           └──────────┘          └──────────┘
                                                    │
                                                    ▼
4. EXTRACTION          5. PROCESSING         6. OUTPUT
┌──────────┐           ┌──────────┐          ┌──────────┐
│ Read     │<──────────│ Extract  │─────────>│ Save PNG │
│ Pixels   │           │ Metadata │          │ + JSON   │
└──────────┘           └──────────┘          └──────────┘
```

### File Organization

```
Input Structure:
lab_workflow/exams/input/
├── study1/
│   ├── series1/
│   │   ├── image001.dcm
│   │   ├── image002.dcm
│   │   └── ...
│   └── series2/
│       └── ...
└── study2/
    └── ...

Output Structure:
lab_workflow/exams/output/
├── series_<uid1>/
│   ├── slice_0000.png
│   ├── slice_0001.png
│   ├── metadata.json
│   └── processing_results.json
├── series_<uid2>/
│   └── ...
└── processing_summary.json
```

## Component Details

### DICOM Slicer (`dicom_slicer.py`)

**Purpose:** Extract and process DICOM MRI slices

**Key Classes:**
- `DICOMSlicer` - Main processing class

**Key Methods:**
- `find_dicom_files()` - Recursive DICOM discovery
- `load_dicom_series()` - Organize by series UID
- `extract_metadata()` - Extract DICOM tags
- `save_slice_as_png()` - Convert and save images
- `process_series()` - Process complete series
- `run()` - Main execution pipeline

**Input:** Folder path containing DICOM files
**Output:** Organized PNG slices + metadata JSON files

### DICOM Viewer (`dicom_viewer.py`)

**Purpose:** Visualize DICOM images and processed slices

**Key Classes:**
- `DICOMViewer` - Main viewer class

**Key Methods:**
- `find_dicom_files()` - Locate DICOM files
- `find_png_slices()` - Locate PNG files
- `view_dicom_series()` - Display DICOM in grid
- `view_png_slices()` - Display PNG in grid
- `run()` - Auto-detect and display

**Input:** Folder path (DICOM or PNG)
**Output:** Matplotlib visualization window

## Configuration

### config.json Structure

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

## Dependencies

```
pydicom  ──> DICOM file reading
   │
   └──> pixel_array extraction

numpy    ──> Array manipulation
   │
   └──> Image normalization

Pillow   ──> PNG export
   │
   └──> Image.fromarray()

matplotlib ──> Visualization
   │
   └──> Grid display
```

## Git Strategy

### Tracked (Version Controlled)
- ✅ Source code (DICOM_VIEWER/, SLICER_DICOM/)
- ✅ Documentation (*.md)
- ✅ Configuration (config.json, requirements.txt)
- ✅ Scripts (run_*.sh)
- ✅ Workflow structure (lab_workflow/)

### Ignored (Protected)
- 🔒 DICOM/ - Patient data
- 🔒 DICOM_DATA/ - Patient data
- 🔒 venv/ - Virtual environment
- 🔒 __pycache__/ - Python cache

## Execution Modes

### Mode 1: Quick Start (Default)
```bash
./run_slicer.sh
# Uses: lab_workflow/exams/input → lab_workflow/exams/output
```

### Mode 2: Custom Folders
```bash
python dicom_slicer.py -i /custom/input -o /custom/output
```

### Mode 3: Protected Data
```bash
python dicom_slicer.py -i ../DICOM -o ../DICOM_DATA/processed
```

## Security & Privacy

### Data Protection Layers

1. **Filesystem Level:** Separate protected folders (DICOM/, DICOM_DATA/)
2. **Git Level:** .gitignore prevents accidental commits
3. **Application Level:** Local processing only, no external calls
4. **Documentation Level:** Clear warnings in all docs

### Verification

```bash
# Check what Git tracks
git status

# Should NOT show:
# - DICOM/
# - DICOM_DATA/
```

## Extensibility

### Future Enhancements
- [ ] 3D volume reconstruction
- [ ] NIfTI format export
- [ ] DICOM anonymization tools
- [ ] Batch processing automation
- [ ] Web-based viewer interface
- [ ] Multi-modality support
