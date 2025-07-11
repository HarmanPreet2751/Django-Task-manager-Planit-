from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('user-details/', views.user_details_view, name='user_details'),
    path('file-manager/', views.file_manager, name='file_manager'),
    path('file/<int:file_id>/', views.serve_file, name='serve_file'),
    path('file/delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('loginuser/', views.login_user, name='login_user'),
    path('registeruser/', views.register_user, name='register_user'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('check-username/', views.check_username, name='check_username'),
    path('add_task/', views.add_task, name='add_task'),
    path('delete_task/', views.delete_task, name='delete_task'),
    path('update_task/', views.update_task, name='update_task'),
]