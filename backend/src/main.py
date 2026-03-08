from flask import Flask, jsonify
from flask_cors import CORS

FRONT_END_SERVER = "http://localhost:3000"

app = Flask(__name__)
CORS(app, origins=[FRONT_END_SERVER])


@app.get("/api/test")
def test():
    return "Hello World"


if __name__ == "__main__":
    app.run(port=8000, debug=True)