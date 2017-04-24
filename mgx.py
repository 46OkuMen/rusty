# Interpreting MGX files for Rusty.
# MGX files are used for graphics in the opening and ending.
# But only the opening MGX files are Japanese, so the focus is on them.

from PIL import Image
from bitstring import BitString
from lzss import little_endianize, write_little_endian
from romtools.disk import Disk
from rominfo import DEST_DISK_PATH

bits = [0b10000000,
        0b01000000,
        0b00100000,
        0b00010000,
        0b00001000,
        0b00000100,
        0b00000010,
        0b00000001]

# x and y relative values for different Action nibble values.
action_dx = [0,1,2,4,0,1,0,1,2,0,1,2,0,1,2,0]
action_dy = [0,0,0,0,1,1,2,2,2,4,4,4,8,8,8,16]

def read_little_endian(file, bytes):
    result = 0
    for i in range(1, bytes+1):
        result += ord(file.read(1)) << (8*(i-1))
    return result


def decompress(filename):
    with open(filename, 'rb') as f:
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

        # pad left and right edges to multiples of 4.
        while x0 % 4 != 0:
            x0 -= 1
        while x1 % 4 != 0:
            x1 += 1

        pixel_row_width = x1 - x0
        print pixel_row_width, pixel_row_width/8

        flag_a_offset = read_little_endian(f, 4)
        assert flag_a_offset == 0x50
        flag_b_offset = read_little_endian(f, 4)
        assert flag_b_offset == 0x5ba
        flag_b_size = read_little_endian(f, 4)
        color_index_stream_offset = read_little_endian(f, 4)
        color_index_stream_size = read_little_endian(f, 4)


        flag_a_location = flag_a_offset + 9
        flag_b_location = flag_b_offset + 9
        color_index_stream_location = color_index_stream_offset + 9

        print flag_b_size
        print color_index_stream_offset
        print color_index_stream_size

        print hex(flag_a_location), hex(flag_b_location), hex(color_index_stream_location)


        flag_a_size = flag_b_location - flag_a_location # right?

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
        flag_b = [ord(b) for b in flag_b]

        # One pixel row's worth of Flag B bytes

        action = [0]*(pixel_row_width//8)

        # Stream of 16-bit values, either four 4-bit colors or two 8-bit colors
        # (4-bit colors for 16-color mode?)
        f.seek(0, 0)
        f.seek(color_index_stream_location)
        color_index_stream = f.read(color_index_stream_size)
        color_index_stream = [(ord(c) << 8) + ord(color_index_stream[(i*2)+1]) for i, c in enumerate(color_index_stream[::2])]

        # Array of 16-bit values
        #output = [0]*pixel_row_width * ((y1 - y0)//2)
        output = []

        b_cursor = -1
        action_cursor = -1
        color_cursor = -1
        for a in flag_a:
            # read bits from highest to lowest bit
            for bit in bits:
                if a & bit:
                    # read the next flag B byte and XOR the next value in the Action buffer with it
                    b_cursor += 1
                    if action_cursor >= len(action)-1:
                        action[0] = action[0] ^ flag_b[b_cursor]
                    else:
                        action[action_cursor+1] = action[action_cursor+1] ^ flag_b[b_cursor]

                action_cursor += 1
                if action_cursor >= len(action):
                    action_cursor = 0

                action_t = (action[action_cursor] & 0xf0) >> 4
                action_b = action[action_cursor] & 0xf
                
                for nibble in (action_t, action_b):
                    if nibble == 0:
                        color_cursor += 1
                        output.append(color_index_stream[color_cursor])
                    else:
                        copy_location = len(output) - action_dx[nibble] - (pixel_row_width*action_dy[nibble])
                        print output
                        assert copy_location > 0, (nibble, len(output), copy_location)
                        #print nibble, action_dx[nibble], (pixel_row_width*action_dy[nibble])
                        output.append(output[copy_location])
                #print output

                # read the next Action buffer byte; loop to the beginning if went past the end of the buffer
                # use the top nibble of the Aciton byte to get a 16-bit value (see the site);
                    # (it's complicated)
                # write that value to Output
                # do the same for the bottom nibble
                # repeat until one of the buffers runs out


def compress(src, dest):
    im = Image.open(src)
    print im.size

    palette = [b'\x00\x00\x00', b'\x00\x00\x77', b'\x00\x77\x00', b'\x00\x77\x77',
               b'\x77\x00\x00', b'\x77\x00\x77', b'\x77\x77\x00', b'\x77\x77\x77',
               b'\xaa\xaa\xaa', b'\x00\x00\xff', b'\x00\xff\x00', b'\x00\xff\xff',
               b'\xff\x00\x00', b'\xff\x00\xff', b'\xff\xff\x00', b'\xff\xff\xff'
              ]

    BW_palette = [b'\x00\x00\x00']*16
    BW_palette[1] = b'\xFF\xFF\xFF'
    #BW_palette.extend([b'\xFF\xFF\xFF'])
    #BW_palette.extend([b'\xFF\xFF\xFF']*15)

    with open(dest, 'wb') as f:
        x0 = 232
        y0 = 158
        x1 = 380
        y1 = 210

        flag_a_size = 0x20
        flag_b_size = 0x400

        # x1: x0 + width - 4.

        # Really important to get the width right, obviously!!
        # R_A23: 8, 140, 620, 232, flag_a= 0x20, flag_b = 0x1b00
        # R_A31: 16, 116, 608, 255, flag_a = 0x30, flag_b = 0x2900
        # R_A36: 16, 116, 584, 247, flag_a = 0x30, flag_b = 0x2400
        # STAFF1: 232, 168, 372, 192 flag_b = 0x500
        # STAFF2: 216, 130, 404, 206, flag_a = 0x20, flag_b = 0x700
        # STAFF3: 232, 120, 420, 226, flag_a = 0x20, flag_b = 0xa00
        # STAFF4: 232, 130, 404, 241, flag_a = 0x20, flag_b = 0xa00
        # STAFF5: 248, 190, 384, 213, flag_a = 0x20, flag_b = 0x200
        # STAFF6: 232, 168, 432, 196, flag_a = 0x20, flag_b = 0x300
        # STAFF7: 232, 158, 396, 226, flag_a = 0x20, flag_b = 0x800

        # R_A23: 41 kb -> 36 kb
        # R_A31: 54 kb -> 52 kb
        # R_A36: 50 kb -> 48 kb

        # STAFF1: 4 kb
        # STAFF2: 10 kb
        # STAFF3: 14 kb
        # STAFF4: 13 kb
        # STAFF5: 6 kb -> 3 kb
        # STAFF6: 4 kb
        # STAFF7: 8 kb -> 6 kb

        # Need room for last 3 files, or 18 kb.
        # Still 5 kb left on the disk, so need 13 kb of reductions
        # Need 1 kb more reductions after R and STAFF5

        flag_a_location = 0x50
        flag_b_location = flag_a_size + flag_a_location
        color_index_stream_location = flag_b_location + flag_b_size

        # Flag A should be the output / 8.
        # Flag B can be 0, for all I know.

        color_index_stream_size = 0xb000 # has no effect on anything...?

        print hex(flag_a_size)
        print hex(flag_b_size)

        f.write(b'MAKI02A ') # magic word
        f.write(b'\x1a\x00\x00\x00\x00') # beginning of header, screen modes
        write_little_endian(f, x0, 2)
        write_little_endian(f, y0, 2)
        write_little_endian(f, x1, 2)
        write_little_endian(f, y1, 2)
        write_little_endian(f, flag_a_location, 4)
        write_little_endian(f, flag_b_location, 4)
        write_little_endian(f, flag_b_size, 4)
        write_little_endian(f, color_index_stream_location, 4)
        write_little_endian(f, color_index_stream_size, 4)
        f.write(''.join([p for p in BW_palette]))
        #f.write(''.join([p for p in palette]))
        f.write('\x00'*flag_a_size)
        f.write('\x00'*flag_b_size)

        color_index_stream_actual_size = 0

        image = im.load()
        print im.size
        for row in range(0, im.size[1]):
            for col in range(0, im.size[0], 8):
                bool_array = [image[col+p, row] > 0 for p in range(0, 8)]
                #print bool_array
                bitstring = BitString(bool_array)
                top = bitstring[:4]
                bot = bitstring[4:]


                #print bs
                f.write(chr(int(top.hex, 16)))
                f.write(chr(0x00))
                f.write(chr(int(bot.hex, 16)))
                f.write(chr(0x00))
                color_index_stream_actual_size += 4

        print "Wrote file to %s" % dest
        print hex(color_index_stream_actual_size)

# 01 00 02 00 etc:
# 0000 0001 (black, blue)
# 0010 0011 (black, blue) == 0x23
# 0100 0101 (black, blue) == 0x45
# That dark blue is #00 00 77, or the first color in the palette



if __name__ == '__main__':
    target = 'STAFF7'
    compress(target + '.bmp', target + '.MGX')
    RustyDisk = Disk(DEST_DISK_PATH)
    RustyDisk.insert(target + '.MGX', '/RUSTY')