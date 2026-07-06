#!/bin/bash
# Quick start script for DICOM slicer

echo "=========================================="
echo "DICOM MRI Image Slicer - Quick Start"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Running DICOM slicer..."
echo "Input: lab_workflow/exams/input"
echo "Output: lab_workflow/exams/output"
echo ""

# Run the slicer
cd SLICER_DICOM
python dicom_slicer.py "$@"

# Return to original directory
cd ..

echo ""
echo "Done! To view results, run:"
echo "  source venv/bin/activate"
echo "  cd DICOM_VIEWER"
echo "  python dicom_viewer.py -f ../lab_workflow/exams/output"
