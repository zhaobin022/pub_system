# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.shortcuts import HttpResponse
from cmdb import models
from django.db.models import Count
from cmdb.controller import PublishHandler
import pika
import threading
import Queue
import json
from utils.ssh_tools import SshHandler
from utils.tools import format_remote_dir_output
from utils.tools import filter_the_null_obj
from utils.tools import local_exec_cmd
from utils.tools import local_exec_cmd_nomq
from pub_system import settings as django_settings
from config import settings as custom_settings
from django.db.models import Q
import os
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import logging
from datetime import timedelta
logger = logging.getLogger('web_apps')
try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET


GLOBAL_QUEUE_DIC = {}


def auth_required(view):
    """身份认证装饰器，
    :param view:
    :return:
    """
    def decorator(request, *args, **kwargs):
        app_get_id =  request.GET.get('app_id')
        app_post_id =  request.POST.get('app_id')
        if app_get_id and app_get_id.strip() != '' and app_get_id.isdigit():
            app_ids = []
            for g in  request.user.groups.select_related():
                ids = g.groupprofile.apps.select_related().values_list("id")
                app_ids.extend(ids)
            app_ids = map(lambda x:str(x[0]),app_ids)
            app_ids = set(app_ids)
            app_ids = list(app_ids)
            if app_get_id in app_ids:
                return view(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/403')


        elif app_post_id and app_post_id.strip() != '' and app_post_id.isdigit():
            app_ids = []
            for g in  request.user.groups.select_related():
                ids = g.groupprofile.apps.select_related().values_list("id")
                app_ids.extend(ids)
            app_ids = map(lambda x:str(x[0]),app_ids)
            app_ids = set(app_ids)
            app_ids = list(app_ids)
            if app_post_id in app_ids:
                return view(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/403')

        return HttpResponseRedirect('/403')
    return decorator


# @auth_required
@login_required
def get_ret(request):
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        ret_queue_name = 'task_ret_%s'% task_id

        ret = {'status':False,
               'msg':''
               }

        if  GLOBAL_QUEUE_DIC.has_key(ret_queue_name):
            q = GLOBAL_QUEUE_DIC[ret_queue_name]
        else:
            GLOBAL_QUEUE_DIC[ret_queue_name] = Queue.Queue()
            q = GLOBAL_QUEUE_DIC[ret_queue_name]
        try:
            temp = q.get(timeout=custom_settings.GET_RESULT_TIMEOUT)
            temp = json.loads(temp)
            ret['status'] = True


            if temp.has_key('stop') and temp['stop'] == True:
                ret['stop'] = True
                ret['action_type'] = temp['action_type']
                if temp.has_key("ret_status"):
                    ret['ret_status'] = temp['ret_status']
                    ret['ret_msg'] = temp['ret_msg']

                del GLOBAL_QUEUE_DIC[ret_queue_name]
            if temp.has_key('data'):
                ret['msg'] = temp['data']
            return HttpResponse(json.dumps(ret))
        except Queue.Empty,e:
            ret['msg'] = 'get_timeout'
            del GLOBAL_QUEUE_DIC[ret_queue_name]
            return HttpResponse(json.dumps(ret))
        except Exception,e:
            print str(e)
            del GLOBAL_QUEUE_DIC[ret_queue_name]
        finally:
            print 'GLOBAL_QUEUE_DIC',GLOBAL_QUEUE_DIC


def pre_process(app_id,task_obj,func,user,args=None):
    app_obj = models.App.objects.get(id=app_id)
    ret_queue_name = 'task_ret_%s'% task_obj.id

    if  GLOBAL_QUEUE_DIC.has_key(ret_queue_name):
        q = GLOBAL_QUEUE_DIC[ret_queue_name]
    else:
        GLOBAL_QUEUE_DIC[ret_queue_name] = Queue.Queue()
        q = GLOBAL_QUEUE_DIC[ret_queue_name]
    publish_handler = PublishHandler(app_obj=app_obj,task_obj=task_obj,memory_queue=q,user=user)
    if hasattr(publish_handler,func):
        handler_func = getattr(publish_handler,func)

    if args:
        t = threading.Thread(target=handler_func,args=args)
    else:
        t = threading.Thread(target=handler_func)
    t.start()


def page_403(request):
    if request.method == 'GET':
        return render(request,'403.html',{})

@login_required
def index(request):
    if request.method == "GET":
        return render(request,'layout.html',{})


@login_required
def app_list(request):
    if request.method == "GET":
        # app_list = models.App.objects.annotate(Count('server'))
        return render(request,'app_list.html',{})


@login_required
def get_app_list(request):
    if request.method == "GET":
        user = request.user
        apps_list = []
        for g in user.groups.select_related():
            apps_list.extend(g.groupprofile.apps.select_related().annotate(Count('server')).values_list("app_name","summary","server__count","id"))
        apps_list = set(apps_list)
        # app_list = models.App.objects.annotate(Count('server')).values_list("app_name","summary","server__count","id")
        return HttpResponse(json.dumps(list(apps_list)))


@auth_required
@login_required
def server_list(request):
    if request.method == "GET":
        app_id =  request.GET.get('app_id')
        if app_id:
            app_obj = models.App.objects.get(id=app_id)
        return render(request,'server_list.html',{'app_obj':app_obj})

@auth_required
@login_required
def get_server_list(request):
    '''
    :param request:
    :return:
    '''
    if request.method == 'GET':
        app_id =  request.GET.get('app_id')
        if app_id:
            ret = {"data":''}
            server_list = list(models.Server.objects.filter(app__id = app_id ).values(
                'id',
                'server_name',
                'ipaddr',
                'app_status',
                'publish_date',
                'current_version',
                'server_status',
            ))
            for s in server_list:
                if s["app_status"]:
                    s["app_status"] = '<span style="color:green;">ONLINE<span>'
                else:
                    s["app_status"] = '<span style="color:red;">OFFLINE<span>'

                if s['publish_date']:
                    s['publish_date']+=timedelta(hours=8)
                    s['publish_date'] = s['publish_date'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    s['publish_date'] = "没有更新"

                if s["server_status"]:
                    s["server_status"] = '<button type="button" class="btn btn-sm btn-success" onclick="change_status(%s)">DISABLE</button>' % s["id"]
                else:
                    s["server_status"] = '<button type="button" class="btn btn-sm btn-danger" onclick="change_status(%s)">ENABLE</button>' % s["id"]

                if s['ipaddr']:
                    s['ipaddr'] = '<a href="http://%s" target="_blank">%s</a>' % (s['ipaddr'],s['ipaddr'])
                if not s["current_version"]:
                    s["current_version"] = '无当前版本'
            ret["data"] = server_list
            return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def gen_war_file(request):
    if request.method == "POST":
        app_id =  request.POST.get('app_id')
        ret = {
            "status": False,
            "message": '',
            "if_has_sub": False,
            "sub_info": []
        }
        if app_id:
            app_obj = models.App.objects.get(id = app_id)
            if app_obj:
                task_obj = models.TaskLog(task_type=8)
                task_obj.save()
                ret_queue_name = 'task_ret_%d' % task_obj.id
                # channel = MQ_CONN.channel()
                if GLOBAL_QUEUE_DIC.has_key(ret_queue_name):
                    q = GLOBAL_QUEUE_DIC[ret_queue_name]
                else:
                    q = Queue.Queue()
                    GLOBAL_QUEUE_DIC[ret_queue_name] = q
                gen_war_obj = PublishHandler(app_obj=app_obj,task_obj=task_obj,memory_queue = q,user=request.user)
                t = threading.Thread(target=gen_war_obj.process)
                t.start()
                ret["status"] = True
                ret["task_id"] = task_obj.id
            else:
                ret["message"] = "无效的应用id"
        else:
            ret["message"] = "应用id不能为空"
        return HttpResponse(json.dumps(ret))


@auth_required
@login_required
def pub_war_to_server(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=0)
        task_obj.save()
        app_id =  request.POST.get('app_id')


        pre_process(app_id,task_obj,"publish_war",request.user)

        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def reboot_app(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=9)
        task_obj.save()
        app_id =  request.POST.get('app_id')
        pre_process(app_id,task_obj,"reboot_app",request.user)

        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def start_app(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=3)
        task_obj.save()
        app_id =  request.POST.get('app_id')
        pre_process(app_id,task_obj,"start_app",request.user)
        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def stop_app(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=4)
        task_obj.save()
        app_id =  request.POST.get('app_id')
        pre_process(app_id,task_obj,"stop_app",request.user)

        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def check_app(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=7)
        task_obj.save()
        app_id =  request.POST.get('app_id')

        pre_process(app_id,task_obj,"check_app",request.user)

        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))


@auth_required
@login_required
def init_app(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=12)
        task_obj.save()
        app_id =  request.POST.get('app_id')
        pre_process(app_id,task_obj,"init_app_env",request.user)

        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))


