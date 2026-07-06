#!/usr/bin/env python3
"""
DICOM MRI Image Viewer
Interactive viewer for DICOM images and processed slices
"""

import os
import sys
import argparse
from pathlib import Path
import pydicom
import matplotlib.pyplot as plt
import numpy as np


class DICOMViewer:
    """Interactive DICOM image viewer"""

    def __init__(self, folder_path):
        """
        Initialize DICOM viewer

        Args:
            folder_path: Path to folder containing DICOM files or processed slices
        """
        self.folder_path = Path(folder_path)

        if not self.folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

    def find_dicom_files(self):
        """Find all DICOM files in folder"""
        dicom_files = []

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                filepath = Path(root) / file
                try:
                    pydicom.dcmread(filepath, stop_before_pixels=True)
                    dicom_files.append(filepath)
                except:
                    continue

        return sorted(dicom_files)

    def find_png_slices(self):
        """Find all PNG slice files"""
        png_files = []

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.png'):
                    png_files.append(Path(root) / file)

        return sorted(png_files)

    def view_dicom_series(self, dicom_files):
        """
        View DICOM series in grid layout

        Args:
            dicom_files: List of DICOM file paths
        """
        if not dicom_files:
            print("No DICOM files to display")
            return

        # Load all slices
        slices = []
        for filepath in dicom_files:
            try:
                ds = pydicom.dcmread(filepath)
                slices.append({
                    'array': ds.pixel_array,
                    'instance': getattr(ds, 'InstanceNumber', 0),
                    'description': getattr(ds, 'SeriesDescription', 'Unknown')
                })
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

        if not slices:
            print("No valid DICOM images loaded")
            return

        # Sort by instance number
        slices.sort(key=lambda x: x['instance'])

        # Create figure
        num_slices = len(slices)
        cols = min(4, num_slices)
        rows = (num_slices + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(15, 4*rows))
        fig.suptitle(f"DICOM Series: {slices[0]['description']} ({num_slices} slices)",
                     fontsize=14, fontweight='bold')

        if num_slices == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if rows > 1 else axes

        for idx, slice_data in enumerate(slices):
            if idx < len(axes):
                axes[idx].imshow(slice_data['array'], cmap='gray')
                axes[idx].set_title(f"Slice {slice_data['instance']}")
                axes[idx].axis('off')

        # Hide unused subplots
        for idx in range(num_slices, len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()
        plt.show()

    def view_png_slices(self, png_files):
        """
        View PNG slice files in grid layout

        Args:
            png_files: List of PNG file paths
        """
        if not png_files:
            print("No PNG files to display")
            return

        from PIL import Image

        # Create figure
        num_slices = len(png_files)
        cols = min(4, num_slices)
        rows = (num_slices + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(15, 4*rows))
        fig.suptitle(f"Processed Slices ({num_slices} images)",
                     fontsize=14, fontweight='bold')

        if num_slices == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if rows > 1 else axes

        for idx, filepath in enumerate(png_files[:len(axes)]):
            img = Image.open(filepath)
            axes[idx].imshow(img, cmap='gray')
            axes[idx].set_title(filepath.name)
            axes[idx].axis('off')

        # Hide unused subplots
        for idx in range(num_slices, len(axes)):
            axes[idx].axis('off')


    def run(self):
        """Main execution - automatically detect file types and display"""
        print(f"Scanning folder: {self.folder_path}")

        # Try DICOM files first
        dicom_files = self.find_dicom_files()
        if dicom_files:
            print(f"Found {len(dicom_files)} DICOM files")
            self.view_dicom_series(dicom_files)
            return

        # Try PNG slices
        png_files = self.find_png_slices()
        if png_files:
            print(f"Found {len(png_files)} PNG slice files")
            self.view_png_slices(png_files)
            return

        print("No DICOM or PNG files found to display")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='DICOM MRI Image Viewer - View DICOM images or processed slices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View DICOM files from input folder
  python dicom_viewer.py -f ../lab_workflow/exams/input

  # View processed slices from output folder
  python dicom_viewer.py -f ../lab_workflow/exams/output

  # View specific series folder
  python dicom_viewer.py -f ../lab_workflow/exams/output/series_xxxxx
        """
    )

    parser.add_argument(
        '-f', '--folder',
        required=True,
        help='Folder containing DICOM files or processed slices'
    )

    args = parser.parse_args()

    try:
        viewer = DICOMViewer(args.folder)
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
