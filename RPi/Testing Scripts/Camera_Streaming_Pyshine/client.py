# Part 03 using opencv access webcam and transmit the video in HTML
import picamera
import  pyshine as ps #  pip3 install pyshine==0.0.9
HTML="""
<html>
<head>
<title>PyShine Live Streaming</title>
</head>

<body>
<center><h1> PyShine Live Streaming using PiCamera </h1></center>
<center><img src="stream.mjpg" width='640' height='480' autoplay playsinline></center>
</body>
</html>
"""
def main():
    StreamProps = ps.StreamProps
    StreamProps.set_Page(StreamProps,HTML)
    address = ('192.168.14.14',5000) # Enter your IP address 
    StreamProps.set_Mode(StreamProps,'picamera')    
    with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
        output = ps.StreamOut()
        StreamProps.set_Output(StreamProps,output)
        camera.rotation = 180
        camera.start_recording(output, format='mjpeg')
        try:
            server = ps.Streamer(address, StreamProps)
            print('Server started at','http://'+address[0]+':'+str(address[1]))
            server.serve_forever()
        finally:
            camera.stop_recording()
   
        
if __name__=='__main__':
    main()