# import argparse
import logging
import queue
import threading
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

# TODO add optional cmdline argument for display resolution. default 112 x 16
# TODO add optional cmdline argument for display color. default black and yellow
# TODO add optional cmdline argument for mirroring the display horizontally. default: mirror


def input_handler_thread(queue, event):
    address = 1
    while not event.is_set():
        data = sys.stdin.buffer.read()
        if len(data):
            queue.put(data)
        else:
            time.sleep(0.1) # Some delay to prevent high CPU load
            
    if event.is_set():
        logging.info("Producer received event. Exiting")
    else:
        # In case thread crashed, make sure to close other threads by setting event
        event.set()



def display_thread(queue, event):
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
    while running and (not event.is_set()):
        
        # Handle events
        for pgEvent in pygame.event.get():
            if pgEvent.type == pygame.locals.QUIT:
                running = False    


        # Receive commands
        
        try:
            if not queue.empty():
                data = queue.get(block=False)

                # logging.info(
                #     "Size %d", queue.qsize()
                # )

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

    # In case thread crashed, make sure to close other threads by setting event
    if event.is_set():
        logging.info("Consumer received event. Exiting")
    else:
        # In case thread crashed, make sure to close other threads by setting event
        event.set()

    # Quit pygame
    pygame.quit()

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    pipeline = queue.Queue(maxsize=10)
    event = threading.Event()

    x = threading.Thread(target=display_thread, args=(pipeline, event))
    y = threading.Thread(target=input_handler_thread, args=(pipeline, event))
    x.start()
    y.start()
    
    y.join()
    logging.info("Main: about to set event")
    event.set()
    x.join()

    logging.info("Main: All done!")


