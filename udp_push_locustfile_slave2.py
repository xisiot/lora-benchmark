# /usr/bin/python3
from locust import TaskSet, task
import sys
sys.path.append('./lib')
from udplocust import UdpLocsut
import DeviceJoin
import PushData
import random
import json
import yaml

# Set host and port
config_file = './config/config.yml'
with open(config_file) as f:
    config = yaml.load(f)
target = (config.get('dest').get('hostname'), config.get('dest').get('port'))
timeMin = config.get('testInterval').get('min')
timeMax = config.get('testInterval').get('max')

pull_data = DeviceJoin.form_pullData('8cd98f00b204e980')
key_infos = []
gateway_ids = []

# load gateway id
with open('./info/gateway.csv') as f:
    for each in f.readlines():
        gateway_ids.append(each.replace('\n', ''))
    gateway_ids = gateway_ids[1000:2:000]

# load key	
with open('./info/key_info_lora.csv') as f:
    print(f.readline())
    for each in f.readlines():
        key_info = each.replace('\n', '').split(',')
        key_infos.append(key_info)

    key_infos = key_infos[1000:2000]

# Add send port list
sendports = []
for num in range(1000,2000):
    sendports.append(30000 + num)
    
class UdpTasks(TaskSet):
    def on_start(self):
        #  Bind send port 
        # sendport = sendports.pop()
        # self.client.bind(address = ('',sendport))

        key_info = key_infos.pop()
        self.client.devui = key_info[0]
        self.client.DevAddr = key_info[1]
        self.client.NwkSKey = key_info[2]
        self.client.AppSKey = key_info[3]

        gateway_id = gateway_ids.pop()
        self.client.gateway_id = gateway_id
        pull_data = DeviceJoin.form_pullData(self.client.gateway_id)

        self.client.send(pull_data)
        self.client.recv()

        self.client.fcount = 0

				# Add fcnt check
        #with open('./info/fcnt.json', 'r') as f:
        #    fcnt_dict = json.load(f)
        #    if self.client.devui in fcnt_dict:
        #         self.client.fcount = fcnt_dict[self.client.devui]
        #    else:
        #        self.client.fcount = 0

    @task
    def test(self):
        #pull_data = DeviceJoin.form_pullData(self.client.gateway_id)
        #self.client.send(pull_data)
        #print('pull_data receive', self.client.recv())

        payload = PushData.form_pushData(self.client.gateway_id, self.client.DevAddr, self.client.NwkSKey,
                                         self.client.AppSKey, self.client.fcount)
        self.client.send_to_lora(payload, target, request_name='app req', timeout=10)

				# Add fcnt check
        #self.client.fcount += 1
        #fcnt_dict = {}
        #with open('./info/fcnt.json', 'r') as f:
        #    fcnt_dict = json.load(f)
        #with open('./info/fcnt.json', 'w') as f:
        #    fcnt_dict[self.client.devui] = self.client.fcount
        #    f.write(json.dumps(fcnt_dict))

   # @task(10)
   # def test2(self):
 
    #    payload = PushData.form_pushData(self.client.gateway_id, self.client.DevAddr, self.client.NwkSKey,
    #                                     self.client.AppSKey, self.client.fcount)

    #    self.client.send_to_lora(payload, target=(host, port), request_name='app req', timeout=10)
     
class User(UdpLocsut):
    task_set = UdpTasks
    min_wait = timeMin
    max_wait = timeMax
    host = target
