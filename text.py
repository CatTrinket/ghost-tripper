from struct import unpack
from sys import argv

from tables import text_table, colors

def lz_decompress(bytes):
    # Copy-pasted straight out of bw_animations.py; pretty unreadable but I
    # guess it works!
    lz_type = bytes[0]
    size = unpack('<L', bytes[:4])[0] >> 8
    bytes = bytes[4:]
    data = bytearray()
    while bytes and len(data) < size:
        type_flags = bytes[0]
        bytes = bytes[1:]
        for bit in reversed(range(8)):
            if len(data) >= size:
                break
            if type_flags >> bit & 1:
                indicator = bytes[0] >> 4
                if lz_type == 0x10:
                    thing, = unpack('>H', bytes[:2])
                    num = (thing >> 12) + 3
                    distance = thing & 0xfff
                    bytes = bytes[2:]
                elif indicator == 0:
                    thing, = unpack('>L', b'\x00' + bytes[:3])
                    num = (thing >> 12) + 0x11
                    distance = thing & 0xfff
                    bytes = bytes[3:]
                elif indicator == 1:
                    thing, = unpack('>L', bytes[:4])
                    num = (thing >> 12 & 0xffff) + 0x111
                    distance = thing & 0xfff
                    bytes = bytes[4:]
                else:
                    thing, = unpack('>H', bytes[:2])
                    num = (thing >> 12) + 1
                    distance = thing & 0xfff
                    bytes = bytes[2:]

                for byte_read in range(num):
                    data.append(data[-(distance + 1)])
            else:
                try:
                 data.append(bytes[0])
                 bytes = bytes[1:]
                except IndexError: print (data, len(data), size, bytes)
    return data

def read_char():
    global data
    char, = unpack('<H', data[:2])
    data = data[2:]
    return char

data = lz_decompress(open(argv[1], 'rb').read())

while data:
    char = read_char()

    if char == 0xff01:
        print()
    elif char == 0xff02:
        print('\n')
    elif char == 0xff05:
        color = read_char()
        color = colors.setdefault(color, '#' + str(color))
        print('[[COLOR {0}]]'.format(color), end='')
    else:
        char = text_table.setdefault(char, r'\x{0:04x}'.format(char))
        print(char, end='')

print()
