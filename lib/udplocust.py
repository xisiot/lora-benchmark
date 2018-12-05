# coding: utf8
# /usr/bin/python3
import time
import json
from locust import events
from locust.core import Locust
from locust.exception import LocustError
import gevent
import socket
import sys
import asyncio
class UdpBaseClient:
    """
    使用socket通信实现udp client base 类
    """

    def __init__(self, target, address=None):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.s = None
        self.address = address
        if address:
            self.s.bind(address)
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



class UdpLocsut(Locust):
    """
        Represents an UDP "user" which is to be hatched and attack the system that is to be load tested.

        The behaviour of this user is defined by the task_set attribute, which should point to a
        :py:class:`TaskSet <locust.core.TaskSet>` class.

        This class creates a *client* attribute on instantiation which is an UDP client.
        """
    client = None
    address = None
    """
        Instance of UDP client that is created upon instantiation of Locust.
    """
    def __init__(self):
        super(UdpLocsut, self).__init__()
        if self.host is None:
            raise LocustError(
                "You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")
        self.client = UdpClient(target=self.host, address=self.address)

class UdpClient(UdpBaseClient):
    """
    继承UdpBaseClient类，构造locust使用的UdpClient
    """
    host = None
    def __init__(self, target, address, *args, **kwargs):
        super(UdpClient, self).__init__(target=target, address=address)
        self.on_send = self._on_send_callback
        self.on_recv = self._on_recv_callback
        self._on_success_response = self._on_recv_success
        self._on_fail_response = self._on_recv_fail


    def send_to_lora(self, payload, target, request_name, timeout):
        print('send to lora')
        # self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


        send_time = time.time()
        # gevent.spawn(self._set_timer, request_name, timeout, send_time)
        #if self.address:
        #    self.bind(self.address)
        self.send(payload)

        try:
            self.s.settimeout(timeout)
            print(self.s.getsockname())
            print('first recv',self.recv())
            print('second recv', self.recv())
            self.s.settimeout(None)


            recv_time = time.time()
            response_time = recv_time - send_time
            # self.s.shutdown(2)
            # self.s.close()
            self.on_success_response(payload, response_time, request_name)
            print('request success')



        except socket.timeout:
            print('Socket timeout    ' + str(self.s.getsockname()))
            self.__fire_timeout(request_name, timeout)
        except OSError:
            print('Socket timeout during recv')
            print(OSError)






    @property
    def on_success_response(self):
        return self._on_success_response

    @on_success_response.setter
    def on_success_response(self, func):
        self._on_success_response = func

    @property
    def on_fail_response(self):
        return self._on_fail_response

    @on_fail_response.setter
    def on_fail_response(self, func):
        self._on_fail_response = func

    def _on_send_callback(self, *args):
        print('userdata: ','*args: ', args)

    def _on_recv_callback(self, *args):
        print('receive ','*args: ', args)

    def _on_recv_success(self, payload, response_time, request_name):
        print('_on_recv_success')
        events.request_success.fire(
            request_type="udp",
            name=request_name,
            response_time=int(response_time * 1000),
            response_length=sys.getsizeof(payload)
        )

    def _on_recv_fail(self, payload, request_name):
        print('_on_recv_fail')
        events.request_failure.fire(
            request_type="udp",
            name=request_name,
            response_time=int(response_time * 1000),
            exception='%s %ds' % ("timeout", timeout)
        )

    def __fire_timeout(self, request_name, timeout):
        print('__fire_timeout')
        events.request_failure.fire(
            request_type="udp",
            name=request_name,
            response_time=timeout,
            exception='%s %ds' % ("timeout", timeout)
        )
        # self.s.shutdown(2)
        # self.s.close()
