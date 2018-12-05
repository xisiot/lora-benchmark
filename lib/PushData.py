from Crypto.Hash import CMAC
from Crypto.Cipher import AES
import struct
import math
import base64
import time
import json


def form_base_block(**kwargs):
    DevAddr = struct.pack(
        '<I', *struct.unpack('>I', bytearray.fromhex(kwargs.get('DevAddr')))).hex()
    # FCnt = struct.pack(
    #     '<I', *struct.unpack('>I', bytearray.fromhex(kwargs.get('FCnt')))).hex()
    FCnt = kwargs.get('FCnt')
    return '00000000{}{}{}00'.format(kwargs['direction'], DevAddr, FCnt)


def form_A(**kwargs):
    base_block = form_base_block(**kwargs)
    return '01{base_block}{i}'.format(
        base_block=base_block,
        i=kwargs.get('i')
    )


def form_B0(**kwargs):
    base_block = form_base_block(**kwargs)
    return '49{base_block}{msg_length}'.format(
        base_block=base_block,
        msg_length=kwargs.get('msg_length')
    )


def encrypt(key, payload, **kwargs):
    pld_len = len(payload)
    # print(pld_len)
    k = math.ceil(pld_len / 16)
    payload += b'\x00'*(16*k - pld_len)
    cryptor = AES.new(key, AES.MODE_ECB)
    S = b''
    for i in range(1, k + 1):
        kwargs['i'] = '{:0>2x}'.format(i)
        _A_each = form_A(**kwargs)
        Ai = bytearray.fromhex(_A_each)
        Si = cryptor.encrypt(Ai)
        S += Si
    return b''.join([bytearray.fromhex('{:0>2x}'.format(x ^ y)) for (x, y) in zip(S, payload)])[:pld_len]


def mic_cal(key, **kwargs):
    msg = '{MHDR}{FHDR}{FPort}{FRMPayload}'.format(**kwargs)
    # print(msg)
    # print(len(msg))
    msg_bytes = bytearray.fromhex(msg)
    msg_length = '{:0>2x}'.format(len(msg_bytes) % 0xFF)
    B0 = form_B0(msg_length=msg_length, **kwargs)
    obj_msg = B0 + msg
    print(obj_msg)
    # print(len(obj_msg))
    obj_msg = bytearray.fromhex(obj_msg)
    cobj = CMAC.new(key, ciphermod=AES)
    cobj.update(obj_msg)
    return cobj.hexdigest()[:8]


def form_FCtrl(direction='up', ADR=0, ADRACKReq=0, ACK=0, ClassB=0, FOptsLen=0, FPending=0):
    if direction == 'up':
        FCtrl = (ADR << 7) + (ADRACKReq << 6) + (ACK << 5) + (ClassB << 4)
        FCtrl += (FOptsLen & 0b1111)
    else:
        FCtrl = (ADR << 7) + (0 << 6) + (ACK << 5) + (FPending << 4)
        FCtrl += (FOptsLen & 0b1111)
    return '{:0>2x}'.format(FCtrl)


def form_FHDR(DevAddr, FCtrl, FCnt, FOpts):
    DevAddr = struct.pack(
        '<I', *struct.unpack('>I', bytearray.fromhex(DevAddr))).hex()
    if len(FCnt) == 8:
        FCnt = FCnt[:4]
        # print(FCnt)
    FCtrl['FOptsLen'] = len(FOpts) // 2
    FCtrl = form_FCtrl(**FCtrl)
    return '{}{}{}{}'.format(DevAddr, FCtrl, FCnt, FOpts)


def form_payload(NwkSKey, AppSKey, **kwargs):
    FRMPayload = kwargs.pop('FRMPayload')
    FPort = kwargs.get('FPort')
    if FPort == '00':
        enc_key = NwkSKey
        FRMPayload = bytearray.fromhex(FRMPayload)
    else:
        enc_key = AppSKey
    if FRMPayload:
        if isinstance(FRMPayload, str):
            FRMPayload = FRMPayload.encode()
        FRMPayload = encrypt(
            key=enc_key,
            payload=FRMPayload,
            **kwargs
        ).hex()
    else:
        FRMPayload = ''
    FHDR = kwargs.get('FHDR')
    kwargs['FRMPayload'] = FRMPayload
    kwargs['FHDR'] = FHDR
    MIC = mic_cal(NwkSKey, **kwargs)
    print(MIC)
    return ''.join([
        kwargs.get('MHDR'),
        kwargs.get('FHDR'),
        kwargs.get('FPort'),
        FRMPayload,
        MIC
    ])


def form_phy(DevAddr, NwkSKey, AppSKey, fcnt):
    MHDR = '80'
    FCnt = struct.pack('<i', fcnt).hex()
    # print(FCnt)
    FPort = struct.pack('<b', 1).hex()
    payload = 'hello'
    direction = '00'
    F_ADR = 0
    F_ADRACKReq = 0
    F_ACK = 0
    F_ClassB = 0
    FCtrl = {
        'ADR': F_ADR,
        'ADRACKReq': F_ADRACKReq,
        'ACK': F_ACK,
        'ClassB': F_ClassB,
    }
    FOpts = ""
    FHDR = form_FHDR(DevAddr, FCtrl, FCnt, FOpts)
    kwargs = {
        'DevAddr': DevAddr,
        'FCnt': FCnt,
        'FHDR': FHDR,
        'MHDR': MHDR,
        'FPort': FPort,
        'direction': direction,
        'FCtrl': FCtrl,
        'FRMPayload': payload,
    }
    phyPayload = form_payload(
        NwkSKey=bytearray.fromhex(NwkSKey),
        AppSKey=bytearray.fromhex(AppSKey),
        **kwargs
    )
    return bytearray.fromhex(phyPayload)


def form_rxpk(DevAddr, NwkSKey, AppSKey, fcnt):
    data = form_phy(DevAddr, NwkSKey, AppSKey, fcnt)
    # print(data.hex())
    data_size = len(data) // 2
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
    return json.dumps(rxpk).encode('ascii')


def form_pushData(gatewayId, DevAddr, NwkSKey, AppSKey, fcnt):
    json_bytes = form_rxpk(DevAddr, NwkSKey, AppSKey, fcnt)
    version = '02'
    token = '83ec'
    identifier = '00'
    gateway_id = gatewayId
    data_dict = {
        'version': version,
        'token': token,
        'identifier': identifier,
        'gateway_id': gateway_id,
        'json_obj': json_bytes.hex()
    }
    bytes_str = (
        '{version}'
        '{token}'
        '{identifier}'
        '{gateway_id}'
        '{json_obj}'.format(**data_dict)
    )
    return bytearray.fromhex(bytes_str)


gatewayId = 'bbbbbbbbbbbbbbbb'
DevAddr = '00ffe0f8'
NwkSKey = '8184fd7e7be46fb059a8fa1796eca330'
AppSKey = '3838f9ffca0b1ea7b4c1778bd17569e7'
fcnt = 1   #range from 0 to 65535
data = form_pushData(gatewayId, DevAddr, NwkSKey, AppSKey, fcnt)
print(data)
