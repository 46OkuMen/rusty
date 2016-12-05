import os
from bitstring import BitArray

directory = os.curdir + os.sep
target_filepath = os.path.join(directory, 'RUSTY', 'VISUAL.COM')

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

assert interpret_flag('0x00') == [False, False, False, False, False, False, False, False]
assert interpret_flag(0) == interpret_flag('0x00')
assert interpret_flag('0xff') == [True,  True,  True,  True,  True,  True,  True,  True]
assert interpret_flag('0x7c') == [False, False, True,  True,  True,  True,  True,  False]
assert interpret_flag('0x76') == [False, True,  True,  False, True,  True,  True,  False]

assert flag_length('0x00') == 16
assert flag_length('0xFF') == 8
assert flag_length('0x7c') == 11

buf = []
with open(target_filepath, 'rb') as f:
	header = f.read(7) # 4c 5a 1a 3e 46 00 00
	flag = f.read(1)
	print hex(ord(flag)), ":",
	while flag != "":
		things = interpret_flag(ord(flag))
		for literal in things:
			if literal:
				literal_byte = f.read(1)
				print hex(ord(literal_byte)),
			else:
				pointer_bytes = f.read(1), f.read(1)
				print "[%s %s]" % (hex(ord(pointer_bytes[0])), hex(ord(pointer_bytes[1]))),
		print ""

		flag = f.read(1)
		print hex(ord(flag)), ":", 

# header: 4c5a ("LZ"), almost like 4d5a ("MZ"), but suggesting LZ* compression