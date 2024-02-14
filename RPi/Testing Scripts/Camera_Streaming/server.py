from flask import Flask, render_template, Response, request

app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/stream', methods=['POST'])
def stream():
    """Handle incoming frames from the Raspberry Pi."""
    frame = request.data
    return Response(frame, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)