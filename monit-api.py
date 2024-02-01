from flask import Flask, abort, jsonify
import json

app = Flask(__name__)
app.secret_key = b'secret_key'


@app.route('/reports', methods=['GET'])
def get_reports():
    with open('reports.json', 'r') as file:
        reports = json.load(file)
        return jsonify(reports)


@app.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    with open('reports.json', 'r') as file:
        reports = json.load(file)
        for report in reports:
            if report['id'] == report_id:
                return jsonify(report)
            else:
                abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
