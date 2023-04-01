# TODO add optional cmdline arguments for setting the output type: serial, pipe or file. default: serial
# TODO add optional cmdline argument for the serial port. default: None
# TODO add optional cmdline argument fro the serial baudrate. default: 74880. unit: bits per second
# TODO add optional cmdline argument for the input type: pipe or file. default: file
# TODO add optional cmdline argument for the input file name


import win32pipe, win32file

# if args.output_type == 'serial':
#     import serial
#     ser = serial.Serial(args.serial_port, args.serial_baudrate)

# import argparse

# if args.output_type == 'pipe':
if True:
    # Create the named pipe
    pipe_name = r'\\.\pipe\mypipe'
    pipe = win32pipe.CreateNamedPipe(
        pipe_name,                          # Pipe name
        win32pipe.PIPE_ACCESS_OUTBOUND,     # Pipe open mode (write-only)
        win32pipe.PIPE_TYPE_BYTE | 
            win32pipe.PIPE_WAIT,            # Pipe mode
        1,                                  # Maximum number of instances
        0,                                  # Output buffer size
        0,                                  # Input buffer size
        0,                                  # Timeout in ms
        None                                # Security attributes
    )

    # Connect to the pipe
    win32pipe.ConnectNamedPipe(pipe, None)

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
    win32file.WriteFile(pipe, bytes([cmdh, cmdl]))    

# Clear the display
# for y in range(height):
#         for x in range(width):
#             flip(x,y,1)

#     input("press enter please")


# read the pixel data of the bitmap file
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
    
    f.seek(offset)
    padding = (4 - ((width * 1) % 4)) % 4
    padding += 2 # todo why do I need to add +2??? This calculation seems wrong

    

    for y in range(height):
        for x in range(width // 8):
            b = int.from_bytes(f.read(1), byteorder='little')
            #print(b)
            for i in range(8):
                if x * 8 + i >= width:
                    break
                pixel = (b >> (7-i)) & 1
                #print("X" if pixel else "_",end='')
                flip((width - 1 - (x * 8 + i)) % width,height - 1 - y,0 if pixel else 1)
        #print('')
        f.seek(padding, 1)

# Close the pipe
win32pipe.DisconnectNamedPipe(pipe)
win32file.CloseHandle(pipe)