from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Jenkins CI/CD Pipeline! MSSV: 22127477asdf"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
