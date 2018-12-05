from Crypto.Cipher import AES
import json
import base64
import struct

def paser_dlk(data):
    print(len(data))
    if data[3] in (1, 4):
        return None
    else:
        txpk = data[4:]
        txpk_json = json.loads(txpk.decode('ascii'))
        return txpk_json.get('txpk')

def gen_keys(data, DevNonce):
    txpk = paser_dlk(data)
    AppKey = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
    macpayload = base64.b64decode(txpk.get('data'))
    macpayload = macpayload[1:]
    cryptor = AES.new(bytearray.fromhex(AppKey), AES.MODE_ECB)
    macpayload = cryptor.encrypt(macpayload)
    AppNonce = macpayload[0:3].hex()
    NetID = macpayload[3:6].hex()
    cryptor = AES.new(bytearray.fromhex(AppKey), AES.MODE_ECB)
    pad = '00000000000000'
    DevNonce = struct.pack(
        '<H', *struct.unpack('>H', bytearray.fromhex(DevNonce))).hex()
    NwkSKeybytes = '01' + AppNonce + NetID + DevNonce + pad
    AppSKeybytes = '02' + AppNonce + NetID + DevNonce + pad
    NwkSKeybytes = bytes.fromhex(NwkSKeybytes)
    AppSKeybytes = bytes.fromhex(AppSKeybytes)
    # NwkSKeybytes = Padding.pad(NwkSKeybytes, 16)
    # AppSKeybytes = Padding.pad(AppSKeybytes, 16)
    NwkSKey = cryptor.encrypt(NwkSKeybytes)
    AppSKey = cryptor.encrypt(AppSKeybytes)
    return NwkSKey.hex(), AppSKey.hex()

def get_DevAddr(data):
    txpk = paser_dlk(data)
    AppKey = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
    macpayload = base64.b64decode(txpk.get('data'))
    macpayload = macpayload[1:]
    cryptor = AES.new(bytearray.fromhex(AppKey), AES.MODE_ECB)
    macpayload = cryptor.encrypt(macpayload)
    DevAddr = struct.pack('<I', *struct.unpack('>I', macpayload[6:10]))
    return DevAddr.hex()


# data = '0203eb037b227478706b223a7b22696d6d65223a66616c73652c22746d7374223a3835393938303238342c2266726571223a3433352e392c2272666368223a302c22706f7765223a31342c226d6f6475223a224c4f5241222c2264617472223a22534631324257313235222c22636f6472223a22342f35222c2269706f6c223a747275652c2273697a65223a31372c2264617461223a22494f445a69444f343358364d343242573970636c37456b3d222c22627264223a302c22616e74223a307d7d'
# DevNonce = '2cfa'

# devAddr = get_DevAddr(data)
# # print(devAddr)
# keys = gen_keys(data, DevNonce)
# print(keys)
