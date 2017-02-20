import os
from rominfo import FILE_BLOCKS, SRC_DISK_PATH, SRC_DISK_DIR, DEST_DISK_PATH, DEST_DISK_DIR, CONTROL_CODES
from romtools.disk import Disk, Gamefile
from romtools.dump import PointerExcel, DumpExcel, BorlandPointer, Translation
from romtools.lzss import compress
from fake_halfwidth import ascii_to_fullwidth_sjis

OriginalDisk = Disk(SRC_DISK_PATH)
DestDisk = Disk(DEST_DISK_PATH)
DumpXl = DumpExcel('rusty_dump.xlsx')
PtrXl = PointerExcel('rusty_pointer_dump.xlsx')

files_to_reinsert = ['VISUAL.COM', 'STORY1.COM', 'STORY2.COM', 'STORY3.COM']

for filename in files_to_reinsert:
    gamefile_path = os.path.join(SRC_DISK_DIR, 'decompressed_' + filename)
    GF = Gamefile(gamefile_path, disk=OriginalDisk, dest_disk=DestDisk)
    translations = DumpXl.get_translations(GF)
    pointers = PtrXl.get_pointers(GF)
    print pointers
    indexed_pointers = pointers.values()
    diff = 0
    if filename == 'VISUAL.COM':
        diff = 0
        GF.edit(0x3ac7, '\x1a')     # font table column subtraction
        GF.edit(0x403c, '\x02')     # halfwidth cursor incrementing
        GF.edit(0x4006, '\xb4\x82') # prepend 0x82 to characters
        GF.edit(0x3e39, '\x04\xdf\x90\x90\x90\x90\x90\x90') # fix lowercase char shifting by 1
        GF.edit(0x403e, '\x2c\x82') # comma pause handling
        GF.edit(0x4048, '\x2e\x82') # period pause handling



        for i, p in enumerate(pointers.itervalues()):
            if (p.text_location < 0x1462) or (p.text_location >= 0x1800): # Only doing the first two scenes for now
                continue

            print "considering translations from pointer", p

            start = p.text_location
            try:
                next_p = indexed_pointers[i+1]
                stop = indexed_pointers[i+1].text_location
            except IndexError:
                next_p = None
                stop = GF.length

            for t in [t for t in translations if start <= t.location < stop]:
                for cc in CONTROL_CODES:
                    t.english = t.english.replace(cc, CONTROL_CODES[cc])
                    t.japanese = t.japanese.replace(cc, CONTROL_CODES[cc])

                print repr(t.english)
                print repr(t.japanese)

                j = GF.filestring.index(t.japanese)
                this_diff = len(t.english) - len(t.japanese)
                diff += this_diff
                GF.filestring = GF.filestring.replace(t.japanese, t.english, 1)

            if next_p:
                print "editing %s with diff %s" % (next_p, diff)
                next_p.edit(diff)

        GF.filestring = GF.filestring[:0x2330-diff] + GF.filestring[0x2330:] # blank part of the file

        # So, that scene 2 crash. Doesn't have to do with the translations, control codes, or the ASM hacks.
        # But it does have to do with large blank spaces in the ROM...?
        # Can't just replace them with 20's, either. Weird.
        # Solved by overwriting parts of scenes we don't care about, without blanking them at all.

        assert len(GF.filestring) == len(GF.original_filestring), hex(len(GF.filestring)) + " " + hex(len(GF.original_filestring))


    else:
        for i, p in enumerate(pointers.itervalues()):
            start = p.text_location
            try:
                next_p = indexed_pointers[i+1]
                stop = indexed_pointers[i+1].text_location
            except IndexError:
                next_p = None
                stop = GF.length
            for t in [t for t in translations if start <= t.location < stop]:
                diff += (len(t.english) - len(t.japanese))
                j = GF.filestring.index(t.japanese)
                GF.filestring = GF.filestring.replace(t.japanese, t.english, 1)

            if next_p:
                print "editing %s with diff %s" % (next_p, diff)
                next_p.edit(diff)


    GF.write(path_in_disk='\\RUSTY\\', compression=True)
    # TODO: Fix paths for this thing. Use relative paths. "ndc P "patched\rusty.hdi" 0 patched\VISUAL.COM \RUSTY\"
    # This also works: ndc P "patched\rusty.hdi" 0 C:\Users\Max\Code\roms\rusty\patched\VISUAL.COM \RUSTY\