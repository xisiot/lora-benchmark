import requests
import json

gateway_ids = []
devuis = []
with open('./info/gateway.csv') as f:
    for each in f.readlines():
        gateway_ids.append(each.replace('\n', ''))
with open('./info/DevEUI.csv') as f:
    for each in f.readlines():
        devuis.append(each.replace('\n', ''))

# headers一般需要修改'grpc-metadata-authorization'，相当于普通网页中的cookie，与登录相关.也可以为空
headers = {
    'grpc-metadata-authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJsb3JhLWFwcC1zZXJ2ZXIiLCJleHAiOjE1NDMzMDczMjUsImlzcyI6ImxvcmEtYXBwLXNlcnZlciIsIm5iZiI6MTU0MzIyMDkyNSwic3ViIjoidXNlciIsInVzZXJuYW1lIjoiYWRtaW4ifQ.oyZsy3_4mh8H-Weo1P36Y8UuZpEa1CJiusjGvcpr2RY',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'origin': 'https://10.3.242.236:8080',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.8',
    'content-type': 'text/plain;charset=UTF-8'
}
# 设备注册，第一个请求注册设备，第二个绑定applicationKey
# 可能需要修改对应的ProfileID
def device_register():
    for devui in devuis:
        data1 = {"device":{"name":devui,"description":"deveui","devEUI":devui,"deviceProfileID":"440f72c2-c3b2-42e5-a5a0-0ff3b2376e18","applicationID":"1"}}
        data2 = {"deviceKeys":{"nwkKey":"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF","devEUI":devui}}
        response1 = requests.post(url='http://10.3.242.233:8080/api/devices', headers=headers, data=json.dumps(data1), verify=False)
        print('Join response: ', response1.content)
        response2 = requests.post(url='http://10.3.242.233:8080/api/devices/{}/keys'.format(devui), headers=headers,data=json.dumps(data2), verify=False)
        print('appKey bind response: ', response2.content)
# 网关注册
def gateway_register():
    for gateway_id in gateway_ids:
        data1 = {"gateway":{"location":{},"name":gateway_id,"description":"testest","id":gateway_id,"gatewayProfileID":"0360099e-82c2-4411-a8a2-517e77ed6b03","networkServerID":"1","organizationID":"2"}}
        # data2 = {"deviceKeys": {"appKey": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"}}
        response1 = requests.post(url='http://10.3.242.233:8080/api/gateways', headers=headers, data=json.dumps(data1), verify=False)
        print(response1.content)

# def get_keys():
#     url = ""
#     response = requests.get()
if __name__ == '__main__':
    # 先注册网关，后注册设备
    gateway_register()
    device_register()
