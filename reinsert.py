import os
from rominfo import SRC_DISK_PATH, SRC_DISK_DIR, DEST_DISK_PATH, DEST_DISK_DIR, CONTROL_CODES
from romtools.disk import Disk, Gamefile
from romtools.dump import PointerExcel, DumpExcel, Translation

OriginalDisk = Disk(SRC_DISK_PATH)
DestDisk = Disk(DEST_DISK_PATH)
DumpXl = DumpExcel('rusty_dump.xlsx')
PtrXl = PointerExcel('rusty_pointer_dump.xlsx')

#files_to_reinsert = ['VISUAL.COM', 'STORY1.COM', 'STORY2.COM', 'STORY3.COM', 'STORY4.COM', 'STORY5.COM', 'STORY6.COM',
#                     'STORY7.COM', 'STORY8.COM', 'STORY9.COM', 'STORY10.COM', 'ENEMY1.COM', 'ENEMY4.COM',
#                     'ENEMY9.COM', 'ENEMY10.COM' ]
files_to_reinsert = ['VISUAL.COM']

for filename in files_to_reinsert:
    scene_texts = []

    gamefile_path = os.path.join(SRC_DISK_DIR, 'decompressed_' + filename)
    GF = Gamefile(gamefile_path, disk=OriginalDisk, dest_disk=DestDisk)
    translations = DumpXl.get_translations(GF)
    pointers = PtrXl.get_pointers(GF)
    indexed_pointers = pointers.values()
    diff = 0
    if filename == 'VISUAL.COM':
        GF.edit(0x3ac7, '\x1a')     # font table column subtraction
        GF.edit(0x403c, '\x02')     # halfwidth cursor incrementing
        GF.edit(0x4006, '\xb4\x82') # prepend 0x82 to characters
        GF.edit(0x403e, '\x2c\x82') # comma pause handling
        GF.edit(0x4048, '\x2e\x82') # period pause handling
        GF.edit(0x3e39, '\x04\xdf\x90\x90\x90\x90\x90\x90') # fix lowercase char shifting by 1

        diff = 0

        for i, p in enumerate(pointers.itervalues()):
            #if p[0].text_location < 0x1462 or p[0].text_location > 0x1800: # scene 2 only
            if p[0].text_location >= 0x1800: # first two scenes only
                continue

            print "considering translations from pointer", p

            start = p[0].text_location
            try:
                next_p = indexed_pointers[i+1]
                stop = next_p[0].text_location
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
                for loc in next_p:
                    if loc.location > loc.text_location:
                        # Update the pointer location with the new diff.
                        cc = '[01' + "{0:x}".format(loc.text_location & 0xff) + "{0:x}".format((loc.text_location & 0xff00) >> 8) +  ']'
                        print "moving %s with diff %s" % (loc, diff)
                        loc.move_pointer_location(diff)
                    
                        # Reassign that control code to point somewhere else.
                        cc_bytes = '\x01' + chr((loc.text_location+diff) & 0xff) + chr(((loc.text_location+diff) & 0xff00) >> 8)
                        CONTROL_CODES[cc] = cc_bytes

                    print "editing %s with diff %s" % (loc, diff)
                    loc.edit(diff)

        #blank_length = 0x1420-0x632
        #GF.filestring = GF.filestring[:0x632] + '\x00'*blank_length + GF.filestring[0x1420:] # blank scene 1
        GF.filestring = GF.filestring[:0x2330-diff] + GF.filestring[0x2330:] # blank part of the file

        # So, that scene 2 crash. Doesn't have to do with the translations, control codes, or the ASM hacks.
        # But it does have to do with large blank spaces in the ROM...?
        # Can't just replace them with 20's, either. Weird.
        # Solved by overwriting parts of scenes we don't care about, without blanking them at all.

        # This is a problem with the control code 01 39 14.
        # Some of the similar control codes in the previous section are like 01 20 06, 01 2d 06, etc.
        # Probably pointing to something toward the beginning of each scene. (0x620, 0x62d, 0x1439, 0x142a, etc)
        # 0x142a = 04 00 05 0a 00 02 01 03 00 05 04 46 ff 2e 14
        # 0x1439 = 04 00 05 0a 02 05 03 0f 02 06 05 0f 02 04 03

        # vs2_00.mag = background
        # vs2_01.mag = Gateau
        # vs2_02.mag = Rusty
        # Yep, they're pointers to stuff in the scene headers. But, before the stuff that gets pointed to!

        # So they're basically pointers mixed in with text.
        # Pointable stuff between ?(0x142a, 0x2fd1)
        # So, look for stuff between (012a14) and (01d12f).

        # Why is it reading two bytes at once for ir???

        # Getting stuck at 8312:4419. "movsb, loop 4419"
        # Probably pops something stupidly big off the stack, then loops forever

        # Check the things that get pointed to in the headers. Are they code, or pointers to other things?

        # Is it worth just trying to get the length of the blocks down??
        # Scene 1 is ~2500 characters, and needs to be 193 shorter
        # Can I get rid of any control codes with no repercussions?

        assert len(GF.filestring) == len(GF.original_filestring), hex(len(GF.filestring)) + " " + hex(len(GF.original_filestring))


    # STORY/ENEMY.COM files are a bit simpler.
    else:
        for i, p in enumerate(pointers.itervalues()):
            start = p[0].text_location
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
