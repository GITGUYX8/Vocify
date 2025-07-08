from flask import Flask, request, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'voice_sender.html')  # Serve the HTML page

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save('received_audio.webm')
    print("✅ Received voice file")
    return 'OK'

if __name__ == '__main__':
    app.run()
