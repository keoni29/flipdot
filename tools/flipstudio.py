import serial

ser = serial.Serial('COM13',74880)

"""
   * Serial command format: Two consecutive bytes containing x,y coordinates and dot polarity (on/off.)
   * CMDH = 1CCC CCCC
   * CMDL = 0xxP RRRR
   * 
   * C = column address
   * R = row address
   * P = dot polarity (1= on/ 0=off)
   * x = reserved for future use, set to 0 for now
   """
def flip(col, row, pol):
    if pol:
        cmdl = (1<<4)
    else:
        cmdl = 0

    cmdl |= (row & 0x0F)

    cmdh = (1<<7) | (col & 0x7F)

    ser.write(bytes([cmdl]))
    ser.write(bytes([cmdh]))

with open('pixelbar-open-day.bmp', 'rb') as f:
    # read the header information of the bitmap file
    f.seek(10)
    offset = int.from_bytes(f.read(4), byteorder='little')
    f.seek(18)
    width = int.from_bytes(f.read(4), byteorder='little')
    height = int.from_bytes(f.read(4), byteorder='little')
    f.seek(28)
    num_colors = int.from_bytes(f.read(4), byteorder='little')
    if num_colors == 0:
        num_colors = 2
    
    # read the pixel data of the bitmap file
    f.seek(offset)
    padding = (4 - ((width * 1) % 4)) % 4
    for y in range(height):
        for x in range(width):
            b = int.from_bytes(f.read(1), byteorder='little')
            for i in range(8):
                if x * 8 + i >= width:
                    break
                pixel = (b >> (7 - i)) & 1
                flip(x,y,pixel)
        f.seek(padding, 1)
