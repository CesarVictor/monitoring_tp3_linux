import json
import psutil
import os
import subprocess
import datetime
import socket
import uuid
import argparse
import logging

parser = argparse.ArgumentParser(description='Linux Monitoring Tool')
parser.add_argument('command', choices=['check', 'list', 'get_last', 'get_avg'],
                    help='Command to execute (check, list, get_last, get_avg)')
args = parser.parse_args()

MONIT_DIR = '/var/monit'
REPORT_DIR = os.path.join(MONIT_DIR, 'reports')
CONFIG_FILE = '/etc/monit/config.json'
LOG_DIR = '/var/log/monit'
LOG_FILE = os.path.join(LOG_DIR, 'monit.log')


def create_monit_dir():
    if not os.path.exists(MONIT_DIR):
        os.makedirs(MONIT_DIR)


def create_report_dir():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)


def create_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def setup_logging():
    create_log_dir()
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_unique_id():
    return str(uuid.uuid4())


def log_command_call(command):
    logging.info(f"Command called: {command}")


def check_resources():
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    cpu_usage = psutil.cpu_percent(interval=1)
    tcp_ports = [80, 443]
    port_status = {port: is_port_open(port) for port in tcp_ports}

    return {
        'timestamp': get_timestamp(),
        'id': get_unique_id(),
        'ram_usage': ram_usage,
        'disk_usage': disk_usage,
        'cpu_usage': cpu_usage,
        'port_status': port_status
    }


def is_port_open(port):
    try:
        sock = socket.create_connection(('127.0.0.1', port), timeout=1)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False


def save_report(report):
    report_path = os.path.join(REPORT_DIR, f"{report['id']}.json")
    with open(report_path, 'w') as file:
        json.dump(report, file)


def list_reports():
    return os.listdir(REPORT_DIR)


def get_last_report():
    reports = list_reports()
    if reports:
        last_report_path = os.path.join(REPORT_DIR, max(reports))
        with open(last_report_path, 'r') as file:
            return json.load(file)
    else:
        return None


def get_avg_report(hours):
    # Placeholder for calculating average report
    pass


def main():
    create_monit_dir()
    create_report_dir()
    setup_logging()

    commands = {
        'check': check_resources,
        'list': list_reports,
        'get_last': get_last_report,
        'get_avg': get_avg_report
    }

    if args.command in commands:
        log_command_call(args.command)
        result = commands[args.command]()
        print(result)
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
