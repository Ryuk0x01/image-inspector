#!/usr/bin/env python3
import sys
import argparse
import string
import re
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def print_help():
    help_msg = """Welcome to Image Inspector

OPTIONS:
    -m  Metadata          Extract metadata from the image (e.g., geolocation, device info)
    -s  Steganography     Detect and extract hidden data from the image using steganography techniques
    -o  "FileName"        Specify the file name to save output
    --help                Display this help message"""
    print(help_msg)

def parse_rational(val):
    if val is None:
        return 0.0
    if isinstance(val, (tuple, list)) and len(val) == 2:
        try:
            return float(val[0]) / float(val[1])
        except ZeroDivisionError:
            return 0.0
    try:
        return float(val)
    except Exception:
        return 0.0

def dms_to_decimal(dms, ref):
    try:
        if len(dms) < 3:
            return None
        degrees = parse_rational(dms[0])
        minutes = parse_rational(dms[1])
        seconds = parse_rational(dms[2])
        val = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref and str(ref).strip().upper() in ['S', 'W']:
            val = -val
        return val
    except Exception:
        return None

def extract_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
    except Exception as e:
        return f"Error loading image EXIF data: {e}"

    if not exif_data:
        return "Lat/Lon: Not found\nDevice: Unknown\nDate: Unknown"

    parsed_exif = {}
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        parsed_exif[tag_name] = value

    # Extract Camera Make & Model
    make = parsed_exif.get('Make')
    model = parsed_exif.get('Model')
    
    # Process make and model strings
    make_str = str(make).strip() if make is not None else ""
    model_str = str(model).strip() if model is not None else ""
    
    if make_str and model_str:
        if make_str in model_str:
            device = model_str
        else:
            device = f"{make_str} {model_str}"
    elif make_str:
        device = make_str
    elif model_str:
        device = model_str
    else:
        device = "Unknown"

    # Extract Date/Time
    date_val = parsed_exif.get('DateTimeOriginal') or parsed_exif.get('DateTime')
    date_str = str(date_val).strip() if date_val is not None else "Unknown"

    # Extract GPS Info
    lat_val = None
    lon_val = None
    gps_info = parsed_exif.get('GPSInfo')
    
    if gps_info:
        resolved_gps = {}
        for k, v in gps_info.items():
            tag_name = GPSTAGS.get(k, k)
            resolved_gps[tag_name] = v
            
        lat_dms = resolved_gps.get('GPSLatitude')
        lat_ref = resolved_gps.get('GPSLatitudeRef')
        lon_dms = resolved_gps.get('GPSLongitude')
        lon_ref = resolved_gps.get('GPSLongitudeRef')
        
        if lat_dms and lat_ref:
            lat_val = dms_to_decimal(lat_dms, lat_ref)
        if lon_dms and lon_ref:
            lon_val = dms_to_decimal(lon_dms, lon_ref)

    if lat_val is not None and lon_val is not None:
        # Format lat/lon matching user expected outputs (13.731) / (-1.1373)
        lat_str = str(round(lat_val, 6))
        lon_str = str(round(lon_val, 6))
        gps_str = f"({lat_str}) / ({lon_str})"
    else:
        gps_str = "Not found"

    lines = [
        f"Lat/Lon: {gps_str}",
        f"Device: {device}",
        f"Date: {date_str}"
    ]
    return "\n".join(lines)

def extract_steganography(image_path):
    try:
        with Image.open(image_path) as original_img:
            img = original_img.convert('RGB')
            width, height = img.size
            # Read pixels while the image context is active
            bits = []
            for y in range(height):
                for x in range(width):
                    pixel = img.getpixel((x, y))
                    bits.append(pixel[0] & 1)  # Red LSB
                    bits.append(pixel[1] & 1)  # Green LSB
                    bits.append(pixel[2] & 1)  # Blue LSB
    except Exception as e:
        return f"Error loading image for steganography: {e}"

    def bits_to_bytes(bit_list, msb_first):
        bytes_data = bytearray()
        for i in range(0, len(bit_list), 8):
            chunk = bit_list[i:i+8]
            if len(chunk) < 8:
                break
            byte_val = 0
            if msb_first:
                for bit in chunk:
                    byte_val = (byte_val << 1) | bit
            else:
                for idx, bit in enumerate(chunk):
                    byte_val |= (bit << idx)
            if byte_val == 0:
                break
            bytes_data.append(byte_val)
        return bytes_data

    # Try MSB-first
    bytes_msb = bits_to_bytes(bits, msb_first=True)
    text_msb = bytes_msb.decode('utf-8', errors='replace')

    # Try LSB-first
    bytes_lsb = bits_to_bytes(bits, msb_first=False)
    text_lsb = bytes_lsb.decode('utf-8', errors='replace')

    pgp_pattern = re.compile(r'(-----BEGIN PGP[\s\S]+?-----END PGP[\s\S]+?-----)')
    
    # Check MSB-first text for PGP block
    match_msb = pgp_pattern.search(text_msb)
    if match_msb:
        return match_msb.group(1).strip()
        
    # Check LSB-first text for PGP block
    match_lsb = pgp_pattern.search(text_lsb)
    if match_lsb:
        return match_lsb.group(1).strip()

    # If no PGP key, look for printable ASCII text in MSB/LSB
    printable = set(string.printable)
    
    def clean_printable_text(text):
        if not text:
            return ""
        filtered = "".join([c for c in text if c in printable])
        if len(filtered) > 10 and (len(filtered) / len(text)) > 0.8:
            return filtered.strip()
        return ""

    valid_msb = clean_printable_text(text_msb)
    if valid_msb:
        return valid_msb
        
    valid_lsb = clean_printable_text(text_lsb)
    if valid_lsb:
        return valid_lsb

    # Fallback 1: EXIF comment fields scan
    try:
        img_exif = img._getexif()
        if img_exif:
            for val in img_exif.values():
                if isinstance(val, str) and "-----BEGIN PGP" in val:
                    match = pgp_pattern.search(val)
                    if match:
                        return match.group(1).strip()
                elif isinstance(val, dict):
                    for sub_val in val.values():
                        if isinstance(sub_val, str) and "-----BEGIN PGP" in sub_val:
                            match = pgp_pattern.search(sub_val)
                            if match:
                                return match.group(1).strip()
    except Exception:
        pass

    # Fallback 2: Trailing EOF data scan
    try:
        with open(image_path, 'rb') as f:
            data = f.read()
        eof_idx = -1
        if data.startswith(b'\xff\xd8'):  # JPEG
            eof_idx = data.rfind(b'\xff\xd9')
            if eof_idx != -1:
                eof_idx += 2
        elif data.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
            eof_idx = data.rfind(b'\x49\x45\x4e\x44\xae\x42\x60\x82')
            if eof_idx != -1:
                eof_idx += 8
                
        if eof_idx != -1 and eof_idx < len(data):
            trailing_data = data[eof_idx:]
            trailing_text = trailing_data.decode('utf-8', errors='ignore')
            if "-----BEGIN PGP" in trailing_text:
                match = pgp_pattern.search(trailing_text)
                if match:
                    return match.group(1).strip()
            elif len(trailing_text.strip()) > 5:
                t_clean = "".join([c for c in trailing_text if c in printable])
                if len(t_clean) > 5 and (len(t_clean) / len(trailing_text)) > 0.8:
                    return t_clean.strip()
    except Exception:
        pass

    return "No hidden data detected."

def main():
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

    # If neither is specified, default to executing both
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
