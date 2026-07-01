"""
URL configuration for drinkshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from products import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.mode_selection),          # 告诉系统，如果顾客访问首页('')，就让服务员拿出饮料菜单
    path('menu/', views.standard_menu),      # /menu/ ：官方饮品大厅
    path('diy/', views.diy_menu),            # /diy/  ：DIY 调配实验室
    path('transition/<str:mode>/', views.transition_view),  #动态中转站通道（<str:mode> 代表它可以接收变化的名字）
    path('add_to_cart/', views.add_to_cart), # 处理加入动作
    path('cart/', views.show_cart),          # 购物车查看页面
    path('clear-cart/', views.clear_cart),   # 指向清空购物车的服务员
    path('login/', views.login_view),        # 这两行门禁网线
    path('register/', views.register_view),
    path('logout/', views.logout_view),      # 退出登录
    path('checkout/', views.checkout),       # 指向确认下单的处理函数
    path('register_loading/', views.loading_view),   # 指向跳转过渡页
    path('add_diy_to_cart/', views.add_diy_to_cart),  # DIY 合成通道
    path('tng_qr/', views.tng_qr_view, name='tng_qr'),
    path('success/', views.success_view),
    path('wallet/', views.user_wallet, name='wallet'),
    path('remove-item/', views.remove_item, name='remove_item'),  # 购物车单项删除网线




]
