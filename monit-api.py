from flask import Flask, abort, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = b'secret_key'

MONIT_DIR = '/var/monit'
REPORT_DIR = os.path.join(MONIT_DIR, 'reports')


@app.route('/reports', methods=['GET'])
def get_reports():
    file_report = os.path.join(REPORT_DIR, 'reports.json')
    with open(file_report, 'r') as file:
        reports = json.load(file)
        return jsonify(reports)


@app.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id=None):
    file_report = os.path.join(REPORT_DIR, report_id, '.json')
    if os.path.exists(file_report):
        with open(file_report, 'r') as file:
            report = json.load(file)
        return jsonify(report)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
