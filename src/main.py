#!/usr/bin/env python3
import sys
import os
from PIL import Image

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
        
    try:
        with Image.open(args.image_path) as img:
            img.verify()
    except Exception:
        print(f"Error: '{args.image_path}' is not a valid image.", file=sys.stderr)
        sys.exit(1)

    results = []
    if args.metadata:
        results.append(extract_metadata(args.image_path))

    if args.steganography:
        results.append(extract_steganography(args.image_path))

    combined = "\n\n".join(results)

    if args.output:
        output_dir = os.path.dirname(os.path.abspath(args.output))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(combined + "\n")

        print(combined)
        print(f"Data saved in {args.output}")
    else:
        print(combined)

if __name__ == '__main__':
    main()
