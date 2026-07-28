#!/usr/bin/env python3
import sys
import os

# Ensure the 'src' directory is in sys.path so relative sibling imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import parse_args
from metadata import extract_metadata
from stego import extract_steganography

def main():
    args = parse_args()

    # Validate that the input image exists and is a file
    if not os.path.exists(args.image_path):
        print(f"Error: The file '{args.image_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.image_path):
        print(f"Error: '{args.image_path}' is not a valid file.", file=sys.stderr)
        sys.exit(1)

    run_metadata = args.metadata
    run_steg = args.steganography
    if not run_metadata and not run_steg:
        run_metadata = True
        run_steg = True

    results = []
    if run_metadata:
        meta_res = extract_metadata(args.image_path)
        results.append(meta_res)
    if run_steg:
        steg_res = extract_steganography(args.image_path)
        results.append(steg_res)

    combined = "\n".join(results)

    if args.output:
        # Prepend 'output/' if the path is relative and doesn't start with 'output'
        output_path = args.output
        if not os.path.isabs(output_path):
            norm_path = os.path.normpath(output_path)
            parts = norm_path.split(os.sep)
            if parts[0] != 'output':
                output_path = os.path.join('output', output_path)
                
        try:
            # Create destination directory if it doesn't exist
            output_dir = os.path.dirname(os.path.abspath(output_path))
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined + "\n")
            print(f"Data saved in {output_path}")
        except Exception as e:
            print(f"Error saving output to {output_path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(combined)

if __name__ == '__main__':
    main()
