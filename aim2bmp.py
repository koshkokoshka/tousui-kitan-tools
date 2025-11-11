import struct
import sys
from pathlib import Path
from PIL import Image


def aim_to_bmp(input_path: Path, output_path: Path) -> Image.Image:
    data = input_path.read_bytes()

    # Validate BMP signature
    if data[0x10:0x12] != b"BM":
        raise ValueError("Invalid .aim file")

    print(f"Image name: {data[0x00:0x10].decode("ascii")} (from header)")

    # Read BMP header
    bfOffBits = struct.unpack_from("<I", data, 0x1A)[0]
    biWidth = struct.unpack_from("<I", data, 0x22)[0]
    biHeight = struct.unpack_from("<I", data, 0x26)[0]
    biBitCount = struct.unpack_from("<H", data, 0x2C)[0]

    # Decode pixels
    img = Image.new("RGBA", (biWidth, biHeight))
    pixels = img.load()
    size = biWidth * biHeight * 3

    i = bfOffBits
    x = 0
    y = 0
    while i < len(data):
        r, g, b, count = data[i:i+4]  # RLE-compressed
        i += 4
        for _ in range(count):
            pixels[x, biHeight - 1 - y] = (b, g, r, 255)
            x += 1
            if x == biWidth:
                x = 0
                y += 1

    # Fix image orientation: flip unside down
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # Save as .bmp file
    img.save(output_path)
    print(f"Saved as: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python aim2bmp.py <input_file.aim>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = input_path.with_suffix(".bmp")
    aim_to_bmp(input_path, output_path)
