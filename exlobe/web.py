import sys
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

def main():
    port = int(sys.argv[1])
    app.debug = True
    app.run(port=port)
