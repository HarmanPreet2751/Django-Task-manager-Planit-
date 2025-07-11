from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('groups/',views.groups_view,name='groups'),
    path('group/create/', views.group_create, name='group_create'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
]