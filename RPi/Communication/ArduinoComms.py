import serial
import time

class ArduinoComm(object):

    #Initialize the items required for Arduino Comms
    #Remember to check baud rate and communication port!
    def __init__(self, port='/dev/ttyUSB0'):
        self.commPort = port #TOCHECK from Pi on connections
        self.isEstablished = False
        self.baud = 115200 #Technical documentation
        

    #Good to have to check if connected
    def isConnected(self):
        return self.isEstablished

    def connect(self):
        while True:
            retry = False
            try:
                #Let's wait for connection
                print ('[ARDUINO_INFO] Waiting for serial connection from Arduino')

                self.serialConn = serial.Serial(self.commPort, self.baud, timeout=None, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
                print('[ARDUINO_ACCEPTED] Connected to Arduino.')
                self.isEstablished = True
                retry = False

            except Exception as e:
                print('[ARDUINO_ERROR] Arduino Connection Error: %s' % str(e))
                retry = True

            #When established, break the while(true)
            if (not retry):
                break

            #When not yet established, keep retrying
            print('[ARDUINO_INFO] Retrying Arduino Establishment')
            time.sleep(1)

    #Disconnect when done
    def disconnect(self):
        if not (self.serialConn is None): #if (self.serialConn):
            print('[ARDUINO_CLOSE] Shutting down Arduino Connection')
            self.serialConn.close()
            self.isEstablished = False

    #The fundamental trying to receive
    def read(self):
        try:
            readData = self.serialConn.readline()
            self.serialConn.flush() #Clean the pipe
            readData = readData.decode('ascii')
            if readData == '':
                return None
            print('[ARDUINO_INFO] Received: ' + readData)
            return readData

        except Exception as e:
            print('[ARDUINO_ERROR] Receiving Error: %s' % str(e))
            if ('Input/output error' in str(e)):
                self.disconnect()
                print('[ARDUINO_INFO] Re-establishing Arduino Connection.')
                self.connect()

    #The fundamental trying to send
    def write(self, message):
        try:
            #Make sure there is a connection first before sending
            if self.isEstablished:
                message = message.encode('ascii')
                self.serialConn.write(message)
                return

            #There is no connections. Send what?
            else:
                print('[ARDUINO_INVALID] No Arduino Connections')

        except Exception as e:
            print('[ARDUINO_ERROR] Cannot send message: %s' % str(e))
            
#arduino = ArduinoComm()
#arduino.connect()
#arduino.show_settings()


# msg_read = "FP|(1,1,N);(2,1,N);(2,2,E)"
# pc_msg = pcMsgParser(msg_read)
# print(pc_msg)

#while True:
'''
    try:
        msg = arduino.read()
        if msg is not None:
            print(msg)
    except Exception as e:
        pass
'''
    #command = input("Enter command to send to Arduino:")
'''
    if command == 'demo':
        print('Init demo')
        arduino.write(pc_msg['payload']['arduino'])
    else:
'''
    #arduino.write(command)