@auth_required
@login_required
def get_remote_backup_list(request):
    if request.method == 'GET':
        app_id =  request.GET.get('app_id')

        app_obj = models.App.objects.get(id=app_id)
        server_obj = models.Server.objects.filter(app=app_obj).first()
        cmd = '''ls -tlh --time-style="+%%Y-%%m-%%d %%H:%%M:%%S"  %s''' % app_obj.app_path
        ssh_handler = SshHandler(server_obj.ipaddr,server_obj.port,server_obj.username,server_obj.password)
        ssh_ret = ssh_handler.remote_cmd(cmd)
        ret = {}
        if ssh_ret['status'] == True:
            sub_ret = ssh_ret['msg']
            file_list = sub_ret.split("\n")
            file_list = map(format_remote_dir_output,file_list)
            file_list = filter(filter_the_null_obj,file_list)
            ret['data'] = file_list
        else:
            ret['data'] = ''
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def get_local_backup_list(request):
    if request.method == 'GET':
        app_id =  request.GET.get('app_id')

        app_obj = models.App.objects.get(id=app_id)
        workspace = os.path.join(os.path.join(django_settings.BASE_DIR,custom_settings.WORKSPACE),app_obj.app_name)
        local_war_file_path = os.path.join(workspace,custom_settings.WAR_FILE_DIR)
        if not os.path.exists(local_war_file_path):
            ret = {'data':''}
            return HttpResponse(json.dumps(ret))
        server_obj = models.Server.objects.filter(app=app_obj).first()
        cmd = '''ls -tlh --time-style="+%%Y-%%m-%%d %%H:%%M:%%S"  %s''' % local_war_file_path
        try:
            ssh_ret = local_exec_cmd_nomq(cmd)
            ret = {}
            if ssh_ret['status'] == True:
                sub_ret = ssh_ret['message']
                file_list = sub_ret.split("\n")
                file_list = map(format_remote_dir_output,file_list)
                file_list = filter(filter_the_null_obj,file_list)
                ret['data'] = file_list
                return HttpResponse(json.dumps(ret))
        except Exception,e:
             return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def delete_remote_backup(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=10)
        task_obj.save()
        app_id =  request.POST.get('app_id')
        file_name =  request.POST.get('file_name')
        pre_process(app_id,task_obj,"delete_remote_backup",request.user,args=(file_name,))

        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def delete_local_backup(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=5)
        task_obj.save()
        app_id =  request.POST.get('app_id')
        file_name =  request.POST.get('file_name')
        pre_process(app_id,task_obj,"delete_local_backup",request.user,args=(file_name,))

        ret = {
            "status": True,
            "message": '',
            'task_id':task_obj.id
        }
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def rollback_select_backup(request):
    if request.method == 'POST':
        task_obj = models.TaskLog(task_type=2)
        task_obj.save()
        app_id =  request.POST.get('app_id')
        file_name =  request.POST.get('file_name')
        pre_process(app_id,task_obj,"rollback_select_backup",request.user,args=(file_name,))

        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def rollback_from_publish_server(request):
    if request.method == 'POST':

        app_id =  request.POST.get('app_id')
        file_name =  request.POST.get('file_name')
        task_obj = models.TaskLog(task_type=11)
        task_obj.save()
        pre_process(app_id,task_obj,"rollback_from_publish_server",request.user,args=(file_name,))

        ret = {
                "status": True,
                "message": '',
                'task_id':task_obj.id
            }
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def log_list(request):
    if request.method == 'GET':
        app_id =  request.GET.get('app_id')
        return render(request,'log_list.html',{'app_id':app_id})

