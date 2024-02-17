from flask import Flask, render_template, Response, request
from PIL import Image
import tempfile
import io

app = Flask(__name__)

frame = None

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/stream', methods=['POST'])
def stream():
    """Handle incoming frames from the Raspberry Pi."""
    global frame
    frame = request.data
    return('Frame received', 200)

def generate():
    """Return a single frame in byte format."""
    global frame
    while True:
        if frame is not None:
            image = Image.open(io.BytesIO(frame))
            
            # Save the image to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            image.save(temp_file, 'JPEG')
            temp_file.close()
            
            # ADD YOLO OBJECT DETECTION HERE - BOHUI
            # you can use temp_file.name to get the file name of the saved image.
            # e.g. model.predict(temp_file.name, save=True, imgsz=640, conf=0.5)... etc.
            
            
            # Read the image back into memory
            with open(temp_file.name, 'rb') as f:
                frame = f.read()
            
            # yield is to show the frame in the browser. To see the browser, open up 127.0.0.1:5000 in your browser.
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)