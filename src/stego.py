import string
import re
from PIL import Image

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
        with Image.open(image_path) as img:
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
