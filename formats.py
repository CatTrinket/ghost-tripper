from collections import namedtuple
from struct import unpack

### cpac stuff

CPACSection = namedtuple('Section', ['offset', 'length'])

def _cpac_pointers(source):
    source.seek(0)
    pointers_length, = unpack('<L', source.read(4))

    source.seek(0)
    source = source.read(pointers_length)

    while source:
        yield CPACSection(*unpack('<LL', source[:8]))
        source = source[8:]

def parse_cpac(source):
    sections = []

    for section in _cpac_pointers(source):
        source.seek(section.offset)
        sections.append(source.read(section.length))

    return sections
