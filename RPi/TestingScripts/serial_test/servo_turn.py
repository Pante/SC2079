from serial import Serial

com = Serial('/dev/ttyUSB0', 115200)

while True:
    next_val = input('Servo val >> ') + '\n'
    com.write(bytes(next_val, 'utf-8'))