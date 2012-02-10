from io import BytesIO
from struct import unpack

from formats import parse_cpac

def untile(data, width, height):
    """Width and height are tiles.  Needs a toooon of improvement."""
    pixel_width = width * 8
    pixel_height = height * 8

    # Each pixel is pixels[y][x]
    pixels = [[None for x in range(pixel_width)] for y in range(pixel_height)]

    for tile in range(width * height):
        #  0  1  4  5
        #  2  3  6  7
        #  8  9 12 13
        # 10 11 14 15
        tile_x = tile % 8 // 4 * 2 + tile % 2
        tile_y = tile // 8 * 2 + tile // 2 % 2

        for pixel_y in range(8):
            y = tile_y * 8 + pixel_y

            for pixel_x in range(8):
                x = tile_x * 8 + pixel_x

                pixels[y][x] = data.pop(0)

    return pixels


# Dump cpac_2d.bin's sections to separate files for easier individual
# staring-down
with open('/tmp/GT/fsroot/cpac_2d.bin', 'rb') as cpac_2d:
    data_sections = parse_cpac(cpac_2d)

for n, section in enumerate(data_sections):
    output = open('/tmp/cpac/{0}'.format(n), 'wb')
    output.write(section)


# Rip a few tiles of... something to a PGM.
data = BytesIO(data_sections[4])
data.seek(0xd3300 - 512)

pixels = untile(bytearray(data.read(1024)), 4, 4)

with open('/tmp/tiles.pgm', 'w') as output:
    # PGM header
    output.write(
        'P2\n'
        '32 32\n'
        '255\n'
    )

    for row in pixels:
        output.write(' '.join(str(pixel) for pixel in row))
        output.write('\n')
