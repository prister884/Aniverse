import time

# Get the current time in seconds
start_time = time.time()

# Define the duration (4 hours in seconds)
count_seconds = 4 * 3600

while True:
    # Get the current time
    current_time = time.time()
    
    # Calculate elapsed time
    elapsed_time = current_time - start_time
    
    # Check if 4 hours have passed
    if elapsed_time >= count_seconds:
        print("4 hours have passed!")
        break
    
    # Calculate hours, minutes, and seconds
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    
    # Print the elapsed time
    print(f"Elapsed time: {hours} hours, {minutes} minutes, {seconds} seconds", end='\r')
    
    # Wait for a second before updating
    time.sleep(1)