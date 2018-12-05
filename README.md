# 安装 
pypthon 3.5

```
pip install locustio
pip install pycryptodome

```

# 使用
```
locust -f udp_push_locust.py
```
## 分布式
```
locust -f udp_push_locust.py --master
locust -f udp_push_locust.py --slave (--master-host=IP)
locust -f udp_push_locust.py --slave (--master-host=IP)
```

# 文件说明
- util：util文件夹中有udplocust.py文件，即自己定义的locust client类

- DevEUI.csv：存储DevEUI
- gateway.csv：存储GatewayId
- key_info.csv：存储根据DevEUI查找到的AppSKey，NwkSKey等信息
- key_info_github_lora：存储开源项目loraserver上注册的相关AppSkey，NwkSkey等信息

- DeviceAccept.py：解析join请求的下行包，提取AppSkey，NwkSkey等信息
- DeviceJioin.py：构造join请求的payload
- PushData.py：构造普通请求的payload

- register_github_lora.py：用requests库在网页上注册设备（for github lora server）
- register_script.py：使用DevEUI.csv中的数据，用UdpBaseClient循环发送join请求（for ic2 or github lora server）

- udp_join_locustfile.py：join请求locus脚本
- udp_push_locustfile.py：普通请求脚本
- udp_push_locustfile_slave.py：普通请求脚本

