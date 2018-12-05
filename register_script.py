import sys
sys.path.append('./lib')
import DeviceJoin
import socket
import DeviceAccept
import csv
import PushData

class UdpBaseClient:
    """
    使用socket通信实现udp client base 类
    """

    def __init__(self, target, address=None):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.s = None
        self.address = address
        # if address:
        #     self.s.bind(address)
        self.target = target
        self.result = None
        self._on_send = None
        self._on_recv = None

    def bind(self, address=None):
        if address:
            self.s.bind(address)
        else:
            raise ('Address is None')
    """
    不绑定直接发送，系统会自动分配一个端口给client
    """
    def send(self, data):
        self.s.sendto(data, self.target)
        if self._on_send:
            self._on_send()

    def recv(self, size=4096):
        self.result = self.s.recvfrom(size)
        if self._on_recv:
            self._on_recv()
        return self.result
    def close(self):
        self.s.close()

    @property
    def on_send(self, client, payload, *args):
        return self._on_send

    @on_send.setter
    def on_send(self, func):
        self._on_send = func

    @property
    def on_recv(self, client, payload, *args):
        return self._on_recv

    @on_recv.setter
    def on_recv(self, func):
        self._on_recv = func

def main():
    dev_uis = []
    gateway_ids = []
    host = "10.3.242.233"
    # 修改对应UDP端口
    port = 1700
    # port = 12234

    udp_client = UdpBaseClient(target=(host, port))

    with open('./info/gateway.csv') as f:
        for each in f.readlines():
            gateway_ids.append(each.replace('\n', ''))
    # with open('key_info.csv') as f:
    #     for each in f.readlines():
    #         # print(each)
    #         key_info = each.replace('\n', '').split(',')
    #         dev_uis.append(key_info[0])
    with open('./info/DevEUI.csv') as f:
        for each in f.readlines():
            dev_uis.append(each.replace('\n', ''))
    with open('./log/Error.txt', 'w') as f:

        # 需修改对应的秘钥管理文件
        with open('./info/key_info_github_lora_new.csv', 'w', newline='') as lf:
            headers = ['DevEUI', 'DevAddr', 'NwkSKey', 'AppSKey']
            lf_csv = csv.writer(lf, headers)
            lf_csv.writerow(headers)
            for index, dev_ui in enumerate(dev_uis):
                gateway_id = gateway_ids[index]
                pull_data = DeviceJoin.form_pullData(gateway_id)
                udp_client.send(pull_data)
                udp_client.recv()
                payload, DecNonce = DeviceJoin.form_pushData(gateway_id, dev_ui)
                try:
                    # 发送注册数据包
                    udp_client.send(payload)
                    udp_client.s.settimeout(10)
                    print(udp_client.recv())
                    response = udp_client.recv()[0]
                    print(response)
                    udp_client.s.settimeout(None)

                    # 发送普通数据包，loraserver的特殊要求 
                    DevAddr = DeviceAccept.get_DevAddr(response)
                    NwkSKey,AppSKey = DeviceAccept.gen_keys(response,DecNonce)
                    udp_client.s.settimeout(10)
                    udp_client.send(PushData.form_pushData(gateway_id, DevAddr, NwkSKey, AppSKey,0))
                    udp_client.recv()
                    udp_client.recv()
                    udp_client.s.settimeout(None)

                except socket.timeout:
                    print('Socket timeout during recv:', dev_ui)
                    f.write(dev_ui + '\n')
                lf_csv.writerow((dev_ui, DevAddr, NwkSKey, AppSKey))

if __name__ == '__main__':
    main()
