import os
import xlsxwriter
from rominfo import FILES, FILE_BLOCKS

dir = os.curdir

workbook = xlsxwriter.Workbook('rusty_dump.xlsx')
header = workbook.add_format({'bold': True, 'align': 'center', 'bottom': True, 'bg_color': 'gray'})

for gamefile in FILES:

    worksheet = workbook.add_worksheet(gamefile)
    worksheet.set_column('B:B', 60)
    worksheet.set_column('D:D', 60)
    worksheet.write(0, 0, 'Offset', header)
    worksheet.write(0, 1, 'Japanese', header)
    worksheet.write(0, 2, 'JP_Char', header)
    worksheet.write(0, 3, 'English', header)
    worksheet.write(0, 4, 'EN_Char', header)
    row = 1

    print "\n" + gamefile + "\n"
    if gamefile == 'JO.EXE':
        filename = gamefile
    else:
        filename = 'decompressed_' + gamefile
    with open(filename, 'rb') as f:
        for block in FILE_BLOCKS[gamefile]:
            block_length = block[1] - block[0]
            print "block:", hex(block[0])
            print "block length:", block_length
            f.seek(block[0], 0)
            contents = f.read(block_length+1)

            cursor = 0
            sjis_buffer = ""
            sjis_buffer_start = block[0]
            sjis_strings = []
            while cursor < len(contents):
                if 0x80 <= ord(contents[cursor]) & 0Xf0 <= 0x9f:
                    sjis_buffer += contents[cursor]
                    cursor += 1
                    sjis_buffer += contents[cursor]
                elif ord(contents[cursor]) == 0x4:
                    # [LN]
                    cursor += 1
                    if ord(contents[cursor]) == 0x0:
                        cursor += 1
                        if ord(contents[cursor]) == 0x73:
                            sjis_buffer += '[LN]'
                elif ord(contents[cursor]) == 0x1:
                    # [FACE1-nn]
                    cursor += 1
                    face = hex(ord(contents[cursor])).lstrip('0x')
                    cursor += 1
                    if ord(contents[cursor]) == 0x05:
                        sjis_buffer += '[FACE1-' + face + ']'
                elif ord(contents[cursor]) == 0xf:
                    # [FACEF-nn]
                    cursor += 1
                    face = hex(ord(contents[cursor])).lstrip('0x')
                    cursor += 1
                    if ord(contents[cursor]) == 0x45:
                        sjis_buffer += '[FACEF-' + face + ']'

                elif ord(contents[cursor]) == 0x5:
                    cursor += 1
                    if ord(contents[cursor]) == 0x1e:
                        cursor += 1
                        if ord(contents[cursor]) == 0x0d:
                            sjis_buffer += '[SCRL]'

                elif ord(contents[cursor]) == 0x15:
                    cursor += 1
                    dialogue_id = hex(ord(contents[cursor])).lstrip('0x')
                    cursor += 1
                    color = hex(ord(contents[cursor])).lstrip('0x')
                    sjis_buffer += '[TXT' + dialogue_id.zfill(2) + "-" + color.zfill(2) + ']'
                else:
                    if sjis_buffer:
                        sjis_strings.append((sjis_buffer_start, sjis_buffer))
                    sjis_buffer = ""
                    sjis_buffer_start = block[0] + cursor+1
                cursor += 1

            if len(sjis_strings) == 0:
                continue

            for s in sjis_strings:
                loc = '0x' + hex(s[0]).lstrip('0x').zfill(4)
                print loc
                print repr(s[1])
                jp = s[1].decode('shift-jis')
                worksheet.write(row, 0, loc)
                worksheet.write(row, 1, jp)
                row += 1
workbook.close()
