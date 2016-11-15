__author__ = 'zhaobin022'
# -*- coding:utf-8 -*-
import paramiko
from utils.mq_simple_api import pub_msg
import logging
logger = logging.getLogger('web_apps')


class SshHandler(object):
    def __init__(self,ipaddr ,port, username,passowrd,task_id=None,memory_queue=None):
        self.ipaddr = ipaddr
        self.port = port
        self.username = username
        self.passowrd = passowrd
        self.task_id = task_id
        self.memory_queue = memory_queue
        if task_id:
            self.ret_queue_name = 'task_ret_%d'% task_id
        self.ret = {
            'status':False,
            'msg':''
        }

    def remote_cmd(self, cmd,send_ret_to_queue=False):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ipaddr,self.port,self.username, self.passowrd)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            ret_out = ''
            ret_err = ''
            while True:
                msg = stdout.readline()
                if not msg:break
                if send_ret_to_queue:
                    pub_msg(self.memory_queue,msg)
                ret_out+=msg
            while True:
                msg = stderr.readline()
                if not msg:break
                pub_msg(self.memory_queue,msg)
                ret_err+=msg
            if ret_err:
                self.ret['status'] = False
                self.ret['msg'] = ret_err
            else:
                self.ret['status'] = True
                self.ret['msg'] = ret_out
            return_code = stdout.channel.recv_exit_status()
            self.ret['return_code'] = return_code
            ssh.close()

        except Exception,e:
            self.ret['status'] = False
            self.ret['msg'] = str(e)
            pub_msg(self.memory_queue,str(e))
            self.ret['return_code'] = 1
        finally:

            logger.info("cmd : %s -- status : %s -- result : %s" % (cmd,str(self.ret['status']),self.ret["msg"] ))
            return self.ret

    def push_file_to_remote(self,remotepath,localpath):
        try:
            t = paramiko.Transport((self.ipaddr,self.port))
            t.connect(username = self.username, password = self.passowrd)
            sftp = paramiko.SFTPClient.from_transport(t)
            remotepath=remotepath
            localpath=localpath
            sftp.put(localpath,remotepath)
            t.close()
            self.ret['status'] = True
            self.ret['msg'] = '传输成功\n\n'
        except Exception,e:
            self.ret['status'] = False
            self.ret['msg'] = '传输失败\n\n'

        finally:

            logger.info("push_file_to_remote : from %s to %s" % (localpath,remotepath ))
            return self.ret

    def pull_file_to_local(self,remotepath,localpath):
        try:
            t = paramiko.Transport((self.ipaddr,self.port))
            t.connect(username = self.username, password = self.passowrd)
            sftp = paramiko.SFTPClient.from_transport(t)
            remotepath=remotepath
            localpath=localpath
            sftp.get(remotepath, localpath)
            t.close()
            self.ret['status'] = True
            self.ret['msg'] = '传输成功\n\n\n'
        except Exception,e:
            self.ret['status'] = False
            self.ret['msg'] = '传输失败\n\n\n'
        finally:

            logger.info("pull_file_to_local : from %s to %s" % (remotepath,localpath ))
            return self.ret