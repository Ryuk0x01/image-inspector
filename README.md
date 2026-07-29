# Image Inspector

`image-inspector` is a command-line digital forensics tool that analyzes image files to extract metadata and detect hidden information using basic steganography techniques. It can retrieve EXIF metadata such as GPS coordinates, camera information, and capture date, and detect hidden PGP public keys embedded using Least Significant Bit (LSB) steganography or appended after the end of the image file (EOF).

## Repository

```bash
git clone https://learn.zone01oujda.ma/git/sohachimi/image-inspector.git
cd image-inspector
```

## Prerequisites

* Python 3.8 or newer
* Pillow library

## Installation

Create a virtual environment (recommended), activate it, and install the required dependency.

```bash
python3 -m venv venv

source venv/bin/activate

pip install Pillow

chmod +x image-inspector
```

## Project Structure

```text
image-inspector/
├── image-inspector
├── src/
│   ├── main.py
│   ├── cli.py
│   ├── metadata.py
│   └── stego.py
├── images/
├── output/
└── README.md
```

## Usage

Display the help message:

```bash
./image-inspector --help
```

Output:

```text
Welcome to Image Inspector

OPTIONS:
    -m  Metadata          Extract metadata from the image (e.g., geolocation, device info)
    -s  Steganography     Detect and extract hidden data from the image using steganography techniques
    -o  "FileName"        Specify the file name to save output
    --help                Display this help message
```

---

### Extract Metadata

```bash
./image-inspector -m image.jpeg
```

Save the output to a file:

```bash
./image-inspector -m -o metadata.txt image.jpeg
```

Example output:

```text
Lat/Lon: (13.731) / (-1.1373)
Device: Canon EOS 5D Mark III
Date: 2023-07-20 14:32:10

Data saved in metadata.txt
```

---

### Detect Hidden Data

```bash
./image-inspector -s image.jpeg
```

Save the output:

```bash
./image-inspector -s -o hidden_data.txt image.jpeg
```

Example output:

```text
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: 01
...
-----END PGP PUBLIC KEY BLOCK-----

Data saved in hidden_data.txt
```

---

### Run Both Analyses

```bash
./image-inspector -m -s image.jpeg
```

Save both results:

```bash
./image-inspector -m -s -o results.txt image.jpeg
```

## Features

### Metadata Extraction

The tool extracts available EXIF metadata including:

* GPS coordinates (Latitude and Longitude)
* Camera manufacturer
* Camera model
* Date and time the image was taken

### Steganography Detection

The tool searches for hidden PGP public keys using:

* Least Significant Bit (LSB) extraction from RGB image pixels.
* End Of File (EOF) inspection to detect data appended after the image.

## Error Handling

The program reports clear error messages for situations such as:

* Image file does not exist.
* Invalid image file.
* Missing metadata.
* No hidden data detected.

## Ethical and Legal Considerations

This tool is intended for educational purposes and authorized digital forensic investigations only.

Always:

* Obtain permission before analyzing images that you do not own.
* Respect the privacy of individuals whose information may be contained in image metadata.
* Follow applicable laws and regulations regarding digital evidence and privacy.
* Use this tool responsibly and ethically.

The authors are not responsible for any misuse of this software.
