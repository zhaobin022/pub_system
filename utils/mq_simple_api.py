__author__ = 'zhaobin022'
import json
import pika


def pub_msg(memory_queue,msg,stop=False,kwargs=None):
    temp = {
        'msg_type':'ret_msg',
        'data':msg
    }
    if kwargs:
        temp.update(kwargs)
    if stop:
        temp['stop'] = True
    memory_queue.put(json.dumps(temp))