# Tousui Kitan Tools

These scripts allow you to **extract, convert, and repack** assets from the original **Tousui Kitan** game data files.

## Supported Formats

| Format | Description | Tools |
|:-------|:-------------|:------|
| `.aim` | Game texture format (RLE-compressed BMP variant) | `aim_to_bmp.py`, `bmp_to_aim.py` |
| `.aod` | Game archive containing images, sounds, and scripts | `aod_unpack.py`, `aod_pack.py` |

## Usage

```bash
# Convert .AIM to .BMP
python aim2bmp.py btn_hajime.aim btn_hajime.bmp

# Convert .BMP to .AIM
python bmp2aim.py btn_hajime.bmp btn_hajime.aim

# Unpack .AOD archive
python aod_unpack.py img1.aod

# Pack directory back into .AOD archive
python aod_pack.py img1/
```

---

![bg_cv_kanata](https://github.com/user-attachments/assets/0eebff6a-1dac-4f1c-bbc0-85eb72eaa8f5)
