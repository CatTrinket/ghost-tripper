from struct import unpack

def untile(data, width, height):
    """Width and height are in tiles note to self better docstring"""

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

data = open('/tmp/GT/fsroot/cpac_2d.bin', 'rb')

#print(data.index(b'\xc4\xd6\x03'))

#exit()

data.seek(0x3e36100 - 512)

pixels = untile(bytearray(data.read(1024)), 4, 4)
for row in pixels:
    print(*row)

exit()

data.seek(0x124200)  # First RNAN
data.seek(0x10, 1)  # Skip RNAN header

assert data.read(4) == b'KNBA'

size, animations, frames = unpack('<LHH', data.read(8))

data.seek(0x14, 1)  # Skip more junk

animation_data = []
for i in range(animations):
    animation_data.append(unpack('<L8xL', data.read(16)))

frame_widths = []
for i in range(frames):
    frame_widths.append(*unpack('<4xH2x', data.read(8)))

data.seek(0x124210 + size)  # Skip to the good part I guess???

for frame in frame_widths:
    print(data.read(frame * 4))
