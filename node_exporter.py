import psutil
from prometheus_client import Gauge, start_http_server
import time
import toml
import logging
import requests

# Setup basic logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Prometheus metrics
event_stream_buffer_length_gauge = Gauge('event_stream_buffer_length', 'Length of the event stream buffer')
qps_limit_gauge = Gauge('qps_limit', 'Query per second limit for RPC server')
api_version_gauge = Gauge('api_version_info', 'API version of the Casper Node', ['version'])
next_upgrade_gauge = Gauge('next_upgrade_version', 'Next upgrade version of the Casper Node', ['version'])
reactor_state_gauge = Gauge('reactor_state', 'Current state of the reactor', ['state'])


def find_config_path():
    """Searches for the casper-node process and extracts the configuration path from its command line."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'casper-node' and len(proc.info['cmdline']) > 1:
            for arg in proc.info['cmdline']:
                if arg.endswith('.toml'):
                    logging.info(f"Found configuration file at: {arg}")
                    return arg
    logging.warning("casper-node process not found or config file argument missing.")
    return None

def parse_toml_config(config_path):
    """Parses the TOML configuration file for specific values, focusing on nested structures."""
    if config_path is None:
        logging.error("No configuration path provided.")
        return 0, 0
    try:
        config = toml.load(config_path)
        event_stream_buffer_length = config['event_stream_server']['event_stream_buffer_length']
        qps_limit = config['rpc_server']['qps_limit']
        logging.info(f"event_stream_buffer_length: {event_stream_buffer_length}, qps_limit: {qps_limit}")
        return event_stream_buffer_length, qps_limit
    except Exception as e:
        logging.error(f"Error reading TOML configuration: {e}")
        return 0, 0

def fetch_api_version():
    """Fetches the API version, next upgrade version, and reactor state from the specified endpoint and updates the gauges."""
    try:
        response = requests.get("http://localhost:8888/status")
        response.raise_for_status()
        data = response.json()

        api_version = data.get('api_version', "unknown")
        api_version_gauge.labels(version=api_version).set(1)

        next_upgrade = data.get('next_upgrade', "unknown")
        next_upgrade_gauge.labels(version=next_upgrade).set(1 if next_upgrade != "unknown" else 0)

        # Resetting and setting the reactor state
        current_states = list(reactor_state_gauge.collect()[0].samples)
        for sample in current_states:
            reactor_state_gauge.remove(sample.labels['state'])

        reactor_state = data.get('reactor_state', "unknown")
        reactor_state_gauge.labels(state=reactor_state).set(1)
        logging.info(f"API Version: {api_version}, Next Upgrade: {next_upgrade}, Reactor State: {reactor_state}")

    except requests.RequestException as e:
        logging.error(f"Failed to fetch status data: {e}")
        api_version_gauge.labels(version="unknown").set(0)
        next_upgrade_gauge.labels(version="unknown").set(0)
        reactor_state_gauge.labels(state="unknown").set(0)

def update_metrics_from_config(config_path):
    """Update the Prometheus metrics with values from the TOML config."""
    event_stream_buffer_length, qps_limit = parse_toml_config(config_path)
    event_stream_buffer_length_gauge.set(event_stream_buffer_length)
    qps_limit_gauge.set(qps_limit)
    fetch_api_version()

if __name__ == '__main__':
    config_path = find_config_path()
    if config_path:
        start_http_server(8000)
        logging.info("Prometheus metrics server running on port 8000")
        while True:
            update_metrics_from_config(config_path)
            time.sleep(30)
    else:
        logging.error("Script initialization failed due to missing configuration path.")