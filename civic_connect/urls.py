from django.urls import path
from connect import admin
from connect import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('post/', views.post_query, name='post' ),
    #path('api/posts/<int:post_id>/vote/', views.toggle_vote, name='toggle_vote'),
    path('api/posts/<int:post_id>/vote-status/', views.vote_status, name='vote_status'),
    path('view_all_posts/', views.view_all_posts, name='view_all_post'),
    path('api/posts/<int:post_id>/public_vote/', views.public_toggle_vote, name='public_vote'),

]