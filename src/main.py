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
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(combined + "\n")
            print(f"Data saved in {args.output}")
        except Exception as e:
            print(f"Error saving output to {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(combined)

if __name__ == '__main__':
    main()
