#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from help import mysql_helper2
import datetime, time

def select_task(channel_id):
    t_sql = 'select t2.start_time, t2.end_time from shim_channel as t1, shim_info as t2 where t1.shim_id = t2.id and t1.channel_id = %s'
    t_params = (channel_id, )
    re = mysql_helper2.find_all(sql=t_sql, params=t_params)
    return re

def format_time(d_time):

	## zs
	un_time = time.mktime(d_time.timetuple())
	return un_time

def Changetime(str1):
    Unixtime = time.mktime(time.strptime(str1, '%Y-%m-%d %H:%M:%S'))
    return Unixtime



if __name__ == '__main__':
	r = select_task(0)
	print r

	#test
	for i in r:
		start_time = i[0]
		un_s_time = format_time(start_time)
		end_time = i[1]
		un_e_time = format_time(end_time)
		print un_e_time 
	# a = Changetime('2018-04-08 12:00:01')
	# print a
