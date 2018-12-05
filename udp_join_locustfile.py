import yaml
import DeviceJoin
from udplocust import UdpLocsut
from locust import TaskSet, task
import sys
sys.path.append('./lib')

# Set host and port
config_file = './config/config.yml'
with open(config_file) as f:
    config = yaml.load(f)
target = (config.get('dest').get('hostname'), config.get('dest').get('port'))
timeMin = config.get('testInterval').get('min')
timeMax = config.get('testInterval').get('max')

pull_data = DeviceJoin.form_pullData('8cd98f00b204e980')
gateway_ids = []
devuis = []

with open('./info/gateway.csv') as f:
    for each in f.readlines():
        gateway_ids.append(each.replace('\n', ''))
with open('./info/DevEUI.csv') as f:
    for each in f.readlines():
        devuis.append(each.replace('\n', ''))


class UdpTasks(TaskSet):
    def on_start(self):

        gateway_id = gateway_ids.pop()
        devui = devuis.pop()
        self.client.gateway_id = gateway_id
        self.client.devui = devui
        pull_data = DeviceJoin.form_pullData(gateway_id)
        self.client.send(pull_data)
        self.client.recv()

    @task
    def test1(self):
        payload, DevNonce = DeviceJoin.form_pushData(
            self.client.gateway_id, self.client.devui)
        self.client.send_to_lora(
            payload, target, request_name='join', timeout=5)


class User(UdpLocsut):
    task_set = UdpTasks
    min_wait = timeMin
    max_wait = timeMax
    host = target
