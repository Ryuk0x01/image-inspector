from PIL import Image

def extract_steganography(image_path):
    END_TAG = "-----END PGP PUBLIC KEY BLOCK-----"
    
    # ---------- LSB ----------
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            width, height = img.size
            pixels = img.load()

            bits = []

            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    bits.append(r & 1)
                    bits.append(g & 1)
                    bits.append(b & 1)

            data = bytearray()

            for i in range(0, len(bits), 8):
                if i + 8 > len(bits):
                    break

                value = 0
                for bit in bits[i:i + 8]:
                    value = (value << 1) | bit

                if value == 0:
                    break

                data.append(value)

            text = data.decode("utf-8", errors="ignore")

            start = text.find("-----BEGIN PGP")
            end = text.find(END_TAG)

            if start != -1 and end != -1:
                return text[start:end + len(END_TAG)]

    except Exception as e:
        return f"Error: {e}"

    # ---------- EOF ----------
    try:
        with open(image_path, "rb") as f:
            text = f.read().decode("utf-8", errors="ignore")

        start = text.find("-----BEGIN PGP")
        end = text.find(END_TAG)

        if start != -1 and end != -1:
            return text[start:end + len(END_TAG)]

    except Exception:
        pass

    return "No hidden data detected."