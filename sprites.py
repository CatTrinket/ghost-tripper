from io import BytesIO
from struct import unpack

from formats import parse_cpac
from lzss3 import decompress

def rgb(color):
    if color > 0x7fff:
        raise ValueError("color too big")  # Yes I know about the transparency bit

    return (color & 31, color >> 5 & 31, color >> 10 & 31)

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
        # tile_x = tile % 8 // 4 * 2 + tile % 2
        # tile_y = tile // 8 * 2 + tile // 2 % 2

        tile_x = tile % width
        tile_y = tile // width

        for pixel_y in range(8):
            y = tile_y * 8 + pixel_y

            for pixel_x in range(8):
                x = tile_x * 8 + pixel_x

                try:
                    pixels[y][x] = data.pop(0)
                except OverflowError:
                    pixels[y][x] = 0

    return pixels


# Dump cpac_2d.bin's sections to separate files for easier individual
# staring-down
with open('/tmp/GT/fsroot/cpac_2d.bin', 'rb') as cpac_2d:
    data_sections = parse_cpac(cpac_2d)

for n, section in enumerate(data_sections):
    output = open('/tmp/cpac/{0}'.format(n), 'wb')
    output.write(section)


# Rip a palette that I think goes with the Capcom logo
data = BytesIO(data_sections[0])
data.seek(0x2d80)  # Pointer found at 0x14

palette = [rgb(color) for color in unpack('<256H', data.read(0x200))]


# Rip the Capcom logo... sort of
data = BytesIO(data_sections[2])
data.seek(0xa00)  # Pointer found at 0x14

pixels = decompress(data)
pixels = untile(pixels, 24, 8)

with open('/tmp/logo.ppm', 'w') as output:
    # PPM header
    output.write(
        'P3\n'
        '192 64\n'
        '31\n'
    )

    for row in pixels:
        for pixel in row:
            print(*palette[pixel], file=output, end='  ')

        print(file=output)
