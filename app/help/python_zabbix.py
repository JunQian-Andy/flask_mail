#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from zabbix.api import ZabbixAPI
from pyzabbix import ZabbixMetric, ZabbixSender
import json

class ZabbixMetricUtf8(ZabbixMetric):

    def __repr__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, encoding="utf-8")


class ZabbixSenderUtf8(ZabbixSender):
    def _create_request(self, messages):
        msg = ','.join(messages)
        print "meg: {0}" .format(msg)
        request = '{{"request":"sender data","data":[{msg}]}}'.format(msg=msg)
        print "request: {0}" .format(request)
        return request


def zabbix_send_mes(mes_type, stream_info = {}):
    packet = []
    if mes_type == "create":
        send_create_mes ='''直播流异常
直播频道: {0}
流地址: {1}
故障类型: {2}
故障开始时间: {3}''' .format(stream_info['name'], stream_info['ip'], stream_info['type'],stream_info['startTime'])
        packet.append(ZabbixMetricUtf8('stream_monitor_02.bkpt', 'stream_info', send_create_mes))
        result = ZabbixSenderUtf8(use_config=True).send(packet)
        return result
    elif mes_type == 'clear':
        send_clear_mes ='''直播流恢复
直播频道: {0}
流地址: {1}
故障类型: {2}
故障恢复时间: {3}''' .format(stream_info['name'], stream_info['ip'], stream_info['type'],stream_info['endTime'])
        packet.append(ZabbixMetricUtf8('stream_monitor_02.bkpt', 'stream_info', send_clear_mes))
        result = ZabbixSenderUtf8(use_config=True).send(packet)
        return result