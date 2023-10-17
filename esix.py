import os
import subprocess
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from mail import send_mail

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
devices = {'192.168.245.69':['2', '3']}

# SNMP walk cmd
ifname_str = 'snmpwalk -v 2c -c SAGA {} IF-MIB::ifName.{}'
ifstatus_str = 'snmpwalk -v 2c -c SAGA {} IF-MIB::ifOperStatus.{}'

# Functions
def write_ts_data(device, metric, value):
    data_point = influxdb_client.Point(device).field(metric, value)
    api_writer.write(bucket=bucket, org=org, record=data_point)

def snmp_get(cmd):
    return filter(subprocess.check_output(cmd, shell=True).decode())

def filter(data_str):
    return data_str.split(': ')[1].split('\n')[0]

# esix
class ESIX:
    def __init__(self):
        self.subject = 'SAGA Found eSix Device Interface Down!'
        self.body = 'Device: {}\n - Interface {} is {}!\n\nThis is a test mail, do not reply!'
        self.data = self.get_port_health()

    def get_port_health(self):
        data = {}
        for host in devices:
            data[host] = []
            for if_id in devices[host]:
                if_name = snmp_get(ifname_str.format(host, if_id))
                if_status = snmp_get(ifstatus_str.format(host, if_id))
                if_status_int = int(if_status.split('(')[1].split(')')[0])
                write_ts_data(host, if_name, if_status_int)
                if 'up' not in if_status:
                    send_mail(subject=self.subject,
                              body=self.body.format(host, if_name, if_status[-3:]))
                data[host].append({if_name: if_status})
        return data
    
if __name__ == "__main__":
    esix = ESIX()
