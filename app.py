from flask import Flask, render_template, jsonify
import os
import socket
from datetime import datetime
import random

app = Flask(__name__)

VERSION = os.getenv('VERSION', 'blue')
PORT = int(os.getenv('PORT', 5000))

@app.route('/')
def home():
    hostname = socket.gethostname()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    visitor_count = random.randint(1000, 9999)
    
    return render_template('index.html', 
                         version=VERSION,
                         hostname=hostname,
                         current_time=current_time,
                         visitor_count=visitor_count)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': VERSION,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/about')
def about():
    return render_template('about.html', version=VERSION)

@app.route('/api/stats')
def stats():
    return jsonify({
        'version': VERSION,
        'hostname': socket.gethostname(),
        'uptime': 'Running',
        'requests': random.randint(100, 1000),
        'response_time': f"{random.randint(10, 100)}ms"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
