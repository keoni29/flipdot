# TODO add optional cmdline arguments for setting the output type: serial, pipe or file. default: serial
# TODO add optional cmdline argument for the serial port. default: None
# TODO add optional cmdline argument fro the serial baudrate. default: 74880. unit: bits per second
# TODO add optional cmdline argument for the input type: pipe or file. default: file
# TODO add optional cmdline argument for the input file name

# if args.output_type == 'serial':
#     import serial
#     ser = serial.Serial(args.serial_port, args.serial_baudrate)

import sys,time

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

    #ser.write(bytes([cmdh,cmdl]))
    sys.stdout.buffer.write(bytes([cmdh, cmdl]))    

# Clear the display
# for y in range(height):
#         for x in range(width):
#             flip(x,y,1)

#     input("press enter please")


def serialize_bitmap(filename, xoffset):
    # read the pixel data of the bitmap file
    sys.stderr.write('Oy')
    with open(filename, 'rb') as f:
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
        
        f.seek(offset)
        padding = (4 - ((width * 1) % 4)) % 4
        padding += 2 # todo why do I need to add +2??? This calculation seems wrong

        

        for y in range(height):
            for x in range(width // 8):
                b = int.from_bytes(f.read(1), byteorder='little')
                for i in range(8):
                    if x * 8 + i >= width:
                        break
                    pixel = (b >> (7-i)) & 1
                    #print("X" if pixel else "_",end='')
                    flip((width - 1 - (x * 8 + i) + xoffset) % width,height - 1 - y,0 if pixel else 1)
            f.seek(padding, 1)
    

if __name__ == "__main__":
    serialize_bitmap('pixelbar-open-day.bmp', 0)
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(1)
    serialize_bitmap('pixelbar-open-day.bmp', 1)
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(1)
    serialize_bitmap('pixelbar-open-day.bmp', 2)
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(1)
    serialize_bitmap('pixelbar-open-day.bmp', 3)
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(1)