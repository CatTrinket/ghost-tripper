from collections import namedtuple
from struct import unpack

### sprite things

class NTFP():
    """A DS palette entry.

    RGBA, five bits per colour channel and one bit for transparency.
    """

    def __init__(self, color):
        color, = unpack('<H', color)

        self.r = color & 0x1f
        self.g = color >> 5 & 0x1f
        self.b = color >> 10 & 0x1f
        self.a = color >> 15

class NTFS():
    """A single tile in a screen."""
    def __init__(self, tile):
        tile, = unpack('<H', tile)

        self.palette = tile >> 12
        self.transformation = tile >> 10 & 0x3
        self.tile = tile & 0x3ff

class Screen():
    """Data to put together a sprite that takes up the entire screen."""
    def __init__(self, source):
        self.ntfs = []

        while source:
            self.ntfs.append(NTFS(source[:2]))
            source = source[2:]

    def image(self, palettes, tiles):
        """Actually put together the sprite."""
        # Prep the pixel matrix; each pixel is pixels[y][x] for easy iterating
        pixels = [[None for x in range(256)] for y in range(192)]

        for tile_num, tile in enumerate(self.ntfs):
            tile_x = tile_num % 32
            tile_y = tile_num // 32

            for pixel_num, pixel in enumerate(tiles[tile.tile]):
                # XXX Transforming will go here once I need it
                if tile.transformation != 0:
                    raise Exception('NTFS tile transformation')

                # The pixel's location within the entire image
                x = pixel_num % 8 + tile_x * 8
                y = pixel_num // 8 + tile_y * 8

                pixels[y][x] = palettes[tile.palette][pixel]

        return pixels


### cpac stuff

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