@auth_required
@login_required
def get_log_list(request):
    if request.method == 'GET':
        app_id =  request.GET.get('app_id')
        keyword = request.GET.get("search[value]")
        dir = request.GET.get("order[0][dir]")
        column = request.GET.get("order[0][column]")

        con = Q()
        if keyword:
            q1 = Q()
            q1.connector = 'OR'
            q1.children.append(('server__server_name__icontains', keyword))
            q1.children.append(('user__username__icontains', keyword))

            task_list = models.TaskLog.task_type_list
            for k,v in task_list:
                if v.lower().find(keyword.lower()) != -1:
                    q1.children.append(('task__task_type', k))

            q2 = Q()
            q2.connector = 'OR'
            q2.children.append(('app__id', app_id))
            con.add(q1, 'AND')
            con.add(q2, 'AND')

        else:
            con.add(('app__id', app_id),'AND')

        draw = int(request.GET.get('draw', '5'))
        page_length = int(request.GET.get('length', '5'))
        page_start = int(request.GET.get('start', '0'))
        page_end = page_start + page_length
        total_length = models.Logger.objects.filter(con).count()
        rest = {
            "draw": draw,   # 本次加载记录数量
            "recordsTotal": total_length,
            "recordsFiltered": total_length,
            "data": []
        }
        # page_data = models.Logger.objects.filter(con).order_by("id")[page_start:page_end]
        if column == '0':
            if dir == 'asc':
                page_data = models.Logger.objects.filter(con).order_by("-id")[page_start:page_end]
            else:
                page_data = models.Logger.objects.filter(con).order_by("id")[page_start:page_end]
        elif column == '1':
            if dir == 'asc':
                page_data = models.Logger.objects.filter(con).order_by("user")[page_start:page_end]
            else:
                page_data = models.Logger.objects.filter(con).order_by("-user")[page_start:page_end]
        elif column == '2':
            if dir == 'asc':
                page_data = models.Logger.objects.filter(con).order_by("app__app_name")[page_start:page_end]
            else:
                page_data = models.Logger.objects.filter(con).order_by("-app__app_name")[page_start:page_end]
        elif column == '3':
            if dir == 'asc':
                page_data = models.Logger.objects.filter(con).order_by("server__server_name")[page_start:page_end]
            else:
                page_data = models.Logger.objects.filter(con).order_by("-server__server_name")[page_start:page_end]
        elif column == '4':
            if dir == 'asc':
                page_data = models.Logger.objects.filter(con).order_by("task__task_type")[page_start:page_end]
            else:
                page_data = models.Logger.objects.filter(con).order_by("-task__task_type")[page_start:page_end]
        elif column == '5':
            if dir == 'asc':
                page_data = models.Logger.objects.filter(con).order_by("happened_time")[page_start:page_end]
            else:
                page_data = models.Logger.objects.filter(con).order_by("-happened_time")[page_start:page_end]


        data = []
        for item in page_data:
            temp = []
            temp.append(item.id)
            if item.user:
                temp.append(item.user.username)
            else:
                temp.append('')
            temp.append(item.app.app_name)
            if item.server:
                temp.append(item.server.server_name)
            else:
                temp.append('')

            temp.append(item.task.get_task_type_display())

            item.happened_time+=timedelta(hours=8)

            time = item.happened_time.strftime("%Y-%m-%d %H:%M:%S")
            temp.append(time)
            data.append(temp)
        rest["data"] = data
        return HttpResponse(json.dumps(rest))         #


