class AndroidDummy():
    def connect(self):
        print("Connected to Android dummy.")
    
    def disconnect(self):
        print("Disconnected from Android dummy.")

    def send(self, message):
        print(f"Sent {message} to Android dummy.")
    
    def receive(self):
        while True:
            pass