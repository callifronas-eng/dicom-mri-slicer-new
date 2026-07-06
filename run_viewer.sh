#!/bin/bash
# Quick start script for DICOM viewer

echo "=========================================="
echo "DICOM MRI Image Viewer - Quick Start"
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

# Install dependencies if needed
if ! python -c "import pydicom" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
fi

echo ""
echo "✓ Setup complete!"
echo ""

# Determine folder to view
FOLDER="${1:-../lab_workflow/exams/output}"

echo "Launching viewer for: $FOLDER"
echo ""

# Run the viewer
cd DICOM_VIEWER
python dicom_viewer.py -f "$FOLDER"

cd ..
