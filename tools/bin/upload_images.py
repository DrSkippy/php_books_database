#!/usr/bin/env python3
"""
Stand-alone tool to upload a directory of images via the upload_image API endpoint.

Usage:
    python upload_images.py <directory_path>
    python upload_images.py <directory_path> --recursive
    python upload_images.py <directory_path> --extensions jpg,png,gif
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

CONFIG_PATH = "/book_service/config/configuration.json"  # root is "tools"


def get_config():
    """Load configuration from configuration.json file."""
    config_paths = [
        f".{CONFIG_PATH}",
        f"..{CONFIG_PATH}",
        "../book_service/config/configuration.json",
        "./book_service/config/configuration.json"
    ]

    for config_path in config_paths:
        try:
            with open(config_path, "r") as cfile:
                config = json.load(cfile)
                endpoint = config["endpoint"]
                api_key = config["api_key"]
                return endpoint, api_key
        except (OSError, FileNotFoundError, KeyError):
            continue

    print("ERROR: Configuration file not found!")
    print(f"Tried paths: {config_paths}")
    sys.exit(1)


def get_image_files(directory, recursive=False, extensions=None):
    """
    Get list of image files from the specified directory.

    Args:
        directory: Path to the directory containing images
        recursive: If True, search subdirectories recursively
        extensions: List of file extensions to include (e.g., ['jpg', 'png'])

    Returns:
        List of Path objects for image files
    """
    if extensions is None:
        extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']

    # Normalize extensions (remove dots, convert to lowercase)
    extensions = [ext.lower().lstrip('.') for ext in extensions]

    directory_path = Path(directory)

    if not directory_path.exists():
        print(f"ERROR: Directory '{directory}' does not exist!")
        sys.exit(1)

    if not directory_path.is_dir():
        print(f"ERROR: '{directory}' is not a directory!")
        sys.exit(1)

    image_files = []

    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"

    for file_path in directory_path.glob(pattern):
        if file_path.is_file():
            ext = file_path.suffix.lower().lstrip('.')
            if ext in extensions:
                image_files.append(file_path)

    return sorted(image_files)


def upload_image(endpoint, api_key, file_path, custom_filename=None):
    """
    Upload a single image file to the API endpoint.

    Args:
        endpoint: API endpoint URL
        api_key: API key for authentication
        file_path: Path to the image file
        custom_filename: Optional custom filename for the uploaded file

    Returns:
        Tuple of (success: bool, response_data: dict)
    """
    url = f"{endpoint}/upload_image"
    headers = {'x-api-key': api_key}

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, f'image/{file_path.suffix.lstrip(".")}')}
            data = {}
            if custom_filename:
                data['filename'] = custom_filename

            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json() if response.text else {"error": f"HTTP {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}
    except Exception as e:
        return False, {"error": f"Unexpected error: {str(e)}"}


def main():
    """Main function to process command-line arguments and upload images."""
    parser = argparse.ArgumentParser(
        description='Upload images from a directory to the API endpoint',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/images
  %(prog)s /path/to/images --recursive
  %(prog)s /path/to/images --extensions jpg,png
  %(prog)s /path/to/images --recursive --extensions jpg,png,gif --verbose
        """
    )

    parser.add_argument('directory', help='Directory containing images to upload')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Search subdirectories recursively')
    parser.add_argument('-e', '--extensions', type=str,
                        help='Comma-separated list of file extensions (default: jpg,jpeg,png,gif,bmp,webp,tiff)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print detailed output for each file')
    parser.add_argument('--dry-run', action='store_true',
                        help='List files that would be uploaded without actually uploading')

    args = parser.parse_args()

    # Parse extensions if provided
    extensions = None
    if args.extensions:
        extensions = [ext.strip() for ext in args.extensions.split(',')]

    # Get configuration
    print("Loading configuration...")
    endpoint, api_key = get_config()
    print(f"Endpoint: {endpoint}")

    # Get list of image files
    print(f"\nScanning directory: {args.directory}")
    print(f"Recursive: {args.recursive}")
    if extensions:
        print(f"Extensions: {', '.join(extensions)}")

    image_files = get_image_files(args.directory, args.recursive, extensions)

    if not image_files:
        print("\nNo image files found!")
        sys.exit(0)

    print(f"\nFound {len(image_files)} image file(s)")

    if args.dry_run:
        print("\n--- DRY RUN MODE (no files will be uploaded) ---")
        for file_path in image_files:
            print(f"  - {file_path}")
        sys.exit(0)

    # Upload images
    print("\nUploading images...")
    print("-" * 70)

    success_count = 0
    error_count = 0

    for idx, file_path in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] Uploading: {file_path.name}", end="")

        success, response_data = upload_image(endpoint, api_key, file_path)

        if success:
            success_count += 1
            print(" ✓")
            if args.verbose:
                print(f"    Response: {response_data}")
        else:
            error_count += 1
            print(" ✗")
            print(f"    ERROR: {response_data.get('error', 'Unknown error')}")

    # Print summary
    print("-" * 70)
    print(f"\nSummary:")
    print(f"  Total files:      {len(image_files)}")
    print(f"  Successfully uploaded: {success_count}")
    print(f"  Failed:           {error_count}")

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
