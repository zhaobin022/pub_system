from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django import forms


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    alias = models.CharField(max_length=30)

    def __unicode__(self):
        return self.alias


class GroupProfile(models.Model):
    group = models.OneToOneField(Group)
    group_name = models.CharField(max_length=30)
    summary = models.CharField(max_length=255)
    apps = models.ManyToManyField("App")


    def __unicode__(self):
        return self.group_name


class Scripts(models.Model):
    script_name = models.CharField(max_length=30,unique=True)
    script_path = models.CharField(max_length=100)

    def __unicode__(self):
        return self.script_name


class App(models.Model):
    app_name =  models.CharField(max_length=30,unique=True)
    summary = models.CharField(max_length=100,blank=True,null=True)
    upload_path = models.CharField(max_length=100)
    app_path = models.CharField(max_length=100,default='release')
    backup_path = models.CharField(max_length=100)
    start_script_path = models.ForeignKey(Scripts,related_name='start_script')
    stop_script_path = models.ForeignKey(Scripts,related_name='stop_script')
    check_script_path = models.ForeignKey(Scripts,related_name='check_script',blank=True,null=True)
    publish_date = models.DateTimeField(null=True,blank=True)
    svn_url =  models.CharField(max_length=255,null=True,blank=True)
    svn_username = models.CharField(max_length=100,null=True,blank=True)
    svn_password = models.CharField(max_length=100,null=True,blank=True)
    def __unicode__(self):
        return self.app_name


class ServerGroup(models.Model):
    group_name = models.CharField(max_length=30,unique=True)
    servers = models.ManyToManyField('Server')
    description = models.TextField()

    def __unicode__(self):
        return self.group_name


class OsUser(models.Model):
    username =  models.CharField(max_length=30,unique=True)
    server_group = models.ManyToManyField(ServerGroup)


class Server(models.Model):
    server_name = models.CharField(max_length=30,unique=True)
    ipaddr = models.GenericIPAddressField(null=True,unique=True)
    port = models.IntegerField(blank=True,null=True,default='22310')
    username = models.CharField(max_length=30,null=True,default='root')
    password = models.CharField(max_length=40,null=True)
    new_password = models.CharField(max_length=40,null=True,blank=True)
    app = models.ForeignKey(App,null=True,blank=True)
    app_status = models.BooleanField(default=True)
    publish_date = models.DateTimeField(blank=True,null=True)
    rollbackup_status = models.CharField(max_length=30,null=True,blank=True)
    task = models.ForeignKey('TaskLog',null=True,blank=True)
    ssh_check_status = (
        (0, 'Successfull'),
        (1, 'Failed'),
    )
    ssh_check = models.IntegerField(choices=ssh_check_status,blank=True,null=True,default=1)
    change_password_status = (
        (0, 'Successfull'),
        (1, 'Failed'),
    )
    change_password_tag = models.IntegerField(choices=change_password_status,blank=True,null=True,default=1)
    change_password_time = models.DateTimeField(blank=True,null=True)
    current_version = models.CharField(max_length=255,null=True,blank=True)
    server_status =  models.BooleanField(default=True)

    def __unicode__(self):
        return self.server_name


class Logger(models.Model):
    happened_time = models.DateTimeField(auto_now_add=True)
    app = models.ForeignKey(App,null=True,blank=True)
    server = models.ForeignKey(Server,blank=True,null=True)
    user = models.ForeignKey(User,blank=True,null=True)
    operation_status = (
        (0, 'Successfull'),
        (1, 'Failed'),
    )
    status = models.IntegerField(choices=operation_status,blank=True,null=True)
    description = models.TextField()
    task = models.ForeignKey('TaskLog',null=True)
    #
    def __unicode__(self):
        return self.task.get_task_type_display()


class TaskLog(models.Model):
    task_type_list = (
        (0, 'Publish'),
        (1, 'Backup'),
        (2, 'Rollback'),
        (3, 'Startup'),
        (4, 'Shutdown'),
        (5, 'DeleteBackup'),
        (6, 'UnzipWar'),
        (7, 'CheckApp'),
        (8, 'GenWarFile'),
        (9, 'RebootApp'),
        (10,'DeleteRemoteBackup'),
        (11,'RollbackFromServer'),
        (12,'CheckoutApp'),
    )
    task_type = models.IntegerField(choices=task_type_list,null=True,blank=True)
    total_count = models.IntegerField(default=0,blank=True,null=True)
    complete_count = models.IntegerField(default=0,blank=True,null=True)

    def __unicode__(self):
        return str(self.id)


class JumpServerAudit(models.Model):
    happened_time = models.DateTimeField(auto_now_add=True)
    username =  models.CharField(max_length=30)
    content = models.TextField()

    def __unicode__(self):
        return str(self.id)