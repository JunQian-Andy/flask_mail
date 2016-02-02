#!/usr/bin/env python3
#encoding = utf-8

from flask import request, json, jsonify
from app import app
import subprocess, time, datetime
import json

def send_mail(mailinfo = {}):
    mailto, mailcc, mailbody, mailsubject = mailinfo['EMAILTO'], mailinfo['EMAILCC'], mailinfo['EMAILBODY'], mailinfo['EMAILSUBJECT']
    mailto = ','.join(mailto)
    if mailcc == None:
        cmd = 'echo "%s" | mailx -s "%s" "%s"' %(mailbody, mailsubject, mailto)
    else:
        #mailcc = ','.join(mailcc)
        cmd = 'echo "%s" | mailx -s "%s" -c "%s" "%s"' %(mailbody, mailsubject, mailcc, mailto)
    print(cmd)
    start = datetime.datetime.now()
    #print "cmd is %s" %(cmd)
    p = subprocess.Popen(cmd, bufsize=10000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while p.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds > 300:
            try:
                p.terminate()
            except Exception as e:
                return None
    return p.stderr.read()


@app.route('/mail', methods = ['POST'])
def mail():
    print(request.json)
    ld = {
        'EMAILTO':request.json['emailto'],
        'EMAILCC':request.json['emailcc'],
        'EMAILBODY':request.json['emailbody'],
        'EMAILSUBJECT':request.json['emailsubject'],
    }
    print(ld)
    mail_info = json.dumps(ld)
    result = send_mail(ld)
    if result == 0:
        print("mail send ok")
    return jsonify({'result':ld})
