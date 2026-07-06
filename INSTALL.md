# 📦 Installation Guide

## Prerequisites

- **Python:** 3.8 or higher
- **pip:** Latest version recommended
- **Operating System:** Linux, macOS, or Windows

## Quick Installation

### Option 1: Automated (Recommended)

The run scripts automatically set up a virtual environment and install dependencies:

```bash
# Make scripts executable (Linux/macOS)
chmod +x run_slicer.sh run_viewer.sh

# Run the slicer (will auto-install dependencies)
./run_slicer.sh

# Or run the viewer (will auto-install dependencies)
./run_viewer.sh
```

### Option 2: Manual Installation

#### Step 1: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

## Verify Installation

### Check Python Version

```bash
python --version
# Should output: Python 3.8.x or higher
```

### Test Dependencies

```bash
python -c "import pydicom; print('pydicom:', pydicom.__version__)"
python -c "import numpy; print('numpy:', numpy.__version__)"
python -c "import PIL; print('Pillow: OK')"
python -c "import matplotlib; print('matplotlib:', matplotlib.__version__)"
```

Expected output:
```
pydicom: 2.4.x
numpy: 1.24.x
Pillow: OK
matplotlib: 3.7.x
```

### Test Application Syntax

```bash
python SLICER_DICOM/dicom_slicer.py --help
python DICOM_VIEWER/dicom_viewer.py --help
```

## Platform-Specific Notes

### Linux

Most dependencies should install without issues. If you encounter build errors:

```bash
# Install system dependencies (Debian/Ubuntu)
sudo apt-get update
sudo apt-get install python3-dev python3-pip

# For matplotlib GUI
sudo apt-get install python3-tk
```

### macOS

```bash
# Using Homebrew
brew install python3

# Install dependencies
pip3 install -r requirements.txt
```

### Windows

```bash
# Use Python from python.org or Microsoft Store
# Open PowerShell or Command Prompt

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install
pip install -r requirements.txt
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "matplotlib backend error"

**Solution:** Set backend environment variable
```bash
# Linux/macOS
export MPLBACKEND=TkAgg

# Or edit matplotlib config
echo "backend: TkAgg" > ~/.matplotlib/matplotlibrc
```

### Issue: "Permission denied" on scripts

**Solution:** Make scripts executable
```bash
chmod +x run_slicer.sh run_viewer.sh
```

### Issue: "pip: command not found"

**Solution:** Install pip
```bash
# Linux
sudo apt-get install python3-pip

# macOS
python3 -m ensurepip
```

## Advanced Installation

### Optional Dependencies

For advanced 3D processing capabilities, install optional packages:

```bash
# SimpleITK for advanced image processing
pip install SimpleITK

# NiBabel for NIfTI format support
pip install nibabel
```

Update `requirements.txt` to include these permanently.

### Development Installation

For development with additional tools:

```bash
# Install with development tools
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run code formatter
black SLICER_DICOM/ DICOM_VIEWER/

# Run linter
flake8 SLICER_DICOM/ DICOM_VIEWER/
```

## Post-Installation

### Quick Test

1. **Create test structure:**
   ```bash
   # Input folder should already exist
   ls lab_workflow/exams/input/
   ```

2. **If you have sample DICOM files:**
   ```bash
   # Copy them to input folder
   cp /path/to/dicom/*.dcm lab_workflow/exams/input/
   
   # Run slicer
   ./run_slicer.sh
   
   # View results
   ./run_viewer.sh
   ```

### Verify Git Protection

```bash
# Check git status
git status

# Protected folders should NOT appear
# ✓ Should see: DICOM_VIEWER/, SLICER_DICOM/, etc.
# ✗ Should NOT see: DICOM/, DICOM_DATA/
```

## Uninstall

To remove the application:

```bash
# Deactivate virtual environment (if active)
deactivate

# Remove virtual environment
rm -rf venv/

# Remove application (if desired)
cd ..
rm -rf dicom-mri-slicer/
```

## Next Steps

After installation:
1. Read [QUICKSTART.md](QUICKSTART.md) for usage instructions
2. See [README.md](README.md) for full documentation
3. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

---

**Installation Complete!** 🎉

You're ready to process DICOM MRI images!
