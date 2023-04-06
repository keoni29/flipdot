# TODO add optional cmdline arguments for setting the output type: serial, pipe or file. default: serial
# TODO add optional cmdline argument for the serial port. default: None
# TODO add optional cmdline argument fro the serial baudrate. default: 74880. unit: bits per second
# TODO add optional cmdline argument for the input type: pipe or file. default: file
# TODO add optional cmdline argument for the input file name

# if args.output_type == 'serial':
#     import serial
#     ser = serial.Serial(args.serial_port, args.serial_baudrate)

# import argparse
import logging
import time
import sys
import pygame
from pygame.locals import *


# Colors
C_BACKGROUND = (0,0,0)  # color for the background
C_DOT_OFF = (20,20,20)  # color for the OFF state of flipdots
C_DOT_ON = (180,180,0)  # color for the ON state of flipdots

# Framerate
MAXIMUM_FRAMERATE = 60  # pygame maximum framerate, unit : frames per second

# Display appearance
DIAMETER = 14 		    # diameter of flipdots, unit: pixels
RADIUS = DIAMETER // 2  # radius of flipdots, unit: pixels
SPACING = 2 		    # spacing in between flipdots, unit: pixels
OFFSET_X = 10           # x axis offset of the display, unit: pixels
OFFSET_Y = 10           # y axis offset of the display, unit: pixels

# Display resolution
NOF_COLUMNS = 112       # number of columns of the display on the x axis
NOF_ROWS = 16           # number of rows of the display on the y axis

# Pixel state
OFF = 0                 # pixel OFF state
ON = 1                  # pixel ON state

pixel = [[OFF]*NOF_COLUMNS for i in range(NOF_ROWS)]

# TODO add optional cmdline argument for display resolution. default 112 x 16
# TODO add optional cmdline argument for display color. default black and yellow
# TODO add optional cmdline argument for mirroring the display horizontally. default: mirror

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
    # if pol:
    #     cmdl = (1<<4)
    # else:
    #     cmdl = 0

    # cmdl |= (row & 0x0F)

    # cmdh = (1<<7) | (col & 0x7F)

    # #ser.write(bytes([cmdh,cmdl]))
    # # sys.stdout.buffer.write(bytes([cmdh, cmdl]))    
    # queue.put(bytes([cmdh, cmdl]))
    pixel[row][col] = pol


def serialize_bitmap(filename, xoffset):
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
                    flip((width - 1 - (x * 8 + i) + xoffset) % width,height - 1 - y,0 if pixel else 1)
            f.seek(padding, 1)
    

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    
    # Initialize pygame loop
    pygame.init()

    hres = NOF_COLUMNS * (DIAMETER + SPACING) + 2 * OFFSET_X    # Horizontal resolution
    vres = NOF_ROWS * (DIAMETER + SPACING) + 2 * OFFSET_Y       # Vertical resolution
    window = pygame.display.set_mode((hres,vres))
    clock = pygame.time.Clock()
    
    running = True

    counter = 0
    offset = 0

    # Pygame loop
    while running:
        
        # Handle events
        for pgEvent in pygame.event.get():
            if pgEvent.type == pygame.locals.QUIT:
                running = False    

        # Fill background color
        window.fill(C_BACKGROUND)

        counter += 1
        if counter >= 20:
            serialize_bitmap('pixelbar-open-day.bmp', offset)
            counter = 0
            offset += 1
            if offset >= 112:
                offset = 0



        # Redraw frame
        for col in range(0, NOF_COLUMNS):
            for row in range(0, NOF_ROWS): 
                color = C_DOT_ON if pixel[row][col] else C_DOT_OFF

                xx = col
                # Mirror display horizontally
                xx = NOF_COLUMNS - 1 - col
                center = (xx * (DIAMETER + SPACING) + OFFSET_X + RADIUS, 
                        row * (DIAMETER + SPACING) + OFFSET_Y + RADIUS)

                pygame.draw.circle(window, color, center, RADIUS)

        pygame.display.update()

        # Limit and display framerate
        clock.tick(MAXIMUM_FRAMERATE)
        pygame.display.set_caption(f"FPS: {clock.get_fps():.1f}")

    # Quit pygame
    pygame.quit()

    logging.info("Main: All done!")
