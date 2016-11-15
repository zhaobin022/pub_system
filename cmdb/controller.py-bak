# -*- coding:utf-8 -*-
__author__ = 'zhaobin022'
import os
from pub_system import settings as django_settings
from config import settings as custom_settings
from utils.tools import local_exec_cmd
import svn.local
from cmdb import models
import datetime
from utils import tools
from utils.mq_simple_api import pub_msg
from utils.ssh_tools import SshHandler
from utils.tools import get_filename_from_pom
from utils.tools import get_md5_num
import time
import logging
import django.utils.timezone
try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

logger = logging.getLogger('web_apps')

class PublishHandler(object):

    def __init__(self,app_obj,task_obj,memory_queue,user):
        self.app_workspace = os.path.join(os.path.join(django_settings.BASE_DIR,custom_settings.WORKSPACE),app_obj.app_name)
        self.app_obj = app_obj
        self.task_obj = task_obj
        self.memory_queue = memory_queue
        self.user = user

    def init_app_env(self):
        if not os.path.exists(self.app_workspace):
            os.mkdir(self.app_workspace)
            pub_msg(self.memory_queue,'mkdir %s\n\n' % self.app_workspace)
        else:
            pub_msg(self.memory_queue,'the app workspace %s is exist !\n\n' % self.app_workspace)

        checkout_path = os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR)
        if not os.path.exists(checkout_path):
            os.mkdir(checkout_path)
            pub_msg(self.memory_queue,'mkdir %s\n\n' % checkout_path)
        else:
            pub_msg(self.memory_queue,'the checkout path %s is exist !\n\n' % checkout_path)

        checkout_path_flag = False
        try:
            r = svn.local.LocalClient(os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR))
            info = r.info()
            checkout_path_flag = True
        except Exception,e:
            pub_msg(self.memory_queue,"%s\n\n" % str(e))

        if not checkout_path_flag:
            cmd = 'svn co --username %s --password xxxxxxxxxxxxx %s %s' % (
                self.app_obj.svn_username,
                self.app_obj.svn_url,
                os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR)
            )

            pub_msg(self.memory_queue,cmd)
            cmd = 'svn co --username %s --password %s %s %s' % (
                self.app_obj.svn_username,
                self.app_obj.svn_password,
                self.app_obj.svn_url,
                os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR)
            )
            ret = local_exec_cmd(cmd,self.memory_queue,slow=True)
            ret["opt_type"]="Checkout App"
            if ret['status']:
                models.Logger.objects.create(app=self.app_obj,status=0,description=ret['message'],task=self.task_obj,user=self.user)
            else:
                models.Logger.objects.create(app=self.app_obj,status=1,description=ret['message'],task=self.task_obj,user=self.user)
        war_file_path = os.path.join(self.app_workspace,custom_settings.WAR_FILE_DIR)
        if not os.path.exists(war_file_path):
            os.mkdir(war_file_path)
            pub_msg(self.memory_queue,'mkdir %s' % war_file_path)
        else:
            pub_msg(self.memory_queue,'the war file path %s is exist !\n\n' % war_file_path)

        tomcat_path = os.path.join(django_settings.BASE_DIR,"static/upload/tomcat.tar.gz")
        server_list = models.Server.objects.filter(app=self.app_obj)
        test_tomcat_dir_cmd = 'test -d /xebest/tomcat'
        mk_archive_dir = self.app_obj.app_path
        mk_archive_dir_cmd = 'mkdir %s' % mk_archive_dir
        for s in server_list:
            ssh_handler = SshHandler(s.ipaddr,s.port,s.username,s.password,task_id=self.task_obj.id,memory_queue=self.memory_queue)

            sub_ret = ssh_handler.remote_cmd(test_tomcat_dir_cmd)
            if sub_ret['return_code'] == 0:
                pub_msg(self.memory_queue,'Tomcat 已部署!\n\n')
            else:
                ret = ssh_handler.push_file_to_remote("/tmp/tomcat.tar.gz",tomcat_path)
                unzip_tomcat_cmd = 'tar zxfv %s -C %s' % ('/tmp/tomcat.tar.gz','/xebest')
                if ret['status']:
                    pub_msg(self.memory_queue,'Tomcat 上传成功\n\n')
                    sub_ret = ssh_handler.remote_cmd(unzip_tomcat_cmd)
                    if sub_ret['return_code'] == 0:
                        pub_msg(self.memory_queue,'Tomcat 解压成功\n\n')
                    else:
                        pub_msg(self.memory_queue,'Tomcat 解压失败\n\n')
                else:
                    pub_msg(self.memory_queue,'Tomcat 上传失败\n\n')

            sub_ret = ssh_handler.remote_cmd(mk_archive_dir_cmd)
            if sub_ret['return_code'] == 0:
                pub_msg(self.memory_queue,'创建%s成功\n\n' % mk_archive_dir )
            else:
                pub_msg(self.memory_queue,'文件夹已存在%s\n\n' % mk_archive_dir )
        kwargs = {
            'action_type':'checkout_app',
            'ret_status' : True,
            'ret_msg' :'CheckOut App',
        }
        pub_msg(self.memory_queue,'stop',stop=True,kwargs=kwargs)

    def update_checkout_root(self):
        cmd = 'svn update --username %s --password %s %s' % (
            self.app_obj.svn_username,
            self.app_obj.svn_password,
            os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR)
        )

        pub_msg(self.memory_queue,"Update Svn\n\n")
        ret = local_exec_cmd(cmd,self.memory_queue)
        ret["opt_type"]="Update Svn"
        if ret['status']:
            models.Logger.objects.create(app=self.app_obj,status=0,description=ret['message'],task=self.task_obj,user=self.user)
        else:
            models.Logger.objects.create(app=self.app_obj,status=1,description=ret['message'],task=self.task_obj,user=self.user)



        r = svn.local.LocalClient(os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR))
        info = r.info()
        self.current_app_svn_num = info["commit#revision"]

        models.Logger.objects.create(app=self.app_obj,status=0,description="checkout dir svn num : %s" % self.current_app_svn_num ,task=self.task_obj,user=self.user)
        return ret

    def complie_java_gen_war(self):
        cmd = 'mvn clean install -P dev -f %s' % (os.path.join(os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR),'pom.xml'))


        pub_msg(self.memory_queue,"Complie The War File\n\n")
        ret = local_exec_cmd(cmd,self.memory_queue)

        ret["opt_type"]="Complie The War File"
        if ret['status']:
            models.Logger.objects.create(app=self.app_obj,status=0,description=ret['message'],task=self.task_obj,user=self.user)
        else:
            models.Logger.objects.create(app=self.app_obj,status=1,description=ret['message'],task=self.task_obj,user=self.user)


        return ret

    def backup_current_war(self):

        try:
            pom_file_path = os.path.join(os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR),'pom.xml')
            file_name = get_filename_from_pom(pom_file_path)
            #生成的WAR 文件路径
            war_file_dir = os.path.join(os.path.join(self.app_workspace,custom_settings.APP_CHECKOUT_DIR),'target')
            war_file_path = os.path.join(war_file_dir,'%s.war' % file_name)
            #生成的WAR 文件的md5值
            md5_value = tools.get_md5_num(war_file_path)
            #生成要归档的文件路径
            current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            current_war_file_name = '%s_%s_%s_%s.war' % (file_name,current_datetime,md5_value,self.current_app_svn_num)
            archive_war_path = os.path.join(os.path.join(self.app_workspace,custom_settings.WAR_FILE_DIR),current_war_file_name)
            #copy 新生成的WAR到归档目录
            cmd = 'cp %s %s' % (war_file_path,archive_war_path)


            pub_msg(self.memory_queue,cmd)
            ret = local_exec_cmd(cmd,self.memory_queue)
            source_md5_num = get_md5_num(war_file_path)
            target_md5_num = get_md5_num(archive_war_path)
            msg = ''
            if source_md5_num == target_md5_num:
                msg = u"归档WAR包成功!\n"
                pub_msg(self.memory_queue,msg)
            else:
                msg = u"归档WAR包失败!\n"
                pub_msg(self.memory_queue,msg)

            cmd = 'ls -tl %s ' % os.path.join(self.app_workspace,custom_settings.WAR_FILE_DIR)

            ret = local_exec_cmd(cmd,self.memory_queue)

            if ret['status']:
                models.Logger.objects.create(app=self.app_obj,status=0,description=ret['message'],task=self.task_obj,user=self.user)
            else:
                models.Logger.objects.create(app=self.app_obj,status=1,description=ret['message'],task=self.task_obj,user=self.user)

            kwargs = {
                'action_type':'gen_war',
                'ret_status': ret['status'],
                'ret_msg' :msg,
            }
            pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

        except Exception, e:
            print "Error:cannot parse file:country.xml."

    def publish_war(self):
        app_workspace = os.path.join(os.path.join(django_settings.BASE_DIR,custom_settings.WORKSPACE),self.app_obj.app_name)
        pom_file_path = os.path.join(os.path.join(app_workspace,custom_settings.APP_CHECKOUT_DIR),'pom.xml')
        file_name = get_filename_from_pom(pom_file_path)
        war_file_dir = os.path.join(os.path.join(app_workspace,custom_settings.APP_CHECKOUT_DIR),'target')
        war_file_path = os.path.join(war_file_dir,'%s.war' % file_name)
        server_list = models.Server.objects.filter(app=self.app_obj)
        current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        remote_file_name = "%s_%s.war" % (file_name,current_datetime)
        for s in server_list:
            ssh_handler = SshHandler(s.ipaddr,s.port,s.username,s.password,task_id=self.task_obj.id,memory_queue=self.memory_queue)
            pub_msg(
                self.memory_queue,
                '%s :\npush war %s to remote %s\n' % (s.ipaddr,war_file_path,os.path.join(self.app_obj.app_path,remote_file_name))
            )
            ret = ssh_handler.push_file_to_remote(os.path.join(self.app_obj.app_path,remote_file_name),war_file_path)
            pub_msg(
                self.memory_queue,
                ret['msg']
            )
            cmd = 'md5sum %s' % os.path.join(self.app_obj.app_path,remote_file_name)

            pub_msg(self.memory_queue,cmd+'\n')
            ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)

            file_check_flag = False
            if ret['status'] == True:
                remote_file_md5num = ret['msg'].split()[0]
                local_file_md5num = get_md5_num(war_file_path)
                pub_msg(self.memory_queue,"%s:%s %s:%s\n" % (remote_file_name,remote_file_md5num,war_file_path,local_file_md5num))
                msg = ''
                if remote_file_md5num == local_file_md5num:
                    msg = '文件效验成功'
                    pub_msg(self.memory_queue,msg+"\n\n")
                    s.current_version = remote_file_name
                    s.publish_date = django.utils.timezone.now()
                    s.save()
                    file_check_flag = True
                else:
                    msg = "文件效验失败"
                    pub_msg(self.memory_queue,msg+"\n\n")


            if file_check_flag and s.server_status:
                cmd = 'ln -svf %s %s' % (os.path.join(self.app_obj.app_path,remote_file_name),"/xebest/tomcat/webapps/current.war")
                pub_msg(self.memory_queue,cmd+'\n')
                ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)
                msg = ''
                if ret['status'] == True:
                    msg = "软链接创建成功"
                    pub_msg(self.memory_queue,msg+"\n\n")
                else:
                    msg = "软链接创建失败"
                    pub_msg(self.memory_queue,msg+"\n\n")




        kwargs = {
            'action_type':'publish_war'
        }
        pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

    def start_app(self,reboot=False):
        cmd = '%s' % self.app_obj.start_script_path.script_path
        check_cmd = '%s' % self.app_obj.check_script_path.script_path
        server_list = models.Server.objects.filter(app=self.app_obj,server_status=True)
        successfull = True
        msg = ''
        for s in server_list:
            if not reboot:
                pub_msg(self.memory_queue,"%s:\n\n" % s.ipaddr)
            ssh_handler = SshHandler(s.ipaddr,s.port,s.username,s.password,task_id=self.task_obj.id,memory_queue=self.memory_queue)

            sub_ret = ssh_handler.remote_cmd(check_cmd)
            if sub_ret['return_code'] == 0:
                msg = "应用已经在运行\n\n"
                models.Logger.objects.create(app=self.app_obj,server=s,status=0,description=sub_ret['msg'],task=self.task_obj)
                pub_msg(self.memory_queue,msg)
            else:
                pub_msg(self.memory_queue,cmd+"\n")
                ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)


                if ret['return_code'] == 0:
                    models.Logger.objects.create(app=self.app_obj,server=s,status=0,description=ret['msg'],task=self.task_obj,user=self.user)
                    s.app_status = True
                    s.save()
                    msg = "启动应用成功\n\n"
                    pub_msg(self.memory_queue,msg)
                else:
                    models.Logger.objects.create(app=self.app_obj,server=s,status=1,description=ret['msg'],task=self.task_obj,user=self.user)
                    successfull = False
                    msg = "启动应用失败\n\n"
                    pub_msg(self.memory_queue,msg)


        if not reboot:
            kwargs = {
                'action_type':'start_app',
                'ret_status':successfull,
                'ret_msg' :msg,
            }
            pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)
        else:
            kwargs = {
                'action_type':'reboot_app',
                'ret_status':successfull,
                'ret_msg' :msg,
            }
            pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

    def stop_app(self,reboot=False):
        cmd = '%s' % self.app_obj.stop_script_path.script_path
        server_list = models.Server.objects.filter(app=self.app_obj,server_status=True)
        successfull = True
        msg = ''
        for s in server_list:
            if not reboot:
                pub_msg(self.memory_queue,"%s:\n\n" % s.ipaddr)
            ssh_handler = SshHandler(s.ipaddr,s.port,s.username,s.password,task_id=self.task_obj.id,memory_queue=self.memory_queue)
            pub_msg(self.memory_queue,cmd+"\n")
            ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)

            if ret['status'] == True:
                models.Logger.objects.create(app=self.app_obj,server=s,status=0,description=ret['msg'],task=self.task_obj,user=self.user)
                s.app_status = False
                s.save()
                msg = "停止应用成功\n\n"
                pub_msg(self.memory_queue,msg)
            else:
                models.Logger.objects.create(app=self.app_obj,server=s,status=1,description=ret['msg'],task=self.task_obj,user=self.user)
                successfull = False
                msg = "停止应用失败\n\n"
                pub_msg(self.memory_queue,msg)


        if not reboot:
            kwargs = {
                'action_type':'stop_app',
                'ret_status':successfull,
                'ret_msg' :msg,
            }
            pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

    def reboot_app(self):
        self.stop_app(reboot=True)
        time.sleep(1)
        self.start_app(reboot=True)

    def check_app(self):
        cmd = '%s' % self.app_obj.check_script_path.script_path
        server_list = models.Server.objects.filter(app=self.app_obj,server_status=True)
        for s in server_list:
            ssh_handler = SshHandler(s.ipaddr,s.port,s.username,s.password,task_id=self.task_obj.id,memory_queue=self.memory_queue)
            pub_msg(self.memory_queue,cmd+"\n")
            ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)
            if ret['return_code'] == 0:
                models.Logger.objects.create(app=self.app_obj,server=s,status=0,description=ret['msg'],task=self.task_obj)
                s.app_status = True
                s.save()
                pub_msg(self.memory_queue,"应用正在运行\n\n")
            else:
                models.Logger.objects.create(app=self.app_obj,server=s,status=1,description=ret['msg'],task=self.task_obj)
                s.app_status = False
                s.save()
                pub_msg(self.memory_queue,"应用已经停止\n\n")
        kwargs = {
            'action_type':'check_app'
        }
        pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

    def delete_remote_backup(self,file_name):
        cmd = "rm -vf %s" % os.path.join(self.app_obj.app_path,file_name)

        server_list = models.Server.objects.filter(app=self.app_obj,server_status=True)
        successfull = True
        msg = ''
        current_version_server = models.Server.objects.filter(current_version=file_name.strip())
        if current_version_server:
            pub_msg(self.memory_queue,"有服务器正在引用该版本,不能删除!(%s)\n" % file_name)
        else:
            for s in server_list:
                ssh_handler = SshHandler(s.ipaddr,s.port,s.username,s.password,task_id=self.task_obj.id,memory_queue=self.memory_queue)
                pub_msg(self.memory_queue,cmd+"\n")
                ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)
                if ret['status'] == True:
                    models.Logger.objects.create(app=self.app_obj,server=s,status=0,description=ret['msg'],task=self.task_obj,user=self.user)
                    msg = u"删除备份文件成功\n\n"
                    pub_msg(self.memory_queue,msg)
                else:
                    models.Logger.objects.create(app=self.app_obj,server=s,status=1,description=ret['msg'],task=self.task_obj,user=self.user)
                    msg = u"删除备份文件失败\n\n"
                    pub_msg(self.memory_queue,msg)

        kwargs = {
            'action_type':'delete_remote_backup',
            'ret_status': successfull,
            'ret_msg' :msg,
        }

        pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

    def delete_local_backup(self,file_name):
        war_file_dir = os.path.join(self.app_workspace,custom_settings.WAR_FILE_DIR)
        cmd = "rm -vf %s" % os.path.join(war_file_dir,file_name)

        pub_msg(self.memory_queue,cmd)
        ret = local_exec_cmd(cmd,self.memory_queue)
        msg = ''
        if  ret['status']:
            models.Logger.objects.create(app=self.app_obj,status=0,description=ret['message'],task=self.task_obj,user=self.user)
            msg = '删除文件成功'
        else:
            models.Logger.objects.create(app=self.app_obj,status=1,description=ret['message'],task=self.task_obj,user=self.user)
            msg = '删除文件失败'

        kwargs = {
            'action_type':'delete_local_backup',
            'ret_status': ret['status'],
            'ret_msg' :msg,
        }

        pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

    def rollback_select_backup(self,file_name):
        cmd = 'ln -svf %s %s' % (os.path.join(self.app_obj.app_path,file_name),"/xebest/tomcat/webapps/current.war")
        server_list = models.Server.objects.filter(app=self.app_obj,server_status=True)
        successfull = True
        msg = ''
        for s in server_list:
            ssh_handler = SshHandler(s.ipaddr,s.port,s.username,s.password,task_id=self.task_obj.id,memory_queue=self.memory_queue)
            pub_msg(self.memory_queue,cmd+"\n")
            ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)
            if ret['status'] == True:
                models.Logger.objects.create(app=self.app_obj,server=s,status=0,description=ret['msg'],task=self.task_obj,user=self.user)
                msg = u"重新连接文件成功\n\n"
                pub_msg(self.memory_queue,msg)
                s.current_version = file_name
                s.publish_date = django.utils.timezone.now()
                s.save()
            else:
                models.Logger.objects.create(app=self.app_obj,server=s,status=1,description=ret['msg'],task=self.task_obj,user=self.user)
                msg = u"重新连接文件失败\n\n"
                pub_msg(self.memory_queue,msg)
        kwargs = {
            'action_type':'rollback_select_backup',
            'ret_status': successfull,
            'ret_msg' :msg,
        }

        pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

    def rollback_from_publish_server(self,file_name):
        app_workspace = os.path.join(os.path.join(django_settings.BASE_DIR,custom_settings.WORKSPACE),self.app_obj.app_name)
        local_path = os.path.join(app_workspace,custom_settings.WAR_FILE_DIR)
        local_file_path = os.path.join(local_path,file_name)

        server_list = models.Server.objects.filter(app=self.app_obj)
        successfull = True
        msg = ''
        for s in server_list:
            ssh_handler = SshHandler(s.ipaddr,s.port,s.username,s.password,task_id=self.task_obj.id,memory_queue=self.memory_queue)
            pub_msg(
                self.memory_queue,
                '%s :\npush war %s to remote %s\n' % (s.ipaddr,local_file_path,os.path.join(self.app_obj.app_path,file_name))
            )
            ret = ssh_handler.push_file_to_remote(os.path.join(self.app_obj.app_path,file_name),local_file_path)
            pub_msg(
                self.memory_queue,
                ret['msg']
            )
            cmd = 'md5sum %s' % os.path.join(self.app_obj.app_path,file_name)
            pub_msg(self.memory_queue,cmd+'\n')
            ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)

            file_check_flag = False
            if ret['status'] == True:
                remote_file_md5num = ret['msg'].split()[0]
                local_file_md5num = get_md5_num(local_file_path)
                msg = "%s:%s %s:%s\n" % (file_name,remote_file_md5num,local_file_path,local_file_md5num)
                pub_msg(self.memory_queue,msg)
                models.Logger.objects.create(app=self.app_obj,server=s,status=0,description=msg,task=self.task_obj,user=self.user)

                if remote_file_md5num == local_file_md5num:
                    pub_msg(self.memory_queue,"文件效验成功\n\n")
                    models.Logger.objects.create(app=self.app_obj,server=s,status=0,description="文件效验成功\n\n",task=self.task_obj,user=self.user)
                    s.current_version = file_name
                    s.publish_date = django.utils.timezone.now()
                    s.save()
                    file_check_flag = True
                else:
                    pub_msg(self.memory_queue,"文件效验失败\n\n")
                    models.Logger.objects.create(app=self.app_obj,server=s,status=1,description="文件效验失败\n\n",task=self.task_obj,user=self.user)


            if file_check_flag and s.server_status:
                cmd = 'ln -svf %s %s' % (os.path.join(self.app_obj.app_path,file_name),"/xebest/tomcat/webapps/current.war")
                pub_msg(self.memory_queue,cmd+'\n')
                ret = ssh_handler.remote_cmd(cmd,send_ret_to_queue=True)
                if ret['return_code'] == 0:
                    models.Logger.objects.create(app=self.app_obj,server=s,status=0,description=ret["msg"],task=self.task_obj,user=self.user)
                    msg = "软链接创建成功\n\n"
                    pub_msg(self.memory_queue,msg)

                else:
                    models.Logger.objects.create(app=self.app_obj,server=s,status=1,description=ret["msg"],task=self.task_obj,user=self.user)
                    successfull = False
                    msg = "软链接创建失败\n\n"
                    pub_msg(self.memory_queue,msg)



        kwargs = {
            'action_type':'rollback_from_publish_server',
            'ret_status': successfull,
            'ret_msg' :msg,
        }
        pub_msg(self.memory_queue,None,stop=True,kwargs=kwargs)

    def process(self):
        sub_ret = self.update_checkout_root()
        if sub_ret["status"]:
            sub_ret = self.complie_java_gen_war()
            if sub_ret["status"]:
                self.backup_current_war()
                pub_msg(self.memory_queue,None,stop=True)
            else:
                pass
        else:
            pass