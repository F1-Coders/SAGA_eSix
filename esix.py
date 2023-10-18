import os
import time
import logging
import subprocess
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from mail import send_mail

# Logging config
logging.basicConfig(filename='history.log', 
                    level=logging.INFO,
                    format = '%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
                    datefmt = '%Y-%m-%d %A %H:%M:%S')

logging.info('SAGA Running!')

# DB Server Config
org = "eSix"
bucket = "network"
influx_server = "http://172.16.130.22:8086"
influx_token = os.environ.get('eSixInflux')
client = influxdb_client.InfluxDBClient(url=influx_server, token=influx_token, org=org)
api_writer = client.write_api(write_options=SYNCHRONOUS)

# Teams Alert Config
teams_token = os.environ.get('eSixTeams')

# devices {device_ip: [interface_id]}
## 192.168.245.69: [eth0]
devices = {'192.168.245.69': 'eBridge2',
           '192.168.245.68': 'eBridge1'}

# SNMP walk cmd
ifname_str = 'snmpwalk -v 2c -c SAGA {} IF-MIB::ifName'
ifstatus_str = 'snmpwalk -v 2c -c SAGA {} IF-MIB::ifOperStatus'

# Functions
def write_ts_data(device, metric, value):
    data_point = influxdb_client.Point(device).field(metric, value)
    api_writer.write(bucket=bucket, org=org, record=data_point)

def snmp_get(cmd):
    result = subprocess.check_output(cmd, shell=True).decode()
    result_list = [line.split(': ')[1] for line in result.split('\n')[:-1]]
    return result_list

# esix
class ESIX:
    def __init__(self):
        self.subject = 'SAGA Found eSix Device Interface Down!'
        self.body = '<h3>Device: {}</h3>'
        self.part = '<li>Interface {} is {}</li>'
        self.data = {}
        self.is_init = True

    def get_port_health(self):
        data = {}
        for host in devices:
            data[host] = {}
            if_name_list = snmp_get(ifname_str.format(host))
            if_status_list = snmp_get(ifstatus_str.format(host))

            # Create host mail taxt main part and init issue state to False
            msg = self.body.format(devices[host])
            is_issue = False
            for i in range(len(if_name_list)):
                # Collect data
                if_name = if_name_list[i]
                if_status = if_status_list[i]

                # Storage data to InfluxDB
                if_status_int = int(if_status.split('(')[1].split(')')[0])
                write_ts_data(host, if_name, if_status_int)

                # Process interface issue
                if self.is_init == True:
                    if host not in self.data.keys():
                        self.data[host] = []
                    self.data[host][if_name] = if_status
                else:
                    data[host][if_name] = if_status
                    if if_status != self.data[host][if_name]:
                        is_issue = True
                        part_str = self.part.format(if_name, if_status[-3:])
                        msg += part_str

            # Send mail when there is issue
            if is_issue:
                send_mail(subject=self.subject, body=msg)
                logging.error(msg)
        self.is_init = False
    
if __name__ == "__main__":
    esix = ESIX()
    while True:
        esix.get_port_health()
        time.sleep(60)
