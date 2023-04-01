import win32pipe, win32file
import time
# Create the named pipe
pipe_name = r'\\.\pipe\mypipe'
pipe = win32pipe.CreateNamedPipe(
    pipe_name,                  # Pipe name
    win32pipe.PIPE_ACCESS_OUTBOUND,  # Pipe open mode (write-only)
    win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_WAIT, # Pipe mode
    1,                          # Maximum number of instances
    0,                          # Output buffer size
    0,                          # Input buffer size
    0,                          # Timeout in ms
    None                        # Security attributes
)

# Connect to the pipe
win32pipe.ConnectNamedPipe(pipe, None)

# Send data through the pipe
for i in range(0,20):
    data = b"\x80\x10"
    win32file.WriteFile(pipe, data)
    time.sleep(0.2)
    print("pixel on")

    data = b"\x80\x00"
    win32file.WriteFile(pipe, data)
    time.sleep(0.2)
    print("pixel off")

# Close the pipe
win32pipe.DisconnectNamedPipe(pipe)
win32file.CloseHandle(pipe)
