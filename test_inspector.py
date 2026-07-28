#!/usr/bin/env python3
import os
import unittest
from PIL import Image
from PIL.ExifTags import TAGS
from image_inspector import extract_metadata, extract_steganography, dms_to_decimal

class TestImageInspector(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.meta_img_path = os.path.join(self.test_dir, "test_metadata.jpg")
        self.steg_msb_path = os.path.join(self.test_dir, "test_steg_msb.png")
        self.steg_lsb_path = os.path.join(self.test_dir, "test_steg_lsb.png")
        self.steg_eof_path = os.path.join(self.test_dir, "test_steg_eof.jpg")
        
        # 1. Create a mock image with EXIF metadata (Make, Model, Date, GPS)
        # Lat/Lon ref: 13.731 N, 1.1373 W (meaning -1.1373 lon)
        # DMS conversion:
        # 13.731 = 13 degrees, 43 minutes, 51.6 seconds
        # 1.1373 = 1 degree, 8 minutes, 14.28 seconds
        lat_dms = [13.0, 43.0, 51.6]
        lon_dms = [1.0, 8.0, 14.28]
        
        img_meta = Image.new('RGB', (10, 10), color=(200, 200, 200))
        exif = img_meta.getexif()
        exif[271] = "Canon"  # Make
        exif[272] = "Canon EOS 5D Mark III"  # Model
        exif[306] = "2023-07-20 14:32:10"  # DateTime
        
        # GPS tag is 34853 (0x8825)
        # We can construct the GPS IFD (Image File Directory) or just set a dictionary
        gps_ifd = exif.get_ifd(0x8825)
        gps_ifd[1] = "N"          # GPSLatitudeRef
        gps_ifd[2] = lat_dms      # GPSLatitude
        gps_ifd[3] = "W"          # GPSLongitudeRef
        gps_ifd[4] = lon_dms      # GPSLongitude
        
        img_meta.save(self.meta_img_path, exif=exif)

        # 2. Create a mock image with MSB-first LSB steganography (PGP Key)
        pgp_key = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: 01

mQENBF/h1mQBCAD
-----END PGP PUBLIC KEY BLOCK-----"""
        
        self.create_lsb_image(self.steg_msb_path, pgp_key, msb_first=True)
        self.create_lsb_image(self.steg_lsb_path, pgp_key, msb_first=False)

        # 3. Create a mock image with EOF trailing data
        img_eof = Image.new('RGB', (10, 10), color=(100, 100, 100))
        img_eof.save(self.steg_eof_path, format="JPEG")
        with open(self.steg_eof_path, 'ab') as f:
            f.write(b"\n" + pgp_key.encode('utf-8') + b"\n")

    def tearDown(self):
        for path in [self.meta_img_path, self.steg_msb_path, self.steg_lsb_path, self.steg_eof_path]:
            if os.path.exists(path):
                os.remove(path)

    def create_lsb_image(self, path, message, msb_first):
        img = Image.new('RGB', (100, 100), color=(120, 120, 120))
        msg_bytes = message.encode('utf-8') + b'\x00'
        bits = []
        for byte in msg_bytes:
            for i in range(8):
                if msb_first:
                    bits.append((byte >> (7 - i)) & 1)
                else:
                    bits.append((byte >> i) & 1)
                    
        width, height = img.size
        pixels = img.load()
        bit_idx = 0
        
        for y in range(height):
            for x in range(width):
                if bit_idx >= len(bits):
                    break
                r, g, b = pixels[x, y]
                if bit_idx < len(bits):
                    r = (r & ~1) | bits[bit_idx]
                    bit_idx += 1
                if bit_idx < len(bits):
                    g = (g & ~1) | bits[bit_idx]
                    bit_idx += 1
                if bit_idx < len(bits):
                    b = (b & ~1) | bits[bit_idx]
                    bit_idx += 1
                pixels[x, y] = (r, g, b)
        img.save(path, format='PNG')

    def test_dms_to_decimal(self):
        # 13 degrees, 43 minutes, 51.6 seconds N
        val_n = dms_to_decimal(((13, 1), (43, 1), (516, 10)), 'N')
        self.assertAlmostEqual(val_n, 13.731, places=4)
        
        # 1 degree, 8 minutes, 14.28 seconds W
        val_w = dms_to_decimal(((1, 1), (8, 1), (1428, 100)), 'W')
        self.assertAlmostEqual(val_w, -1.1373, places=4)

    def test_metadata_extraction(self):
        output = extract_metadata(self.meta_img_path)
        self.assertIn("Lat/Lon: (13.731) / (-1.1373)", output)
        self.assertIn("Device: Canon EOS 5D Mark III", output)
        self.assertIn("Date: 2023-07-20 14:32:10", output)

    def test_steganography_msb_lsb(self):
        output = extract_steganography(self.steg_msb_path)
        self.assertIn("-----BEGIN PGP PUBLIC KEY BLOCK-----", output)
        self.assertIn("-----END PGP PUBLIC KEY BLOCK-----", output)

    def test_steganography_lsb_lsb(self):
        output = extract_steganography(self.steg_lsb_path)
        self.assertIn("-----BEGIN PGP PUBLIC KEY BLOCK-----", output)
        self.assertIn("-----END PGP PUBLIC KEY BLOCK-----", output)

    def test_steganography_eof(self):
        output = extract_steganography(self.steg_eof_path)
        self.assertIn("-----BEGIN PGP PUBLIC KEY BLOCK-----", output)
        self.assertIn("-----END PGP PUBLIC KEY BLOCK-----", output)

if __name__ == '__main__':
    unittest.main()
