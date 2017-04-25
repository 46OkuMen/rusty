# Non-functioning MAG file interpreter.
# Don't know what went wrong, but keeping it around in case I really need to write one someday.
# But you should just use AtoB converter, or the great HTML5 tool that RECOIL has:
# http://recoil.sourceforge.net/html5recoil.html

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
        irrelevant_stuff = f.read(0x3a)
        x0 = read_little_endian(f, 2)
        assert x0 == 0x00
        y0 = read_little_endian(f, 2)
        assert y0 == 0x00
        x1 = read_little_endian(f, 2)
        assert x1 == 0x9f
        y1 = read_little_endian(f, 2)
        assert y1 == 0xef

        # pad left and right edges to multiples of 4.
        while x0 % 4 != 0:
            x0 -= 1
        while x1 % 4 != 0:
            x1 += 1

        pixel_row_width = x1 - x0
        print pixel_row_width, pixel_row_width/8

        flag_a_offset = read_little_endian(f, 4)
        print flag_a_offset
        flag_b_offset = read_little_endian(f, 4)
        flag_b_size = read_little_endian(f, 4)
        color_index_stream_offset = read_little_endian(f, 4)
        color_index_stream_size = read_little_endian(f, 4)

        flag_a_location = flag_a_offset + 0x36
        flag_b_location = flag_b_offset + 0x36
        color_index_stream_location = color_index_stream_offset + 0x36
        print hex(flag_a_location), hex(flag_b_location), hex(color_index_stream_location)

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
        flag_b = [ord(b) for b in flag_b]

        # One pixel row's worth of Flag B bytes
        print pixel_row_width
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
                        assert copy_location >= 0, (nibble, len(output), copy_location)
                        print nibble, action_dx[nibble], (pixel_row_width*action_dy[nibble])
                        output.append(output[copy_location])
                #print output

                # read the next Action buffer byte; loop to the beginning if went past the end of the buffer
                # use the top nibble of the Aciton byte to get a 16-bit value (see the site);
                    # (it's complicated)
                # write that value to Output
                # do the same for the bottom nibble
                # repeat until one of the buffers runs out


decompress('decompressed_VS1_04.MAG')