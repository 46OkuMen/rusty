import os
import xlsxwriter
from rominfo import FILES, FILE_BLOCKS

dir = os.curdir

workbook = xlsxwriter.Workbook('rusty_dump.xlsx')
header = workbook.add_format({'bold': True, 'align': 'center', 'bottom': True, 'bg_color': 'gray'})
block_division = workbook.add_format({'top': True, })

for gamefile in FILES:

    worksheet = workbook.add_worksheet(gamefile)
    worksheet.write(0, 0, 'Offset', header)
    worksheet.write(0, 1, 'Japanese', header)
    worksheet.write(0, 2, 'JP_Char', header)
    worksheet.write(0, 3, 'English', header)
    worksheet.write(0, 4, 'EN_Char', header)
    worksheet.write(0, 5, 'Comments', header)
    worksheet.set_column('A:A', 7)
    worksheet.set_column('B:B', 60)
    worksheet.set_column('C:C', 6)
    worksheet.set_column('D:D', 60)
    worksheet.set_column('E:E', 6)
    worksheet.set_column('F:F', 60)
    row = 1

    print "\n" + gamefile + "\n"
    if gamefile == 'JO.EXE' or gamefile == 'OP.COM':
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

                # First byte of SJIS text. Read the next one, too
                if 0x80 <= ord(contents[cursor]) & 0Xf0 <= 0x9f:
                    sjis_buffer += contents[cursor]
                    cursor += 1
                    sjis_buffer += contents[cursor]

                # [LN] ctrl code. 0x69 is top line, 0x73 is bottom line...
                elif ord(contents[cursor]) == 0x4:
                    # [LN]
                    cursor += 1
                    if ord(contents[cursor]) == 0x0:
                        cursor += 1
                        if ord(contents[cursor]) == 0x73:
                            sjis_buffer += '[LN]'

                # [1-nn] face animation control code. Talking state?
                elif ord(contents[cursor]) == 0x1 and sjis_buffer and cursor < block_length-2:
                    # [FACE1-nn]
                    cursor += 1
                    face = hex(ord(contents[cursor])).lstrip('0x')
                    cursor += 1
                    if ord(contents[cursor]) == 0x05:
                        sjis_buffer += '[1-' + face + ']'

                # [F-nn] face animation control code. Blinking state?
                elif ord(contents[cursor]) == 0xf and sjis_buffer and cursor < block_length-2:
                    cursor += 1
                    face = hex(ord(contents[cursor])).lstrip('0x')
                    cursor += 1
                    if ord(contents[cursor]) == 0x45:
                        sjis_buffer += '[F-' + face + ']'

                # [SCRL] scroll to empty line ctrl code
                elif ord(contents[cursor]) == 0x5 and cursor < block_length-2:
                    cursor += 1
                    if ord(contents[cursor]) == 0x1e:
                        cursor += 1
                        if ord(contents[cursor]) == 0x0d:
                            sjis_buffer += '[SCRL]'
                        else:
                            sjis_buffer += '[PAUSE]'
                            cursor -= 1

                # [1416] animation control code, advances BG frames in VS3
                elif ord(contents[cursor]) == 0x14 and cursor < block_length-1:
                    cursor += 1
                    if ord(contents[cursor]) == 0x16:
                        sjis_buffer += '[1416]'

                # [TXT-nn-yy] text ID, color ctrl code
                elif ord(contents[cursor]) == 0x15 and sjis_buffer:
                    cursor += 1
                    dialogue_id = hex(ord(contents[cursor])).lstrip('0x')
                    cursor += 1
                    color = hex(ord(contents[cursor])).lstrip('0x')
                    sjis_buffer += '[TXT' + dialogue_id.zfill(2) + "-" + color.zfill(2) + ']'

                # ASCII $
                elif ord(contents[cursor]) == 0x24:
                    sjis_buffer += "$"

                # End of continuous SJIS string, so add the buffer to the strings and reset buffer
                else:
                    if sjis_buffer:
                        sjis_strings.append((sjis_buffer_start, sjis_buffer))
                    sjis_buffer = ""
                    sjis_buffer_start = block[0] + cursor+1
                cursor += 1

            # Catch anything left after exiting the loop
            if sjis_buffer:
                sjis_strings.append((sjis_buffer_start, sjis_buffer))


            if len(sjis_strings) == 0:
                continue

            for s in sjis_strings:
                loc = '0x' + hex(s[0]).lstrip('0x').zfill(4)
                print loc
                print repr(s[1])
                try:
                    jp = s[1].decode('shift-jis')
                except UnicodeDecodeError:
                    # 86 a5 control code causes some problems
                    jp = s[1][2:].decode('shift-jis') 

                # Remove all ctrl code prefixes that aren't [LN]
                while jp.startswith('[') and not jp.startswith('[LN]'):
                    first_ctrl_code_index = jp.index(']')
                    jp = jp[first_ctrl_code_index+1:]

                # Remove all ctrl code suffixes that aren't [LN]
                while jp.endswith(']') and not jp.endswith('[LN]'):
                    last_ctrl_code_index = len(jp) - 1 - jp[::-1].index('[')
                    jp = jp[:last_ctrl_code_index]

                if len(jp) == 0 or jp == "$":
                    continue

                worksheet.write(row, 0, loc)
                worksheet.write(row, 1, jp)
                row += 1

            worksheet.set_row(row, 15, block_division)

workbook.close()
