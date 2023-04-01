# TODO create separate thread for receiving data from pipe

import pygame
from pygame.locals import *
import win32file

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

# Open the named pipe
pipe_name = r'\\.\pipe\mypipe'
pipe = win32file.CreateFile(
    pipe_name,                  # Pipe name
    win32file.GENERIC_READ,     # Access mode (read-only)
    0,                          # No sharing
    None,                       # Security attributes
    win32file.OPEN_EXISTING,    # Open existing pipe
    0,                          # No attributes
    None                        # No template file
)

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
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            running = False    


    # Receive commands
    pipe_data = win32file.ReadFile(pipe, 1)[1][0]
    print(pipe_data)
    
    if pipe_data is not None:
        if (cmdl & (1<<7)):
            cmdh = cmdl
            # Read data from the pipe
            cmdl = pipe_data
            

            data = (cmdl >> 4) & 0x01
            row = cmdl & 0x0F
            col = cmdh & 0x7F
            cmdl = 0
            if col < NOF_COLUMNS and row < NOF_ROWS:
                pixel[row][col] = data   
        else:
            # Read data from the pipe
            cmdl = pipe_data



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

# Close the pipe
win32file.CloseHandle(pipe)

# Quit pygame
pygame.quit()

