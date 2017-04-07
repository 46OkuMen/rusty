import os
from rominfo import SRC_DISK_PATH, SRC_DISK_DIR, DEST_DISK_PATH, DEST_DISK_DIR, CONTROL_CODES, SCENE_POINTERS, WINDOW_EXPANSIONS
from romtools.disk import Disk, Gamefile
from romtools.dump import PointerExcel, DumpExcel, Translation

OriginalDisk = Disk(SRC_DISK_PATH)
DestDisk = Disk(DEST_DISK_PATH)
DumpXl = DumpExcel('rusty_dump.xlsx')
PtrXl = PointerExcel('rusty_pointer_dump.xlsx')

files_to_reinsert = ['VISUAL.COM', 'STORY1.COM', 'STORY2.COM', 'STORY3.COM', 'STORY4.COM', 'STORY5.COM', 'STORY6.COM',
                     'STORY7.COM', 'STORY8.COM', 'STORY9.COM', 'STORY10.COM', 'ENEMY1.COM', 'ENEMY4.COM',
                     'ENEMY9.COM', 'ENEMY10.COM' ]
#files_to_reinsert = ['VISUAL.COM']

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
        GF.edit(0x4043, '\x3f\x82') # question mark pause/blip handling (new, experimental)
        GF.edit(0x4048, '\x2e\x82') # period pause handling
        GF.edit(0x3e39, '\x04\xdf\x90\x90\x90\x90\x90\x90') # fix lowercase char shifting by 1

        for i, p in enumerate(pointers.itervalues()):
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
                if next_p[0].text_location == pointers[SCENE_POINTERS[2]][0].text_location:
                    stable_location = GF.filestring.index('\x07\x02\x76\x73\x33')
                    print hex(stable_location)
                    print "Scene 3 is next, so padding it here"
                    # (diff is negative here)
                    GF.filestring = GF.filestring[:stable_location] + '\x00'*((-1)*diff) + GF.filestring[stable_location:]
                    diff = 0

                for loc in next_p:
                    if loc.location > loc.text_location:
                        # Update the pointer location with the new diff.
                        cc = '[01' + "{0:02x}".format(loc.text_location & 0xff) + "{0:2x}".format((loc.text_location & 0xff00) >> 8) +  ']'
                        print "moving %s with diff %s" % (loc, diff)
                        loc.move_pointer_location(diff)
                    
                        # Some of these are embedded in the text, so they have a certain control code in the sheet.
                        # Reassign that control code to point somewhere else.
                        cc_bytes = '\x01' + chr((loc.text_location+diff) & 0xff) + chr(((loc.text_location+diff) & 0xff00) >> 8)
                        print "reassigning %s to %s" % (cc, repr(cc_bytes))
                        CONTROL_CODES[cc] = cc_bytes

                    print "editing %s with diff %s" % (loc, diff)
                    loc.edit(diff)

        print "final diff is", diff
        code_block_location = GF.filestring.index('\xe8\x99\x01\xb2\x0a\xb8\x13\x00')
        if diff > 0:
            GF.filestring = GF.filestring[:code_block_location-diff] + GF.filestring[code_block_location:] # blank part of the file
        else:
            GF.filestring = GF.filestring[:code_block_location] + '\x0d'*((-1)*diff) + GF.filestring[code_block_location:]

        SCENE_TO_TEST = 1     # 0-5 for scenes 1-6.
        scene_diff = pointers[SCENE_POINTERS[SCENE_TO_TEST]][0].new_text_location - pointers[SCENE_POINTERS[0]][0].new_text_location
        pointers[SCENE_POINTERS[0]][0].edit(scene_diff)

        SCENE_2_CORRUPTION_LOCATION = 0x167f

        assert len(GF.filestring) == len(GF.original_filestring), hex(len(GF.filestring)) + " " + hex(len(GF.original_filestring))


    # STORY/ENEMY.COM files are a bit simpler.
    else:
        for i, p in enumerate(pointers.itervalues()):
            start = p[0].text_location
            try:
                next_p = indexed_pointers[i+1][0]
                stop = indexed_pointers[i+1][0].text_location
            except IndexError:
                next_p = None
                stop = GF.length
            for t in [t for t in translations if start <= t.location < stop]:
                t.english = t.english.replace('[SLN]', '\x0d')
                t.japanese = t.japanese.replace('[SLN]', '\x0d')
                diff += (len(t.english) - len(t.japanese))
                j = GF.filestring.index(t.japanese)
                GF.filestring = GF.filestring.replace(t.japanese, t.english, 1)

            if next_p:
                print "editing %s with diff %s" % (next_p, diff)
                next_p.edit(diff)
        for (gamefile, offset, newvalue) in WINDOW_EXPANSIONS:
            if gamefile == filename:
                print "Adjusting window size:", gamefile, offset, newvalue
                GF.filestring = GF.filestring[:offset] + chr(newvalue) + GF.filestring[offset+1:]


    GF.write(path_in_disk='\\RUSTY\\', compression=True)
