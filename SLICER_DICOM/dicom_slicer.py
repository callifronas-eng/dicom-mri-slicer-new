#!/usr/bin/env python3
"""
DICOM MRI Image Slicer
Processes DICOM images from input folder and saves sliced results to output folder
"""

import os
import sys
import argparse
import numpy as np
import pydicom
from pathlib import Path
import json
from datetime import datetime


class DICOMSlicer:
    """Main class for DICOM MRI image slicing operations"""

    def __init__(self, input_folder, output_folder):
        """
        Initialize the DICOM Slicer

        Args:
            input_folder: Path to folder containing DICOM files
            output_folder: Path to folder where results will be saved
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)

        # Create output folder if it doesn't exist
        self.output_folder.mkdir(parents=True, exist_ok=True)

        print(f"✓ Input folder: {self.input_folder}")
        print(f"✓ Output folder: {self.output_folder}")

    def find_dicom_files(self):
        """Recursively find all DICOM files in input folder"""
        dicom_files = []

        for root, dirs, files in os.walk(self.input_folder):
            for file in files:
                filepath = Path(root) / file
                # Try to read as DICOM
                try:
                    pydicom.dcmread(filepath, stop_before_pixels=True)
                    dicom_files.append(filepath)
                except:
                    continue

        return sorted(dicom_files)

    def load_dicom_series(self, dicom_files):
        """
        Load DICOM files and organize into series

        Returns:
            dict: Series organized by SeriesInstanceUID
        """
        series_dict = {}

        for filepath in dicom_files:
            try:
                ds = pydicom.dcmread(filepath)
                series_uid = getattr(ds, 'SeriesInstanceUID', 'unknown')

                if series_uid not in series_dict:
                    series_dict[series_uid] = []

                series_dict[series_uid].append({
                    'filepath': filepath,
                    'dataset': ds,
                    'instance_number': getattr(ds, 'InstanceNumber', 0)
                })
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")

        # Sort each series by instance number
        for series_uid in series_dict:
            series_dict[series_uid].sort(key=lambda x: x['instance_number'])

        return series_dict

    def extract_metadata(self, dataset):
        """Extract relevant metadata from DICOM dataset"""
        metadata = {
            'PatientID': getattr(dataset, 'PatientID', 'Unknown'),
            'StudyDate': getattr(dataset, 'StudyDate', 'Unknown'),
            'SeriesDescription': getattr(dataset, 'SeriesDescription', 'Unknown'),
            'Modality': getattr(dataset, 'Modality', 'Unknown'),
            'ImageType': str(getattr(dataset, 'ImageType', 'Unknown')),
            'Rows': getattr(dataset, 'Rows', 0),
            'Columns': getattr(dataset, 'Columns', 0),
            'SliceThickness': getattr(dataset, 'SliceThickness', 'Unknown'),
        }
        return metadata

    def save_slice_as_png(self, pixel_array, output_path, normalize=True):
        """Save a slice as PNG image"""
        try:
            from PIL import Image

            if normalize:
                # Normalize to 0-255 range
                img_array = pixel_array.astype(float)
                img_array = ((img_array - img_array.min()) /
                           (img_array.max() - img_array.min()) * 255)
                img_array = img_array.astype(np.uint8)
            else:
                img_array = pixel_array.astype(np.uint8)

            # Create image and save
            img = Image.fromarray(img_array)
            img.save(output_path)
            return True
        except Exception as e:
            print(f"Error saving PNG: {e}")
            return False

    def process_series(self, series_uid, series_data):
        """
        Process a DICOM series and extract slices

        Args:
            series_uid: Series instance UID
            series_data: List of DICOM datasets in the series
        """
        print(f"\n{'='*60}")
        print(f"Processing Series: {series_uid}")
        print(f"Number of slices: {len(series_data)}")

        # Create output directory for this series
        series_folder = self.output_folder / f"series_{series_uid[:16]}"
        series_folder.mkdir(exist_ok=True)

        # Extract metadata from first slice
        first_ds = series_data[0]['dataset']
        metadata = self.extract_metadata(first_ds)

        print(f"Modality: {metadata['Modality']}")
        print(f"Series Description: {metadata['SeriesDescription']}")
        print(f"Image Size: {metadata['Rows']} x {metadata['Columns']}")

        # Save metadata
        metadata_path = series_folder / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Process each slice
        results = []
        for idx, slice_data in enumerate(series_data):
            try:
                ds = slice_data['dataset']
                pixel_array = ds.pixel_array

                # Save as PNG
                slice_filename = f"slice_{idx:04d}.png"
                slice_path = series_folder / slice_filename

                if self.save_slice_as_png(pixel_array, slice_path):
                    results.append({
                        'slice_index': idx,
                        'instance_number': slice_data['instance_number'],
                        'filename': slice_filename,
                        'shape': pixel_array.shape,
                        'success': True
                    })
                    print(f"  ✓ Saved slice {idx+1}/{len(series_data)}: {slice_filename}")
                else:
                    results.append({
                        'slice_index': idx,
                        'instance_number': slice_data['instance_number'],
                        'success': False
                    })

            except Exception as e:
                print(f"  ✗ Error processing slice {idx}: {e}")
                results.append({
                    'slice_index': idx,
                    'success': False,
                    'error': str(e)
                })

        # Save processing results
        results_path = series_folder / "processing_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)

        successful = sum(1 for r in results if r.get('success', False))
        print(f"\n✓ Series complete: {successful}/{len(results)} slices saved successfully")
        print(f"✓ Output folder: {series_folder}")

        return results

    def run(self):
        """Main execution method"""
        print(f"\n{'='*60}")
        print("DICOM MRI Image Slicer")
        print(f"{'='*60}")

        # Check if input folder exists
        if not self.input_folder.exists():
            print(f"✗ Error: Input folder does not exist: {self.input_folder}")
            return False

        # Find DICOM files
        print("\n[1/3] Scanning for DICOM files...")
        dicom_files = self.find_dicom_files()

        if not dicom_files:
            print(f"✗ No DICOM files found in {self.input_folder}")
            return False

        print(f"✓ Found {len(dicom_files)} DICOM files")

        # Load and organize series
        print("\n[2/3] Loading DICOM series...")
        series_dict = self.load_dicom_series(dicom_files)
        print(f"✓ Found {len(series_dict)} series")

        # Process each series
        print("\n[3/3] Processing series and extracting slices...")
        all_results = {}

        for series_uid, series_data in series_dict.items():
            results = self.process_series(series_uid, series_data)
            all_results[series_uid] = results

        # Save overall summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'input_folder': str(self.input_folder),
            'output_folder': str(self.output_folder),
            'total_dicom_files': len(dicom_files),
            'total_series': len(series_dict),
            'series_processed': len(all_results)
        }

        summary_path = self.output_folder / "processing_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n{'='*60}")
        print("✓ Processing Complete!")
        print(f"{'='*60}")
        print(f"Total DICOM files: {len(dicom_files)}")
        print(f"Total series: {len(series_dict)}")
        print(f"Output location: {self.output_folder}")
        print(f"Summary saved: {summary_path}")

        return True


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='DICOM MRI Image Slicer - Process DICOM images and extract slices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process DICOM files with default paths
  python dicom_slicer.py

  # Process with custom input/output folders
  python dicom_slicer.py -i /path/to/dicom/data -o /path/to/output

  # Use lab workflow structure
  python dicom_slicer.py -i ../lab_workflow/exams/input -o ../lab_workflow/exams/output
        """
    )

    parser.add_argument(
        '-i', '--input',
        default='../lab_workflow/exams/input',
        help='Input folder containing DICOM files (default: ../lab_workflow/exams/input)'
    )

    parser.add_argument(
        '-o', '--output',
        default='../lab_workflow/exams/output',
        help='Output folder for processed slices (default: ../lab_workflow/exams/output)'
    )

    args = parser.parse_args()

    # Create slicer instance and run
    slicer = DICOMSlicer(args.input, args.output)
    success = slicer.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

