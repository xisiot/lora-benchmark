from Crypto.Hash import CMAC
from Crypto.Cipher import AES
import base64
import struct
import os
import time
import json
import hashlib

MHDR = '00'
AppKey = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
AppEUI = '9816be466f467a17'
NetID = '00'


def mic_cal(key, micField):
    fmt = '>s8s8s2s'
    msg = struct.pack(fmt, micField['MHDR'], micField['AppEUI'],
                      micField['DevEUI'], micField['DevNonce'])
    cobj = CMAC.new(bytearray.fromhex(key), ciphermod=AES)
    cobj.update(msg)
    return cobj.hexdigest()[:8]


def form_join(DevEUI):
    DevNonce = os.urandom(2).hex()
    micField = {
        'MHDR': bytearray.fromhex(MHDR),
        'AppEUI': struct.pack('<Q', *struct.unpack('>Q', bytearray.fromhex(AppEUI))),
        'DevEUI': struct.pack('<Q', *struct.unpack('>Q', bytearray.fromhex(DevEUI))),
        'DevNonce': struct.pack('<H', *struct.unpack('>H', bytearray.fromhex(DevNonce)))
    }
    mic = mic_cal(AppKey, micField)
    fmt = '>s8s8s2s4s'
    join_mac = struct.pack(fmt, micField['MHDR'], micField['AppEUI'],
                           micField['DevEUI'], micField['DevNonce'], bytearray.fromhex(mic))
    print('join_mac: ' + join_mac.hex())
    return join_mac, DevNonce


def form_rxpk(DevEUI):
    data, DevNonce = form_join(DevEUI)
    data_size = len(data.hex()) // 2
    data = base64.b64encode(data).decode()
    GMTformat = "%Y-%m-%d %H:%M:%S GMT"
    rxpk = {
        'rxpk': [{
            "tmst": 854980284,
            "chan": 7,
            "rfch": 0,
            "freq": 435.9,
            "stat": 1,
            "modu": 'LORA',
            "datr": 'SF12BW125',
            "codr": '4/5',
            "lsnr": 2,
            "rssi": -119,
            "size": data_size,
            "data": data,
        }],
        "stat": {
            "time": time.strftime(GMTformat, time.localtime()),
            "rxnb": 1,
            "rxok": 0,
            "rxfw": 0,
            "ackr": 100,
            "dwnb": 0,
            "txnb": 0,
        }
    }
    return json.dumps(rxpk).encode('ascii'), DevNonce


def form_pushData(gatewayId, DevEUI):
    json_bytes, DevNonce = form_rxpk(DevEUI)
    version = '02'
    token = '83ec'
    identifier = '00'
    data_dict = {
        'version': version,
        'token': token,
        'identifier': identifier,
        'gateway_id': gatewayId,
        'json_obj': json_bytes.hex()
    }
    bytes_str = (
        '{version}'
        '{token}'
        '{identifier}'
        '{gateway_id}'
        '{json_obj}'.format(**data_dict)
    )
    return bytearray.fromhex(bytes_str), DevNonce


def generate_devAddr(DevEUI):
    str = AppEUI + DevEUI
    hash = hashlib.md5()
    hash.update(bytearray.fromhex(str))
    DevAddr = NetID + hash.hexdigest()[:6]
    return DevAddr


def form_pullData(gatewayId):
    version = '02'
    token = '83ec'
    identifier = '02'
    data_dict = {
        'version': version,
        'token': token,
        'identifier': identifier,
        'gateway_id': gatewayId,
    }
    bytes_str = (
        '{version}'
        '{token}'
        '{identifier}'
        '{gateway_id}'.format(**data_dict)
    )
    return bytearray.fromhex(bytes_str)


# gatewayId = 'bbbbbbbbbbbbbbbb'
# DevEUI = 'AAAAAAAAAAAAAAAA'
# data = form_pushData(gatewayId, DevEUI)
# print(data)
# devAddr = generate_devAddr(DevEUI)
# print(devAddr)
# pullData = form_pullData(gatewayId)
# print(pullData)
