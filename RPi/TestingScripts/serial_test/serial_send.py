from serial import Serial

com = Serial('/dev/ttyUSB0', 115200)
with open('cmds.txt', 'r') as f:
	for cmd in f.readlines():
		cmd = cmd.rstrip() + '\n'
		com.write(bytes(cmd, "utf-8"))
		print(f"wrote {cmd.strip()}")
		
		while com.in_waiting <= 0:
			pass
		
		print(f"received {str(com.read_all(), 'utf-8')}")

com.close()
