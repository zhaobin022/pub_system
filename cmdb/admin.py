from django.contrib import admin
from cmdb.models import *
from django import forms

# Register your models here.

class LoggerAdmin(admin.ModelAdmin):

    def get_task_type(self,obj):
        return obj.task.get_task_type_display()
    def get_server_name(self,obj):
        if obj.server:
            return obj.server.server_name
        else:
            return "no server"
    list_display = ('id','user','app','get_server_name','get_task_type','status','description','happened_time')
# #    list_filter = ('operation','username','happened_time')
# #     list_filter = ('operation','username','happened_time','server__server_name','server__app__app_name')
#     search_fields = ('operation','username')
#     # readonly_fields = Logger._meta.get_all_field_names()


class ServerAdmin(admin.ModelAdmin):
 #   def get_group_name(self,obj):
  #      if obj.server_group:
   #         return obj.server_group.group_name
    #    else:
     #       return 'not in any group'
    list_display = ('id','server_name','ipaddr','port','username','password','app',)
    list_editable = ('app',)
#    list_filter = ('operation','username','happened_time')
    search_fields = ('server_name','ipaddr',)


class TaskLogAdmin(admin.ModelAdmin):
    def get_task_type_name(self,obj):
        return obj.get_task_type_display()
    list_display = ('id','get_task_type_name')
 #   readonly_fields = TaskLog._meta.get_all_field_names()

    #list_display = ('id',)
#    list_filter = ('operation','username','happened_time')
class OsUserAdmin(admin.ModelAdmin):
    list_display = ('id','username')


# class AppForm(forms.ModelForm):
#     class Meta:
#         widgets = {
#             'svn_password': forms.PasswordInput,
#         }


class AppForm(forms.ModelForm):
    svn_password = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'type':'password'}))
    class Meta:
        forms.model = App


class AppAdmin(admin.ModelAdmin):
    form = AppForm



admin.site.register(Server,ServerAdmin)
admin.site.register(App,AppAdmin)
admin.site.register(ServerGroup)
admin.site.register(TaskLog,TaskLogAdmin)
admin.site.register(Logger,LoggerAdmin)
admin.site.register(OsUser,OsUserAdmin)
admin.site.register(JumpServerAudit)
admin.site.register(UserProfile)
admin.site.register(GroupProfile)
admin.site.register(Scripts)