# Image Inspector

`image-inspector` is a specialized digital forensics and cybersecurity tool designed to analyze images, extract embedded metadata (such as device type, creation date, and GPS coordinates), and detect hidden information/keys using steganography techniques.

## Repository Information
- **Repository URL:** [https://learn.zone01oujda.ma/git/sohachimi/image-inspector](https://learn.zone01oujda.ma/git/sohachimi/image-inspector)

## Prerequisites
To run the tool, ensure you have Python 3 and the Pillow library installed.

- **Python:** Version 3.6 or higher
- **Pillow (Python Imaging Library):** Required for image decoding and EXIF parsing.

## Installation
Clone the repository, install the dependencies, and set up the execution permission for the command-line wrapper:

```bash
# Clone the repository
git clone https://learn.zone01oujda.ma/git/sohachimi/image-inspector.git
cd image-inspector

# Install Pillow dependency
pip install Pillow

# Make the wrapper script executable
chmod +x image-inspector
```

## Usage
The tool can be executed directly using the `./image-inspector` wrapper.

### Help Message
```bash
$> ./image-inspector --help
```
**Output:**
```text
Welcome to Image Inspector

OPTIONS:
    -m  Metadata          Extract metadata from the image (e.g., geolocation, device info)
    -s  Steganography     Detect and extract hidden data from the image using steganography techniques
    -o  "FileName"        Specify the file name to save output
    --help                Display this help message
```

### Examples

#### 1. Metadata Extraction
Extract camera specifications, date of creation, and GPS locations (automatically converted from Degrees, Minutes, Seconds to Decimal Degrees):
```bash
$> ./image-inspector -m -o metadata.txt image.jpeg
```
**On-Screen Console Output:**
```text
Lat/Lon: (13.731) / (-1.1373)
Device: Canon EOS 5D Mark III
Date: 2023-07-20 14:32:10
Data saved in metadata.txt
```

#### 2. Steganography Detection
Search for hidden ASCII texts or PGP keys (checking pixel Least Significant Bits (LSB) in both MSB-first and LSB-first formats, metadata comments, and trailing EOF binary blocks):
```bash
$> ./image-inspector -s -o hidden_data.txt image.jpeg
```
**On-Screen Console Output:**
```text
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: 01
...
-----END PGP PUBLIC KEY BLOCK-----
Data saved in hidden_data.txt
```

## Testing
You can run the automated unit test suite to verify all extraction mechanisms (including DMS conversion, LSB reconstructions, and EOF tail search):

```bash
python3 test_inspector.py
```

## Ethical and Legal Considerations

> [!IMPORTANT]
> - **Get Permission:** Always obtain explicit, written permission from the owner before analyzing any image files. Operating without authorization is legally actionable under computer misuse regulations.
> - **Respect Privacy:** Images can contain sensitive private data, such as precise home coordinates or timestamps. Handle all extracted data responsibly and securely.
> - **Follow Laws:** Adhere to national and international data privacy regulations (e.g., GDPR, CCPA).
> - **Disclaimer:** This tool is created for educational and cybersecurity training purposes. The authors and institutions accept no liability for any unauthorized use or misuse of the software.
