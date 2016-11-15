__author__ = 'zhaobin022'
# -*- coding:utf-8 -*-
import subprocess
import pika
import time
import threading
import json
import hashlib
import io
import re
import os
from utils.mq_simple_api import pub_msg
from cmdb import models
import sys
import logging
import time
logger = logging.getLogger('web_apps')

reload(sys)
sys.setdefaultencoding('utf-8')
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def local_exec_cmd(cmd,memory_queue,slow=False):

    ret = {"status": False, "message": ''}
    s=subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

    count = 0
    batch_msg = ''
    while True:
        count +=1
        msg = s.stdout.readline()
        if not msg:break
        if slow:
            batch_msg+=msg
            if count%100 == 1:
                pub_msg(memory_queue,batch_msg)
                batch_msg=''
        else:
            pub_msg(memory_queue,msg)


        ret["message"] += msg
    if slow:
        pub_msg(memory_queue,batch_msg)


    while True:
        msg = s.stderr.readline()
        if not msg:break
        pub_msg(memory_queue,msg)
        ret["message"] += msg

    # retcode = s.poll()
    retcode = s.poll()
    while retcode == None:
        retcode = s.poll()

    retcode = s.returncode
    print retcode,'retcode'
    if retcode == 0:
        ret['status'] = True
    else:
        ret['status'] = False
    if slow:
        logger.info("status : %s -- result : %s" % (str(ret['status']),ret["message"] ))
    else:
        logger.info("cmd : %s -- status : %s -- result : %s" % (cmd,str(ret['status']),ret["message"] ))
    return  ret

def local_exec_cmd_nomq(cmd):

    ret = {"status": False, "message": ''}
    s=subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)


    while True:
        msg = s.stdout.readline()
        if not msg:break

        ret["message"] += msg

    while True:
        msg = s.stderr.readline()
        if not msg:break
        ret["message"] += msg

    retcode = s.poll()
    while retcode == None:
        retcode = s.poll()

    if retcode == 0:
        ret['status'] = True
    else:
        ret['status'] = False

    logger.info("cmd : %s -- status : %s -- result : %s" % (cmd,str(ret['status']),ret["message"] ))

    return  ret

def get_md5_num(file_path):
    m = hashlib.md5()
    file = io.FileIO(file_path,'r')
    bytes = file.read(1024)
    while(bytes != b''):
        m.update(bytes)
        bytes = file.read(1024)
    file.close()

    #md5value = ""
    md5value = m.hexdigest()
    return md5value

def get_filename_from_pom(pom_file_path):
    tree = ET.parse(pom_file_path)     #打开xml文档
    root = tree.getroot()         #获得root节点
    def get_namespace(element):
        m = re.match('\{.*\}', element.tag)
        return m.group(0) if m else ''

    namespace = get_namespace(root)
    #root = ET.fromstring(country_string) #从字符串传递xml
    file_name = root.find('%sbuild/%sfinalName'% (namespace,namespace)).text
    return file_name

def format_remote_dir_output(msg):
    '''
    -rw-r--r-- 1 root root 21M 2016-10-20 15:31:06 /xebest/archive/epay-schedule_20161020153055.war

                    { "data": "filename" },
                    { "data": "permission" },
                    { "data": "user" },
                    { "data": "group" },
                    { "data": "size" },
                    { "data": "datetime" }
    '''
    data = {}
    if msg != '' and not msg.startswith("total"):
        l = []
        msg = msg.split()
        l.append(msg[7])
        l.append(msg[0])
        l.append(msg[2])
        l.append(msg[3])
        l.append(msg[4])
        l.append(msg[5]+" "+msg[6])
        '''
        data['permission'] = msg[0]
        data['user'] = msg[2]
        data['group'] = msg[3]
        data['size'] = msg[4]
        data['datetime'] = msg[5]+" "+msg[6]
        data['filename'] = msg[7]
        print data,111111111111111
        '''
        return l

def filter_the_null_obj(msg):
    if msg:
        return True
    # return


'''
def local_exec_cmd(cmd,mq_chan,ret_queue_name):

    ret = {"status": False, "message": ''}
    s=subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    # output,errout = s.communicate()
    time.sleep(0.1)
    retcode = s.poll()
    temp = {
        'msg_type':'ret_msg',
        'data':''
    }

    if retcode == 0:
        ret["status"] = True
        while True:
            msg = s.stdout.readline()
            if not msg:break
            temp['data'] = msg
            mq_chan.basic_publish(exchange='',
                      routing_key=ret_queue_name,
                      body=json.dumps(temp)
                      )
            ret["message"] += msg

    else:
        ret["status"] = False
        while True:
            msg = s.stderr.readline()
            if not msg:break
            temp['data'] = msg
            mq_chan.basic_publish(exchange='',
                      routing_key=ret_queue_name,
                      body=json.dumps(temp),
                      )
            ret["message"] += msg
    print cmd
    print ret,'before local_exec_cmd return'
    return  ret





'''
'''
def local_exec_cmd(cmd):
    ret = {"status": False, "message": ''}
    s=subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output,errout = s.communicate()
    retcode = s.poll()
    if retcode == 0:
        ret["status"] = True
        ret["message"] = output
    else:
        ret["message"] = errout

    return  ret
'''



