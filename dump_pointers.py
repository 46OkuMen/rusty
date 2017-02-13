import re
import os
import openpyxl
from collections import OrderedDict
from romtools.dump import BorlandPointer, PointerExcel
from romtools.disk import Gamefile


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

pointer_locations = OrderedDict()
pointer_count = 0

PtrXl = PointerExcel('rusty_pointer_dump.xlsx')

for gamefile in ['STORY1.COM',]:
    gamefile_path = os.path.join('original', 'decompressed_' + gamefile)
    print gamefile_path
    GF = Gamefile(gamefile_path)
    with open(gamefile_path, 'rb') as f:
        bytes = f.read()
        target_area = (0x32a0, len(bytes)) # TODO: Don't hardcode this obviously
        #print hex(target_area[0]), hex(target_area[1])

        only_hex = ""
        for c in bytes:
            only_hex += '\\x%02x' % ord(c)

        pointers = capture_pointers_from_function(only_hex)

        for p in pointers:
            pointer_location = p.start()/4 + 1


            pointer_location = '0x%05x' % pointer_location
            text_location = location_from_pointer((p.group(1), p.group(2)),)

            if not target_area[0] <= int(text_location, 16) <= target_area[1]:
                continue

            all_locations = [pointer_location,]

            if (GF.filename, text_location) in pointer_locations:
                all_locations = pointer_locations[(GF.filename, text_location)]
                all_locations.append(pointer_location)

            pointer_locations[(GF, text_location)] = all_locations

            print text_location

    # Setup the worksheet for this file
    worksheet = PtrXl.add_worksheet(GF.filename)

    row = 1

    for (gamefile, text_location), pointer_locations in sorted((pointer_locations).iteritems()):
        obj = BorlandPointer(gamefile, pointer_locations, text_location)
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