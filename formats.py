from collections import namedtuple
from struct import unpack

from construct import *

### sprite things

class NTFPAdapter(Adapter):
    """A DS palette entry.

    RGBA, five bits per colour channel and one bit for transparency.
    """

    def _encode(self, rgba, context):
        return rgba.r | rgba.g << 5 | rgba.b << 10 | rgba.a << 15

    def _decode(self, color, context):
        return Container(
            r=color & 0x1f,
            g=color >> 5 & 0x1f,
            b=color >> 10 & 0x1f,
            a=bool(color >> 15)
        )

ntfp = NTFPAdapter(ULInt16('color'))
palette = GreedyRepeater(ntfp)


class NTFSAdapter(Adapter):
    """A single tile in a screen.

    No relation to the filesystem of the same name.
    """

    def _encode(self, obj, context):
        return obj.tile | obj.transformation << 10 | obj.palette << 12

    def _decode(self, obj, context):
        return Container(
            palette=obj >> 12,
            transformation=obj >> 10 & 0x3,
            tile=obj & 0x3ff
        )

ntfs = NTFSAdapter(ULInt16('tile'))
ntfs_repeater = GreedyRepeater(ntfs)

class Screen():
    """Data to put together a sprite that takes up the entire screen.

    A collection of NTFS cells; essentially an NSCR/NRCS without the headers.
    """

    def __init__(self, source):
        self.ntfs = ntfs_repeater.parse(source)

    def image(self, palettes, tiles):
        """Actually put together the sprite."""
        # Prep the pixel matrix; each pixel is pixels[y][x] for easy iterating
        pixels = [[None for x in range(256)] for y in range(192)]

        for tile_num, tile in enumerate(self.ntfs):
            tile_x = tile_num % 32
            tile_y = tile_num // 32

            for pixel_num, pixel in enumerate(tiles[tile.tile]):
                # The pixel's location within the entire image
                if tile.transformation == 0:
                    # No change
                    x = pixel_num % 8 + tile_x * 8
                    y = pixel_num // 8 + tile_y * 8
                elif tile.transformation == 1:
                    # Flip along the x axis
                    x = pixel_num % 8 + tile_x * 8
                    y = 7 - pixel_num // 8 + tile_y * 8
                elif tile.transformation == 2:
                    # Flip along the y axis
                    x = 7 - pixel_num % 8 + tile_x * 8
                    y = pixel_num // 8 + tile_y * 8
                else:
                    # XXX Is this actually invalid or does it just do both flips?
                    raise ValueError('invalid NTFS transformation')

                pixels[y][x] = palettes[tile.palette][pixel]

        return pixels


### cpac stuff
# XXX Turn these into pretty structs, too

CPACSection = namedtuple('CPACSection', ['offset', 'length'])

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
