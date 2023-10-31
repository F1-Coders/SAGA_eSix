import time
import datetime
from mail import send_mail
from spider import Monitor

devices = ['eBridge2', 'eBridge1', 'CCBI-KIC', 'CCBI-CCBT']
receiver = 'servicedesk@f1.hk'
check_url = 'https://sdm.hk.esixcloud.net:20001/ui#/main-page'

def run():
    while True:
        try:
            monitor = Monitor('f1', 'f1@123')
            result = monitor.get_device_status()
            log = ','.join(result)
            with open('log', 'a') as f:
                now = str(datetime.datetime.today()).split('.')[0]
                f.write(now + '  ' + log + '\n')
            #monitor.driver.close()
            if len(result) != 8:
                print('Error')
            else:
                data = result[:4]
                for i in range(len(data)):
                    if data[i] != 'Online':
                        subject = f"eSix alert: Device {devices[i]} has issue"
                        body = f"SAGA find eSix device {devices[i]} has issue, the health-state is not Online\nPlease login into {check_url} to check it!"
                        send_mail(receiver, subject, body)
            time.sleep(300)
            monitor.driver.close()
        except:
            pass

def test():
    monitor = Monitor('f1', 'f1@123')
    result = monitor.get_device_status()
    data = result[1:5]
    for i in range(len(data)):
        if data[i] != 'Online':
            subject = f"eSix alert: Device {devices[i]} has issue"
            body = f"SAGA find eSix device {devices[i]} has issue, the health-state is not Online\nPlease login into {check_url} to check it!"
            send_mail(receiver, subject, body)

run()
#test()
