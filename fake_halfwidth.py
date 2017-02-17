from rominfo import CONTROL_CODES

def remove_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string

def ascii_to_fullwidth_sjis(ascii):

    result = ""
    while ascii:
        c = ascii[0]
        if ord(c) < 0x20:
            for ctrl in CONTROL_CODES.itervalues():
                if ascii.startswith(ctrl):
                    result += ctrl
                    ascii = remove_prefix(ascii, ctrl)

        else:
            result += '\x82'
            if ord(c) < 0x60: # uppercase or punctuation
                result += chr(ord(c)+0x1f)
            else: # lowercase
                result += chr(ord(c)+0x20)
            ascii = ascii[1:]
    return result

if __name__ == '__main__':
    print repr(ascii_to_fullwidth_sjis('AaBbCcDd\x04\x00\x73EeFfGg'))
