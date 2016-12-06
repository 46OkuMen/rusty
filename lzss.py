import os
from bitstring import BitArray

directory = os.curdir + os.sep
target_filepath = os.path.join(directory, 'RUSTY', 'VISUAL.COM')
output_filepath = os.path.join(directory, 'RUSTY', 'decompressed_VISUAL.COM')

# Methods for dealing with flags.
# 0: pointer
# 1: literal

def interpret_flag(h):
    if isinstance(h, int):
        h = "%x" % h
        h = h.zfill(2)
        h = '0x' + h
    ba = BitArray(hex=h)
    return [x == '1' for x in ba.bin[::-1]]

def flag_length(h):
    flag_interpretation = interpret_flag(h)
    length = 8
    # All literal: 8, all pointers: 16
    # True is equal to 1, so just sum them to get the length above 8.
    return length + (8 - sum(flag_interpretation))

def pointer_pack(first, second):
    """Ex. pointer_pack(0xab, 0xcd) == 0xabcd"""
    return (first << 8) + second

def pointer_length(p):
    """The lowest nybble of the pointer is its length, minus 3."""
    return (p & 0xF) + 3

def pointer_offset(p):
    """The offset is something like the top three nybbles of the packed bytes."""
    # 4 bytes: a b c d
    # length is 0xcab, which is c << 12
    # Ex. 0x0700 should return 15h.
    #return (p & 0xF0) << 8) + (p >> 8) + 8
    return ((p & 0xF0) << 4) + (p >> 8) + 0x12

assert interpret_flag('0x00') == [False, False, False, False, False, False, False, False]
assert interpret_flag(0) == interpret_flag('0x00')
assert interpret_flag('0xff') == [True,  True,  True,  True,  True,  True,  True,  True]
assert interpret_flag('0x7c') == [False, False, True,  True,  True,  True,  True,  False]
assert interpret_flag('0x76') == [False, True,  True,  False, True,  True,  True,  False]

assert flag_length('0x00') == 16
assert flag_length('0xFF') == 8
assert flag_length('0x7c') == 11

assert pointer_offset(0x0000) == 0x12
assert pointer_offset(0x0700) == 0x19
assert pointer_offset(0x3800) == 0x4a
assert pointer_offset(0x4401) == 0x56
assert pointer_offset(0x4c14) == 0x15e
assert pointer_offset(0x3920) == 0x24b

output = []
buf = [0] * 0x1000
with open(target_filepath, 'rb') as f:
    #header = f.read(7) # 4c 5a 1a 3e 46 00 00f
    # header stuff
    # Simple header = easier to change lengths of files??? Maybe.
    # Game is 5MB, and has 2.8MB free. (great)
    magic_number = f.read(3)
    expected_output_length = f.read(2) # still gotta flip the bytes
    _ = f.read(2)

    flag = f.read(1)
    cursor = 0
    print hex(cursor), hex(ord(flag)), ":",
    while flag != "":
        things = interpret_flag(ord(flag))
        for literal in things:
            if literal:
                literal_byte = ord(f.read(1))
                print hex(literal_byte),
                buf[cursor % 0x1000] = literal_byte
                output.append(literal_byte)
                cursor += 1
            else:
                try:
                    pointer_bytes = ord(f.read(1)), ord(f.read(1))
                except TypeError:
                    break
                print "[%s %s]" % (hex(pointer_bytes[0]), hex(pointer_bytes[1])),
                packed = pointer_pack(pointer_bytes[0], pointer_bytes[1])
                length = pointer_length(packed)
                offset = pointer_offset(packed)
                if offset >= (cursor+0x12):
                    print "compressed zeroes",

                # Sometimes it does a cool thing where it points to bytes
                # as it's writing them!!
                # So you need to access buf one byte at a time to allow that.
                for b in range(0, length):
                    pointed_byte = buf[(offset+b) % 0x1000]
                    buf[cursor % 0x1000] = pointed_byte
                    output.append(pointed_byte)
                    cursor += 1
        print ""

        flag = f.read(1)
        try:
            print hex(cursor), hex(ord(flag)), ":", 
        except TypeError:
            print "end of input"
            break

#print [hex(b) for b in buf]
print hex(len(buf))

with open(output_filepath, 'wb') as f:
    for b in output:
        f.write(chr(b))


# header: 4c5a ("LZ"), almost like 4d5a ("MZ"), but suggesting LZ* compression