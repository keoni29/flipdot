import serial
import time

ser = serial.Serial('COM5',74880)

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

    ser.write(bytes([cmdh]))
    ser.write(bytes([cmdl]))
    

mybitmap = []

# for y in range(height):
#         for x in range(width):
#             flip(x,y,1)

#     input("press enter please")


# read the pixel data of the bitmap file
for oops in [2]:
    while True:
        for xoffset in range(112):
            with open('pixelbar-leip.bmp', 'rb') as f:
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
                
                #print("oops = ", oops)
                f.seek(offset)
                padding = (4 - ((width * 1) % 4)) % 4

                

                for y in range(height):
                    for x in range(width // 8):
                        b = int.from_bytes(f.read(1), byteorder='little')
                        #print(b)
                        for i in range(8):
                            if x * 8 + i >= width:
                                break
                            pixel = (b >> (7-i)) & 1
                            #print("X" if pixel else "_",end='')
                            flip((width - 1 - (x * 8 + i) + xoffset) % width,height - 1 - y,0 if pixel else 1)
                            #time.sleep(0.0001)
                    #print('')
                    f.seek(padding + oops, 1)
            time.sleep(0.062)
