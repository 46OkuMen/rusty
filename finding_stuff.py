import os

dir = os.path.join(os.path.curdir, 'RUSTY')

files = os.listdir(dir)

files.remove('rusty.hdi')
for file in files:
	with open(os.path.join(dir, file), 'rb') as f:
		## looking for "ko-no-(hen)" SJIS
		#if f.read().find('\x82\xb1\x82\xcc\x95\xd3') != -1:
		#	print file
		# looking for all files that begin with the header 'LZ' (4c5a)
		if f.read(2) == b'\x4c\x5a':
			print file