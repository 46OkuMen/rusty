import re
import os
import openpyxl
from collections import OrderedDict
from romtools.dump import BorlandPointer, PointerExcel, unpack
from romtools.disk import Gamefile
from rominfo import FILE_BLOCKS

SCENE_2_START = 0x14cd
SCENE_2_HEADER = 0x1420
ENDING_STOP = 0x2fd1
SCENES_AFTER_1 = FILE_BLOCKS['VISUAL.COM'][1:]

#60 1e 06 8c c8 8e d8 be xx yy b9
pointer_regex = r'\\xd8\\xbe\\x([0-f][0-f])\\x([0-f][0-f])'
visual_pointer_regex = r'\\x1e\\x06\\xbe\\x([0-f][0-f])\\x([0-f][0-f])'
animation_pointer_regex = r'\\x01\\x([0-f][0-f])\\x([0-f][0-f])'
ani_loop_pointer_regex = r'\\xff\\x([0-f][0-f])\\x([0-f][0-f])'

def capture_pointers_from_function(hx, regex): 
    return re.compile(regex).finditer(hx)

def location_from_pointer(pointer):
    return '0x' + str(format((unpack(pointer[0], pointer[1])), '04x'))

try:
    os.remove('rusty_pointer_dump.xlsx')
except WindowsError:
    pass
PtrXl = PointerExcel('rusty_pointer_dump.xlsx')

# TODO: Alphanumeric sort on the files still does STORY1, STORY10, STORY2, etc
for gamefile in sorted(FILE_BLOCKS):
    if gamefile in ['JO.EXE', 'OP.COM']:
        gamefile_path = os.path.join('original', gamefile)
    else:
        gamefile_path = os.path.join('original', 'decompressed_' + gamefile)
    GF = Gamefile(gamefile_path)
    with open(gamefile_path, 'rb') as f:
        bytes = f.read()
        target_areas = FILE_BLOCKS[gamefile]

        only_hex = ""
        for c in bytes:
            only_hex += '\\x%02x' % ord(c)

        if gamefile == 'VISUAL.COM':
            pointers = capture_pointers_from_function(only_hex, visual_pointer_regex)
            animation_pointers = capture_pointers_from_function(only_hex, animation_pointer_regex)
            ani_loop_pointers = capture_pointers_from_function(only_hex, ani_loop_pointer_regex)
            target_areas = None
        else:
            pointers = capture_pointers_from_function(only_hex, pointer_regex)
            animation_pointers = []
            ani_loop_pointers = []

        pointer_locations = OrderedDict()

        for p in pointers:
            if gamefile == 'VISUAL.COM':
                pointer_location = p.start()/4 + 3
            else:
                pointer_location = p.start()/4 + 2


            pointer_location = '0x%05x' % pointer_location
            text_location = location_from_pointer((p.group(1), p.group(2)),)

            if target_areas:
                if not any([t[0] <= int(text_location, 16) <= t[1] for t in target_areas]):
                    continue

            # TODO: Is it necessary to collect all_locations here? Might just need to get them in the extractor.
            all_locations = [pointer_location,]

            if text_location in pointer_locations:
                all_locations = pointer_locations[text_location]
                all_locations.append(pointer_location)

            print GF, text_location
            pointer_locations[text_location] = all_locations

        for a in animation_pointers:
            pointer_location = a.start()/4 + 1
            text_location = location_from_pointer((a.group(1), a.group(2)),)

            # pointer_location should be in the text blocks themselves.
            # text_location should be in the headers, between the text blocks.

            if not any([pointer_location >= scene[0] and pointer_location <= scene[1] for scene in SCENES_AFTER_1]):
                continue

            # If it's outside the text blocks entirely, skip it.
            if int(text_location, 16) < SCENE_2_HEADER or int(text_location, 16) > ENDING_STOP:
                continue
            else:
                # If it's in the text blocks themselves, and not the headers, skip it.
                if any([int(text_location, 16) >= scene[0] and int(text_location, 16) <= scene[1] for scene in SCENES_AFTER_1]):
                    continue

            pointer_location = '0x%05x' % pointer_location

            all_locations = [pointer_location,]

            if text_location in pointer_locations:
                all_locations = pointer_locations[text_location]
                all_locations.append(pointer_location)

            pointer_locations[text_location] = all_locations


        for a in ani_loop_pointers:
            pointer_location = a.start()/4 + 1
            text_location = location_from_pointer((a.group(1), a.group(2)),)



            # pointer_location should be in the text blocks themselves.
            # text_location should be in the headers, between the text blocks.

            # For these, both text_location and pointer_location should be in the headers between text blocks.

            print text_location

            # If it's outside the text blocks entirely, skip it.
            if int(text_location, 16) < SCENE_2_HEADER or int(text_location, 16) > ENDING_STOP:
                continue
            else:
                # If it's in the text blocks themselves, and not the headers, skip it.
                if any([int(text_location, 16) >= scene[0] and int(text_location, 16) <= scene[1] for scene in SCENES_AFTER_1]):
                    continue

            pointer_location = '0x%05x' % pointer_location

            all_locations = [pointer_location,]

            if text_location in pointer_locations:
                all_locations = pointer_locations[text_location]
                all_locations.append(pointer_location)

            print GF, text_location
            pointer_locations[text_location] = all_locations


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