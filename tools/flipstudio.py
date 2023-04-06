# TODO add optional cmdline argument fro the serial baudrate. default: 74880. unit: bits per second
# TODO add optional cmdline argument for the input type: pipe or file. default: file
# TODO add optional cmdline argument for the input file name

import serial
import time

SERIAL_TIMEOUT = 0.02

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
def flip(ser, col, row, pol):
    if pol:
        cmdl = (1<<4)
    else:
        cmdl = 0

    cmdl |= (row & 0x0F)

    cmdh = (1<<7) | (col & 0x7F)

    ser.write(bytes([cmdh,cmdl]))


def serialize_bitmap(ser, filename, xoffset):
    # read the pixel data of the bitmap file
    
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
                    flip(ser, (width - 1 - (x * 8 + i) + xoffset) % width,height - 1 - y,1 if pixel else 0)
            f.seek(padding, 1)
    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('serial_port')

    args = parser.parse_args()

    with serial.Serial(args.serial_port, 74880, timeout=SERIAL_TIMEOUT) as ser:
        for offset in range(112):
            serialize_bitmap(ser, 'pixelbar-open-day.bmp', offset)
            time.sleep(0.5)
