# Interpreting MGX files for Rusty.
# MGX files are used for graphics in the opening and ending.
# But only the opening MGX files are Japanese, so the focus is on them.

from PIL import Image
from lzss import little_endianize

bits = [0b10000000,
        0b01000000,
        0b00100000,
        0b00010000,
        0b00001000,
        0b00000100,
        0b00000010,
        0b00000001]

def read_little_endian(file, bytes):
    result = 0
    for i in range(1, bytes+1):
        result += ord(file.read(1)) << (8*(i-1))
    return result


def decompress(filename):
    with open(filename, 'rb') as f:
        file_bytes = f.read()
        f.seek(0, 0)
        magic_word = f.read(9)
        assert magic_word == b'MAKI02A \x1a'
        irrelevant_stuff = f.read(4)
        x0 = read_little_endian(f, 2)
        assert x0 == 19, hex(x0)
        y0 = read_little_endian(f, 2)
        assert y0 == 128
        x1 = read_little_endian(f, 2)
        assert x1 == 628
        y1 = read_little_endian(f, 2)
        assert y1 == 271

        pixel_row_width = x1 - x0
        # pad the row width to a multiple of four bytes
        while pixel_row_width % 4 == 0:
            pixel_row_width += 1

        flag_a_offset = read_little_endian(f, 4)
        assert flag_a_offset == 0x50
        flag_b_offset = read_little_endian(f, 4)
        assert flag_b_offset == 0x5ba
        flag_b_size = read_little_endian(f, 4)
        color_index_stream_size = read_little_endian(f, 4)
        pixel_color_size = read_little_endian(f, 4)

        flag_a_location = flag_a_offset + 9
        flag_b_location = flag_b_offset + 9

        flag_a_size = flag_b_location - flag_a_location # right?
        print flag_a_size

        palette = []
        for i in range(0, 16):
            # numbers representing GRB triplets
            palette.append(read_little_endian(f, 3))

        # Flag A is a stream of single-bit boolean flags, read one bit at a time
        # from highest to lowest bit in each byte. 
        # These indicate whether to fetch the next Flag B byte or not.
        f.seek(0, 0)
        f.seek(flag_a_location)
        flag_a = f.read(flag_a_size)
        flag_a = [ord(a) for a in flag_a]

        # Flag B is an array of nibbles (4-bit values), read one byte at a time,
        # and processed top nibble first. These are XORed into the Action buffer.
        f.seek(0, 0)
        f.seek(flag_b_location)
        flag_b = f.read(flag_b_size)

        # One pixel row's worth of Flag B bytes
        action = []

        # Stream of 16-bit values, either four 4-bit colors or two 8-bit colors
        # (4-bit colors for 16-color mode?)
        color = []

        # Array of 16-bit values
        output = []

        for a in flag_a:
            b_cursor = 0
            action_cursor = 0
            # read bits from highest to lowest bit
            for bit in bits:
                if a & bit:
                    # read th enext flag B byte and XOR the next value in the Action buffer with it
                    print a
                # read the next Action buffer byte; loop to the beginning if went past the end of the buffer
                # use the top nibble of the Aciton byte to get a 16-bit value (see the site);
                    # (it's complicated)
                # write that value to Output
                # do the same for the bottom nibble
                # repeat until one of the buffers runs out


decompress('R_A11.MGX')