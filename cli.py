import sys
import argparse

def print_help():
    help_msg = """Welcome to Image Inspector

OPTIONS:
    -m  Metadata          Extract metadata from the image (e.g., geolocation, device info)
    -s  Steganography     Detect and extract hidden data from the image using steganography techniques
    -o  "FileName"        Specify the file name to save output
    --help                Display this help message"""
    print(help_msg)

def parse_args():
    if '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        sys.exit(0)

    if len(sys.argv) == 1:
        print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-m', '--metadata', action='store_true')
    parser.add_argument('-s', '--steganography', action='store_true')
    parser.add_argument('-o', '--output', type=str)
    parser.add_argument('image_path', nargs='?')
    
    args = parser.parse_args()
    
    if not args.image_path:
        print("Error: Input image path is required.", file=sys.stderr)
        print_help()
        sys.exit(1)
        
    return args
