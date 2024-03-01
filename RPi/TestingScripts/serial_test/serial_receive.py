from serial import Serial

com = Serial('/dev/ttyUSB0', 115200)
while True:
    if com.in_waiting > 0:
        print(str(com.read_all(), 'utf-8'))

com.close()