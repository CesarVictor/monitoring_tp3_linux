from flask import Flask, abort, jsonify
import json


app = Flask(__name__)
app.secret_key = b'secret_key'


@app.route('/reports', methods=['GET'])
def get_reports():
 pass