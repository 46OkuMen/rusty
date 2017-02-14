import os
from lzss import compress
from rominfo import FILE_BLOCKS, SRC_DISK_PATH, SRC_DISK_DIR, DEST_DISK_PATH, DEST_DISK_DIR
from romtools.disk import Disk, Gamefile
from romtools.dump import PointerExcel, DumpExcel, BorlandPointer, Translation

OriginalDisk = Disk(SRC_DISK_PATH)
DestDisk = Disk(DEST_DISK_PATH)
DumpXl = DumpExcel('rusty_dump.xlsx')
PtrXl = PointerExcel('rusty_pointer_dump.xlsx')
files_to_reinsert = ['STORY1.COM',]

for filename in files_to_reinsert:
    gamefile_path = os.path.join(SRC_DISK_DIR, 'decompressed_' + filename)
    print gamefile_path
    GF = Gamefile(gamefile_path, disk=OriginalDisk, dest_disk=DestDisk)
    translations = DumpXl.get_translations(GF)
    pointers = PtrXl.get_pointers(GF)
    indexed_pointers = pointers.values()
    for i, p in enumerate(pointers.itervalues()):
        start = p.text_location
        try:
            stop = indexed_pointers[i+1].text_location
        except IndexError:
            stop = GF.length
        for t in [t for t in translations if start <= t.location < stop]:
            diff = len(t.en_bytestring) - len(t.jp_bytestring)
            j = GF.filestring.index(t.jp_bytestring)
            GF.filestring = GF.filestring.replace(t.jp_bytestring, t.en_bytestring, 1)

    GF.write()