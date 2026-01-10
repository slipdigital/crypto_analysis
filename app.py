"""
Flask application to display major cryptocurrency data
"""

from flask import Flask, render_template
import json
import os

app = Flask(__name__)

def load_crypto_data():
    """Load cryptocurrency data from JSON file"""
    json_file_path = os.path.join("crypto_data", "major_crypto_currencies.json")
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            return data.get('major_cryptos', [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

@app.route('/')
def index():
    """Main route to display cryptocurrency table"""
    crypto_list = load_crypto_data()
    return render_template('index.html', cryptos=crypto_list)

if __name__ == '__main__':
    app.run(debug=True)