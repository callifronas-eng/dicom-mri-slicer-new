# Lab Workflow

This folder contains the standard workflow structure for processing DICOM exams.

## Structure

```
lab_workflow/
└── exams/
    ├── input/      # Place DICOM files here for processing
    └── output/     # Processed slices and results are saved here
```

## Usage

1. **Input folder (`exams/input/`):**
   - Copy or move DICOM files here
   - Can contain multiple series or studies
   - Organized automatically by the slicer

2. **Output folder (`exams/output/`):**
   - Automatically created by the slicer
   - Contains extracted slices organized by series
   - Includes metadata and processing summaries

## Quick Start

From the project root:

```bash
# Process DICOM files
cd SLICER_DICOM
python dicom_slicer.py

# View results
cd ../DICOM_VIEWER
python dicom_viewer.py -f ../lab_workflow/exams/output
```

## Notes

- Both input and output folders are tracked in Git (empty folders preserved)
- Actual DICOM data is safe to commit here (unlike DICOM/ and DICOM_DATA/ folders)
- For protected patient data, use the DICOM/ or DICOM_DATA/ folders instead
