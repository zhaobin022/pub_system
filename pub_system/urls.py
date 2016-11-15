"""pub_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from cmdb import views
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',views.index ),
    url(r'^app_list$', views.app_list),
    url(r'^server_list$', views.server_list),
    url(r'^gen_war_file$', views.gen_war_file),
    url(r'^get_ret$', views.get_ret),
    # url(r'^get_ret_ws$', views.get_ret_ws),
    url(r'^pub_war_to_server$', views.pub_war_to_server),
    url(r'^reboot_app$', views.reboot_app),
    url(r'^start_app$', views.start_app),
    url(r'^stop_app$', views.stop_app),
    url(r'^check_app', views.check_app),
    url(r'^get_remote_backup_list$', views.get_remote_backup_list),
    url(r'^get_local_backup_list', views.get_local_backup_list),
    url(r'^delete_remote_backup$', views.delete_remote_backup),
    url(r'^delete_local_backup', views.delete_local_backup),
    url(r'^rollback_select_backup$', views.rollback_select_backup),
    url(r'^rollback_from_publish_server', views.rollback_from_publish_server),
    url(r'^get_server_list$', views.get_server_list),
    url(r'^get_app_list$', views.get_app_list),
    url(r'^log_list$', views.log_list),
    url(r'^get_log_list$', views.get_log_list),
    url(r'^log_detail$', views.log_detail),
    url(r'^login$', views.login_view,name="login"),
    url(r'^logout$', views.logout_view),
    url(r'^403$', views.page_403),
    url(r'^resetpassword$', views.reset_password,name="reset_password"),
    url(r'^change_status$', views.change_status),
    url(r'^change_server_status$', views.change_server_status),
    url(r'^init_app$', views.init_app),
]
