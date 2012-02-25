from io import BytesIO
from struct import unpack

from formats import NTFP, NTFS, Screen, parse_cpac
from lzss3 import decompress

def split_into_tiles(data):
    t = []
    while data:
        t.append(data[:64])
        data = data[64:]
    return t


# Dump cpac_2d.bin's sections to separate files for easier individual
# staring-down
with open('/tmp/GT/fsroot/cpac_2d.bin', 'rb') as cpac_2d:
    data_sections = parse_cpac(cpac_2d)

for n, section in enumerate(data_sections):
    output = open('/tmp/cpac/{0}'.format(n), 'wb')
    output.write(section)


# Rip a palette that goes with the Capcom logo
data = BytesIO(data_sections[0])
data.seek(0x2d80)
palette = []

for color in range(0x100):
    palette.append(NTFP(data.read(2)))


# Rip the Capcom logo
data = BytesIO(data_sections[2])
data.seek(0xa00)  # Pointer found at 0x14

tiles = decompress(data)
tiles = split_into_tiles(tiles)

data.seek(0xa00 + 0xde8)
screen = Screen(decompress(data))

image = screen.image([palette], tiles)

with open('/tmp/logo.ppm', 'w') as output:
    # PPM header
    output.write(
        'P3\n'
        '256 192\n'
        '31\n'
    )

    for row in image:
        for pixel in row:
            print(pixel.r, pixel.g, pixel.b, file=output, end='  ')

        print(file=output)
