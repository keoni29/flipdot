import pygame
from pygame.locals import *
import serial


# Colors
C_BACKGROUND = (0,0,0)  # color for the background
C_DOT_OFF = (20,20,20)  # color for the OFF state of flipdots
C_DOT_ON = (180,180,0)  # color for the ON state of flipdots

# Framerate
MAXIMUM_FRAMERATE = 60  # pygame maximum framerate, unit : frames per second
SERIAL_TIMEOUT_S = 0.02
MAX_NOF_SERIAL_BYTES = 2000

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

# TODO add optional cmdline argument for display resolution. default 112 x 16
# TODO add optional cmdline argument for display color. default black and yellow
# TODO add optional cmdline argument for mirroring the display horizontally. default: mirror

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('serial_port')

    args = parser.parse_args()

    with serial.Serial(args.serial_port, 74880, timeout=SERIAL_TIMEOUT_S) as ser:
        # Initialize pygame loop
        pygame.init()

        hres = NOF_COLUMNS * (DIAMETER + SPACING) + 2 * OFFSET_X    # Horizontal resolution
        vres = NOF_ROWS * (DIAMETER + SPACING) + 2 * OFFSET_Y       # Vertical resolution
        window = pygame.display.set_mode((hres,vres))
        clock = pygame.time.Clock()
        pixel = [[OFF]*NOF_COLUMNS for i in range(NOF_ROWS)]
        cmdl = cmdh = 0
        running = True

        # Pygame loop
        while running:
            
            # Handle events
            for pgEvent in pygame.event.get():
                if pgEvent.type == pygame.locals.QUIT:
                    running = False    


            # Receive commands
            
            try:
                
                data = ser.read(MAX_NOF_SERIAL_BYTES)
                if data is not None:
                    for byte in data:
                        if (cmdl & (1<<7)):
                            cmdh = cmdl
                            cmdl = byte
                            

                            pol = (cmdl >> 4) & 0x01
                            row = cmdl & 0x0F
                            col = cmdh & 0x7F
                            cmdl = 0
                            if col < NOF_COLUMNS and row < NOF_ROWS:
                                pixel[row][col] = pol   
                        else:
                            cmdl = byte

            except BaseException as e:
                raise e

            # Fill background color
            window.fill(C_BACKGROUND)

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
