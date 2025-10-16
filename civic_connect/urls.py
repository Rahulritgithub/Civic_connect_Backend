from django.urls import path
from connect import admin
from connect import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('post/', views.post_query, name='post' ),

]