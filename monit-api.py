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
    with open('reports.json', 'r') as file:
        reports = json.load(file)
        for report in reports:
            if report['id'] == report_id:
                return jsonify(report)
            else:
                abort(404)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)
