import os
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)
APP_NAME = os.getenv('APP_NAME', 'local')


@app.route('/')
def index():
    return f'Hello from {APP_NAME}!'


@app.route('/info')
def info():
    return jsonify(
        {
            'method': request.method,
            'path': request.path,
            'user_agent': request.headers.get('User-Agent'),
            'headers': dict(request.headers),
        }
    )


@app.route('/echo', methods=['POST'])
def echo():
    return jsonify({'you_sent': request.get_json(silent=True)}), 201


@app.route('/visit')
def visit():
    os.makedirs('data', exist_ok=True)
    with open('data/visits.log', 'a', encoding='utf-8') as f:
        f.write(f'{datetime.now().isoformat()} {request.remote_addr}\n')
    return 'Visit saved\n'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
