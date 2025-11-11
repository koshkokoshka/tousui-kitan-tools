import sys
from pathlib import Path
from PIL import Image
import struct


def bmp_to_aim(input_path: Path, output_path: Path, image_name: str = None):
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    output = bytearray()
    
    # 1. Write image name (first 16 bytes of .aim file header)
    output += (image_name or input_path.stem).encode("ascii")[:16].ljust(16, b'\0')

    # 2. Write BMP signature
    output += b'BM'

    # 3. Write BMP header
    bfReserved1 = 0
    bfReserved2 = 0
    bfOffBits = 14 + 40  # размер заголовка
    biSize = 40
    biWidth = width
    biHeight = height
    biPlanes = 1
    biBitCount = 24
    biCompression = 0  # BI_RGB
    biSizeImage = width * height * 3
    biXPelsPerMeter = 0
    biYPelsPerMeter = 0
    biClrUsed = 0
    biClrImportant = 0
    bfSize = bfOffBits + biSizeImage
    output += struct.pack("<IHHI", bfSize, bfReserved1, bfReserved2, bfOffBits)
    output += struct.pack("<IIIHHIIIIII",
                                biSize, biWidth, biHeight, biPlanes, biBitCount,
                                biCompression, biSizeImage, biXPelsPerMeter,
                                biYPelsPerMeter, biClrUsed, biClrImportant)

    # 3. Write RLE-encoded pixels
    for y in range(height):  # BMP bottom-up
        x = 0
        while x < width:
            r, g, b, a = pixels[x, y]
            
            # Count number of repeated pixels
            count = 1
            while (
                x + count < width 
                and pixels[x + count, y][:3] == (r, g, b) 
                and count < 255
            ):
                count += 1
            
            # Write in BGR order
            output += bytes((b, g, r, count))
            x += count

    # Save .aim file
    with open(output_path, "wb") as f:
        f.write(output)

    print(f"Saved {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bmp2aim.py <input.bmp> [output.aim] [image_name]")
        sys.exit(0)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_suffix(".aim")
    image_name = sys.argv[3] if len(sys.argv) > 3 else None

    bmp_to_aim(input_path, output_path, image_name)
