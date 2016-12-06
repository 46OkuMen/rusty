import os

dir = os.path.join(os.path.curdir, 'RUSTY')

files = os.listdir(dir)

files.remove('rusty.hdi')
for file in files:
	with open(os.path.join(dir, file), 'rb') as f:
		## looking for "ko-no-(hen)" SJIS
		# (it's in VISUAL.COM)
		#if f.read().find('\x82\xb1\x82\xcc\x95\xd3') != -1:
		#	print file

		## looking for "kon kanga" SJIS
		# (probably compressed)
		#if f.read().find('\x8d\xa1\x82\xf0') != -1:
	#		print file

		# looking for 'rugoto' SJIS
		# (probably compressed)
		#if f.read().find('\x82\xe9\x82\xb1\x82\xc6') != -1:
	#		print file

		# looking for all files that begin with the header 'LZ[1a]' (4c5a1a)
		# (it's a lot of them)
		#if f.read(3) == b'\x4c\x5a\x1a':
	#		print file