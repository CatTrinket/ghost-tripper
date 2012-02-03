from struct import unpack
from sys import argv

from lzss3 import decompress
from tables import *

def read_char():
    global data
    char, = unpack('<H', data[:2])
    data = data[2:]
    return char

data = decompress(open(argv[1], 'rb'))

#print(data[0xe9c:])
#exit()

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
    elif char == 0xff08:
        portrait = read_char()
        portrait = portraits.setdefault(portrait, '#' + hex(portrait))
        print('[[PORTRAIT: {0}]]'.format(portrait))
    else:
        char = text_table.setdefault(char, r'\x{0:04x}'.format(char))
        print(char, end='')

print()
