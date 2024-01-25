import json
import sys

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
args, unknown = parser.parse_known_args()
hours = 1

if args.command == 'get_avg' and unknown:
    last_arg = unknown[-1]
    if last_arg.isdigit():
        hours = int(last_arg)
    else:
        hours = 1

MONIT_DIR = '/var/monit'
REPORT_DIR = os.path.join(MONIT_DIR, 'reports')
CONFIG_DIR = '/etc/monit'
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
LOG_DIR = '/var/log/monit'
LOG_FILE = os.path.join(LOG_DIR, 'monit.log')


def create_monit_dir():
    if not os.path.exists(MONIT_DIR):
        os.makedirs(MONIT_DIR)


def create_report_dir():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)


def create_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def create_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print("Create log")


def create_config_file():
    config = {
        'ram_threshold': 20
    }
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(config, config_file)



def setup_logging():
    create_log_dir()
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_unique_id():
    return str(uuid.uuid4())


def log_command_call(command):
    logging.info(f"Command called: {command}")


def load_config(file_path):
    try:
        with open(CONFIG_FILE, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data
    except FileNotFoundError:
        print(f"Config file not found at {file_path}")
        sys.exit(1)


def send_alert(message):
    print(f"ALERT: {message}")


def check_resources():
    config = load_config(CONFIG_FILE)
    ram_threshold = config.get('ram_threshold', 20)
    ram_usage = psutil.virtual_memory().percent

    if ram_usage > ram_threshold:
        alert_message = f"Critical Alert: RAM usage exceeded the threshold ({ram_threshold}%): {ram_usage}%"
        send_alert(alert_message)
    disk_usage = psutil.disk_usage('/').percent
    cpu_usage = psutil.cpu_percent(interval=1)
    tcp_ports = [80, 443]
    port_status = {port: is_port_open(port) for port in tcp_ports}
    report = create_report(ram_usage, disk_usage, cpu_usage, port_status)
    save_report(report)
    return report


def create_report(ram_usage, disk_usage, cpu_usage, port_status):
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
        last_report_path = os.path.join(REPORT_DIR, reports[-1])
        with open(last_report_path, 'r') as file:
            return json.load(file)
    else:
        return None


def get_report_from_last_hours(hours):
    reports = list_reports()
    last_hours_reports = []
    for report in reports:
        report_path = os.path.join(REPORT_DIR, report)
        with open(report_path, 'r') as file:
            report_data = json.load(file)
            report_timestamp = datetime.datetime.strptime(report_data['timestamp'], "%Y-%m-%d %H:%M:%S")
            if report_timestamp > datetime.datetime.now() - datetime.timedelta(hours=hours):
                last_hours_reports.append(report_data)
    return last_hours_reports


def get_avg_report(hours=1):
    last_hours_reports = get_report_from_last_hours(hours)
    if last_hours_reports:
        ram_usage = sum([report['ram_usage'] for report in last_hours_reports]) / len(last_hours_reports)
        disk_usage = sum([report['disk_usage'] for report in last_hours_reports]) / len(last_hours_reports)
        cpu_usage = sum([report['cpu_usage'] for report in last_hours_reports]) / len(last_hours_reports)
        port_status = {
            port: sum([report['port_status'][port] for report in last_hours_reports]) / len(last_hours_reports)
            for port in last_hours_reports[0]['port_status']}
        return {
            'timestamp': get_timestamp(),
            'ram_usage': ram_usage,
            'disk_usage': disk_usage,
            'cpu_usage': cpu_usage,
            'port_status': port_status
        }


def main():
    create_monit_dir()
    create_report_dir()
    create_config_dir()
    setup_logging()

    commands = {
        'check': check_resources(),
        'list': list_reports(),
        'get_last': get_last_report(),
        'get_avg': get_avg_report(hours)
    }

    if args.command in commands:
        log_command_call(args.command)
        result = commands[args.command]
        print(result)
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
