import os
import struct
import sys

ENTRY_SIZE = 64


def unpack_aod(aod_path):
    # Make sure output directory exists
    out_dir = os.path.splitext(os.path.basename(aod_path))[0]
    os.makedirs(out_dir, exist_ok=True)

    # Extract .AOD entries
    with open(aod_path, 'rb') as f:
        table_offset = 0

        while True:
            # Go to table
            f.seek(table_offset)

            # Read table entries
            entries = []
            next_table_offset = 0
            while True:
                marker = f.peek(1)
                if marker[0] == 0x00:
                    # Skip empty entries (0x00)
                    while f.peek(1) == 0x00:
                        f.seek(ENTRY_SIZE, 1)
                    break
                if marker[0] == 0xFF:
                    # End of table (0xFF)
                    data = f.read(ENTRY_SIZE)
                    next_table_offset = struct.unpack('<I', data[40:44])[0]
                    break

                # Read entry table record
                data = f.read(ENTRY_SIZE)
                name = data[:40].split(b'\x00', 1)[0].decode('ascii')  # Read CString
                offset, size = struct.unpack('<II', data[40:48])

                entries.append({ 'name': name, 'offset': offset, 'size': size })

            # Extract entries
            entry_data_base = table_offset + ENTRY_SIZE
            for index, entry in enumerate(entries):

                # Read entry data
                f.seek(entry_data_base + ENTRY_SIZE * index + entry['offset'])
                data = f.read(entry['size'])

                # Make sure output directory exists
                out_path = os.path.join(out_dir, entry['name'])
                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                # Write file data
                with open(out_path, 'wb') as out:
                    out.write(data)

                print(f'Extracted: {entry["name"]} ({entry["size"]} bytes)')

            # Move to the next table or exit
            if next_table_offset == 0:
                break

            table_offset += ENTRY_SIZE * (len(entries) + 1) + next_table_offset  # move to the next table


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <input.aod>')
        sys.exit(1)

    unpack_aod(sys.argv[1])
