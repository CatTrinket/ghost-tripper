from collections import namedtuple
from io import BytesIO
from struct import unpack
from sys import argv

from lzss3 import decompress
from tables import *

def message_iterator(data, pointer):
    """Yield the message at the given pointer, character by character.

    Each character is two bytes long and little endian.
    """
    data.seek(pointer)
    while True:
        char, = unpack('<H', data.read(2))

        if char == 0xfffe:
            raise StopIteration
        else:
            yield char

with open(argv[1], 'rb') as text_file:
    data = decompress(text_file)

data = BytesIO(data)

assert data.read(4) == b'1LMG'

# Seek to message pointers
data.seek(8)
pointers_offset, = unpack('<H', data.read(2))
data.seek(pointers_offset + 0x34)

assert data.read(4) == b'\x2a\x00\x00\x00'  # Not sure of the significance

message_count, = unpack('<L', data.read(4))
messages = []
Message = namedtuple('Message', ['label_offset', 'message_pointer'])

for m in range(message_count):
    messages.append(
        Message( *unpack('<LL', data.read(8)) )
    )

labels_pointer = data.tell()  # XXX Can I actually *find* this anywhere?

for message in messages:
    # Find the label and print it as a header
    data.seek(labels_pointer + message.label_offset)

    label = bytearray(b'')

    while True:
        char, = data.read(1)
        if char == 0:
            break
        else:
            label.append(char)

    label = label.decode('ASCII')
    print(label)
    print('=' * len(label))


    # Extract the actual message
    message = message_iterator(data, message.message_pointer)

    for char in message:
        if char == 0xff01:
            print()
        elif char == 0xff02:
            print('\n\n', end='')
        elif char == 0xff05:
            color = next(message)
            color = colors.setdefault(color, '#' + str(color))
            print('[[COLOR {0}]]'.format(color), end='')
        elif char == 0xff08:
            portrait = next(message)
            portrait = portraits.setdefault(portrait, '#' + hex(portrait))
            print('[[PORTRAIT: {0}]]'.format(portrait))
        else:
            char = text_table.setdefault(char, r'\x{0:04x}'.format(char))
            print(char, end='')

    print('\n\n', end='')  # Blank line between messages
