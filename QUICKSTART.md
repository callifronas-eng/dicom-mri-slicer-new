# 🚀 Quick Start Guide

## Installation (One-time setup)

```bash
# Install Python dependencies
pip install -r requirements.txt
```

Or use the automated scripts (recommended):
```bash
# The scripts will create a virtual environment and install dependencies automatically
chmod +x run_slicer.sh run_viewer.sh
```

## Basic Usage

### Option 1: Using Scripts (Easiest)

**Process DICOM files:**
```bash
./run_slicer.sh
```

**View results:**
```bash
./run_viewer.sh
```

### Option 2: Manual Commands

**Process DICOM files:**
```bash
cd SLICER_DICOM
python dicom_slicer.py -i ../lab_workflow/exams/input -o ../lab_workflow/exams/output
```

**View processed slices:**
```bash
cd DICOM_VIEWER
python dicom_viewer.py -f ../lab_workflow/exams/output
```

## Folder Configuration

### Default Workflow (Tracked in Git)
- **Input:** `lab_workflow/exams/input/` - Place your DICOM files here
- **Output:** `lab_workflow/exams/output/` - Processed results appear here

### Protected Data Folders (NOT in Git) 🔒
- **DICOM/** - For sensitive patient data (automatically ignored by Git)
- **DICOM_DATA/** - For sensitive patient data (automatically ignored by Git)

To use protected folders:
```bash
cd SLICER_DICOM
python dicom_slicer.py -i ../DICOM -o ../DICOM_DATA/processed
```

## Common Commands

### Process specific folder
```bash
cd SLICER_DICOM
python dicom_slicer.py -i /path/to/mri/data -o /path/to/output
```

### View specific series
```bash
cd DICOM_VIEWER
python dicom_viewer.py -f /path/to/series/folder
```

### Get help
```bash
python dicom_slicer.py --help
python dicom_viewer.py --help
```

## What Gets Created

When you run the slicer, it creates:

```
output/
├── series_<uid>/
│   ├── slice_0000.png         # Individual slice images
│   ├── slice_0001.png
│   ├── ...
│   ├── metadata.json          # DICOM metadata
│   └── processing_results.json # Processing log
└── processing_summary.json    # Overall summary
```

## Verification

Verify Git protection is working:
```bash
git status
```

You should see:
- ✅ DICOM_VIEWER/ tracked
- ✅ SLICER_DICOM/ tracked  
- ✅ lab_workflow/ tracked
- 🔒 DICOM/ ignored (not shown)
- 🔒 DICOM_DATA/ ignored (not shown)

## Next Steps

1. Place DICOM files in `lab_workflow/exams/input/`
2. Run `./run_slicer.sh`
3. View results with `./run_viewer.sh`
4. Check the full README.md for advanced features

## Troubleshooting

**"No DICOM files found"**
- Check that files are in the input folder
- Verify files are valid DICOM format

**Import errors**
- Run `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

**Viewer not opening**
- Check matplotlib backend: `export MPLBACKEND=TkAgg`
- Ensure X11/display is available (for GUI)
