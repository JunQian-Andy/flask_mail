#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from flask import Flask, request
from flask_restful import Resource, Api
from help import mysql_helper, mysql_helper2, log_helper, soap_helper, python_zabbix
import time

app = Flask(__name__)
api = Api(app)


def logger(mes):
    __log_dir = "/data/logs/cntv4g_inf/log"
    logger= log_helper.get_logger(logName= __log_dir)
    logger.info(mes)

##确定故障的开始时间和类型
def select_task(channel_name):
    bool_channel_sql = 'select name from stream_info where name = %s and monitor = 0'
    ## 查询频道是否有效

    sql = 'select unix_timestamp(startTime), type from arcsoft where name = %s and status = 1'
    ## 查询故障的开始时间和故障类型

    params = (channel_name, )
    if mysql_helper.find_one(sql = bool_channel_sql, params= params):
        re = mysql_helper.find_all(sql=sql, params=params)
    else:
        return "no-exist channelname"
    return re

def stream_monitor_status(event_info={}):
    sql = "select monitor from stream_info where name = %s" 
    params = (event_info['name'], )
    re = mysql_helper.find_one(sql= sql, params= params)
    sql_cid = "select c_id from stream_info where name = %s"
    re_cid = mysql_helper.find_one(sql= sql_cid, params = params)
    mes = "channel_name: {0}; channel_id: {1}; moitor_status: {2}" .format(event_info['name'], re_cid[0], re)
    logger(mes)
    if re:
        if re_cid:
            if re_cid[0] != 0:
                tu_thim = select_shim_info(re_cid)
                # print tu_thim
                if shield_time(arc_s_time= event_info['startTime'] , tu= tu_thim):
                    mes = "channel_id: {0}; In shim_Time" .format(re_cid)
                    logger(mes)
                    return 1
                else:
                    mes = "channel_id: {0}; Out shim_Time" .format(re_cid)
                    logger(mes)
                    return 0
            else:
                return 0
        else:
            return 1
    else:
        return 1


##查询频道的节目id(对应播控平台)
def select_channel_id(event_info={}):
    sql = "select c_id from stream_info where name = %s" 
    params = (event_info['name'], )
    re = mysql_helper.find_one(sql= sql, params= params)
    if re:
        if re[0]:
            return None
        else:
            return re[0]
        ## "0"正常发送报警邮件
        ## "1"不发送报警邮件
    else:
        return None

def monitor_shield(event_info={}):
    sql = "select * from shield_info where %s > startTime and %s < endTime and channel = %s and status = 0 and alarm = %s"
    params = (event_info['startTime'].split(' ')[1], event_info['startTime'].split(' ')[1], event_info['name'], event_info['type'])
    re = mysql_helper.find_all(sql= sql, params = params)
    print re
    if re:
        return 1
    else:
        return 0
    ## "0"正常发送报警邮件
    ## "1"不发送报警邮件


## 查找频道对应的IP地址
def stream_IP(event_info = {}):
    sql = 'select ip from stream_info where name = %s' 
    params = (event_info['name'], )
    re = mysql_helper.find_one(sql = sql , params = params)
    return re

## 从oms_bc库中查询相关节目的垫片信息
def select_shim_info(channel_id):
    t_sql = 'select t2.start_time, t2.end_time from shim_channel as t1, shim_info as t2 where t1.shim_id = t2.id and t1.channel_id = %s'
    t_params = (channel_id, )
    re = mysql_helper2.find_all(sql=t_sql, params=t_params)
    return re

## datetime.datetime转换成unix时间
def format_time(d_time):
    un_time = time.mktime(d_time.timetuple())
    return un_time

## 字符串转换成unix时间
def Changetime(str1):
    Unixtime = time.mktime(time.strptime(str1, '%Y-%m-%d %H:%M:%S'))
    return Unixtime

## 判断是否是是在屏蔽时间内
def shield_time(arc_s_time, tu=()):
    #tu 相关频道垫片数组
    #arc_s_time 虹软上报消息中的故障开始时间
    for i in tu:
        shim_start_time = i[0]
        un_s_time = format_time(shim_start_time)
        shim_end_time = i[1]
        un_e_time = format_time(shim_end_time)
        u_arc_s_time = Changetime(arc_s_time.split(".")[0])
        if u_arc_s_time >= un_s_time and u_arc_s_time <= un_e_time:
            return 1
        else:
            pass
    return 0
    
def create_insert_db(event_info = {}, pigoss_info = {}):
    guid = event_info["guid"]
    id = event_info["id"]
    type = event_info["type"]
    name = event_info["name"]
    startTime = event_info["startTime"]
    logid = event_info["logid"]
    if pigoss_info:
        streamIP = pigoss_info['streamIP']
        eventid = pigoss_info['eventid']
        sql = "insert into arcsoft (guid, id, type, name, startTime, logid, status, eventid, streamIP) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = (guid, id, type, name, startTime, logid, 1, eventid, streamIP)
    else:
        sql = "insert into arcsoft (guid, id, type, name, startTime, logid, status) values (%s, %s, %s, %s, %s, %s, %s)"
        params = (guid, id, type, name, startTime, logid, 1)
    re = mysql_helper.insert_or_update_or_delete(sql= sql, params= params)
    return re

