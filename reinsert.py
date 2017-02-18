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

files_to_reinsert = ['VISUAL.COM',]

for filename in files_to_reinsert:
    gamefile_path = os.path.join(SRC_DISK_DIR, 'decompressed_' + filename)
    GF = Gamefile(gamefile_path, disk=OriginalDisk, dest_disk=DestDisk)
    translations = DumpXl.get_translations(GF)
    pointers = PtrXl.get_pointers(GF)
    indexed_pointers = pointers.values()
    diff = 0
    if len(pointers) == 0: # VISUAL.COM
        diff = 0
        GF.filestring = GF.filestring[:0x3ac7] + '\x1a' + GF.filestring[0x3ac8:] # font table column subtrarction change (sub eax, 2000 -> sub eax, 1a00)
        GF.filestring = GF.filestring[:0x403c] + '\x02' + GF.filestring[0x403d:] # halfwidth cursor incrementing         (add dx, +04   -> add dx, +02)
        GF.filestring = GF.filestring[:0x4006] + '\xb4\x82' + GF.filestring[0x4008:] # SJIS fake prefix adding hack      (or ah, ah     -> mov ah, 82)
        #GF.filestring = GF.filestring[:0x3e3a] + '\x01' + GF.filestring[0x3e3b:] # remove row subtraction by 0x1a        (sub al, 1a    -> sub al, 1)
        GF.filestring = GF.filestring[:0x3e39] + '\x04\xdf\x90\x90\x90\x90\x90\x90' + GF.filestring[0x3e41:] # lowercase/uppercase fix
        removal_length = 0x3010-0x1462
        GF.filestring = GF.filestring[:0x1462] + '\x00'*removal_length + GF.filestring[0x3010:] # removing all non visual 1 data??
        GF.filestring = GF.filestring[:0x403e] + '\x2c\x82' + GF.filestring[0x4040:] # comma pause handling
        GF.filestring = GF.filestring[:0x4048] + '\x2e\x82' + GF.filestring[0x404a:] # period pause handling
        assert len(GF.filestring) == len(GF.original_filestring), hex(len(GF.filestring)) + " " + hex(len(GF.original_filestring))
        for t in [t for t in translations if t.location <= 0x13cd]:
            for cc in CONTROL_CODES:
                t.english = t.english.replace(cc, CONTROL_CODES[cc])
                t.japanese = t.japanese.replace(cc, CONTROL_CODES[cc])

            #t.english = ascii_to_fullwidth_sjis(t.english)
            #print repr(t.english)

            j = GF.filestring.index(t.japanese)
            this_diff = len(t.english) - len(t.japanese)
            if this_diff <= 0:
                print t.english
            diff += this_diff
            GF.filestring = GF.filestring.replace(t.japanese, t.english, 1)

        GF.filestring = GF.filestring[:0x3010-diff] + GF.filestring[0x3010:] # get rid of some 00s

        scene1_data = GF.filestring[0x632:0x1bb3]
        #scene1_new_location = len(GF.filestring) # 463e
        #print hex(scene1_new_location)
        #GF.filestring = GF.filestring[:0x77] + '\x3e\x46' + GF.filestring[0x79:] # edit scene 1 pointer
        #assert len(GF.filestring) == len(GF.original_filestring), hex(len(GF.filestring)) + " " + hex(len(GF.original_filestring))
        #GF.filestring += scene1_data
        #GF.filestring = GF.filestring.replace(scene1_data, '\x00'*len(scene1_data), 1) # make sure it's not loading the old one



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

        print p.text() # TODO: This function produces unspeakable horrors

    GF.write(path_in_disk='./RUSTY/', compression=True)