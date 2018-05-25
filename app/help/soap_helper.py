#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from suds.client import Client
from suds.wsse import datetime

class pigoss:
	def __init__(self):
		self.__uri = 'http://10.40.3.3/EventPort?wsdl'
		self.__pigoss = Client(self.__uri)
		#print self.__pigoss

	def create_event(self, eventDesc, eventDetail, eventSource, eventIP, startTime, severity = 2):
		try:
			#result = pigoss.service.createEvent(eventDesc = 'JSWD stream', eventDetail = 'pcr +5000ms', eventSource = 'ArcSoft', eventIP = 'udp://228.1.0.1:6000', severity = 2, startTime = "2016-12-27T15:05:00")
			result = self.__pigoss.service.createEvent(eventDesc = eventDesc, eventDetail = eventDetail, eventSource = eventSource, eventIP = eventIP, severity = severity, startTime = startTime)
			# print type(result)
			return str(result.msg.split(":")[1])
		except Exception as  e:
			return 1

	def clear_event(self, eventID, ackUser, ackTime, clearUser, clearTime):
		try:
			result = self.__pigoss.service.clearEvent(eventID, ackUser, ackTime, clearUser, clearTime)
			if str(result.success) == "True":
				return 1
			else:
				return 0
		except Exception as e:
			return 1


if __name__ == "__main__":
 	obj_pigoss = pigoss()
	#re = obj_pigoss.create_event(eventDesc="test stream", eventDetail="pcr +6000ms", eventSource = "ArcSoft_sup", eventIP= "228.1.1.23", startTime="2017-02-03T09:46:00")
 	re = obj_pigoss.clear_event(eventID='cc28418b-1119-4355-8994-fa587be42095', ackUser='ArcSoft_sup', ackTime='2017-02-03T10:20:00', clearUser='ArcSoft_sup', clearTime='2017-02-03T10:20:00')
 	print re




