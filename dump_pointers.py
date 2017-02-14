import re
import os
import openpyxl
from collections import OrderedDict
from romtools.dump import BorlandPointer, PointerExcel
from romtools.disk import Gamefile
from rominfo import FILE_BLOCKS


#60 1e 06 8c c8 8e d8 be xx yy b9
pointer_regex = r'\\xd8\\xbe\\x([0-f][0-f])\\x([0-f][0-f])'
# TODO: This is probably not all of them...

def capture_pointers_from_function(hx): 
    return re.compile(pointer_regex).finditer(hx)

def location_from_pointer(pointer):
    return '0x' + str(format((unpack(pointer[0], pointer[1])), '04x'))

def unpack(s, t=None):
    if t is None:
        t = str(s)[2:]
        s = str(s)[0:2]
    s = int(s, 16)
    t = int(t, 16)
    value = (t * 0x100) + s
    return value

os.remove('rusty_pointer_dump.xlsx')
PtrXl = PointerExcel('rusty_pointer_dump.xlsx')

# TODO: Alphanumeric sort on the files still does STORY1, STORY10, STORY2, etc
for gamefile in sorted([f for f in FILE_BLOCKS if f.startswith('STORY') or f.startswith('ENEMY')]):
    gamefile_path = os.path.join('original', 'decompressed_' + gamefile)
    print gamefile_path
    GF = Gamefile(gamefile_path)
    with open(gamefile_path, 'rb') as f:
        bytes = f.read()
        target_areas = FILE_BLOCKS[gamefile]

        only_hex = ""
        for c in bytes:
            only_hex += '\\x%02x' % ord(c)

        pointers = capture_pointers_from_function(only_hex)
        pointer_locations = OrderedDict()

        for p in pointers:
            pointer_location = p.start()/4 + 1


            pointer_location = '0x%05x' % pointer_location
            text_location = location_from_pointer((p.group(1), p.group(2)),)

            if not any([t[0] <= int(text_location, 16) <= t[1] for t in target_areas]):
            #if not target_area[0] <= int(text_location, 16) <= target_area[1]:
                continue

            all_locations = [pointer_location,]

            if text_location in pointer_locations:
                all_locations = pointer_locations[text_location]
                all_locations.append(pointer_location)

            print GF, text_location
            pointer_locations[text_location] = all_locations

            print text_location

    # Setup the worksheet for this file
    worksheet = PtrXl.add_worksheet(GF.filename.lstrip('decompressed_'))

    row = 1

    for text_location, pointer_locations in sorted((pointer_locations).iteritems()):
        obj = BorlandPointer(GF, pointer_locations, text_location)
        print text_location
        print pointer_locations

        for pointer_loc in pointer_locations:
            worksheet.write(row, 0, text_location)
            worksheet.write(row, 1, pointer_loc)
            try:
                worksheet.write(row, 2, obj.text())
            except:
                worksheet.write(row, 2, '')
            row += 1

PtrXl.close()