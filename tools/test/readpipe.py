import win32file, pywintypes, winerror

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

# Set pipe mode to non-blocking
# win32file.SetFileMode(pipe, win32file.PIPE_NOWAIT)

for i in range(100):
    # Read data from the pipe (non-blocking)

    try:
        data = win32file.ReadFile(pipe, 1)
        print("Data read from pipe:", data[1][0])
    except pywintypes.error as e:
        if e.args[0] == winerror.ERROR_NO_DATA:
            print("No data available on pipe.")
        else:
            raise

# Close the pipe
win32file.CloseHandle(pipe)
