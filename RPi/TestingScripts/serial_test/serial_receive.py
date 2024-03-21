from serial import Serial

com = Serial('/dev/ttyUSB0', 115200)
print("Listening...")
while True:
    if com.in_waiting > 0:
        print(f"Received {str(com.read_all(), 'utf-8').strip()}.")