@auth_required
@login_required
def change_status(request):
    if request.method == 'POST':
        ret = {
            'status':True,
            'msg':''
        }

        app_id =  request.POST.get('app_id')
        server_id =  request.POST.get('server_id')
        if not server_id:
            ret['status'] = False
            ret['msg'] = 'server_id 不能为空'
            return HttpResponse(json.dumps(ret))
        server_obj = models.Server.objects.get(id=server_id)
        if server_obj.server_status:
            server_obj.server_status=False
        else:
            server_obj.server_status=True
        server_obj.save()
        ret['msg'] = u'修改服务器状态成功'
        return HttpResponse(json.dumps(ret))


@auth_required
@login_required
def change_server_status(request):
    if request.method == 'POST':
        ret = {
            'status':True,
            'msg':''
        }

        app_id =  request.POST.get('app_id')
        operation_type =  request.POST.get('operation_type')
        if not operation_type or not app_id:
            ret['status'] = False
            ret['msg'] = '参数不正确'
            return HttpResponse(json.dumps(ret))
        server_list = models.Server.objects.filter(app__id=app_id)
        if operation_type == 'enable_all':
            for s in server_list:
                if not s.server_status:
                    s.server_status = True
                    s.save()

        elif operation_type == 'disable_all':
            for s in server_list:
                if s.server_status:
                    s.server_status = False
                    s.save()
        elif operation_type == 'reverse_all':
            for s in server_list:
                if s.server_status:
                    s.server_status = False
                else:
                    s.server_status = True
                s.save()
        ret['msg'] = '执行成功'
        return HttpResponse(json.dumps(ret))

@auth_required
@login_required
def log_detail(request):
    if request.method == 'GET':
        id = request.GET.get("id")

        log_obj = models.Logger.objects.get(id=id)
        return render(request,'log_detail.html',{'log_obj':log_obj})

def login_view(request):
    if request.method == 'GET':
        return render(request,'login.html',{})

    elif request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            errors = '用户名或密码错误!'
            #验证失败，暂时不做处理
            return render(request, 'login.html', {'errors':errors})


@login_required
def logout_view(request):
    if request.method == 'GET':
        logout(request)
        return render(request, 'login.html', {})


@login_required
def reset_password(request):
    if request.method == 'GET':
        return render(request, 'reset_password.html', {})
    elif request.method == 'POST':
        repassword = request.POST['repassword']
        password = request.POST['password']
        oldpassword = request.POST['oldpassword']
        user = authenticate(username=request.user.username, password=oldpassword)
        errors = ""
        successsfull=""
        if user is not None and user.is_active:
            if password.strip() == repassword.strip():
                user = request.user
                user.set_password(password)
                user.save()
                logout(request)
                successsfull = u'''<a href="/login">修改密码成功,请重新登录</a>'''

            else:
                errors = u'新密码不一致'

        else:
            errors = u'旧密码输入错误'
        return render(request, 'reset_password.html', {"successsfull":successsfull,"errors":errors})




