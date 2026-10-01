import os
import struct
import sys

ENTRY_SIZE = 64
ENTRY_NAME_LEN = 40


def align_up(value, align):
    return (value + align - 1) // align * align


def get_vorbis_pcm_size(ogg_path):
    with open(ogg_path, 'rb') as f:
        data = f.read()
        channels = data[data.find(b'\x01vorbis') + 11]  # Get number of channels from the header
        granule = struct.unpack_from('<Q', data, data.rfind(b'OggS') + 6)[0]  # Get number of PCM samples from the tail
        return granule * channels * 2
    return 0


def pack_aod(input_dir: str, output_path: str):

    # Collect all files recursively from the input dir and subdirectories
    file_list = []
    for dir_path, _, files in os.walk(input_dir):
        for file_name in files:
            abs_path = os.path.join(dir_path, file_name)
            file_list.append(abs_path)

    file_count = len(file_list)

    #
    # Prepare .aod archive file table
    #
    table = bytearray()
    table_size = ENTRY_SIZE * (len(file_list) + 2)  # +2 for empty end 0xFF marker
    data_offset = align_up(table_size, 16)
    for i, file_path in enumerate(file_list):
        entry = bytearray(ENTRY_SIZE)

        rel_path = os.path.relpath(file_path, input_dir)  # Get relative path
        file_size = os.path.getsize(file_path)

        # Store entry name (relative path)
        entry_name = rel_path.replace("/", "\\")  # Slashes must be backward
        entry_name = entry_name.encode('ascii', errors='ignore')
        entry_name = entry_name.ljust(ENTRY_NAME_LEN, b"\0")  # Pad the remaining space with null bytes
        entry[:ENTRY_NAME_LEN] = entry_name

        # Store entry offset and size
        entry_offset = data_offset - ENTRY_SIZE - (ENTRY_SIZE * i)
        struct.pack_into('<I', entry, 40, entry_offset)  # offset
        struct.pack_into('<I', entry, 44, file_size)  # size

        # The remaining 4 uints are unknown (with a single exemption for the ogg files)
        struct.pack_into('<I', entry, 48, 0)  # unknown_1
        struct.pack_into('<I', entry, 52, 0)  # unknown_2
        if file_path.endswith('.ogg'):
            pcm_size = get_vorbis_pcm_size(file_path)
            struct.pack_into('<I', entry, 56, pcm_size)  # For .ogg files: 3rd int is the unpacked PCM size
        else:
            struct.pack_into('<I', entry, 56, 0)  # unknown_3
        struct.pack_into('<I', entry, 60, 0)  # unknown_4

        # Store table entry
        table.extend(entry)
        data_offset = align_up(data_offset + file_size, 16)  # Align data (as in the original archive)

    # Empty record
    table.extend(bytearray(ENTRY_SIZE))

    # End-of-table marker (0xFF)
    marker_entry = bytearray(ENTRY_SIZE)
    #marker_entry[0] = 0xFF
    struct.pack_into('<I', marker_entry, 40, 0)
    table.extend(marker_entry)

    #
    # Write .aod archive
    #
    with open(output_path, 'wb') as out:

        # Write .aod archive file table
        out.write(table)

        # Write file data
        for file_path in file_list:

            # Align data (as in the original archive)
            current = out.tell()
            aligned = align_up(current, 16)
            if aligned > current:
                out.write(b"\0" * (aligned - current))

            with open(file_path, 'rb') as f:
                out.write(f.read())

    print(f'Packed {file_count} files into {output_path}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <input_dir> <output.aod>')
        sys.exit(1)

    # Get input directory
    input_dir = os.path.normpath(sys.argv[1])
    if not os.path.isdir(input_dir):
        print(f'Error: {input_dir} does not exist')
        sys.exit(1)

    # Get output directory
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = f"{os.path.basename(input_dir)}.aod"  # Fallback: use input dir name with ".aod" extension

    pack_aod(input_dir, output_path)