def pigoss_soap_create(event_info = {}, req_ip = '0.0.0.0'):
    pigs = soap_helper.pigoss()
    sql_alarm_type = "select alarm_info from alarm_type where alarm_id = %s"
    sql_stream_ip = "select ip from stream_info where name = %s"
    params_alarm_type = (event_info['type'], )
    params_stream_ip = (event_info['name'], )
    eventDetail = mysql_helper.find_one(sql = sql_alarm_type , params = params_alarm_type)
    eventIP = mysql_helper.find_one(sql = sql_stream_ip, params = params_stream_ip)
    eventid = pigs.create_event(eventDesc= "stream monitor", eventDetail= event_info['name'] + ' ' + eventDetail[0], eventSource= eventIP, eventIP= req_ip, severity= 2, startTime = event_info["startTime"].replace(' ','T'))
    re_info = {"eventid": eventid, "streamIP": eventIP}
    #logger("eventid: {0}" .format(eventid))
    return re_info

def pigoss_soap_clear(event_info = {}):
    sql = "select eventid from arcsoft where guid = %s and status = 1 and eventid != 'null' "
    params = (event_info["guid"], )
    r = mysql_helper.find_all(sql= sql, params= params)
    if r:
        eventid = r[0][0]
        pigs = soap_helper.pigoss()
        re = pigs.clear_event(eventID= eventid, ackUser= "ArcSoft_monitor", ackTime= event_info["endTime"].replace(' ','T'), clearUser= "ArcSoft_monitor", clearTime= event_info["endTime"].replace(' ','T'))
        return re
    else:
        return True

def clear_insert_db(event_info = {}):
    sql = "update arcsoft set endTime = %s , status = 0 where guid = %s"
    params = (event_info["endTime"], event_info["guid"])
    re = mysql_helper.insert_or_update_or_delete(sql= sql, params= params)
    return re

class ArcSoft_task(Resource):
    def get(self, channel_name): #pylint: disable=R0201
        re = select_task(channel_name)
        return {"name":channel_name, "info":re}

class ArcSoft(Resource):
    ##主程序,接受虹软多画面报警回调pigoos报警接口
    def post(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')

        ##判断调用接口的json是否为空
        if request.json == None:
            return {"sucess":"false", "message":"post json error"}
        else:
            req_ip = request.remote_addr

        ##记录请求的json
        logger("request json: {0}" .format(str(request.json)))
        sup_info = request.json

        ##判断告警的结束时间是否为空
        ##为空是报警请求
        ##不为空是恢复请求

        stream_info = sup_info
        s_ip = stream_IP(event_info = sup_info)
        if s_ip:
            stream_info['ip'] = s_ip
        else:
            stream_info['ip'] = 'null'

        ##endTime != None
        if sup_info["endTime"]:
            try:
                pig_re = pigoss_soap_clear(event_info= sup_info)
                zabbix_re = python_zabbix.zabbix_send_mes(mes_type="clear", stream_info= stream_info)
                if zabbix_re.failed == 0:
                    mes = "zabbix event clean success -- {0}" .format(stream_info)
                    logger(mes)
                else:
                    mes = "zabbix event clean failed"
                    logger(mes)
                    
                if pig_re == True:
                    clear_insert_db(event_info = sup_info)
                    r_json = {"guid":sup_info["guid"], "type":"clearEvent", "success":"True", "message":0}
                    logger(r_json)
                    return r_json
                else:
                    r_json = {"guid":sup_info["guid"], "type":"clearEvent", "success":"False", "message":"任务清除失败，非有效guid"}
                    logger(r_json)
                    return r_json
            except Exception as e:
                logger(e)
                r_json = {"guid":sup_info["guid"], "type":"clearEvent", "success":"False", "message":"POST错误json信息"}
                logger(r_json)
                return r_json

        ##endtime == None
        else:
            try:
                re_info = stream_monitor_status(event_info = sup_info)
                print "warning info: {0}" .format(re_info)
                if re_info == 0:
                    ## 状态为0的频道报警
                    if monitor_shield(event_info = sup_info):
                        re = create_insert_db(event_info= sup_info)
                    else:
                        pig_info = pigoss_soap_create(event_info= sup_info, req_ip = req_ip)
                        zabbix_re = python_zabbix.zabbix_send_mes(mes_type="create", stream_info= stream_info)
                        re = create_insert_db(event_info= sup_info , pigoss_info= pig_info)
                        if zabbix_re.failed == 0:
                            mes = "zabbix event create success -- {0}" .format(stream_info)
                            logger(mes)
                        else:
                            mes = "zabbix event create failed"
                            logger(mes)
                elif re_info != 0:
                    ##状态为1的频道不报警
                    re = create_insert_db(event_info= sup_info)
            except Exception as e:
                r_json = {"guid":sup_info["guid"], "type":"createEvent", "success":"Fale", "message":"POST错误json信息"}
                logger(e)
                logger(r_json)
                return r_json
            r_json = {"guid":sup_info["guid"], "type":"createEvent", "success":"True", "message":0}
            logger(r_json)
            return r_json
            
        #return {"sucess":"True", "message":"0"}


api.add_resource(ArcSoft, '/4g/stream/api/arcsoft/task/')
api.add_resource(ArcSoft_task, '/4g/stream/api/arcsoft/task/<string:channel_name>')
