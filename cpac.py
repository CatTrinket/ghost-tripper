from collections import namedtuple
from struct import unpack

Section = namedtuple('Section', ['offset', 'length'])

def pointers(source):
    source.seek(0)
    pointers_length, = unpack('<L', source.read(4))

    source.seek(0)
    source = source.read(pointers_length)

    while source:
        yield Section(*unpack('<LL', source[:8]))
        source = source[8:]

cpac_2d = open('/tmp/GT/fsroot/cpac_2d.bin', 'rb')

for n, section in enumerate(pointers(cpac_2d)):
    cpac_2d.seek(section.offset)
    output = open('/tmp/cpac/{0}'.format(n), 'wb')
    output.write(cpac_2d.read(section.length))
